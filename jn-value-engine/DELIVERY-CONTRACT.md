# JN VALUE ENGINE — NON-NEGOTIABLE DELIVERY CONTRACT v5

This contract is mandatory for every normal invocation of `jn-value-engine`.

# 1｜固定流水线：文字 → 文字质检 → 路线图 → 成图质检 → DONE

唯一正常路径：

`USER QUESTION`
→ `INTERNAL DECISION / SCHEMA`
→ `DELIVER COMPLETE TEXT 01–10`
→ `TEXT_QA`
→ `TEXT_QA = PASS`
→ `SELECT SAFE VISUAL RENDERER`
→ `GENERATE JN ROADMAP`
→ `VISUAL_QA`
→ `VISUAL_QA = PASS`
→ `DONE`

完成条件：

`DONE = TEXT_VISIBLE_COMPLETE && TEXT_QA_PASS && ROADMAP_VISIBLE_COMPLETE && VISUAL_QA_PASS && TEXT_VISIBLE_BEFORE_ROADMAP`

文字完成不是 DONE；图片生成完成也不是 DONE。

# 2｜最重要的新规则：先判断宿主如何真正显示内容

不要再假设“commentary/assistant pre-tool 文本”一定会像普通最终回答一样保留在用户界面。

在任何视觉工具调用前，必须判断当前宿主的真实渲染行为：

## A. 若宿主支持“先发送正常用户可见文字，再继续调用视觉工具”
允许：
`VISIBLE TEXT → VISUAL TOOL → IMAGE`

## B. 若宿主会隐藏、折叠、替换、弱化 pre-tool commentary，或 visual tool 输出会覆盖/抢在文字前显示
则禁止使用会破坏顺序的生成式图片调用路径。

必须改用**确定性离屏渲染路径**：
- SVG / HTML / Canvas / Python/PIL 等可先在后台生成文件、且不会提前向用户展示工具输出的 renderer；
- 最终把完整文字和路线图放在同一用户可见交付中，顺序固定为“文字在上，路线图在下”；
- 如果平台支持将生成文件以内嵌图片/附件放在文字之后，优先如此。

核心原则：**选择 renderer 必须服务于真实 UI 顺序，而不是反过来。**

如果 image-generation 工具会导致“图先出现、文字后出现”，该工具在本宿主的标准 JN 交付中视为 `UNSAFE_RENDERER_FOR_ORDER`，不得使用。

# 3｜DELIVERABLE A：先完整文字

必须先对用户展示：
01 决策结论
02 真正的问题
03 关键矛盾
04 方案对比
05 价值创造逻辑
06 建议路线图（文字）
07 关键验证指标
08 决策闸门
09 下一步行动
10 什么会让我改变判断

正式输出隐藏所有内部状态码、置信度、LEVEL、ENGINE-C、Router 等工程术语。

# 4｜TEXT_QA：必须识别实际文字

文字 01–10 生成后，重新读取实际交付文本并检查：

## A. 完整性
- 01–10 全部存在且顺序正确；
- 没有模块被“见下图”“略”替代；
- 结论可独立阅读。

## B. 决策一致性
- 01 核心结论与 04 方案排序一致；
- 06 路线支持 01 结论；
- 08 Gate 与 10 反转条件一致；
- 无前后逻辑漂移。

## C. 证据纪律
- 不编造数据、预算、ROI、概率、月份或 KPI；
- 未知项写“待量化 / 建立基线 / 需验证”；
- 用户关键数字准确保留。

## D. 用户语言
- 不出现内部代码/工程术语；
- 无明显错别字、残句、重复和术语混乱。

## E. 可视化就绪
- 核心结论、真正问题、关键矛盾、A/B/C、阶段、指标、Gate、下一步都已明确。

`TEXT_QA = FAIL` → 修正文案 → 再检查，禁止生图。
`TEXT_QA = PASS` → 必须继续选择安全 renderer。

# 5｜第三阶段：选择安全 Visual Renderer

优先级按以下顺序：

1. **确定性 SVG / HTML / Canvas / Python/PIL 渲染**：优先，用于固定模板、中文文字和严格版式；
2. 其他不会提前显示工具输出、可以最终嵌在文字后的可控 renderer；
3. 生成式图片工具：仅当宿主能保证文字已真实显示且不会被隐藏/覆盖时使用。

不得为了“必须有图”而使用会导致图先文后的工具。

# 6｜DELIVERABLE B：JN 企业价值路线图

路线图只使用通过 TEXT_QA 的同一份 Decision Schema，不重新判断。

固定结构：
Hero → 01 决策结论 → 02 真正的问题 / 03 关键矛盾 / 04 当前痛点 → 05 A/B/C 方案对比 → 06 三阶段路线 → 07 KPI → 08 决策闸门 → 09 下一步 → Footer。

