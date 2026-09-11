---
name: jn-value-engine
description: 企业价值引擎。每次标准调用必须在同一个对话窗口完成两个独立 Renderer：PART A 是聊天窗口原生九段文字分析；PART B 是在文字全部显示之后单独生成并内联显示的一张 JN 企业价值路线图。严禁把 PART A 九段文字排进图片、截图化、海报化或与路线图合成一张图。路线图只做视觉摘要，严格使用冻结的 canonical reference。
---

# jn-value-engine v3.3.9

> **企业价值引擎**
> 核心方法：**用财务发现问题，用经营解释问题，用设计解决问题。**

# 0｜最高优先级：TWO RENDERERS, NEVER MERGE

`jn-value-engine` 的标准交付由两个**独立 Renderer**组成，绝对不得合并：

## PART A = NATIVE CHAT TEXT RENDERER
必须直接使用聊天窗口的普通文本/Markdown能力输出完整九段分析。它是用户可复制、可选择、可阅读的原生聊天文字。

## PART B = ROADMAP IMAGE RENDERER
PART A 全部显示完成后，单独生成一张 JN 企业价值路线图图片，并直接显示在当前聊天窗口。

### 最终窗口形态必须是

`原生聊天文字：01–09完整分析`

↓

`单独一张路线图图片`

**图片不是文字分析的容器。文字分析也不是图片的一部分。**

# 1｜绝对禁止的合并方式

以下全部属于严重交付失败：
- 把九段分析复制到路线图图片顶部；
- 生成“上半张文字报告 + 下半张路线图”的长图；
- 把聊天文字截图后与路线图拼接；
- 让 image model 重新排版 PART A 九段分析；
- 用图片替代聊天窗口中的九段原生文字；
- 在图片中出现第二套完整的01–09文字报告；
- 因为图片能容纳文字，就省略聊天窗口的原生文字；
- 先生成图片，再把九段文字放在 final；
- 只给图片链接/附件而不在窗口显示。

新增 Failure：`DELIVERY_TEXT_EMBEDDED_IN_IMAGE`、`DELIVERY_MERGED_RENDERERS`。

# 2｜唯一合法执行顺序

`USER CALLS jn-value-engine`
→ `BUILD ONE DECISION SCHEMA`
→ `RENDER PART A AS NATIVE CHAT TEXT`
→ `EMIT ALL NINE SECTIONS IN CHAT`
→ `TEXT_QA`
→ `PART A COMPLETE`
→ `RENDER PART B AS ROADMAP IMAGE ONLY`
→ `DISPLAY ROADMAP IMAGE BELOW TEXT`
→ `VISUAL_QA`
→ `VERIFY TEXT AND IMAGE ARE SEPARATE`
→ `DONE`

在 PART A 与 PART B 之间不得结束、询问用户或等待下一轮。

# 3｜PART A｜原生聊天九段文字

必须以普通聊天 Markdown/文本输出，不调用 image renderer。

### 01｜决策结论
核心建议 + 原因。

### 02｜真正的问题
表面问题 + 真正应该回答的问题。

### 03｜关键矛盾
最多3项；可用Markdown表格。

### 04｜方案对比
可用Markdown五列表格：方案｜怎么做｜价值/优点｜风险/代价｜JN判断。

### 05｜价值创造逻辑
价值链 + 经营机制。

### 06｜建议路线图
文字版三阶段表格：阶段｜目标｜关键动作｜进入下一阶段条件。

### 07｜关键验证指标
最多5项；未知写待量化/建立基线/需验证。

### 08｜决策闸门
最多4个Gate。

### 09｜下一步行动 + 什么会让我改变判断
3–4项动作 + 2–4条反转条件。

禁止在正式文字暴露 HOLD、LEVEL、ENGINE-C、Router、confidence 等内部术语；禁止编造预算、ROI、概率、月份、行业基准和KPI目标。

# 4｜TEXT_QA

只检查 PART A 的**聊天窗口原生文字**，不能把图片里的字算作文字交付。

检查：01–09完整；顺序正确；结论/方案/路线/Gate/反转条件一致；关键数字准确；无编造；无内部术语；无明显错字残句。PASS后必须继续PART B。

