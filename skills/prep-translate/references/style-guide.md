# Prep UI translation style guide

Shared by every Prep product. Two kinds of evidence, in order of authority:

1. **Local market teams' corrections** (Sep 2026: TW, HK, KR localization
   feedback on the Practice Lab landing and pricing pages, 517 reviewed
   strings in `approved.csv`). Where a market team has spoken, follow it —
   even when Prep's existing copy does otherwise.
2. **Measured product copy** (597 web keys, 3,677 app keys, 30/09/2026) for
   everything the market teams haven't reviewed.

Where products disagree and no market team has decided, it says so under
**Open decisions** — do not silently pick a side; use the form the target
product already uses and flag it in the report.

## Contents
1. Rules for every language
2. Vietnamese (vi)
3. Thai (th)
4. Indonesian (id)
5. Korean (ko)
6. Japanese (ja)
7. Chinese, Simplified (zh-Hans)
8. Chinese, Traditional (zh-Hant)
9. Open decisions

---

## 1. Rules for every language

**It is software UI, not prose.** A label stays a label: don't turn "Retake"
into a sentence, don't add a full stop the source lacks, don't add
exclamation marks for warmth. Keep the source's line breaks.

**Casing is CSS's job.** Translate in normal sentence case even when the English
key is shouted ("WRITING TASK 2", "PRACTICE LABS"). The web has 26 Vietnamese
strings stored in capitals because someone mirrored the design — they break
the moment the design changes and read as shouting in every other context.
Exception: brand casing in the glossary (Pro, IELTS).

**Placeholders are code.** Never translate, rename, reorder-break or drop
anything in braces: `{name}`, `{count, number}`, `{}` (the app's positional
placeholder), `{{name}}`. Word order may move around them. In ICU plurals,
translate only the words inside each branch and keep `#`.

**Plurals by language.** vi, th, id, ko, ja, zh-Hans and zh-Hant have a single
plural form. Output only the `other` branch:
`{count, plural, other {# bài thi}}`. For app keys that are plural children
(`….one`, `….other`), translate each child with the same text.

**Approved text first.** If a market team reviewed this exact English
(`approved` in the context), use their text. It is the only translation
here a native reviewer signed off.

**Glossary terms win.** `approved` and `consistent` terms must appear in their
glossary form (the validator enforces both). If a `consistent` form looks
wrong — two reviewers flagged 注销 for "Log out" — keep it and report it: the
fix is to change it in every product at once, not in the one you're touching.
A `conflict` term is undecided — use the form the current product already
uses and list it in the report. A `hint` term depends on context; read its note.

**Reuse before you write.** If the same English already exists in either
product (`exactMatches`), reuse that translation unless the context is truly
different — "Previous" is `Câu trước` for a question and `Phần trước` for a
section; both are right. When you deviate, say why in the item's `note`.

**Don't rewrite what is already right.** When a queued key already has a
correct translation, return it unchanged, byte for byte — don't reformat a
plural, re-space, or swap a synonym. `write` skips unchanged values, and
unnecessary edits bury the real ones in Tolgee's history.

**Marketing pages are transcreated; product UI is translated.** Landing,
pricing and testimonial copy (hero headlines, taglines, quotes) carry a pain
point and a promise. Keep those, not the English syntax — the KR team rewrote
"Find out exactly why your / IELTS band is stuck" as "내 IELTS 점수, / 왜
안오르는지 정확히 알려드립니다." App and dashboard strings stay close to the
source. A headline split across two keys (line 1 / line 2) is one sentence:
translate the pair together so each line still reads naturally.

**People's names.** Keep Western names in Latin letters (Jackson Howard stays
Jackson Howard in ko, not 잭슨 하워드). For Vietnamese names outside vi, drop
the diacritics (TW: "Trung Duc", not "Trung Đức") or use the given name only
(KR: "Trang"). Never transliterate or invent a local name.

**Dates follow the market.** TW writes 2027/09/14 (YYYY/MM/DD). Don't copy the
English DD/MM/YYYY order into a locale that doesn't use it.

**Numbers and units stay attached correctly**: "Achieved 7.5" → "7.5 달성"
(not "달성 7.5"), "+1.7 bands" → "+1.7밴드". Put the number where the target
language's grammar puts it.

**Match the moment** (from the ux-writing kit):
- Buttons keep verb + object when the source has it ("Send message" →
  "Gửi tin nhắn", not "Gửi").
- Errors keep what happened, why, and what to do. The product takes the
  blame — never make the learner the subject of a failure.
