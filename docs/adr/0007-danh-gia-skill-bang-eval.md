# ADR-0007: Đánh giá skill bằng eval

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead

## Context

Skill chỉ có ích nếu làm tốt hơn Claude Code không dùng skill, và cách duy nhất biết được
là đo. Eval dễ tự lừa mình theo ba kiểu: đáp án bị rò rỉ, tiêu chí không phân biệt được hai
bản, và môi trường chạy làm lệch kết quả.

## Decision

- **Có baseline:** mỗi tình huống chạy song song một bản có skill và một bản không có skill,
  cùng đề bài, cùng ràng buộc (offline, không ghi repo, không ghi Tolgee).
- **Đáp án là bản sửa của đội local** (S5), không phải ý thích của người viết skill.
- **Chống rò rỉ đáp án:** chuỗi test là chuỗi mới, kiểm cùng quy tắc nhưng không có trong
  `approved.csv`. Chỉ giữ một chuỗi trùng có chủ đích ("Try again") để kiểm việc dùng lại bản duyệt.
- **Chấm bằng script:** cùng một validator và cùng một bộ regex cho cả hai bản. Phần cần đánh
  giá chủ quan (câu headline hay hay dở) để người xem trong trang review.
- **Soi chính eval sau mỗi vòng:** tìm tiêu chí mà hai bản đều qua, và tìm lỗi của môi trường chạy.

## Kết quả

| Vòng | Có skill | Không skill | Ghi chú |
|---|---|---|---|
| 1 | 100% | 90% | Tình huống 2 và 3 không phân biệt được hai bản → thay bằng tình huống khác |
| 2 | 100% | 65% | Tình huống mới: chuỗi landing KR mới, chuỗi TW mới |

Lỗi của chính eval đã phát hiện:

1. Chạy trong repo web thì baseline đọc được `ko.json` đã chứa sẵn bản sửa của đội KR, nên
   điểm của nó cao giả.
2. Tiêu chí "không sửa repo" bị đánh trượt oan vì thư mục do một phiên khác tạo ra.
3. Các bản thử chạy song song ghi đè file của nhau → skill bắt buộc mỗi lần chạy dùng thư mục riêng.

## Consequences

- Giới hạn: mỗi cấu hình mới chạy 1 lần; chưa có người bản ngữ chấm chất lượng câu chữ.
- Vòng tiếp theo: chạy 3 lần mỗi cấu hình; chạy các tình huống KR/TW trong repo prep-app;
  nhờ đội TW/KR chấm trực tiếp output.
- Tiêu chí eval nằm trong `skills/prep-translate/evals/evals.json`; workspace chạy thử để ngoài kit.

## Nguồn

Quy trình của skill-creator; S5 làm đáp án; kết quả vòng 1–2 (30/09/2026).
