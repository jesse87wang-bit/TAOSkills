# JN VALUE ENGINE — NON-NEGOTIABLE DELIVERY CONTRACT v2

This contract is mandatory for every normal invocation of `jn-value-engine` and overrides brevity, routing, complexity, convenience, and default tool-call habits.

## The key implementation rule

**The complete text must be emitted as a USER-VISIBLE assistant message BEFORE the visual/image tool call is issued.**

It is NOT sufficient to internally draft the text and then call the image tool before sending the text in a later final message. If the host UI renders tool output before the final answer, placing the text only in the final answer violates this contract.

Therefore the required runtime sequence is:

`USER QUESTION`
→ `INTERNAL DECISION / SCHEMA`
→ `USER-VISIBLE TEXT MESSAGE (01–10)`
→ `TEXT_VISIBLE_ACK = TRUE`
→ `IMAGE/VISUAL TOOL CALL`
→ `ROADMAP VISIBLE`
→ `DONE`

### Host/channel implementation
If the host supports a user-visible pre-tool assistant/commentary message, **put the entire 01–10 text answer there first**, then call the visual tool. Do NOT defer the 01–10 answer to the final channel after the image tool.

If a host genuinely cannot display user-visible text before a visual tool call, the Agent must not claim the required order was satisfied. It should use a rendering path that can be invoked after visible text, or report the host limitation rather than silently reversing the order.

## Definition of DONE

`DONE = TEXT_VISIBLE_COMPLETE && ROADMAP_VISIBLE_COMPLETE && TEXT_RENDER_TIMESTAMP < ROADMAP_RENDER_TIMESTAMP`

- text only → `DELIVERY_ROADMAP_MISSING`
- roadmap only → `DELIVERY_TEXT_MISSING`
- roadmap visually appears first → `DELIVERY_ORDER_VIOLATION`
- text was internally prepared but not visible before tool call → `DELIVERY_ORDER_VIOLATION`

## Deliverable A — complete text first

Before ANY image/visual tool call, the user must already be able to read all ten sections:

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

Formal output must hide internal codes and engineering terms, including HOLD, CONDITIONAL_GO, NEED_MORE_EVIDENCE, LEVEL 1/2/3, ENGINE-C, Router names and confidence fields.

## Mandatory pre-tool checkpoint

Immediately before calling image generation / SVG / HTML / Canvas / visual renderer, verify:

- [ ] 01–10 have ALREADY BEEN SENT in a user-visible assistant message.
- [ ] The user can see the recommendation before the roadmap starts rendering.
- [ ] No internal status codes appear in the visible text.
- [ ] A/B/C ranking is fixed when material.
- [ ] Roadmap stages, metrics, gates and next actions are fixed.
- [ ] Unknown values use 待量化 / 建立基线 / 需验证.
- [ ] Reversal conditions are present.

If the first checkbox is false, **THE IMAGE TOOL CALL IS FORBIDDEN.**

## Deliverable B — mandatory roadmap after text

Once Deliverable A is visibly complete, continue automatically to roadmap generation. Do not stop, ask permission, or wait for another user turn unless the user explicitly opted out of the image.

The roadmap must use the same Decision Schema and may not add a new conclusion, option, metric, number, budget, timeline or recommendation.

## Fixed JN visual system

Default canvas: vertical 2:3, approximately 1200×1800.

Fixed order:
Hero → 01 决策结论 → 02 真正的问题 / 03 关键矛盾 / 04 当前痛点 → 05 A/B/C 方案对比 → 06 三阶段路线 → 07 KPI → 08 决策闸门 → 09 下一步 → Footer.

Brand: `JN 企业价值引擎`.
Footer: `jn-value-engine` + `从问题到价值，从判断到行动`.

Palette: dark navy #0E2A45, secondary navy #123A5A, text navy #14324A, white #FFFFFF, light blue-gray #F4F7FA, divider #DCE4EB, gold #D6A33D, pale gold #FFF3D6, recommendation green #21A657 / #EAF7EE, risk red #E34E4E / #FDECEC, information blue #3D78B7.

Use a subdued realistic industry-specific hero image, consulting/boardroom PPT aesthetics, pale-gold numbered tabs, equal-width A/B/C cards, blue three-stage arrows, KPI cards, four gold decision gates, and navy footer. No cyberpunk, neon, cartoon, magazine collage, flashy 3D, emoji icon mixing, or free redesign of information architecture.

Do not invent dates, budgets, ROI, benchmark values or target values not established in Deliverable A.

## Exceptions

Only explicit user instructions can change the contract:
- “只要文字 / 不要图” → text only.
- “只要路线图 / 不要文字” → roadmap only.
- “先别生成图” → stop after text for that invocation.
- “简版/30秒版” without opting out of image → shorter text first, roadmap still follows.

Silence, short questions, missing data, high risk, tool inconvenience, or model preference are NOT opt-outs.

## Failure labels

- `DELIVERY_TEXT_MISSING`
- `DELIVERY_ROADMAP_MISSING`
- `DELIVERY_ORDER_VIOLATION`
- `DELIVERY_SCHEMA_DRIFT`
- `DELIVERY_INTERNAL_LEAK`

Any failure means the invocation failed even if the analysis itself was correct.
