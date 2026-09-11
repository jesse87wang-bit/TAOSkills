# jn-value-engine

> **企业价值引擎** · v3.4.0

`jn-value-engine` 是一个面向企业经营、资本配置与价值创造问题的 AI Skill，用于增长、扩产、新市场、融资、第二曲线、新业务、数字化/AI 投资、商业模式、并购、退出与重大资本配置。

## 当前版本的核心变化

v3.4.0 不再只依赖“请按这个格式回答”的提示，而是把执行协议写成明确状态机：

`TRIGGERED → ANALYZED → TEXT_RENDERED → TEXT_VALIDATED → IMAGE_ALLOWED → IMAGE_RENDERED → COMPLETE`

最重要的硬门禁：**01–09 完整文字没有真正输出并通过 TEXT VALIDATION 前，禁止进入图片阶段。**

## Single Source of Truth

`SKILL.md` 是当前版本唯一执行真源。

仓库中历史版本遗留的 `DELIVERY-CONTRACT.md`、旧 renderer/router/schema、实验和 benchmark 文件可以用于研究与追溯，但**不得覆盖 v3.4.0 的 `SKILL.md`**。安装到 ChatGPT / Agent 时，推荐使用干净的 v3.4.0 安装包，而不是把整个历史仓库目录当作并列指令加载。

## 标准交付

用户显式说：

```text
用 jn-value-engine 回答：<企业决策问题>
```

标准执行必须在同一次调用中依次完成：

1. 原生聊天文字：固定 01–09 九模块；
2. TEXT VALIDATION：结构、A/B/C、4 Gate、反证条件等全部校验；
3. 校验通过后才解锁图片；
4. 单独生成并显示同源 TF 企业价值路线图。

固定九模块：

01 决策结论  
02 真正的问题  
03 关键矛盾  
04 方案对比  
05 价值创造逻辑  
06 建议路线图  
07 关键验证指标  
08 决策闸门  
09 下一步行动 + 什么会让我改变判断

## 可验证性

v3.4.0 附带：

- `manifest.json`：状态机与 Fail Closed 定义；
- `tests/validate_output.py`：静态验证九模块、顺序、A/B/C、4 Gate、下一步和反证条件；
- `tests/ACCEPTANCE.md`：验收与回归测试。

第一号回归案例就是“新能源设备公司订单好但回款慢、拖欠供应商、资金链断裂：融资还是缩业务”。

## 安装

ChatGPT 官方 Skills 支持以 `SKILL.md` + 支持资源构成可复用工作流。推荐直接安装 **v3.4.0 clean bundle**；详细说明见 [`INSTALL.md`](./INSTALL.md)。

## 方法边界

本项目区分：

- SOURCE-A：课程/著作明确内容；
- SOURCE-B：从课程案例归纳的稳定思考方式；
- ENGINE-C：为稳定执行加入的工程化规则。

SOURCE-B / ENGINE-C 不应冒充任何教师、学校或机构的官方立场或独创理论。
