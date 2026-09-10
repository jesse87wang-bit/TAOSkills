# jn-value-engine v3.1-rc1｜状态与发布清单

> 目的：把课堂隐性方法蒸馏为可执行、可测试、可回滚的企业价值判断协议。RC1 不代表正式发布，main 仍为 v3.0。

## 1. 当前状态

- 分支：`jn-value-engine-v3.1-rc1`
- 正式版：`main` / v3.0（未修改）
- RC 核心：已完成
- 来源分层：已完成
- Regression 20：已建立
- Failure Library：已建立
- Blind Test Protocol：已建立
- v3.1 RC Schema：已建立
- 跨 Agent 独立盲测：待执行
- 正式 Release：未批准

## 2. RC1 核心变化

### 全局
1. `COMPLEXITY_GATE`：LEVEL 1 / 2 / 3，防止过度分析。
2. `QUALITATIVE_BEFORE_QUANTITATIVE`：先行业/位置/模式/阶段，再解释数字。
3. `QUALITY_BEFORE_QUANTITY`：数量 → 构成 → 质量 → 可持续性 → 价值。
4. `TRACE_TO_VALUE`：数字 → 经营行为 → 商业模式 → 战略选择 → 价值后果。
5. `DESIGN_OVER_OPTIMIZATION`：LEVEL 2/3 必须做 Redesign Pass。

### 条件 Router
- 第二曲线/多元化：`CAPABILITY_TRANSFER_GATE`
- 高不确定项目：`FORECAST_MODE_ROUTER`（FORWARD / MILESTONE / ENDGAME）
- 融资/并购/重大交易：`CAPITAL_RIGHTS_ROUTER`
- 复杂生态/重大交易：`OFF_BALANCE_VALUE_AND_RISK`

### Redesign 工具
固定追问：谁拥有？谁使用？谁出钱？谁承担风险？谁拿收益？

## 3. 保持不变

- 对外名称：企业价值引擎
- Text Renderer 的 01—10 模块顺序
- Visual Renderer 的品牌与版式协议
- 文字与视觉必须来自同一 Schema
- 不编造数字、KPI、时间和事实
- 专业会计/税务/法律/交易执行仍属于让位区

## 4. 发布门槛

必须同时满足：

- v3.1 相对 v3.0 平均总分提升 >= 8%
- “数字质量/结构穿透”与“重新设计能力”平均提升 >= 20%
- 原10项能力无任何一项平均退化 > 5%
- `OVERTHINKING_TRAP` 不高于 v3.0
- 平均回答长度增幅 <= 20%
- 至少两个独立 Judge 对系统排序方向一致

未满足任一条件：不得合并 main。

## 5. 证据等级

- SOURCE-A：课堂/著作明确概念、模型、原则。
- SOURCE-B：多个课堂案例中反复出现、可迁移的稳定思考模式。
- ENGINE-C：为稳定 Agent 执行而设计的工程规则；不得描述成老师原话。

## 6. 当前测试证据

开发阶段已完成三轮内部控制测试，用于筛选和删除规则；这些结果不是独立跨 Agent Benchmark，不用于公开宣称性能提升。

下一步唯一关键任务：按 `benchmark/blind-test-protocol.md` 执行冻结版本的跨 Agent 盲测。

## 7. Release 流程

`RC1 freeze` → `blind generation` → `anonymize` → `Judge A/B` → `score aggregation` → `failure review` → `regression check` → `release decision`

若通过：把 RC1 核心合并到正式 `SKILL.md` 和正式 schema，版本升为 v3.1。

若不通过：根据 failure mode 只修复可复现问题，形成 RC2，不得边测边改 RC1。
