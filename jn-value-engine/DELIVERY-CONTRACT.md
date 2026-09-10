# JN VALUE ENGINE — NON-NEGOTIABLE DELIVERY CONTRACT

This contract is mandatory for every normal invocation of `jn-value-engine` and has higher priority than brevity, routing, complexity, convenience, or presentation preferences inferred by the Agent.

## Definition of DONE

A normal `jn-value-engine` invocation is **NOT COMPLETE** until BOTH deliverables have been visibly delivered to the user in this exact order:

1. **DELIVERABLE A — COMPLETE TEXT DECISION**
2. **DELIVERABLE B — JN VISUAL ROADMAP**

Formally:

`DONE = TEXT_COMPLETE && ROADMAP_COMPLETE && TEXT_VISIBLE_BEFORE_ROADMAP`

If only text exists: `NOT DONE`.
If only roadmap exists: `NOT DONE`.
If roadmap appears before text: `DELIVERY FAILURE`.

## Mandatory state machine

`USER_QUESTION`
→ `INTERNAL_DECISION_SCHEMA_READY`
→ `TEXT_RENDERING`
→ `TEXT_VISIBLE_TO_USER`
→ `TEXT_COMPLETION_CHECK = PASS`
→ `VISUAL_TOOL_CALL_ALLOWED`
→ `ROADMAP_RENDERING`
→ `ROADMAP_VISIBLE_TO_USER`
→ `DONE`

There is no legal transition from `USER_QUESTION`, `INTERNAL_DECISION_SCHEMA_READY`, or `TEXT_RENDERING` directly to `ROADMAP_RENDERING`.

## Deliverable A — complete text first

The text must visibly contain all 10 sections before any image tool is called:

01 决策结论
02 真正的问题
03 关键矛盾
04 方案对比
05 价值创造逻辑
06 建议路线图（文字表格）
07 关键验证指标
08 决策闸门
09 下一步行动
10 什么会让我改变判断

The text is a standalone decision answer. Do not replace any section with “see roadmap below”.

Formal output must hide internal codes and engineering terms, including but not limited to: HOLD, CONDITIONAL_GO, NEED_MORE_EVIDENCE, LEVEL 1/2/3, ENGINE-C, Router names, internal confidence fields.

## Text completion checkpoint

Before invoking ANY image generation, image editing, SVG/HTML visual renderer, or other roadmap tool, verify all are true:

- [ ] Sections 01–10 are already visible to the user.
- [ ] The core recommendation is stated in natural business language.
- [ ] A/B/C ranking is fixed if alternatives are material.
- [ ] Roadmap stages and gates are fixed.
- [ ] Metrics use only known data; unknowns say 待量化 / 建立基线 / 需验证.
- [ ] Internal status codes and engineering terminology are absent from user-facing copy.
- [ ] Reversal conditions are present.

If any box is false: **DO NOT CALL THE VISUAL TOOL. Finish the text first.**

## Deliverable B — roadmap is mandatory after text

Immediately after Deliverable A is complete, the Agent MUST continue to Deliverable B in the same invocation/turn when the host supports visual generation.

Do not stop after the text. Do not ask “要不要生成路线图?”. Do not wait for another user message. Do not treat the text as completion.

The roadmap is a visual compression of the exact same Decision Schema. It may not introduce a new conclusion, new option, new metric, new number, new budget, new timeline, or new recommendation.

## Fixed JN visual system

Default canvas: vertical 2:3, approximately 1200×1800.

Fixed order:
Hero → 01 决策结论 → 02 真正的问题 / 03 关键矛盾 / 04 当前痛点 → 05 A/B/C 方案对比 → 06 三阶段路线 → 07 KPI → 08 决策闸门 → 09 下一步 → Footer.

Brand: `JN 企业价值引擎`.
Footer: `jn-value-engine` + `从问题到价值，从判断到行动`.

Palette: dark navy #0E2A45, secondary navy #123A5A, text navy #14324A, white #FFFFFF, light blue-gray #F4F7FA, divider #DCE4EB, gold #D6A33D, pale gold #FFF3D6, recommendation green #21A657 / #EAF7EE, risk red #E34E4E / #FDECEC, information blue #3D78B7.

Use a subdued realistic industry-specific hero image, consulting/boardroom PPT aesthetics, pale-gold numbered tabs, equal-width A/B/C cards, blue three-stage arrows, KPI cards, four gold decision gates, and navy footer. No cyberpunk, neon, cartoon, magazine collage, flashy 3D, emoji icon mixing, or free redesign of information architecture.

If the text did not establish dates, budgets, ROI, benchmark values, or target values, the roadmap MUST NOT invent them.

## Exceptions

The two-deliverable contract may be changed only by an explicit user instruction such as:
- “只要文字 / 不要图” → text only.
- “只要路线图 / 不要文字” → roadmap only.
- “先别生成图” → stop after text for that invocation.
- “简版/30秒版” without saying no image → shortened text may be used, but roadmap remains required unless the user explicitly opts out of the image.

Silence is NOT an opt-out. A short question is NOT an opt-out. Missing data is NOT an opt-out. High risk is NOT an opt-out. Tool inconvenience is NOT an opt-out.

## Failure labels

- `DELIVERY_TEXT_MISSING`: roadmap delivered without full text.
- `DELIVERY_ROADMAP_MISSING`: full text delivered but roadmap omitted.
- `DELIVERY_ORDER_VIOLATION`: roadmap shown before full text.
- `DELIVERY_SCHEMA_DRIFT`: roadmap changes the text decision.
- `DELIVERY_INTERNAL_LEAK`: internal status/engineering terms appear in formal output.

Any one of these means the invocation failed the JN delivery contract even if the underlying analysis is correct.
