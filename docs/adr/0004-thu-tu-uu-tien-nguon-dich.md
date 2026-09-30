# ADR-0004: Thứ tự ưu tiên giữa các nguồn khi dịch

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead; các thuật ngữ `conflict` do đội nội dung chốt

## Context

Cùng một câu tiếng Anh có thể có nhiều "đáp án": bản đội local đã sửa, cách web đang
dịch, cách app đang dịch, hoặc số liệu đo được. Bản đầu tiên của kit đã chọn sai ở hai
chỗ vì dựa vào số liệu đo:

- Glossary ghi "IELTS không bao giờ dịch", trong khi tiếng Trung viết **雅思**.
- Style guide ghi zh-Hant "xưng 您", trong khi đội TW dùng **你** ở cả 30 chỗ, không có chỗ nào dùng 您.

Ngoài ra, thuật ngữ mà cả hai sản phẩm đang dùng giống nhau cũng chưa chắc đúng:
hai reviewer cho rằng 注销 dễ bị hiểu là "huỷ tài khoản".

## Decision

Thứ tự ưu tiên khi dịch:

1. `approved`: đội local đã duyệt đúng câu tiếng Anh này;
2. thuật ngữ `approved` (đội local duyệt) và `consistent` (mọi sản phẩm đang dùng giống nhau);
3. bản dịch khớp chính xác **trong cùng sản phẩm**;
4. bản dịch khớp chính xác ở sản phẩm khác, trừ khi ngữ cảnh khác thật;
5. dịch mới theo style guide.

Validator bắt lỗi khi vi phạm `approved` hoặc `consistent`; `conflict` chỉ cảnh báo;
`hint` chỉ để tham khảo.

Nếu một thuật ngữ `consistent` có vẻ sai: **giữ nguyên và báo lên**, để sửa đồng thời
mọi sản phẩm. Không tự sửa riêng ở sản phẩm đang làm.

Bản đang đúng thì trả lại nguyên văn; lệnh `write` bỏ qua các giá trị không đổi.

## Consequences

- Ý kiến đội thị trường luôn thắng số liệu đo được, kể cả khi sản phẩm hiện đang viết
  khác (ví dụ app có 1.206 chỗ dùng 您 → bị báo là lệch, không sửa hàng loạt).
- Muốn sửa một thuật ngữ `consistent` phải có quyết định chung, không một team nào tự đổi được.
- Mỗi lần có feedback mới của đội local phải thêm vào `approved.csv`; nếu bỏ qua,
  AI sẽ lặp lại đúng lỗi đó.

## Nguồn

S5 (TW/HK/KR), S6 (số liệu đo), kết quả eval vòng 1–2 (S7 trong ADR-0007).
