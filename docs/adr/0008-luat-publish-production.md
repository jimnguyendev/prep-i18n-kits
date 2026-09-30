# ADR-0008: Luật Publish production

**Status:** Proposed
**Date:** 2026-09-30
**Deciders:** Người giữ i18n, đội nội dung, FE lead

## Context

Skill ghi bản dịch ở trạng thái TRANSLATED (chưa duyệt). Cấu hình CDN hiện xuất cả
TRANSLATED lẫn REVIEWED (theo bản backup; `cf-r2-prod` chưa kiểm được). Vì vậy lần Publish
kế tiếp sẽ đưa **mọi** bản đã lưu lên production, kể cả bản AI chưa ai duyệt. Trên bản
Tolgee free, quyền Publish đi kèm vai trò Manage (toàn quyền quản trị project).

## Options

- **A. Người Publish tự kiểm trước khi bấm.** Đơn giản, key mới luôn có chữ dịch. Nhưng
  phụ thuộc hoàn toàn vào kỷ luật của người bấm.
- **B. CDN production chỉ xuất REVIEWED.** Bản AI chưa duyệt không thể lên production.
  Đổi lại, key chưa duyệt sẽ hiện chữ trong bản build (thường là tiếng Anh) cho tới khi có người duyệt.
- **C. Kết hợp:** dùng B cho các ngôn ngữ đã có reviewer (vi, zh-Hant/TW, ko), dùng A cho các
  ngôn ngữ còn lại. Nếu Tolgee không hỗ trợ lọc trạng thái theo từng ngôn ngữ trong một cấu hình
  thì cần tách thành nhiều cấu hình CDN.

## Đề xuất

C, sau khi kiểm xem cấu hình CDN có lọc được trạng thái theo ngôn ngữ không. Trong lúc chờ,
áp dụng A và giới hạn quyền Publish cho 1–2 người.

## Nguồn

S1 (cấu hình CDN, `ProjectPermissionType`), S7 (sync tự merge sau Publish).
