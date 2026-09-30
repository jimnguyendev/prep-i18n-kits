# ADR-0009: zh-Hant là Đài Loan; Hong Kong chưa có locale riêng

**Status:** Proposed (phần HK chờ quyết định sản phẩm)
**Date:** 2026-09-30
**Deciders:** Product, đội local TW và HK

## Context

Web chỉ có một locale `zh-hant` và đang ship theo bản TW (117/135 chuỗi khớp). Bản của đội HK
khác bản TW ở **156/268 chuỗi (58%)**: HK giữ "IELTS" (TW viết 雅思), viết 聆聽/口語
(TW viết 聽力/口說), dùng 由…以至 và 按 (TW dùng 從 và 依). Như vậy người dùng Hong Kong
hiện đang đọc chữ viết cho Đài Loan.

## Decision (phần đã áp dụng)

Trong kit, `zh-Hant` nghĩa là Đài Loan và theo các quyết định của đội TW. Bản HK được lưu
trong `approved.csv` với lang `zh-Hant-HK`, chỉ để tham khảo, không đưa vào zh-Hant.

## Open

Có tách thành locale `zh-Hant-HK` riêng hay không. Nếu tách: thêm locale ở web (slug, route,
CDN), thêm ngôn ngữ trên Tolgee, dùng các dòng HK trong `approved.csv` làm bản khởi đầu,
và thêm cột HK vào glossary.

## Nguồn

S5 (so sánh HK và TW), S6 (web ship theo bản TW).
