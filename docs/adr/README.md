# ADR — prep-i18n-kit

Mỗi file ghi một quyết định: bối cảnh, các phương án, lý do chọn, hệ quả, và
**nguồn** — quyết định học từ đâu và đã kiểm chứng thế nào. Sửa một quyết định
thì viết ADR mới và đánh dấu ADR cũ `Superseded`, không sửa đè.

| # | Quyết định | Trạng thái |
|---|---|---|
| [0001](0001-dich-bang-claude-code-voi-bo-dich-chung.md) | Dịch bằng Claude Code với một bộ dịch chung (phương án B), không dùng MT/AI của Tolgee | Accepted |
| [0002](0002-plugin-rieng-dung-chung-toan-cong-ty.md) | Kit là plugin riêng dùng chung toàn công ty, không nằm trong repo sản phẩm hay jimmy-kit | Accepted |
| [0003](0003-glossary-va-ban-duyet-la-file-trong-kit.md) | Glossary và bản đã duyệt là file trong kit, không dùng Glossary/TM/language notes của Tolgee | Accepted |
| [0004](0004-thu-tu-uu-tien-nguon-dich.md) | Thứ tự ưu tiên: đội local duyệt > thuật ngữ nhất quán > bản dịch sẵn có > dịch mới | Accepted |
| [0005](0005-tach-script-va-model-ghi-an-toan.md) | Script lo phần có đúng/sai, model lo phần phán đoán; ghi Tolgee chỉ ở TRANSLATED | Accepted |
| [0006](0006-cach-dich.md) | Cách dịch: theo lô có ngữ cảnh code, tự soát 4 trục, transcreate trang marketing | Accepted |
| [0007](0007-danh-gia-skill-bang-eval.md) | Đánh giá skill bằng eval có baseline, đáp án từ đội local, chuỗi mới chống rò rỉ | Accepted |
| [0008](0008-luat-publish-production.md) | Luật Publish production khi bản AI chưa duyệt cũng được xuất | Proposed |
| [0009](0009-zh-hant-la-dai-loan-hk-chua-co-locale.md) | zh-Hant là Đài Loan; Hong Kong chưa có locale riêng | Proposed |

Nguồn dùng chung cho nhiều ADR: [SOURCES.md](SOURCES.md).
