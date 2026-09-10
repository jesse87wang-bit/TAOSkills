# JN VALUE ENGINE — NON-NEGOTIABLE DELIVERY CONTRACT v4

This contract is mandatory for every normal invocation of `jn-value-engine`.

# 1｜固定流水线：文字 → 文字质检 → 路线图 → 成图质检 → DONE

正常调用只有一条合法路径：

`USER QUESTION`
→ `INTERNAL DECISION / SCHEMA`
→ `DELIVER COMPLETE TEXT 01–10`
→ `TEXT_QA`
→ `TEXT_QA = PASS`
→ `CONTINUE_EXECUTION = TRUE`
→ `GENERATE JN ROADMAP`
→ `VISUAL_QA`
→ `VISUAL_QA = PASS`
→ `DONE`

任何一步失败都不得宣告 DONE。

完成条件：

`DONE = TEXT_VISIBLE_COMPLETE && TEXT_QA_PASS && ROADMAP_VISIBLE_COMPLETE && VISUAL_QA_PASS && TEXT_VISIBLE_BEFORE_ROADMAP`

# 2｜DELIVERABLE A：先完整文字

必须先向用户展示：
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

# 3｜TEXT_QA：文字生成后、路线图生成前的强制检查

文字 01–10 已经生成后，必须先识别/读取刚刚生成的文字内容，以用户实际可见版本为准，而不是只相信内部草稿。逐项检查：

## A. 完整性
- [ ] 01–10 十个模块全部存在且顺序正确。
- [ ] 没有模块被“见下图”“略”等替代。
- [ ] 结论能够独立阅读。

## B. 决策一致性
- [ ] 01 的核心结论与 04 的方案排序一致。
- [ ] 06 的三阶段路线支持 01 的结论。
- [ ] 08 的 Gate 与 10 的反转条件不互相冲突。
- [ ] 不存在前文推荐、后文否定同一方案的逻辑漂移。

## C. 证据纪律
- [ ] 用户未提供的数据没有被编造。
- [ ] 未知项统一使用“待量化 / 建立基线 / 需验证”。
- [ ] 没有凭空出现行业均值、ROI、概率、预算、月份、KPI 目标。
- [ ] 用户给出的关键数字被正确保留，不擅自改写。

## D. 用户语言
- [ ] 不出现 HOLD / CONDITIONAL_GO / NEED_MORE_EVIDENCE / LEVEL / ENGINE-C / Router / confidence 等内部语言。
- [ ] 结论是企业经营者可直接理解的自然语言。
- [ ] 表格和段落不存在明显重复、残句、错别字或术语混乱。

## E. 可视化就绪
- [ ] 已明确 1 条核心结论。
- [ ] 已明确真正的问题。
- [ ] 已明确最多 3 个关键矛盾/痛点。
- [ ] A/B/C 方案及排序已确定（若三方案有意义）。
- [ ] 三阶段路线已确定。
- [ ] 3–5 个指标已确定或标记待量化。
- [ ] 4 个 Gate 已确定。
- [ ] 3–4 个下一步动作已确定。

### TEXT_QA 判定
所有必要项通过：`TEXT_QA = PASS`，必须继续生成路线图。
任何必要项失败：`TEXT_QA = FAIL`，先修正文字，再重新检查；不得直接生图。

# 4｜强制继续规则

`TEXT_QA = PASS` 后，只检查用户是否明确说“不要图 / 只要文字 / 先别生成图”。

若没有明确 opt-out：

**下一动作必须是视觉工具调用。不得 STOP、RETURN、FINALIZE、WAIT_FOR_USER。**

文字完成只是中间状态，不是任务完成。

# 5｜DELIVERABLE B：JN 企业价值路线图

路线图必须使用通过 TEXT_QA 的同一份文字/Decision Schema，只做视觉压缩，不重新判断。

固定信息结构：
Hero → 01 决策结论 → 02 真正的问题 / 03 关键矛盾 / 04 当前痛点 → 05 A/B/C 方案对比 → 06 三阶段路线 → 07 KPI → 08 决策闸门 → 09 下一步 → Footer。

固定品牌：`JN 企业价值引擎`。
Footer：`jn-value-engine` + `从问题到价值，从判断到行动`。

默认竖版 2:3，约 1200×1800。

固定色板：深海军蓝 #0E2A45；次级海军蓝 #123A5A；文字深蓝 #14324A；白 #FFFFFF；浅灰蓝 #F4F7FA；分隔线 #DCE4EB；金色 #D6A33D；浅金 #FFF3D6；推荐绿 #21A657 / #EAF7EE；风险红 #E34E4E / #FDECEC；信息蓝 #3D78B7。

固定风格：商业咨询/董事会 PPT；低饱和行业 Hero；浅金编号；白色圆角卡片；A/B/C 等宽；推荐绿、不推荐红、有条件金；三阶段深蓝→中蓝→浅蓝连续箭头；KPI 横卡；4 个金色 Gate；深蓝 Footer；扁平商务图标。禁止自由换主题、赛博朋克、霓虹、卡通、杂志拼贴、闪亮3D和 emoji 混搭。

