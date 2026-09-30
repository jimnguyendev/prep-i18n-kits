# prep-i18n

Claude Code plugin that translates Prep UI copy from English into vi, th, id,
ko, ja, zh-Hans and zh-Hant **consistently across every Prep product and
team** — the same English gets the same translation on every web, app and
internal tool. One kit, one glossary, one set of local-market approvals for
the whole company; each team only adds its repo to `projects.json`.

One skill: `prep-translate`. It reads both products' existing translations,
a shared glossary and a style guide measured from Prep's own copy, translates
with Claude Code, validates placeholders/plurals/glossary with a script, and
writes back to Tolgee as TRANSLATED (never REVIEWED, never Published).

## Install

Per person, once (works in any repo afterwards):

```sh
# local checkout
claude plugin marketplace add /path/to/prep-i18n-kit
claude plugin install prep-i18n@prep-i18n

# or, once this repo is on GitLab
claude plugin marketplace add <gitlab url of prep-i18n-kit>
```

Try without installing: `claude --plugin-dir /path/to/prep-i18n-kit`.

Then, in a product repo: "dịch các key mới trong nhánh này" or
"fill missing Thai translations".

## Supported repos

Listed in `skills/prep-translate/projects.json` and detected by git remote:

| project | repo | Tolgee | writes to |
|---|---|---|---|
| web | learning/practice-lab-web | project 2 | Tolgee |
| app | learning/mobile/prep-app | not yet (Crowdin) | translations file for the app team |

Add a repo (any team): one entry in `projects.json` — git remote, locale dir
and format (`i18next`, `easy_localization`, or `icu`), Tolgee project id or
null, the env var holding that project's key, and the write rule. Open an MR
here; once merged, every team's translations can reuse yours and vice versa.

## Ownership

The kit is shared, so changes go through MR review:
- `glossary.csv` / `approved.csv` — the content team and local-market teams
  decide; the i18n owner merges.
- `style-guide.md` — per-language sections are owned by that market's reviewer.
- `scripts/`, `projects.json` — any team's developer, with one reviewer from
  another team.

## Credentials

The skill reads `TOLGEE_API_KEY` (web) / `TOLGEE_APP_API_KEY` (app) from the
environment or the repo's gitignored `.env.development.local`. Use a personal
key without the `translations.batch-machine` scope. Nothing is written without
an explicit `--apply` after a dry run.

## Updating the glossary

`skills/prep-translate/references/glossary.csv`. `status`:
`approved` (a market team signed it off) and `consistent` (every product uses it) are enforced by the validator; `conflict` (products disagree — the
content team decides, then set one value and `approved`), `proposed` (seen in
one product only).
