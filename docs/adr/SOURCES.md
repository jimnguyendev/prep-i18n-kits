# Nguồn học

Những gì kit học được, từ đâu, và kiểm chứng bằng cách nào. Đường dẫn cục bộ là
máy tác giả tại thời điểm viết (30/09/2026); tài liệu trên web kèm URL.

## S1. Mã nguồn và server Tolgee

- **tolgee-platform**, commit `1c6139c` (28/09/2026), clone nông `backend/` + `ee/backend/`.
  - `Feature.kt` — danh sách tính năng trả phí: `GLOSSARY`, `TRANSLATION_MEMORY`
    (TM dùng chung), `AI_PROMPT_CUSTOMIZATION`, `GRANULAR_PERMISSIONS`, `SSO`, `TASKS`,
    `WEBHOOKS`, `QA_CHECKS`, `BRANCHING`, `TRANSLATION_LABELS`.
  - `GlossaryController.kt` — tạo/nhập glossary có `@RequiresFeatures(Feature.GLOSSARY)`.
  - `TranslationMemoryManagementService.kt:127` — không license thì chỉ tra TM riêng của project.
  - `AiPromptCustomizationController.kt` — language notes không khoá license nhưng
    `@RequiresOrganizationRole(OWNER)`.
  - `SelfHostedLimitsProvider.kt:36` — bản free: 10 seat.
  - `ProjectPermissionType` — `content-delivery.publish` chỉ có trong vai trò `MANAGE` (`Scope.ADMIN`).
  - `Translation.resetFlags()` — ghi bản dịch xoá cờ `outdated` và `auto`.
  - `AutoTranslationEventHandler.kt:61` — auto-translate chỉ chạy khi tiếng Anh đổi **và**
    project bật MT hoặc TM.
  - `ContentDeliveryUploader.kt:64` — prune xoá thư mục **trước** rồi mới ghi file.
  - `PromptFragmentsHelper.kt` — khung prompt AI Translator (intro, styleInfo, glossary,
    translationMemory, relatedKeys, icuInfo, keyDescription, charLimit).
- **Server `tolgee.testsprep.online`**
  - `/api/public/configuration`: `llm.enabled: true`, `PROMPT` bật, `ssoGlobal`/`ssoOrganizations`
    tắt, Google OAuth bật, `allowRegistrations: false`.
  - `/v3/api-docs`: có `single-step-import-resolvable`, `suggest/translation-memory`
    (nhận `baseText`), `/translations` với `filterOutdatedLanguage`.
  - Bản export project 2 (`tolgee-export-backup/translations-full.json`, 28/09): 627 key,
    0 key có description, 0 screenshot; văn bản lưu dạng ICU (`Attempt {number}`);
    tag ngôn ngữ `zh-hans`/`zh-hant`.
  - Cấu hình CDN (bản backup): `filterState = [TRANSLATED, REVIEWED]`, autoPublish tắt.

## S2. Tài liệu Tolgee (docs.tolgee.io)

- Machine translation: https://docs.tolgee.io/platform/translation_process/machine_translation
- Editing translations: https://docs.tolgee.io/platform/projects_and_organizations/editing_translations
- Translation memory (TM dùng chung cần plan): https://docs.tolgee.io/platform/translation_process/managing_translation_memories
- LLM providers (`default-primary`): https://docs.tolgee.io/platform/projects_and_organizations/llm-providers
- AI Playground (sửa prompt nâng cao cần Business): https://docs.tolgee.io/platform/translation_process/ai-playground
- MCP server (22 tool, thiếu glossary/TM/state): https://docs.tolgee.io/platform/integrations/mcp_server/usage

## S3. jimmy-kit — skill ux-writing

`~/workspaces/prep/jimmy-kit/skills/ux/ux-writing/` (+ bản ghi chú `.learn-vi/`).
Lấy: một thứ một tên; nút = động từ + tân ngữ; lỗi nói chuyện gì/vì sao/cách sửa, sản
phẩm nhận lỗi; giọng theo mức căng thẳng; không giọng marketing trong sản phẩm; giới hạn
độ dài; danh sách chữ đệm tiếng Việt cần cắt. Cách phân phối: `.claude-plugin/plugin.json`
+ `marketplace.json`. Ràng buộc: `skills/` của kit cấm tiếng Việt và tên công ty.

## S4. lu-ai-service — pipeline dịch phụ đề

`~/workspaces/lu-ai-service/src/shadowing/shadowing/translate.py`, `prompt_translate.md`,
`AGENTS.md`. Lấy: không dịch từng câu tách rời; dịch theo lô kèm ngữ cảnh; nháp → tự soát
4 trục (chính xác, trôi chảy, thuật ngữ, văn phong) → sửa rồi mới xuất; kiểm đủ số lượng
đầu ra và báo lỗi thay vì tự vá; ghi chú ngữ cảnh làm đổi hành vi model; prompt viết bằng
ngôn ngữ đích; validate ngay trong service.

## S5. Feedback của đội local (09/2026)

Bốn file "IELTS Practice Lab – Master Plan": HK Localization, TW Localization, KR
Localization, INTL2 Copywriting. Chuẩn hoá vào `skills/prep-translate/references/approved.csv`
(TW 242, HK 226, KR 49 chuỗi; KR kèm bản AI bị loại). Phát hiện chính: TW dùng 你 (30/0),
雅思, 口說, ngày YYYY/MM/DD, tên tiếng Việt bỏ dấu, tên gói giữ Latin; HK khác TW ở 156/268
chuỗi; KR sửa 라이브러리 → 자료실, 시도 → 응시, "달성 7.5" → "7.5 달성", tên phương Tây giữ Latin.

## S6. Bản dịch đang chạy của sản phẩm (đo 30/09/2026)

`practice-lab-web/apps/ielts-portal/src/locales/*.json` (597 key) và
`prep-app/lib/assets/l10n/*.json` (3.677 key). 126 câu tiếng Anh trùng, 35 (28%) lệch
tiếng Việt. Quy ước đo được: vi "bạn" 1.165; th คุณ 1.265, ค่ะ 299 / ครับ 3; id Anda 1.287;
ja です/ます, dấu full-width; zh-Hans web 您 69/你 35, app 您 214/你 746; zh-Hant 您 1.282.

## S7. Quy tắc repo practice-lab-web

`docs/I18N.md` (§1 ba quy tắc, §6 lớp phủ CDN, §7 đồng bộ), `scripts/i18n-push-local.sh`
(PUBLISH=1 chỉ cho dev), `scripts/i18n-sync-local.sh` (sync lấy bản đã Publish, tự merge).
