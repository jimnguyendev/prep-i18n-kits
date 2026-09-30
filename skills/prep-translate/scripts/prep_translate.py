#!/usr/bin/env python3
"""Deterministic half of the prep-translate skill.

The model does the translating; this script does everything that must not
depend on the model's memory or mood: finding what needs translating, pulling
the reference corpus of BOTH products, checking placeholders and glossary
terms, and writing back to Tolgee without clobbering a human's edit.

Standard library only, so it runs in the Node repo and the Flutter repo alike.

    prep_translate.py queue    --project web [--langs vi,th] [--mode missing|outdated|both] [--keys a.b,c.d] [--changed-since REF]
    prep_translate.py context  --queue queue.json [--out context.json]
    prep_translate.py validate --context context.json --translations out.json
    prep_translate.py write    --context context.json --translations out.json [--apply]

Every command prints JSON (or a table for `write` dry-runs) and never writes to
Tolgee unless `write --apply` is given.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
CONFIG = json.loads((SKILL_DIR / "projects.json").read_text())
SOURCE = CONFIG["sourceLanguage"]
TARGETS = CONFIG["targetLanguages"]
PLURAL_SUFFIXES = ("zero", "one", "two", "few", "many", "other")


def die(msg: str, code: int = 2) -> None:
    print(f"prep-translate: {msg}", file=sys.stderr)
    sys.exit(code)


def canon_lang(tag: str) -> str:
    """Tolgee project 2 stores `zh-hans`, the app files use `zh-Hans`."""
    for t in [SOURCE, *TARGETS]:
        if t.lower() == tag.lower():
            return t
    return tag


# --------------------------------------------------------------------------
# Repos and credentials
# --------------------------------------------------------------------------


def git_root(start: Path) -> Path | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        return Path(out)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def remote_of(root: Path) -> str:
    try:
        return subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                              capture_output=True, text=True).stdout.strip()
    except FileNotFoundError:
        return ""


def is_project_repo(root: Path, name: str) -> bool:
    """Identify a checkout by its origin remote, not its folder name — people
    clone into whatever directory they like; the GitLab path is stable."""
    return CONFIG["projects"][name]["gitRemote"] in remote_of(root)


def current_project() -> str | None:
    here = git_root(Path.cwd())
    if not here:
        return None
    return next((n for n in CONFIG["projects"] if is_project_repo(here, n)), None)


def repo_path(name: str) -> Path | None:
    """Where a project's repo lives on this machine.

    `PREP_<NAME>_REPO` wins; otherwise the current repo if it is that project;
    otherwise the first sibling of the current repo whose remote matches.
    """
    env = os.environ.get(f"PREP_{name.upper()}_REPO")
    if env:
        return Path(env).expanduser()
    here = git_root(Path.cwd())
    if not here:
        return None
    if is_project_repo(here, name):
        return here
    guess = here.parent / CONFIG["projects"][name].get("repoDirName", "")
    siblings = sorted(p for p in here.parent.iterdir() if p.is_dir() and p != guess)
    for p in [guess, *siblings]:
        if (p / ".git").exists() and is_project_repo(p, name):
            return p
    return None


def api_key(name: str) -> str | None:
    """Same lookup order as scripts/i18n-env.sh: the process env first, then
    the repo's gitignored `.env.development.local`. The key is never printed."""
    env_name = CONFIG["projects"][name]["tolgee"]["apiKeyEnv"]
    if os.environ.get(env_name):
        return os.environ[env_name]
    root = repo_path(name)
    if root:
        f = root / ".env.development.local"
        if f.exists():
            for line in f.read_text().splitlines():
                if line.startswith(env_name + "="):
                    return line.split("=", 1)[1].strip().strip('"') or None
    return None


# --------------------------------------------------------------------------
# Tolgee REST
# --------------------------------------------------------------------------


def tolgee(name: str, method: str, path: str, body: dict | None = None, query: list | None = None):
    t = CONFIG["projects"][name]["tolgee"]
    key = api_key(name)
    if not key:
        die(f"no Tolgee key for '{name}' (set {t['apiKeyEnv']})")
    url = f"{t['apiUrl']}/v2/projects/{t['projectId']}{path}"
    if query:
        url += "?" + urllib.parse.urlencode(query)
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-API-Key", key)
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        die(f"Tolgee {method} {path} → {e.code}: {e.read().decode(errors='replace')[:400]}")


