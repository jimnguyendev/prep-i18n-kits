---
name: prep-translate
description: >-
  Translate Prep UI copy from English into vi, th, id, ko, ja, zh-Hans and zh-Hant
  so every Prep product (practice-lab-web, prep-app, and any repo listed in
  projects.json) uses the same words for the same thing. Use it whenever someone
  wants keys translated or re-translated in a Prep repo: "dịch mấy key mới",
  "bổ sung bản dịch", "dịch lại key bị outdated", "fill missing translations",
  localizing a new feature's strings, checking or fixing a translation, or asking
  how a term should read in Thai/Japanese/etc. Use it even if Tolgee isn't
  mentioned. Not for writing the English source copy (that is UX writing) and not
  for translating documents or articles.
---

# Prep translate

Two products, one vocabulary. The web and the app were translated separately
and it shows: of 126 English strings they share, 35 (28%) already read
differently in Vietnamese — "Core" is `Core` on the web and `Cơ bản` in the app.
The drift comes from terminology, not from who translates. So this skill
translates **with every product's existing translations, the corrections Prep's
local market teams made, and a shared glossary in view**, and leaves the
mechanical checks to a script, which doesn't forget.

The script (`scripts/prep_translate.py`, Python stdlib only) does the
deterministic parts: find what needs translating, gather context from every
product, validate, and write back without overwriting a human's edit. You do
the translating and the judgement calls.

## Before you start

- **Which project?** The script detects it from the current repo's git remote
  (`projects.json` → `gitRemote`). Other products are found as sibling
  checkouts, or through `PREP_<NAME>_REPO=/path`.
- **Tolgee access** is needed only to read live state and to write. The key is
  read the same way `scripts/i18n-env.sh` does: `TOLGEE_API_KEY` (web) /
  `TOLGEE_APP_API_KEY` (app) in the environment, else in the repo's
  gitignored `.env.development.local`. Never print, echo or paste the key.
  Without a key, the script falls back to the repo's locale files.
- **Where results may go** differs per project — read its `writeRule` in
  `projects.json`. Today: web → Tolgee; app → a translations file for the app
  team (it is still on Crowdin).

## Workflow

Run from the root of the product repo. `$PT` below is this skill's
`scripts/prep_translate.py`. Put working files in a directory of their own —
`WORK=$(mktemp -d)` — never in the repo and never in a shared scratch folder
under fixed names: two runs writing `ctx.json` side by side silently swap
each other's keys.

### 1. Queue — decide what to translate

```sh
python3 $PT queue --changed-since origin/main --out q.json   # keys this branch added/changed
python3 $PT queue --mode missing --out q.json                # every empty translation
python3 $PT queue --mode outdated --out q.json               # English changed since translating (Tolgee only)
python3 $PT queue --keys pricing.cta_start_trial,trial.analyze_retry --langs vi,th --out q.json
python3 $PT queue --strings new-copy.json --langs ko --out q.json  # copy not in any repo yet
```

`--strings` takes `{"items": [{"key": "…", "en": "…", "description": "…"}]}` —
for a designer's draft or keys a developer hasn't added yet. Its output can be
validated and handed over, but not written to Tolgee.

`notFound` in the output lists requested keys the source doesn't have. For the
web, a key that is in `en.json` but not in Tolgee yet must go through
`pnpm i18n:keys:send` first — writing translations for a key Tolgee doesn't
know would create it without its English.

### 2. Context — gather what the translator needs

```sh
python3 $PT context --queue q.json --out ctx.json
```

Each item gains:

| field | what it is | how to use it |
|---|---|---|
| `approved` | a local market team's reviewed translation of this exact English (TW, KR; HK as `zh-Hant-HK` for reference) | the answer — use it as is |
| `exactMatches` | same English in any product, with its translations | the main defence against drift — reuse unless the UI context really differs |
| `nearMatches` | similar English elsewhere | phrasing and term hints |
| `glossary` | glossary rows (term × language) whose term appears in the source | `approved` and `consistent` are enforced; `conflict` is undecided (style guide §9); `hint` depends on context |
| `usages` | where the code calls the key | tells you if it's a button, heading, error, badge |
| `siblings` | other keys in the same group | register and wording on the same screen |

`usages` is empty when the key is built at runtime (``t(`pricing.plan_${tier}_name`)``).
Then search the code yourself for the key's last segment before guessing the
context — a 2-word string with no context is the most common cause of a wrong
translation.

### 3. Translate

