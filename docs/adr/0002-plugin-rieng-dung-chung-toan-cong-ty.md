# ADR-0002: Kit là plugin Claude Code riêng, dùng chung toàn công ty

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead

## Context

Phương án B (ADR-0001) chỉ chạy được nếu mọi repo dùng **cùng một** glossary và skill.
Nếu chép bộ dịch vào từng repo, các bản sẽ trôi phiên bản khỏi nhau — đúng kiểu lệch mà
B muốn tránh. Yêu cầu từ người dùng: kit dùng được cho nhiều repo, gồm cả web và app,
và cho mọi team.

## Decision

Một repo riêng `prep-i18n-kit`, phân phối dưới dạng **plugin Claude Code** (`plugin.json`
+ `marketplace.json`, giống cách jimmy-kit phân phối). Mỗi người cài một lần là dùng
được trong mọi repo. Repo của từng sản phẩm được khai trong `projects.json` và nhận diện
qua **git remote**, không qua tên thư mục.

## Options Considered

- **Để trong `practice-lab-web/.agents/skills/`:** tiện cho web, nhưng app và các team
  khác không dùng được nếu không chép sang. Bản đầu tiên đã đặt ở đây, sau đó chuyển ra.
- **Đưa vào jimmy-kit:** kit này cấm tiếng Việt và tên công ty trong `skills/`, trong khi
  skill cần style guide tiếng Việt và thuật ngữ riêng của Prep.
- **Plugin riêng (chọn):** một nguồn duy nhất, cập nhật qua MR và tăng version.

## Consequences

- Thêm repo mới chỉ cần một mục trong `projects.json`.
- Script chỉ dùng Python stdlib, nên chạy được trong cả repo Node lẫn repo Flutter.
- Thay đổi glossary, bản duyệt hay style guide đi qua MR (phân quyền sở hữu ghi trong README).
- Người dùng phải cập nhật plugin để nhận glossary mới.

## Nguồn

S3 (cách phân phối và ràng buộc của jimmy-kit), yêu cầu của người dùng trong phiên 30/09.
