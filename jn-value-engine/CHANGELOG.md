# Changelog

## v3.2

- 不改变 v3.1 的 Decision Engine，主要升级真实聊天场景的交互效率。
- 三层强协议升级为四层：`Decision Engine → Decision Schema → Interaction Router → Renderer`。
- 新增 `QUICK DECISION`：自然的一句话经营问题，首轮只给判断、真正的问题、最多3个关键判断、最多3个关键未知数与1条反转条件。
- 新增 `HIGH-STAKES QUICK`：破产/重整、现金链断裂、控制权、重大并购、海外设厂、大额不可逆投资等高风险问题，在信息不足时短答但不得武断，必须保留条件性判断、关键未知数、最大尾部风险和反转条件。
- 新增 `Interaction Router`：明确回答长度与决策复杂度是两条不同的轴，`QUICK ≠ LEVEL 1`、`FULL ≠ LEVEL 3`。
- 用户明确调用 `jn-value-engine`、要求详细分析、路线图或报告时，直接使用 FULL。
- QUICK 与 FULL 必须读取同一份 Decision Schema；同一事实下不得出现方向漂移。
- QUICK 默认不生成路线图；FULL 继续使用固定 10 模块 Dashboard + 同源路线图。
- 新增 Interaction Failure Modes：`QUICK_OVERSIMPLIFICATION`、`QUICK_OVERCONFIDENCE`、`QUICK_GENERIC`、`QUICK_FULL_DRIFT`、`QUICK_TOO_LONG`、`HIGH_STAKES_FLATTENING`。
- 开发阶段完成 QUICK vs FULL、5道高风险反向题与混合路由的单窗口受控模拟测试；结果仅用于工程筛选，不作为独立跨 Agent 实验或现实决策有效性证明。

## v3.1

- 正式升级 Decision Engine，同时保留 v3.0 的三层强协议：`Decision Engine → Decision Schema → Renderer`。
- 新增 `COMPLEXITY_GATE 2.0`：简单经营题走 FAST ECONOMICS，重大价值题才启用完整引擎。
- 新增 `MINIMUM_EVIDENCE_GATE`：缺失信息会改变结论时，必须给条件性判断，禁止伪精确。
- 强化 `QUALITATIVE_BEFORE_QUANTITATIVE`：先理解赛道、位置、模式、生命周期与目标，再解释数字。
- 新增 `QUALITY_BEFORE_QUANTITY`：关键数字按 `AMOUNT → COMPOSITION → QUALITY → SUSTAINABILITY → VALUE CONSEQUENCE` 拆解。
- 统一 `TRACE TO VALUE`：`数字 → 结构 → 经营行为 → 商业模式 → 战略选择 → 可持续性 → 企业价值后果`。
- 新增 `REDESIGN_MATERIALITY_GATE`：必须检查是否值得重设计，但禁止为了“设计思维”强行创造复杂第三方案。
- 第二曲线、多元化、跨行业与相关并购新增 `CAPABILITY_TRANSFER` 条件路由。
- 新增 `FORECAST_MODE`：区分历史外推、里程碑/实物期权、终局反推三种预测逻辑。
- 融资与交易判断强化为 `Money + Rights + Resources + Constraints`。
- 重大融资、投资、并购、生态问题增加 `OFF_BALANCE_VALUE_AND_RISK` 扫描。
- Schema 正式升级到 v3.1，加入复杂度、战略情境、数字质量、证据闸门、重设计、预测模式等字段。
- LEVEL 1 允许短版输出，不再强行生成三阶段路线图或视觉图；LEVEL 2/3 继续使用固定 10 模块 Dashboard + 路线图。
- 对外统一名称仍为 **企业价值引擎**；不代表任何教师、学校或机构。
- 开发阶段使用真实企业问题回归集与单窗口受控模拟识别失败模式；模拟结果仅用于工程迭代，不作为独立跨 Agent 实验或现实有效性证明。

## v3.0

- 从“软约束 Skill”升级为**强协议 Skill**。
- 新增三层架构：`Decision Engine → Decision Schema → Renderer`。
- 新增固定 `JN Decision Schema`，不同 Agent 必须先填同一结构再输出。
- 文字版固定为 10 个模块，模块名、顺序、表格列名和数量上限统一。
- 视觉版改为固定 Renderer；宿主支持 SVG/HTML 时必须优先确定性渲染。
- 固定画布 1200×1800、2:3，固定 Hero / 诊断区 / A-B-C / 路线 / KPI / Gate / 下一步 / Footer 布局。
- 文字和图片必须从同一份 Schema 生成，禁止图片再次独立分析。
- 生成式图片仅作为无法程序化渲染时的 fallback。
- 新增 `schema/jn-decision-schema.json` 与 `renderer/README.md`。

## v2.4

- 将参考图视觉固化为 `JN VISUAL DESIGN SYSTEM`。
- 新增颜色、栅格、Hero、卡片、A/B/C、时间轴、KPI、Gate、Footer 等跨 Agent 视觉规范。

## v2.3.1

- 明确完整输出必须先完整文字版，再紧接一张路线图。
- 路线图不替代文字答案。

## v2.3

- 品牌统一为 **企业价值引擎**。
- 新增回答后自动生成路线图。
- 移除默认 PDF 输出。

## v2.2

- 新增 `JN Decision Dashboard`。

## v2.1

- 新增 `SCOPE_ROUTER`、`EXECUTIVE_COMPRESSION`、`DIVISIBILITY_CHECK`。

## v2.0

- 升级为 `DEFINE → MECHANISM → DESIGN → DECIDE` 四层思考架构。
