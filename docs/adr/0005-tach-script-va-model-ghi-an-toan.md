# ADR-0005: Script lo phần có đúng/sai, model lo phần phán đoán; ghi Tolgee an toàn

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead

## Context

Model quên và mắc lỗi không đều. Có những lỗi làm hỏng cả gói: một placeholder sai
khiến lớp phủ CDN từ chối toàn bộ gói ngôn ngữ đó (`docs/I18N.md` §6.3). Mặt khác, Tolgee
là dữ liệu dùng chung: người khác có thể đang sửa, và job sync tự merge dựa trên giả định
Publish nghĩa là đã có người duyệt.

## Decision

`scripts/prep_translate.py` (chỉ dùng Python stdlib) lo mọi phần có đúng/sai rõ ràng:

- **queue:** tìm key cần dịch — thiếu, outdated, mới trong nhánh, hoặc chuỗi chưa có trong repo nào;
- **context:** thu bản đã duyệt, glossary, bản khớp chính xác và gần đúng ở mọi sản phẩm,
  chỗ gọi key trong code, các key cùng nhóm;
- **validate:** kiểm placeholder (ICU, `{{x}}`, `{}` của app), thẻ markup, số nhiều (`other` + `#`),
  thuật ngữ bắt buộc, `maxChars`, dấu câu CJK, chữ viết hoa toàn bộ, và cặp key × ngôn ngữ còn thiếu;
- **write:** mặc định chỉ chạy thử (dry-run). Khi có `--apply`, script đọc lại Tolgee và bỏ qua
  giá trị nào đã đổi kể từ lúc queue, dùng `EXPECT_NO_CONFLICT` cho ô đang trống,
  `overrideMode: RECOMMENDED` để không đụng bản REVIEWED được bảo vệ, và bỏ qua giá trị không đổi.

Model lo phần cần phán đoán: đọc ngữ cảnh, văn phong, khi nào được lệch khỏi bản có sẵn,
khi nào viết lại theo ý.

**Những việc không bao giờ làm:** gọi MT của Tolgee, đánh dấu REVIEWED, Publish, sửa tiếng Anh,
sửa file dịch trong repo web.

## Consequences

- Lỗi kỹ thuật bị chặn trước khi tới Tolgee, không đợi CDN từ chối.
- Bản người vừa sửa luôn thắng bản AI.
- Với project chưa có Tolgee (app), script dừng ở bước validate và giao file.

## Nguồn

S1 (`single-step-import-resolvable`, `resetFlags`, `AutoTranslationEventHandler`), S4 (kiểm đủ
số lượng, không tự vá, validate trong service), S7 (§1, §6.3, luật Publish và sync).