def tolgee_enabled(name: str) -> bool:
    t = CONFIG["projects"][name]["tolgee"]
    return bool(t.get("projectId")) and api_key(name) is not None


def fetch_tolgee_rows(name: str, extra_query: list | None = None, snapshot: str | None = None) -> list[dict]:
    """All keys of a Tolgee project as rows in the /translations shape."""
    if snapshot:
        pages = [json.loads(Path(snapshot).read_text())]
    else:
        pages, cursor = [], None
        while True:
            q = [("size", "1000")] + [("languages", l) for l in [SOURCE, *TARGETS]]
            q += extra_query or []
            if cursor:
                q.append(("cursor", cursor))
            page = tolgee(name, "GET", "/translations", query=q)
            pages.append(page)
            cursor = page.get("nextCursor")
            if not cursor or not page.get("_embedded", {}).get("keys"):
                break
    rows = []
    for page in pages:
        for k in page.get("_embedded", {}).get("keys", []):
            tr = {canon_lang(l): v for l, v in (k.get("translations") or {}).items()}
            rows.append({
                "key": k["keyName"],
                "keyId": k.get("keyId"),
                "namespace": k.get("keyNamespace"),
                "description": k.get("keyDescription"),
                "maxChars": k.get("keyMaxCharLimit"),
                "isPlural": k.get("keyIsPlural", False),
                "text": {l: (v or {}).get("text") for l, v in tr.items()},
                "state": {l: (v or {}).get("state") for l, v in tr.items()},
                "outdated": {l: bool((v or {}).get("outdated")) for l, v in tr.items()},
            })
    return rows


# --------------------------------------------------------------------------
# Repo locale files (fallback corpus, and the only source for the app today)
# --------------------------------------------------------------------------


def flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            out.update(flatten(v, f"{prefix}{k}."))
        elif isinstance(v, str):
            out[f"{prefix}{k}"] = v
    return out


def i18next_to_icu(flat: dict[str, str]) -> dict[str, str]:
    """`{{name}}` → `{name}`; `k_one`/`k_other` → one ICU plural under `k`,
    so web-file strings compare like the ICU text Tolgee serves over REST."""
    conv = {k: re.sub(r"\{\{\s*([\w]+)(\s*,[^}]*)?\s*\}\}", lambda m: "{" + m.group(1) + (m.group(2) or "") + "}", v)
            for k, v in flat.items()}
    groups: dict[str, dict[str, str]] = {}
    for k, v in list(conv.items()):
        m = re.match(rf"(.+)_({'|'.join(PLURAL_SUFFIXES)})$", k)
        if m:
            groups.setdefault(m.group(1), {})[m.group(2)] = v
    for base, forms in groups.items():
        if "other" not in forms:
            continue
        branches = " ".join(f"{f} {{{re.sub(r'{count(, number)?}', '#', t)}}}" for f, t in forms.items())
        conv[base] = f"{{count, plural, {branches}}}"
        for f in forms:
            conv.pop(f"{base}_{f}", None)
    return conv


def file_rows(name: str) -> list[dict]:
    proj = CONFIG["projects"][name]
    root = repo_path(name)
    if not root:
        return []
    fcfg = proj["files"]
    d = root / fcfg["dir"]
    texts: dict[str, dict[str, str]] = {}
    for lang in [SOURCE, *TARGETS]:
        fname = fcfg.get("fileTags", {}).get(lang, lang) + ".json"
        p = d / fname
        if not p.exists():
            continue
        flat = flatten(json.loads(p.read_text()))
        if fcfg["format"] == "i18next":
            flat = i18next_to_icu(flat)
        texts[lang] = flat
    rows = []
    for key, en in texts.get(SOURCE, {}).items():
        rows.append({
            "key": key, "keyId": None, "namespace": None, "description": None, "maxChars": None,
            "isPlural": bool(re.search(rf"\.({'|'.join(PLURAL_SUFFIXES)})$", key)) or "plural," in en,
            "text": {l: texts.get(l, {}).get(key) for l in [SOURCE, *TARGETS]},
            "state": {}, "outdated": {},
        })
    return rows


def corpus(name: str, snapshot: str | None = None) -> tuple[list[dict], str]:
    if snapshot:
        return fetch_tolgee_rows(name, snapshot=snapshot), "snapshot"
    if tolgee_enabled(name):
        return fetch_tolgee_rows(name), "tolgee"
    return file_rows(name), "repo-files"


