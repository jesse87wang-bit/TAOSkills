# jn-value-engine Failure Mode Library

用于红队、回归和跨 Agent 盲测。发现失败时记录：题号、Agent、版本、失败标签、错误表现、根因、修复规则、修复后是否回归通过。

## FM-01｜METRIC_TRAP
**定义**：被单一财务指标带跑，把指标本身当成原因或结论。

典型表现：库存高就降库存；负债高就去杠杆；亏损就止损；研发高就认定技术强。

修复：QUALITATIVE_BEFORE_QUANTITATIVE + QUALITY_BEFORE_QUANTITY + TRACE_VALUE_MECHANISM。

## FM-02｜A_B_TRAP
**定义**：用户给出 A/B 后，只在 A/B 里选择，没有寻找更优第三方案或重新设计。

修复：COUNTERFACTUAL_SET + REDESIGN_PASS。

## FM-03｜GROWTH_TRAP
**定义**：看到收入、订单、用户增长就自动乐观，忽略现金、资本占用、增长质量和可持续性。

修复：VALUE_CREATION_TRINITY + QUALITY_BEFORE_QUANTITY + CASH_SURVIVAL。

## FM-04｜FINANCING_TRAP
**定义**：把“能拿到钱/钱很便宜”误认为“应该投资”。

修复：融资能力与投资机会分离；CAPITAL_MATCHING；MILESTONE CAPITAL RULE。

## FM-05｜STORY_TRAP
**定义**：被 AI、新能源、出海、机器人等宏大叙事替代商业证据，使用伪精确预测。

修复：FORECAST_MODE_ROUTER + EVIDENCE_LADDER + FALSIFICATION。

## FM-06｜OVERTHINKING_TRAP
**定义**：对低金额、可逆、低不确定性的简单问题调用完整战略框架，导致冗长、失焦、执行性下降。

修复：COMPLEXITY_GATE。L1 只走 FAST ECONOMICS，不强制 REDESIGN_PASS。

## 记录模板

```yaml
case_id: ""
agent: ""
model: ""
skill_version: ""
failure_modes: []
observed_error: ""
root_cause: ""
proposed_fix: ""
regression_result: "PASS | FAIL | PENDING"
notes: ""
```
