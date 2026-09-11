# Changelog

## v3.7.0

- 移除会接管宿主交互方式的“用户可见输出纯净锁”；明确系统、开发者、用户、工具、安全、进度、引用和最终答复规则始终优先。
- 将图片硬门禁和 Fail Closed 状态机改为建议工作流：图片默认基于已形成的文字生成，但工具时机由宿主规则、用户要求、可用性与代理判断共同决定。
- 图片失败或不可用时保留完整文字答复并说明限制，不再因可选图片失败而判整次回答无效。
- 当前版本与品牌统一为 `v3.7.0`、`TF 企业价值引擎`，Skill 名称及图片署名继续使用 `jn-value-engine`。

## v3.6.0

- 强化用户可见输出纯净锁，明确禁止展示“我会严格按协议执行”等调用说明、执行计划和工具进度。
- 路线图视觉品牌由 `JN` 切换为 `TF`，图片顶部与 Footer 左侧统一为 `TF 企业价值引擎`；Skill 名称及 Footer 右侧署名继续保留 `jn-value-engine`。
- 增加图片品牌目视复核：视觉品牌发现 `JN`，或 Skill 署名不是 `jn-value-engine`，即判定图片无效并重新生成。

## v3.3

- 不改变 v3.1 的 Decision Engine，不改变 v3.2 的 Interaction Router，新增专业边界路由。
- 五层强协议：`Decision Engine → Decision Schema → Interaction Router → Specialist Boundary Router → Renderer`。
- 新增 `SPECIALIST_BOUNDARY_ROUTE`：法律、税务、审计、Treasury、监管、股权激励实施等问题，先保留企业价值层判断，再把会改变最终执行结论的专业事实交专业方验证。
- 专业边界触发后固定回答四层：企业价值层判断 / JN 可判断到哪里 / 1—3个关键专业事实 / 验证方与验证前动作。
- 禁止只有“建议咨询专业人士”的空泛免责，也禁止因为出现“董事会、汇率、海外、并购、破产”等关键词就整体让位。
- 新增 Specialist Boundary Failure Modes：`SPECIALIST_OVERREACH`、`SPECIALIST_DEFLECTION`、`GENERIC_EXPERT_DISCLAIMER`、`BOUNDARY_VALUE_LOSS`。
- 开发阶段完成 10 道边界回归，并对 100 题真实问题库进行了专业边界反向筛查：33 题进入专业邻接候选池，未发现系统性过度触发。
- 测试性质仍为单窗口受控模拟，仅用于工程筛选，不作为独立跨 Agent 实验或现实决策有效性证明。

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
# v3.5.0

- 新增用户可见输出纯净锁：直接输出正式分析，过程读取、校验、解锁和生成状态全部静默。
- 固定交付顺序为“01–09 正式文字 → JN 路线图”，图片后立即结束，不追加尾声。
- 路线图更换并锁定为“纺织企业智能化改造”白底高密度咨询报告母版。
- 图片品牌统一为 `JN 企业价值引擎`，并新增母版模块与连续编号约束。