# --------------------------------------------------------------------------
# Placeholders: ICU (Tolgee/web), i18next {{x}}, easy_localization {} / {x}
# --------------------------------------------------------------------------


def parse_icu(s: str) -> dict:
    """Tiny ICU walker. Returns argument names, plural/select args with their
    branch keys, and whether `#` appears inside a plural branch. Apostrophe
    quoting ('{' … ') is treated as literal text, as ICU does."""
    args: Counter = Counter()
    plurals: dict[str, list[str]] = {}
    hashes = 0
    i, n = 0, len(s)

    def skip_ws(j):
        while j < n and s[j].isspace():
            j += 1
        return j

    def message(j, stop_on_brace, in_plural):
        nonlocal hashes
        while j < n:
            c = s[j]
            if c == "'" and j + 1 < n and s[j + 1] in "{}#'":
                if s[j + 1] == "'":
                    j += 2
                    continue
                end = s.find("'", j + 1)
                j = n if end == -1 else end + 1
                continue
            if c == "}" and stop_on_brace:
                return j + 1
            if c == "#" and in_plural:
                hashes += 1
            if c == "{":
                j = argument(j + 1)
                continue
            j += 1
        return j

    def argument(j):
        j = skip_ws(j)
        m = re.match(r"[\w]*", s[j:])
        name = m.group(0)
        j = skip_ws(j + len(name))
        if j < n and s[j] == "}":
            args[name or "{}"] += 1
            return j + 1
        if j < n and s[j] == ",":
            j = skip_ws(j + 1)
            t = re.match(r"\w+", s[j:])
            typ = t.group(0) if t else ""
            j = skip_ws(j + len(typ))
            args[name] += 1
            if typ in ("plural", "select", "selectordinal"):
                if j < n and s[j] == ",":
                    j += 1
                keys = []
                while True:
                    j = skip_ws(j)
                    if j >= n or s[j] == "}":
                        break
                    sel = re.match(r"(=?[\w-]+)", s[j:])
                    if not sel:
                        break
                    keys.append(sel.group(1))
                    j = skip_ws(j + len(sel.group(1)))
                    if j < n and s[j] == "{":
                        j = message(j + 1, True, typ != "select")
                plurals[name] = keys
                j = skip_ws(j)
                return j + 1 if j < n and s[j] == "}" else j
            depth = 0
            while j < n:
                if s[j] == "{":
                    depth += 1
                elif s[j] == "}":
                    if depth == 0:
                        return j + 1
                    depth -= 1
                j += 1
            return j
        # not an argument (e.g. stray brace): consume to the closing brace
        end = s.find("}", j)
        return n if end == -1 else end + 1

    message(0, False, False)
    return {"args": args, "plurals": plurals, "hashes": hashes}


def placeholders(s: str) -> Counter:
    """Multiset of placeholder names, format-agnostic: `{{name}}`, `{name}`,
    `{name, number}` all count as `name`; easy_localization `{}` counts as `{}`."""
    s2 = re.sub(r"\{\{\s*(\w+)[^}]*\}\}", r"{\1}", s)
    return parse_icu(s2)["args"]


def tags(s: str) -> Counter:
    return Counter(m.lower() for m in re.findall(r"</?\s*([a-zA-Z][\w-]*)", s))


# --------------------------------------------------------------------------
# Glossary
# --------------------------------------------------------------------------


def load_csv(name: str) -> list[dict]:
    path = SKILL_DIR / "references" / name
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def load_glossary() -> list[dict]:
    """One row per term × language: term, lang, text, status, match,
    case_sensitive, source, note. Status: approved (a local team signed it
    off), consistent (every product already uses it), conflict (products
    disagree — undecided), proposed (seen in one product only)."""
    return [r for r in load_csv("glossary.csv") if r.get("term") and r.get("lang")]