Read `references/style-guide.md` §1 and the section for each target language
before writing. Its rules come from two places: what the local teams corrected
(authoritative) and what Prep's copy measurably does (the default).

Work one language at a time, up to ~40 items per pass, so terminology stays
consistent within the batch. For each item, in this order of precedence:

1. an `approved` text for this exact English, as is;
2. `approved` / `consistent` glossary terms, in their glossary form;
3. an exact match **from the same product**, reused as is;
4. an exact match from another product, reused unless context differs;
5. a fresh translation that follows the style guide.

A key that already has a correct translation comes back **unchanged**, byte
for byte. Marketing copy (landing, pricing, testimonials) is transcreated —
keep its pain point and promise, not the English syntax; product UI stays
close to the source (style guide §1).

Then reread the whole batch on the four axes in style guide §1 (accurate,
fluent, consistent, register) and fix before writing the file. Write:

```json
{"items": [
  {"key": "trial.analyze_retry", "lang": "vi", "text": "Thử lại",
   "basis": "tm-exact:app/common.retry",
   "note": "web uses 'Làm lại' for the same English; app form chosen because this is an error retry, not a test retake"}
]}
```

`basis` is one of `approved:<market>`, `glossary`, `tm-exact:<project>/<key>`,
`tm-near:<project>/<key>`, `unchanged`, `new`. Add a `note` whenever you deviate from a match or pick a side of an
open decision — reviewers read these, and they are the data for deciding the
open terms.

### 4. Validate

```sh
python3 $PT validate --context ctx.json --translations out.json
```

Errors must be fixed: placeholder or markup mismatch, missing plural `other`
branch or `#`, an `approved`/`consistent` glossary term not used, empty text, over
`maxChars`, and any queued key/language you didn't translate (`missing`).
Warnings need a decision, not necessarily a change: ALL CAPS, identical to
English, much longer than the source, half-width punctuation in CJK,
undecided glossary terms, differs from local-approved text. Re-run until
errors are zero.

### 5. Write

```sh
python3 $PT write --context ctx.json --translations out.json          # dry run: shows was → now
python3 $PT write --context ctx.json --translations out.json --apply  # Tolgee
```

Show the dry run to the user and get a yes before `--apply`: it changes shared
state other teams read. `--apply` re-reads Tolgee first and skips any value
that changed since the queue — a human's edit always wins over this run.
Values land as TRANSLATED; reviewers promote them to REVIEWED, and the normal
Publish step takes them live.

For a project without Tolgee (the app today), stop after validate and hand
over `out.json` plus the report.

## Lines not to cross, and why

- **No machine translation calls.** Don't use Tolgee's `machine_translate`,
  batch MT, or auto-translate. It costs money per string and bypasses the
  glossary and the cross-product check that are the point of this skill.
- **Don't mark anything REVIEWED, and don't press Publish.** Review and Publish
  are the human gates; the web's CDN sync auto-merges on the assumption that
  Publish means someone approved.
- **Don't change the English.** If the source looks wrong, say so in the
  report; English is owned by the product team.
- **Don't edit target locale files in the web repo.** `docs/I18N.md` §1 rule 3:
  translations reach the repo only through the sync from Tolgee.
- **Don't normalise the other product.** If the app's existing translation is
  wrong, report it; fixing it is that team's call.

## Report

End with a short report, in the user's language:

```
Translated <n> strings for <project> (<langs>). Validation: 0 errors, <w> warnings.
Written to Tolgee: <yes/no — or "file ready for the app team: out.json">.

Reused from the other product: <n>   New: <n>
Decisions to make (open glossary terms you touched):
- "Core" (vi): used "Core" — web form; app says "Cơ bản". Keys: …
Problems spotted in existing copy (not changed):
- web dashboard.go_premium (vi) says "Nâng cấp Pro" on a "Go Premium" button.
```

## Files

- `projects.json` — the products, their Tolgee projects, file formats, write rules. Add a repo here.
- `references/style-guide.md` — shared rules, per-language register, open decisions.
- `references/glossary.csv` — one row per term × language, with `status` (`approved` by a market team, `consistent` across products, `conflict`, `proposed`), `match` (`word`, `label`, `hint`) and the source of the decision.
- `references/approved.csv` — 517 strings reviewed by the TW, HK and KR teams (Sep 2026), with the rejected AI draft for KR in `note`. Add new local-team feedback here.
- `references/tolgee-api.md` — endpoints the script uses and why, for when you need to go beyond it.