# 6｜VISUAL_QA：成图之后的强制检查

路线图生成后必须识别/检查最终成图本身，而不是只检查生成 prompt。优先使用宿主的原生视觉理解直接读取图片；不要默认依赖 OCR。只有原生视觉无法可靠读取时才考虑 OCR。

逐项检查：

## A. 交付顺序
- [ ] 完整文字实际显示在路线图之前。
- [ ] 路线图确实已经生成并可见。

## B. 文图同源
- [ ] 图片核心结论与文字 01 完全同向。
- [ ] A/B/C 方案及推荐关系与文字一致。
- [ ] 三阶段路线与文字 06 一致。
- [ ] KPI/指标只来自文字 07。
- [ ] Gate 只来自文字 08。
- [ ] 下一步只来自文字 09。
- [ ] 图片没有新增文字版不存在的数字、时间、预算、ROI、KPI 或事实。

## C. 文字准确性
- [ ] 标题无错别字、漏字、重复字。
- [ ] 品牌必须为“JN 企业价值引擎”。
- [ ] Footer 必须为 `jn-value-engine` + `从问题到价值，从判断到行动`。
- [ ] 关键数字与文字版一致。
- [ ] 不出现乱码、伪汉字、错误偏旁、明显字体变形。
- [ ] 不出现内部状态码或工程术语。

## D. 信息完整性
- [ ] 01 决策结论存在。
- [ ] 02 真正的问题存在。
- [ ] 03 关键矛盾存在。
- [ ] 04 当前痛点存在。
- [ ] 05 方案对比存在。
- [ ] 06 三阶段路线存在。
- [ ] 07 KPI 存在。
- [ ] 08 决策闸门存在。
- [ ] 09 下一步存在。

## E. 视觉规范
- [ ] 2:3 竖版商业咨询信息图。
- [ ] 深海军蓝 + 金色 + 白/浅灰蓝为主。
- [ ] Hero 与行业相关且低饱和。
- [ ] 卡片、间距、对齐、层级清楚。
- [ ] A/B/C 三列等宽且状态色正确。
- [ ] 三阶段路线为蓝色连续流程。
- [ ] 4 个 Gate 为金色节点。
- [ ] 没有赛博朋克、霓虹、卡通、杂志拼贴或自由改版。
- [ ] 字体大小足以阅读，没有严重拥挤、遮挡、裁切或溢出。

### VISUAL_QA 判定
全部关键项通过：`VISUAL_QA = PASS`，本次调用才允许 DONE。

出现以下任一情况直接 `VISUAL_QA = FAIL`：
- 关键结论错误或文图不一致；
- 关键数字错误；
- 新增不存在的事实/预算/时间/KPI；
- 主要标题或关键模块出现错字/乱码；
- 缺失核心模块；
- 品牌/视觉系统明显偏离；
- 严重排版不可读。

若 FAIL：必须修图/重新生成 → 再次 VISUAL_QA，直到 PASS 或达到宿主可执行限制。不得把明显失败图当正式交付。

# 7｜建议评分制

除硬性 FAIL 项外，对每次交付做 100 分检查：
- 文字完整与逻辑：20
- 决策一致性与证据纪律：20
- 文图同源：20
- 图片文字准确性：15
- 视觉规范与可读性：15
- 顺序与交付完整：10

**90–100：PASS，可正式交付**
**80–89：需修正后交付**
**<80：FAIL，必须重做**

任何硬性 FAIL 项出现，即使总分 ≥90，也必须 FAIL。

# 8｜例外

只有用户明确要求才改变：
- `只要文字 / 不要图 / 先别生成图` → 文字 + TEXT_QA 后可结束。
- `只要路线图 / 不要文字` → 可跳过文字交付，但仍必须做 VISUAL_QA。
- `简版 / 30秒版`且未拒绝图片 → 简版文字 → TEXT_QA → 路线图 → VISUAL_QA。

沉默、短问题、信息不足、高风险、长文本、工具不便都不是例外。

# 9｜Failure Labels

- `TEXT_QA_INCOMPLETE`
- `TEXT_QA_LOGIC_DRIFT`
- `TEXT_QA_FABRICATION`
- `TEXT_QA_INTERNAL_LEAK`
- `DELIVERY_TEXT_MISSING`
- `DELIVERY_ROADMAP_MISSING`
- `DELIVERY_ORDER_VIOLATION`
- `DELIVERY_PREMATURE_STOP`
- `DELIVERY_SCHEMA_DRIFT`
- `VISUAL_QA_TEXT_ERROR`
- `VISUAL_QA_NUMBER_ERROR`
- `VISUAL_QA_MISSING_SECTION`
- `VISUAL_QA_STYLE_DRIFT`
- `VISUAL_QA_LAYOUT_FAILURE`
- `VISUAL_QA_FABRICATION`

Any failure means the invocation is not DONE.