- No jokes or exclamation marks in errors, payments, or destructive actions.
- No marketing words the source doesn't have ("mở khóa sức mạnh…").
- Length: stay close to the source. A 2-word button must stay a short button.

**Self-review before output** (from lu-ai-service's translation pass). Draft
the batch, then reread it on four axes and fix before returning:
1. **Accurate** — the meaning of the source *in this UI spot* (check `usages`).
2. **Fluent** — reads like native UI copy, not machine translation.
3. **Consistent** — same term, same translation across the batch, siblings
   and the other product.
4. **Register** — the per-language rules below.

---

## 2. Tiếng Việt (vi)

Viết như người Việt viết giao diện, không dịch từng chữ.

- **Xưng hô:** gọi người học là **"bạn"** (1.165 lần trên hai sản phẩm). Không
  dùng "mình", "các bạn", "quý khách". Khi sản phẩm tự nói về mình thì dùng
  **"chúng tôi"** hoặc "Prep".
- **Lỗi thì sản phẩm nhận lỗi:** "Chưa lưu được bài làm. Thử lại nhé." — không
  viết "Bạn đã nhập sai".
- **Cắt chữ đệm:** "vui lòng", "xin lưu ý rằng", "hệ thống đang tiến hành",
  "nhằm mục đích", "một cách", "việc" chỉ giữ khi câu nguồn thật sự có ý đó.
  "Saving…" → **"Đang lưu…"**, không phải "Hệ thống đang tiến hành lưu".
- **Nút:** động từ + tân ngữ nếu nguồn có: "Start practice" → "Bắt đầu luyện tập".
- **Viết hoa:** chỉ viết hoa chữ đầu câu và tên riêng. "Phòng luyện tập",
  không "Phòng Luyện Tập", càng không "PHÒNG LUYỆN TẬP".
- **Thuật ngữ IELTS giữ nguyên khi người học quen dùng tiếng Anh:** IELTS, band,
  Writing Task 1/2 khi là tên phần thi, Speaking Part 1/2/3. Tên kỹ năng dịch khi
  đứng một mình trong câu (Nghe, Đọc, Viết, Nói).
- **Dấu câu:** dấu ba chấm dùng "…" theo nguồn; không thêm "!" khi nguồn không có.

## 3. Thai (th)

- Address the learner as **คุณ** (1,265 uses).
- Don't add polite particles to labels, buttons or titles. In full sentences
  the products use **ค่ะ/คะ** (299 uses) and almost never ครับ (3) — follow
  that when a particle is needed.
- No spaces between Thai words; use a space to separate clauses and around
  Latin words and numbers ("ทำ Test อีกครั้ง").
- Loanwords: use the Royal Institute spelling where one exists (อัปเกรด, not อัพเกรด).

## 4. Indonesian (id)

- Address the learner as **Anda** (1,287 uses; "kamu" appears 5 times and is
  wrong for Prep's register).
- Buttons are imperative verbs: "Coba lagi", "Ulangi", "Masuk".
- Keep English product names only when they are in the glossary.

## 5. Korean (ko)

- Buttons and labels are nouns or bare stems ("다시 시도", "업그레이드",
  "로그아웃"): about 90% of short strings have no sentence ending.
- Full sentences lean **해요체** (…요, about 60%) but 합니다체 is common too
  (about 40%, errors included). Don't normalise one into the other: match the
  ending your `siblings` in the same key group use, and keep it uniform within
  one screen.
- Keep a space between Korean and Latin words or numbers where natural
  ("Pro로 업그레이드" attaches the particle directly to the Latin word).

What the KR team corrected in AI-translated copy (`approved.csv`, KR rows —
the rejected AI draft is in each row's `note`):
- **Loanword calques → Korean terms:** 시험 라이브러리 → **시험 자료실**;
  어휘 자원 → **어휘 사용 능력** (Lexical Resource); 점수 보장 →
  **밴드 스코어 보장제**.
- **"attempt" is not 시도.** A test sitting is **응시** ("Free trial attempt" →
  무료 체험 응시); a submitted answer is **답안**.
- **English word order leaking through:** "달성 7.5" → "7.5 달성";
  "연습 4가지 영역 모두" → "4가지 영역 모두 연습".
- **Speak from the learner's side with 내:** "내 실수를 확인하고…",
  "내 답변의 감점 요인을 확인해보세요".
- **Headlines as noun phrases, not literal sentences:** "What changes as you
  move up" → "플랜별 차이 한눈에 보기"; "Let's move closer to your target
  today" → "오늘도 목표를 향해 한 걸음 더".
- **Testimonials in 해요체**, spoken and warm; FAQ answers and notices may
  stay 합니다체.
- **Western-market caveats get localized:** "No card needed" / "No credit
  card required" → "무료로 체험해보세요" or "결제는 필요 없습니다", not a
  literal credit-card sentence.
- "9.0 scorers" → **IELTS 만점자(9.0)**.

## 6. Japanese (ja)

- **です/ます** throughout; never plain だ/である form.
- **Full-width punctuation** 。、！？： after Japanese text.
- Buttons are short nouns ("再試行", "ログアウト"); only about 5% of short
  strings end in する, so drop it unless the siblings keep it.
- Katakana for IELTS skill names is the product norm (リーディング, ライティング).

## 7. Chinese, Simplified (zh-Hans)

- **Full-width punctuation** ，。！？： — never `,` `!` `?` after Chinese characters.
- **Space between Chinese and Latin words or numbers** ("写作任务 2",
  "升级为 PRO"). The web does this 83% of the time; follow it.
- **IELTS is 雅思** in running text (the web does this in all 25 cases).
- Address form: see **Open decisions** — the two products disagree.

## 8. Chinese, Traditional (zh-Hant) — Taiwan

zh-Hant means **Taiwan**. The TW team reviewed 242 Practice Lab strings; their
choices below override what the products currently ship.

- **Address the learner as 你** — the TW team used 你 30 times and 您 never,
  and changed 您可能感興趣 to 你可能有興趣. Existing product copy mostly says
  您 (the app: 1,206 times); that is now drift. Use 你 in new or re-translated
  strings, and report the 您 strings you pass — don't mass-edit them.
- **IELTS is 雅思** ("雅思成績", "達到雅思 7.5 分").
- Skill names: **聽力, 閱讀, 寫作, 口說** (口說, not 口語; 聽力, not 聆聽 —
  those are Hong Kong).
- **Plan names stay Latin:** Free, Core, Premium ("Free 可以獲得什麼？").
  The adjective "free" is 免費 ("永久免費").
- **IELTS criterion names stay English:** Lexical Resource, Grammatical Range
  and Accuracy, Fluency and Coherence, Pronunciation.
- Plan billing: 月繳, 季繳, 年繳; a plan limited to annual billing is **僅限年繳**.
- Taiwan vocabulary: 從 / 依 (not 由 / 按), 點選 (not 點擊), 檢視, 登入, 影片.
- **Dates YYYY/MM/DD:** 會員到期日：2027/09/14.
- **Full-width punctuation**, and a **space between Chinese and Latin words
  or numbers** (87 of 87 cases in the TW copy): "根據 1,800 多萬份", not
  "根據1,800".

### Hong Kong (reference only)

There is no zh-Hant-HK locale; Hong Kong users get the Taiwan copy today,
although the HK team's version differs in 156 of 268 strings (58%): they keep
"IELTS" untranslated, write 聆聽 / 口語, 由…以至, 按. The HK text is returned
as `approved` with lang `zh-Hant-HK` for reference — don't put it in zh-Hant.

---

## 9. Open decisions

These are real disagreements between web and app. Until the content team
decides, use the form the target product already uses, and list every string
you touched here in the report so the decision has data behind it.

| Topic | web | app |
|---|---|---|
| zh-Hans address form | mostly 您 (69 vs 35) | mostly 你 (746 vs 214) |
| vi plan "Core" | "Core" | "Cơ bản" |
| vi "Try again" | "Làm lại" | "Thử lại" |
| "Go Premium" CTA (vi) | "Dùng Premium"; `dashboard.go_premium` says "Nâng cấp Pro" (bug) | "Nâng cấp Premium" |
| "Pro" casing | Pro | PRO |
| zh-Hans "Log out" | 注销 | 注销 — consistent, but reads as "deactivate account"; 退出登录 is usual |

Decisions a market team has already made (apply them; the products still
need to catch up):

| Topic | Decision | By |
|---|---|---|
| zh-Hant address form | 你 (products mostly say 您) | TW team |
| zh-Hant plan names | Free / Core / Premium in Latin (app says 高級 for Premium) | TW team |
| zh-Hant "Try again" | 再試一次 | TW team |
| zh-Hant IELTS | 雅思 | TW team |
| Hong Kong locale | not decided — HK copy differs from TW in 58% of strings | product |

The full term list with status per language is `glossary.csv`.