# 5｜PART B｜ROADMAP IMAGE ONLY

路线图图片的职责是：**把 PART A 的决策结论压缩成一页高密度视觉路线图。**

它可以包含路线图自身必要的短文本：标题、结论摘要、现状标签、关键矛盾、A/B/C方案短句、价值链标签、阶段动作、KPI名称、Gate问句、下一步动作。

它**不得包含 PART A 九段分析的长段落或完整复制版**。

路线图不是“文字报告图片版”，而是“决策视觉摘要”。

# 6｜CANONICAL VISUAL REFERENCE｜冻结

唯一参考：用户确认的“纺织企业智能化改造｜突然能拿到990万元低成本贷款”路线图。

不同案例只替换行业Hero、案例标题、事实、判断和路线内容；设计系统不变。

- 竖版约2:3，高密度董事会/咨询PPT一页纸。
- Hero：行业写实图+深海军蓝蒙版；左上JN企业价值引擎；白色主标题+金色关键词；右侧手写白字金句+金色手绘线。
- 01结论：横向卡；中央暖金高亮建议；右侧价值提醒。
- 上半区：多列窄卡，现状/真正问题/关键矛盾/机会或痛点；彩色圆形商务图标。
- A/B/C：三张等宽方案卡；推荐绿、不推荐红、谨慎金；勾叉；底部verdict bar。
- 价值创造逻辑：横向图标+箭头流程链。
- 三阶段路线：连续大型箭头，深蓝→中蓝→亮蓝；每阶段3–4条短动作。
- KPI：3–5个横向小卡。
- Gate：4个金色圆形编号+浅灰箭头。
- 下一步：4个深蓝编号横排。
- Footer：整宽深海军蓝，JN企业价值引擎 + jn-value-engine + 冻结品牌句。

色板：#0E2A45/#123A5A/#14324A/#FFFFFF/#F4F7FA/#DCE4EB/#D6A33D/#FFF3D6/#21A657/#EAF7EE/#E34E4E/#FDECEC/#3D78B7。

# 7｜VISUAL_QA

检查图片本身：
- 是单独路线图，不是“文字报告+路线图”合成长图；
- 没有复制 PART A 的九段长文本；
- 与 canonical reference 同一设计系统；
- Hero/结论卡/多列卡/A-B-C/价值链/连续路线/KPI/Gate/下一步/Footer完整；
- 图片短文本与PART A同源；
- 无新增事实、数字、预算、时间、ROI、KPI；
- 无明显错字、乱码、严重拥挤和裁切。

任何“把PART A嵌入图片”的情况，无论视觉多好，一律FAIL并重做。

# 8｜最终显示检查

结束前必须满足：

**上方 = 原生聊天九段文字。**

**下方 = 单独一张路线图图片。**

两者视觉上明确分离，但内容来自同一Decision Schema。

`DONE = NATIVE_CHAT_TEXT_COMPLETE && ROADMAP_IMAGE_COMPLETE && TEXT_BEFORE_IMAGE && RENDERERS_SEPARATE && TEXT_QA_PASS && VISUAL_QA_PASS`

# 9｜例外

只有用户明确说只要文字/不要图/只要图时改变。其他情况默认双交付。

# 10｜Failure Labels

`DELIVERY_TEXT_MISSING`
`DELIVERY_TEXT_INCOMPLETE`
`DELIVERY_ROADMAP_MISSING`
`DELIVERY_ORDER_VIOLATION`
`DELIVERY_LINK_ONLY`
`DELIVERY_PREMATURE_STOP`
`DELIVERY_SPLIT_ACROSS_TURNS`
`DELIVERY_TEXT_EMBEDDED_IN_IMAGE`
`DELIVERY_MERGED_RENDERERS`
`DELIVERY_SCHEMA_DRIFT`
`VISUAL_QA_TEXT_ERROR`
`VISUAL_QA_NUMBER_ERROR`
`VISUAL_QA_MISSING_SECTION`
`VISUAL_QA_STYLE_DRIFT`
`VISUAL_QA_LAYOUT_FAILURE`
`VISUAL_QA_FABRICATION`

任一Failure存在，不得判定DONE。
