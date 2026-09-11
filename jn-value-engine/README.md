# jn-value-engine

> **企业价值引擎**

`jn-value-engine` 是一个面向企业经营、资本配置与价值创造问题的 AI Skill。用于增长、扩产、新市场、融资、第二曲线、新业务、数字化/AI投资、商业模式、并购、退出、传承与资本配置等企业价值问题。

## 安装

公开安装说明见：[`INSTALL.md`](./INSTALL.md)

最快方式：把下面这段发给支持 GitHub / Skills 的 Agent：

```text
请从 GitHub 安装并启用 jn-value-engine：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/jn-value-engine

请完整加载整个 jn-value-engine 目录，不要只复制 SKILL.md 的部分内容。安装后用“用 jn-value-engine 回答：……”调用。
```

## 当前交付协议

默认一次调用必须在当前对话窗口完成：

**PART 1｜九段完整文字分析**

→

**PART 2｜1 张同源 JN 企业价值路线图**

不是先出图，不是只给图，也不是把路线图降级成下载链接。

## 固定九段文字结构

01 决策结论  
02 真正的问题  
03 关键矛盾  
04 方案对比  
05 价值创造逻辑  
06 建议路线图  
07 关键验证指标  
08 决策闸门  
09 下一步行动 + 什么会让我改变判断

正式输出隐藏内部状态码、工程术语和内部置信度字段。

## 决策协议

Skill 通过统一的 Decision Engine / Decision Schema / Renderer 协议，让不同 Agent 即使内部推理不同，也尽量保持一致的：

1. 问题重构方式；
2. 价值创造逻辑；
3. 方案比较标准；
4. 分阶段行动路线；
5. 关键验证指标与 Gate；
6. 最终文字结构；
7. 最终路线图信息架构与视觉规范。

## 视觉规范

当前唯一 canonical visual reference 为仓库中已冻结的 JN 企业价值引擎视觉系统。

核心特征：

- 竖版约 2:3；
- 顶部行业实景 Hero + 深海军蓝蒙版；
- `JN 企业价值引擎` 品牌；
- 白色大标题 + 金色关键词；
- 右侧手写金句 + 金色手绘线；
- 高密度咨询式卡片；
- A/B/C 三张等宽方案卡；
- 连续蓝色三阶段路线箭头；
- KPI 横向小卡；
- 4 个金色决策 Gate；
- 底部深海军蓝 Footer。

原则：**内容可以变，设计系统不变。**

## 文件

- [`SKILL.md`](./SKILL.md)：核心执行协议
- [`INSTALL.md`](./INSTALL.md)：公开安装与分享指南
- [`schema/jn-decision-schema.json`](./schema/jn-decision-schema.json)：Decision Schema
- [`renderer/README.md`](./renderer/README.md)：视觉 Renderer 规范
- [`CHANGELOG.md`](./CHANGELOG.md)：版本历史

## 使用

安装后直接问：

```text
用 jn-value-engine 回答：<你的企业决策问题>
```

例如：

```text
用 jn-value-engine 回答：
新能源设备公司订单和客户都不错，但下游回款太慢，导致拖欠供应商500多万元、资金链断了。应该继续融资还是缩业务？
```

## 方法边界

本项目区分：

- SOURCE-A：课程/著作明确内容；
- SOURCE-B：从课程案例归纳的稳定思考方式；
- ENGINE-C：为让 AI 稳定执行而加入的工程化规则。

SOURCE-B / ENGINE-C 不应冒充任何教师、学校或机构的官方立场或独创理论。
