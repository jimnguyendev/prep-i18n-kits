# ADR-0006: Cách dịch

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead

## Context

Tolgee có 627 key nhưng **0 key có description và 0 screenshot**. Một chuỗi 2 chữ không có
ngữ cảnh là nguyên nhân phổ biến nhất khiến dịch sai.

## Decision

- **Ngữ cảnh lấy từ code:** script grep chỗ key được gọi. Nếu key được ghép lúc chạy
  (``t(`pricing.plan_${tier}_name`)``), model tự tìm trong code thay vì đoán.
- **Dịch theo lô**, mỗi lượt một ngôn ngữ, tối đa khoảng 40 item, để thuật ngữ nhất quán trong lô.
- **Tự soát trước khi xuất theo 4 trục:** chính xác, trôi chảy, nhất quán, văn phong.
- **UI sản phẩm dịch sát nguồn; trang marketing được transcreate** (giữ pain point và lời hứa,
  không giữ cú pháp tiếng Anh). Headline bị tách thành 2 key thì dịch cả cặp cùng lúc.
- **Quy tắc giao diện:**
  - nút bấm giữ động từ + tân ngữ;
  - lỗi thì sản phẩm nhận lỗi;
  - không đùa khi báo lỗi hay thanh toán;
  - viết hoa để CSS lo;
  - tên người phương Tây giữ chữ Latin, tên tiếng Việt bỏ dấu khi ở ngôn ngữ khác;
  - ngày viết theo định dạng của thị trường.
- **Style guide tiếng Việt viết bằng tiếng Việt.**
- Các quy ước theo từng ngôn ngữ lấy từ bản sửa của đội local (ưu tiên) và từ số liệu đo.

## Consequences

- Skill tốn thêm khoảng 44 giây và 16k token mỗi lần chạy so với không có skill (đo ở vòng eval 2).
- Chưa làm: báo khi câu tiếng Anh gõ cứng ngày hay số lẽ ra phải là placeholder. Baseline
  ở eval 5 phát hiện được điều này, còn skill thì chưa.

## Nguồn

S2 + S1 (`PromptFragmentsHelper`: cấu trúc ngữ cảnh, quy tắc ICU), S3 (quy tắc UX), S4 (dịch
theo lô, 4 trục, prompt bằng ngôn ngữ đích), S5 (quy tắc từng thị trường), S1 (0 description, 0 screenshot).
