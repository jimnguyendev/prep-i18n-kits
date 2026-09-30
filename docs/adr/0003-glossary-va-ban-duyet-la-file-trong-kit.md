# ADR-0003: Glossary và bản đã duyệt là file trong kit

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead

## Context

Tolgee có sẵn Glossary, TM dùng chung giữa các project và language notes — đúng những
công cụ chống lệch cần dùng. Nhưng server của Prep chạy bản free, không có license.

## Decision

- Glossary nằm ở `references/glossary.csv`: mỗi dòng là một thuật ngữ × một ngôn ngữ,
  kèm `status`, `match` và nguồn của quyết định.
- Bản dịch đã được đội local duyệt nằm ở `references/approved.csv`.
- Việc đối chiếu chéo giữa các sản phẩm do script làm: script đọc toàn bộ bản dịch của
  từng project (qua Tolgee REST, hoặc file trong repo khi chưa có Tolgee) rồi dựng chỉ mục
  theo câu tiếng Anh.

## Options Considered

| Công cụ Tolgee | Vì sao không dùng |
|---|---|
| Glossary | `@RequiresFeatures(GLOSSARY)`: cần license |
| TM dùng chung | `TRANSLATION_MEMORY`: cần license; bản free chỉ tra TM trong một project |
| Language notes | Không cần license nhưng chỉ OWNER tổ chức đọc được; không nên cấp quyền đó cho token của dev |
| Project "Glossary" riêng trên Tolgee (mỗi thuật ngữ là một key) | Khả thi và miễn phí, nhưng tốn seat và chưa cần; có thể xem lại sau |

## Consequences

- Không tốn license hay seat; lịch sử thay đổi nằm trong git.
- Người không biết git (đội nội dung, đội local) sửa glossary qua người giữ i18n.
- Khi có license: chuyển sang Glossary + TM dùng chung của Tolgee, và giữ file làm bản nguồn
  hoặc bỏ hẳn.

## Nguồn

S1 (`Feature.kt`, `GlossaryController`, `TranslationMemoryManagementService`,
`AiPromptCustomizationController`, 10 seat), S2 (docs TM dùng chung).
