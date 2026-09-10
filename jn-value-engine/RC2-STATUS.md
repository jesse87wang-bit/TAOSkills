# jn-value-engine v3.1-RC2 Status

## Current decision

**SIMULATED GATE: PASS**

RC2 已完成单窗口受控模拟回归，并达到预先冻结的 Release Gate。由于当前测试不是独立跨 Agent / 跨 Judge 实验，状态仍记为 **Release Candidate ready**，而非 external-validation complete。

## RC2 相对 RC1 的唯一三项工程修复

1. COMPLEXITY_GATE 2.0：不仅分级，还控制哪些模块必须跳过。
2. REDESIGN_MATERIALITY_GATE：检查 redesign，但只有实质改变经济机制时才输出。
3. MINIMUM_EVIDENCE_GATE：缺少会改变结论的事实时输出条件性判断，不做伪精确决策。

## 冻结原则

RC2 结果已经记录。后续如发现新失败模式，不回写本轮测试规则或分数；形成后续 patch / v3.2 候选。

## 正式 v3.1 建议

从工程角度，RC2 已达到合并为 v3.1 的预设门槛。正式发布时应：

- 保留企业价值引擎名称；
- 不对外称任何教师数字分身或官方工具；
- 保留 SOURCE-A / SOURCE-B / ENGINE-C 边界；
- 保留 v3.0 的 Text Renderer 与 Visual Renderer 稳定外壳；
- 将 RC2 Decision Engine 与 v3.1 Schema 作为正式内核；
- Benchmark 结果明确标记为 simulated controlled benchmark。

## 公开传播边界

可以说：经过真实企业问题库、红队、回归和受控模拟测试持续迭代。

不可以说：独立多 Agent 实测提升 8.6%、全面超过资深 CFO、代表教师本人判断。