def glossary_hits(en: str, gloss: list[dict], langs: list[str]) -> list[dict]:
    """`match=label` terms ("Try again", "Log out") are UI labels: they only
    count when they ARE the whole string, not when the words occur in a
    sentence. `match=word` terms (plan names, IELTS, skills) count anywhere."""
    hits = []
    stripped = norm(re.sub(r"[.!?:…]+$", "", en))
    for g in gloss:
        if g["lang"] not in langs:
            continue
        if g.get("match") == "label":
            if stripped != g["term"].lower():
                continue
        elif g.get("match") == "hint":
            if not re.search(r"(?<![\w])" + re.escape(g["term"]) + r"s?(?![\w])", en, re.I):
                continue
        else:
            pat = r"(?<![\w])" + re.escape(g["term"]) + r"s?(?![\w])"
            if not re.search(pat, en, 0 if g.get("case_sensitive") == "yes" else re.I):
                continue
        hits.append({k: g[k] for k in ("term", "lang", "text", "status", "note") if k in g})
    return hits


def approved_matches(en: str, langs: list[str], approved: list[dict]) -> list[dict]:
    """Translations a local market team reviewed for this exact English.
    Asking for zh-Hant also returns the Hong Kong version for reference."""
    want = set(langs) | ({"zh-Hant-HK"} if "zh-Hant" in langs else set())
    n = norm(en)
    out, seen = [], set()
    for a in approved:
        if a["lang"] in want and norm(a["en"]) == n and (a["lang"], a["text"]) not in seen:
            seen.add((a["lang"], a["text"]))
            out.append({k: a[k] for k in ("lang", "market", "text", "source", "note") if a.get(k)})
    return out


# --------------------------------------------------------------------------
# queue
# --------------------------------------------------------------------------


def changed_keys(name: str, ref: str) -> set[str]:
    """Keys present in the source file now but not at `ref`."""
    root = repo_path(name)
    fcfg = CONFIG["projects"][name]["files"]
    rel = f"{fcfg['dir']}/{fcfg.get('fileTags', {}).get(SOURCE, SOURCE)}.json"
    now = flatten(json.loads((root / rel).read_text()))
    try:
        old_raw = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{rel}"],
                                 capture_output=True, text=True, check=True).stdout
        old = flatten(json.loads(old_raw))
    except subprocess.CalledProcessError:
        old = {}
    new = {k for k in now if k not in old or now[k] != old[k]}
    if fcfg["format"] == "i18next":  # k_one/k_other collapse to k
        new = {re.sub(rf"_({'|'.join(PLURAL_SUFFIXES)})$", "", k) for k in new}
    return new


def cmd_queue(a) -> None:
    name = a.project
    langs = [canon_lang(l) for l in (a.langs.split(",") if a.langs else TARGETS)]
    if a.strings:
        # Copy that exists nowhere yet (a designer's draft, a key not added
        # to en.json): {"items": [{"key": "...", "en": "...", "description"?}]}
        src = json.loads(Path(a.strings).read_text())
        items = [{"key": s["key"], "keyId": None, "namespace": None, "description": s.get("description"),
                  "maxChars": s.get("maxChars"), "isPlural": "plural," in s["en"], "en": s["en"],
                  "todo": {l: {"before": None, "state": None, "outdated": False} for l in langs}}
                 for s in src.get("items", src if isinstance(src, list) else [])]
        emit({"project": name, "source": "strings-file", "langs": langs, "count": len(items),
              "notFound": [], "items": items}, a.out)
        return
    rows, source = corpus(name, a.snapshot)
    if not rows:
        die(f"no data for '{name}': no Tolgee access and no repo files found")
    wanted = set(a.keys.split(",")) if a.keys else None
    if a.changed_since:
        wanted = (wanted or set()) | changed_keys(name, a.changed_since)
    items = []
    for r in rows:
        if wanted is not None and r["key"] not in wanted:
            continue
        en = r["text"].get(SOURCE)
        if not en:
            continue
        todo = {}
        for l in langs:
            cur = r["text"].get(l)
            missing = not cur
            outdated = r["outdated"].get(l, False)
            if wanted is not None or (a.mode in ("missing", "both") and missing) or (a.mode in ("outdated", "both") and outdated):
                todo[l] = {"before": cur, "state": r["state"].get(l), "outdated": outdated}
        if todo:
            items.append({**{k: r[k] for k in ("key", "keyId", "namespace", "description", "maxChars", "isPlural")},
                          "en": en, "todo": todo})
    if wanted is not None:
        found = {i["key"] for i in items}
        missing_keys = sorted(wanted - found)
    else:
        missing_keys = []
    out = {"project": name, "source": source, "langs": langs, "count": len(items),
           "notFound": missing_keys, "items": items}
    emit(out, a.out)


