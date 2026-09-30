# ADR-0001: Dịch bằng Claude Code với một bộ dịch chung (phương án B)

**Status:** Accepted
**Date:** 2026-09-30
**Deciders:** FE lead (người đề xuất), quản lý trực tiếp (duyệt chi phí)

## Context

Web (practice-lab-web) đã chuyển sang Tolgee self-host; app (prep-app) còn trên Crowdin.
Mục tiêu là giảm chi phí dịch. Lo ngại chính: nếu web và app cùng dùng AI để dịch
thì hai bên sẽ lệch nhau. Đo thực tế (S6): **126 câu tiếng Anh trùng nhau, 35 câu (28%)
đã lệch tiếng Việt** dù chưa dùng AI — ví dụ "Core" là `Core` trên web, `Cơ bản` trong app.
Tức là nguyên nhân gây lệch là thuật ngữ, không phải công cụ dịch.

## Decision

Mỗi repo tự dịch bằng Claude Code, nhưng dùng **chung một bộ dịch**: glossary, style guide,
bản đã được đội local duyệt, và một skill `prep-translate` tra bản dịch có sẵn của **mọi**
sản phẩm trước khi dịch. Không cấu hình MT hay LLM provider trên Tolgee.

## Options Considered

| | Phương án | Chi phí | Rủi ro lệch | Nhận xét |
|---|---|---|---|---|
| A | Mỗi repo tự dịch, không chia sẻ gì | Thấp nhất | Cao (28% và tăng dần) | Đang là hiện trạng |
| **B** | **Mỗi repo tự dịch, dùng chung bộ dịch** | **Thấp** | **Thấp với thuật ngữ** | **Chọn** |
| C | Một người dịch tập trung trên Tolgee cho mọi project | Thấp | Thấp nhất | Cần người trực, chậm hơn một nhịp |
| D | AI Translator của Tolgee + key Anthropic riêng | Token (nhỏ) | Trung bình | Không có TM dùng chung khi chưa có license |
| E | Gộp thành một project Tolgee chia theo namespace | Cao (migrate 3.677 key) | Không lệch | Không nên làm lúc này |

## Trade-off Analysis

- Chi phí token không phải là điểm nghẽn: dịch lại toàn bộ web khoảng $2–5, cả app khoảng
  $15–30 với Sonnet (ước tính thô). Điểm nghẽn là công review của người.
- Claude Code chỉ "miễn phí biên" khi dev chạy trên seat của mình. Nếu đưa vào CI thì phải
  dùng API key và chi phí ngang với D. Khi đó nên cân nhắc lại D.
- C chắc chắn nhất về độ nhất quán, nhưng B cho các team tự chủ. Đổi lại, B phải giải
  quyết chuyện bộ dịch lệch phiên bản giữa các repo (xem ADR-0002).

## Consequences

- Dễ hơn: không phát sinh hoá đơn MT; mọi bản dịch đều đối chiếu được với các sản phẩm khác.
- Khó hơn: cần một người giữ glossary và `approved.csv`, và cần đủ reviewer cho từng ngôn ngữ.
- Xem lại khi: có license Tolgee (TM dùng chung + Glossary), hoặc khi cần dịch tự động trong CI.

## Nguồn

S1 (license, `default-primary`, auto-translate), S2 (MT, AI Translator, TM), S6 (đo lệch 28%).