品牌：`JN 企业价值引擎`。
Footer：`jn-value-engine` + `从问题到价值，从判断到行动`。

默认竖版 2:3，约 1200×1800。
固定色板：深海军蓝 #0E2A45；次级海军蓝 #123A5A；文字深蓝 #14324A；白 #FFFFFF；浅灰蓝 #F4F7FA；分隔线 #DCE4EB；金色 #D6A33D；浅金 #FFF3D6；推荐绿 #21A657/#EAF7EE；风险红 #E34E4E/#FDECEC；信息蓝 #3D78B7。

固定视觉：低饱和行业写实 Hero；商业咨询/董事会PPT；浅金编号；白色圆角卡；A/B/C等宽；推荐绿、不推荐红、有条件金；三阶段深蓝→中蓝→浅蓝连续箭头；KPI横卡；4个金色Gate；深蓝Footer；扁平商务图标。

禁止赛博朋克、霓虹、卡通、杂志拼贴、闪亮3D、emoji混搭和自由改版。

# 7｜VISUAL_QA：必须识别最终成图

成图后必须检查最终图片，不只检查 prompt。
优先使用宿主原生视觉理解；不要默认 OCR，只有必要时才使用 OCR。

## A｜顺序与交付
- 完整文字实际显示在图之前；
- 路线图已生成且可见。

## B｜文图同源
- 核心结论与文字01同向；
- A/B/C与文字04一致；
- 三阶段与文字06一致；
- KPI只来自文字07；
- Gate只来自文字08；
- 下一步只来自文字09；
- 不新增事实、数字、时间、预算、ROI或KPI。

## C｜文字准确
- 主标题、模块标题、关键文案无明显错字/乱码；
- 品牌为 `JN 企业价值引擎`；
- Footer正确；
- 用户关键数字一致；
- 无伪汉字、错误偏旁、严重字形变形；
- 无内部状态码。

## D｜信息架构
01决策结论、02真正的问题、03关键矛盾、04当前痛点、05方案对比、06三阶段路线、07KPI、08决策闸门、09下一步全部存在。

## E｜视觉规范
- 2:3竖版商业咨询信息图；
- 深海军蓝+金+白/浅灰蓝；
- Hero行业相关、低饱和；
- 卡片、间距、层级、对齐清晰；
- A/B/C三列等宽；
- 三阶段连续流程；
- 4个金色Gate；
- 无严重拥挤、遮挡、裁切、溢出或不可读小字。

若关键结论/数字错误、文图漂移、编造事实、缺核心模块、明显错字乱码、品牌错误或排版不可读：`VISUAL_QA = FAIL`。

FAIL → 修图/重新生成 → 再次 VISUAL_QA，不得把失败图当正式交付。

# 8｜100分 QA

- 文字完整与逻辑：20
- 决策一致性与证据纪律：20
- 文图同源：20
- 图片文字准确性：15
- 视觉规范与可读性：15
- 顺序与交付完整：10

90–100：PASS
80–89：修正后交付
<80：FAIL

任何硬性 FAIL 项存在，即使总分≥90也不得通过。

# 9｜强制继续与例外

只要 TEXT_QA PASS 且用户没有明确说“只要文字/不要图/先别生成图”，就必须继续生成路线图；不得停止、询问或等待下一条用户消息。

只有明确用户指令可改变：
- 只要文字/不要图/先别生成图 → 文字 + TEXT_QA 后结束；
- 只要路线图/不要文字 → 路线图 + VISUAL_QA；
- 简版/30秒版但未拒绝图片 → 简版文字 + TEXT_QA → 图 + VISUAL_QA。

# 10｜Failure Labels

`TEXT_QA_INCOMPLETE`
`TEXT_QA_LOGIC_DRIFT`
`TEXT_QA_FABRICATION`
`TEXT_QA_INTERNAL_LEAK`
`DELIVERY_TEXT_MISSING`
`DELIVERY_ROADMAP_MISSING`
`DELIVERY_ORDER_VIOLATION`
`DELIVERY_PREMATURE_STOP`
`DELIVERY_SCHEMA_DRIFT`
`UNSAFE_RENDERER_FOR_ORDER`
`VISUAL_QA_TEXT_ERROR`
`VISUAL_QA_NUMBER_ERROR`
`VISUAL_QA_MISSING_SECTION`
`VISUAL_QA_STYLE_DRIFT`
`VISUAL_QA_LAYOUT_FAILURE`
`VISUAL_QA_FABRICATION`

任一 Failure 存在，本次调用不得判定 DONE。

# 11｜外部交付原则

QA过程默认内部执行，不展示状态码、评分过程和工程术语。用户只应看到：**完整文字 → 合格路线图**。