# --------------------------------------------------------------------------
# context
# --------------------------------------------------------------------------


def norm(s: str) -> str:
    s = re.sub(r"\{\{\s*(\w+)[^}]*\}\}", r"{\1}", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def usages(name: str, key: str, limit: int = 3) -> list[str]:
    root = repo_path(name)
    if not root:
        return []
    proj = CONFIG["projects"][name]
    base = re.sub(rf"(_|\.)({'|'.join(PLURAL_SUFFIXES)})$", "", key)
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "grep", "-n", "-F", "-e", f"'{base}", "-e", f'"{base}',
             "--", *proj["codeGlobs"]],
            capture_output=True, text=True,
        ).stdout.splitlines()
    except FileNotFoundError:
        return []
    return [re.sub(r"\s+", " ", l)[:220] for l in out[:limit]]


def cmd_context(a) -> None:
    q = json.loads(Path(a.queue).read_text())
    name = q["project"]
    langs = q["langs"]
    gloss = load_glossary()
    approved = load_csv("approved.csv")
    corpora = {}
    snaps = dict(s.split("=", 1) for s in (a.snapshot or []))
    for p in CONFIG["projects"]:
        rows, src = corpus(p, snaps.get(p))
        corpora[p] = {"rows": rows, "source": src}
    index: dict[str, list] = {}
    for p, c in corpora.items():
        for r in c["rows"]:
            en = r["text"].get(SOURCE)
            if en:
                index.setdefault(norm(en), []).append((p, r))
    all_en = list(index)
    own = {r["key"]: r for r in corpora[name]["rows"]}
    for it in q["items"]:
        key, en = it["key"], it["en"]
        n = norm(en)
        exact = []
        for p, r in index.get(n, []):
            if p == name and r["key"] == key:
                continue
            t = {l: r["text"].get(l) for l in langs if r["text"].get(l)}
            if t:
                exact.append({"project": p, "key": r["key"], "text": t,
                              "state": {l: r["state"].get(l) for l in t}})
        near = []
        if len(n) > 12:
            for cand in difflib.get_close_matches(n, all_en, n=4, cutoff=0.78):
                if cand == n:
                    continue
                p, r = index[cand][0]
                t = {l: r["text"].get(l) for l in langs if r["text"].get(l)}
                if t:
                    near.append({"project": p, "key": r["key"], "en": r["text"][SOURCE], "text": t})
        group = key.split(".")[0]
        siblings = [{"key": r["key"], "en": r["text"].get(SOURCE),
                     "text": {l: r["text"].get(l) for l in langs if r["text"].get(l)}}
                    for k, r in own.items() if k != key and k.split(".")[0] == group and r["text"].get(SOURCE)][:6]
        # Up to 3 per project, so the other product is never crowded out by
        # this one's duplicates — the cross-product view is the whole point.
        per_project = Counter()
        balanced = []
        for m in exact:
            if per_project[m["project"]] < 3:
                per_project[m["project"]] += 1
                balanced.append(m)
        it["context"] = {
            "approved": approved_matches(en, langs, approved),
            "exactMatches": balanced,
            "nearMatches": near[:3],
            "glossary": glossary_hits(en, gloss, langs),
            "usages": usages(name, key),
            "siblings": siblings,
        }
    q["corpusSources"] = {p: c["source"] for p, c in corpora.items()}
    emit(q, a.out)


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------


CJK = {"ja", "zh-Hans", "zh-Hant", "ko"}
FULLWIDTH = {"ja", "zh-Hans", "zh-Hant"}


