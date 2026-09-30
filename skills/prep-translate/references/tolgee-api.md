# Tolgee API notes

What the script calls, and what was verified against the Tolgee source
(tolgee-platform, 28/09/2026) and the self-hosted server's OpenAPI
(`https://tolgee.testsprep.online/v3/api-docs`). Read this only when you need
something the script doesn't do.

## The server

- Self-hosted, **no license**. Glossary, shared translation memory, AI prompt
  customization, tasks, webhooks, QA checks, labels and branching are
  enterprise features (`@RequiresFeatures`) and are unavailable. That is why
  the glossary lives in `glossary.csv` and cross-product matching is done by
  the script instead of a shared TM.
- **10 seats** on the free tier (`SelfHostedLimitsProvider`).
- Project 2 = Practice Lab web. Base `en`. ICU placeholders on; stored texts
  are ICU (`{name}`, `{count, plural, one {# test} other {# tests}}`) even
  though the repo files are i18next — the CLI converts on export.
- Language tags on project 2 are lower-case `zh-hans` / `zh-hant`.

## Endpoints used

| Purpose | Call | Notes |
|---|---|---|
| Read keys + translations | `GET /v2/projects/{id}/translations?languages=…&size=1000&cursor=…` | filters: `filterUntranslatedInLang`, `filterOutdatedLanguage`, `filterKeyName`, `filterTag`. Rows carry `state`, `outdated`, `auto`, `keyDescription`, `keyMaxCharLimit`. |
| Write translations | `POST /v2/projects/{id}/single-step-import-resolvable` | body `{keys:[{name, namespace, translations:{tag:{text, resolution}}}], overrideMode:"RECOMMENDED", errorOnUnresolvedConflict:false}`. `EXPECT_NO_CONFLICT` fails if a value exists; `OVERRIDE` replaces. `RECOMMENDED` refuses protected REVIEWED values. Needs `translations.view` + edit scopes. |
| Per-project TM | `POST /v2/projects/{id}/suggest/translation-memory` | accepts `baseText`, so it can be asked about another project's English. Without a license it searches only that project's own TM — the script's corpus index covers the same ground in one fetch. |

## Behaviour worth knowing

- Writing a translation clears its `outdated` and `auto` flags
  (`Translation.resetFlags()`).
- Changing an English value marks every other language `outdated` and
  demotes REVIEWED → TRANSLATED. It does **not** re-translate anything.
- Auto-translation fires only when the English text changes **and** the
  project has MT or TM auto-translate enabled (`AutoTranslationEventHandler`).
  Project 2 has it off; keep it that way.
- The server reports `llm.enabled: true`. If anyone adds an LLM provider it
  becomes the primary MT engine by default (`default-primary`), and batch or
  auto translation would start spending. Not this skill's business, but worth
  a sentence in the report if you notice auto-translated values (`auto: true`).
- Don't use the Tolgee MCP `machine_translate` tool; it spends MT/LLM credits
  and ignores the glossary.