def check_one(en: str, lang: str, text: str, item: dict, gloss_rows: list[dict]) -> tuple[list, list]:
    errors, warns = [], []
    if not text or not text.strip():
        return ["empty translation"], []
    if placeholders(en) != placeholders(text):
        errors.append(f"placeholders differ: source {dict(placeholders(en))} vs {dict(placeholders(text))}")
    if tags(en) != tags(text):
        errors.append(f"markup tags differ: {dict(tags(en))} vs {dict(tags(text))}")
    src_icu, tgt_icu = parse_icu(en), parse_icu(text)
    for arg, keys in src_icu["plurals"].items():
        tkeys = tgt_icu["plurals"].get(arg)
        if tkeys is None:
            errors.append(f"plural '{arg}' missing in translation")
        elif "other" not in tkeys:
            errors.append(f"plural '{arg}' has no 'other' branch")
    if src_icu["hashes"] and not tgt_icu["hashes"]:
        errors.append("source plural uses # but translation does not")
    # Newlines between ICU plural branches are layout, not content (Tolgee
    # pretty-prints them); only compare line breaks in plain strings.
    if not src_icu["plurals"] and en.count("\n") != text.count("\n"):
        warns.append(f"line breaks differ ({en.count(chr(10))} vs {text.count(chr(10))})")
    if text != text.strip() and en == en.strip():
        warns.append("leading/trailing whitespace added")
    letters = re.sub(r"[^A-Za-zÀ-ỹ]", "", text)
    if len(letters) > 4 and letters.isupper() and not re.sub(r"[^A-Za-z]", "", en).isupper():
        warns.append("ALL CAPS in translation but not in source — casing belongs to CSS")
    mine = [g for g in gloss_rows if g["lang"] == lang]
    if norm(text) == norm(en) and len(en) > 3 and not any(g["text"] == g["term"] for g in mine):
        warns.append("identical to English — intended? (brand/term kept) or untranslated")
    mc = item.get("maxChars")
    if mc and len(text) > mc:
        errors.append(f"exceeds maxChars {mc} ({len(text)})")
    ratio = len(text) / max(len(en), 1)
    if lang not in CJK and len(en) >= 8 and ratio > 1.8:
        warns.append(f"{ratio:.1f}× longer than source — check it fits the UI")
    if lang in FULLWIDTH and re.search(r"[぀-ヿ一-鿿][,!?:;]", text):
        warns.append("half-width punctuation after CJK — use ，！？：")
    for g in mine:
        if g.get("match") == "hint":  # context-dependent: shown to the translator, not enforced
            continue
        want = g["text"].strip()
        if g["status"] == "approved" and want.lower() not in text.lower():
            errors.append(f"glossary: '{g['term']}' must be '{want}' (approved by the local team)")
        elif g["status"] == "consistent" and want.lower() not in text.lower():
            errors.append(f"glossary: '{g['term']}' is '{want}' in every product — keep it; "
                          "if that shared form is wrong, report it instead of changing one side")
        elif g["status"] == "conflict":
            warns.append(f"glossary term '{g['term']}' is undecided ({want}) — note which you used")
    for a in item.get("context", {}).get("approved", []):
        if a["lang"] == lang and norm(a["text"]) != norm(text):
            warns.append(f"differs from the {a.get('market', 'local')}-approved text '{a['text']}' — "
                         "keep the approved text unless the English changed since")
    return errors, list(dict.fromkeys(warns))


def cmd_validate(a) -> int:
    ctx = json.loads(Path(a.context).read_text())
    by_key = {i["key"]: i for i in ctx["items"]}
    out = json.loads(Path(a.translations).read_text())
    results, n_err = [], 0
    seen = set()
    for t in out.get("items", []):
        key, lang = t["key"], canon_lang(t["lang"])
        seen.add((key, lang))
        item = by_key.get(key)
        if not item:
            results.append({"key": key, "lang": lang, "errors": ["key not in context file"], "warnings": []})
            n_err += 1
            continue
        gl = item.get("context", {}).get("glossary", [])
        e, w = check_one(item["en"], lang, t.get("text", ""), item, gl)
        n_err += len(e)
        if e or w:
            results.append({"key": key, "lang": lang, "errors": e, "warnings": w})
    missing = [f"{i['key']}:{l}" for i in ctx["items"] for l in i["todo"] if (i["key"], l) not in seen]
    report = {"checked": len(out.get("items", [])), "errors": n_err, "missing": missing, "issues": results}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if n_err or missing else 0


# --------------------------------------------------------------------------
# write
# --------------------------------------------------------------------------


def cmd_write(a) -> int:
    ctx = json.loads(Path(a.context).read_text())
    name = ctx["project"]
    by_key = {i["key"]: i for i in ctx["items"]}
    out = json.loads(Path(a.translations).read_text())
    # A value that is already right is not rewritten: resending it would only
    # add noise to Tolgee's history and reset nothing useful.
    def before_of(t):
        return by_key.get(t["key"], {}).get("todo", {}).get(canon_lang(t["lang"]), {}).get("before")

    unchanged = [t for t in out.get("items", []) if before_of(t) is not None and before_of(t) == t["text"]]
    items = [t for t in out.get("items", []) if t not in unchanged]
    if not a.apply:
        print(f"DRY RUN — {len(items)} change(s) for project '{name}', {len(unchanged)} unchanged. Nothing written.\n")
        for t in items:
            before = before_of(t)
            print(f"{t['key']} [{t['lang']}] ({t.get('basis', 'new')})")
            if before:
                print(f"    was: {before}")
            print(f"    now: {t['text']}")
        print("\nRe-run with --apply to write to Tolgee.")
        return 0
    if not tolgee_enabled(name):
        die(f"'{name}' has no Tolgee project/key configured — deliver the translations file instead")
    # Re-read the live values: anything a human changed since `queue` is skipped.
    live = {r["key"]: r for r in fetch_tolgee_rows(name)}
    keys, skipped = {}, []
    for t in items:
        key, lang = t["key"], canon_lang(t["lang"])
        todo = by_key.get(key, {}).get("todo", {}).get(lang)
        row = live.get(key)
        if todo is None or row is None:
            skipped.append(f"{key}:{lang} (not in queue or not in Tolgee)")
            continue
        now = row["text"].get(lang)
        if (now or None) != (todo.get("before") or None):
            skipped.append(f"{key}:{lang} (changed in Tolgee since queue)")
            continue
        tag = next((l for l in (row["text"] or {}) if l == lang), lang)
        keys.setdefault(key, {"name": key, "namespace": row.get("namespace"), "translations": {}})
        keys[key]["translations"][tolgee_tag(name, tag)] = {
            "text": t["text"],
            "resolution": "EXPECT_NO_CONFLICT" if not now else "OVERRIDE",
        }
    if not keys:
        print(json.dumps({"written": 0, "skipped": skipped}, ensure_ascii=False, indent=2))
        return 1 if skipped else 0
    body = {"keys": list(keys.values()), "overrideMode": "RECOMMENDED", "errorOnUnresolvedConflict": False}
    res = tolgee(name, "POST", "/single-step-import-resolvable", body=body)
    print(json.dumps({"written": sum(len(k["translations"]) for k in keys.values()),
                      "skipped": skipped, "tolgee": res}, ensure_ascii=False, indent=2))
    return 0


def tolgee_tag(name: str, lang: str) -> str:
    return CONFIG["projects"][name]["tolgee"].get("languageTags", {}).get(lang, lang)


# --------------------------------------------------------------------------


def emit(obj, path: str | None) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=2)
    if path:
        Path(path).write_text(text + "\n")
        print(f"wrote {path} ({obj.get('count', len(obj.get('items', [])))} item(s))")
    else:
        print(text)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("queue", help="list what needs translating")
    q.add_argument("--project", choices=list(CONFIG["projects"]), help="defaults to the project of the current git repo")
    q.add_argument("--langs")
    q.add_argument("--mode", default="both", choices=["missing", "outdated", "both"])
    q.add_argument("--keys", help="comma-separated key names (translates them even if already translated)")
    q.add_argument("--changed-since", help="git ref: keys added/changed in the source file since then")
    q.add_argument("--strings", help="JSON file of new copy not in any repo yet: {items:[{key, en, description?}]}")
    q.add_argument("--snapshot", help="offline: a saved /translations JSON page instead of live Tolgee")
    q.add_argument("--out")

    c = sub.add_parser("context", help="attach cross-project matches, glossary, code usages")
    c.add_argument("--queue", required=True)
    c.add_argument("--snapshot", action="append", help="offline: project=path to a saved /translations page")
    c.add_argument("--out")

    v = sub.add_parser("validate", help="check a translations file against the context")
    v.add_argument("--context", required=True)
    v.add_argument("--translations", required=True)

    w = sub.add_parser("write", help="dry-run (default) or --apply to Tolgee")
    w.add_argument("--context", required=True)
    w.add_argument("--translations", required=True)
    w.add_argument("--apply", action="store_true")

    a = ap.parse_args()
    if a.cmd == "queue":
        a.project = a.project or current_project()
        if not a.project:
            die("not inside a known project repo — pass --project (" + ", ".join(CONFIG["projects"]) + ")")
        cmd_queue(a)
    elif a.cmd == "context":
        cmd_context(a)
    elif a.cmd == "validate":
        sys.exit(cmd_validate(a))
    elif a.cmd == "write":
        sys.exit(cmd_write(a))


if __name__ == "__main__":
    main()
