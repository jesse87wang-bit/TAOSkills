# jn-value-engine

> **企业价值引擎**

`jn-value-engine` 是一个面向企业经营、资本配置与价值创造问题的 AI Skill。它基于《贾宁财务讲义》与《初创企业价值创造与资本战略》课程框架蒸馏，并经过真实企业问题 Benchmark 与红队测试持续迭代。

## v3.0：从 Skill 升级为强协议

v3.0 采用三层结构：

**JN Decision Engine → JN Decision Schema → JN Renderer**

这意味着不同 Agent 可以有不同内部推理，但最终必须：

1. 先填同一份标准 Decision Schema；
2. 再从 Schema 渲染固定格式的文字 Dashboard；
3. 再从同一份 Schema 渲染固定视觉路线图。

因此不会再让每个 Agent 自己决定“怎么排版、怎么画图、哪些模块出现”。

## 固定输出顺序

**PART 1｜完整文字版 JN Decision Dashboard**

→

**PART 2｜1 张 JN 企业价值路线图**

路线图不重新分析问题，只做文字结论的视觉压缩。

## 固定文字结构

01 决策结论  
02 真正的问题  
03 关键矛盾  
04 方案对比  
05 价值创造逻辑  
06 建议路线图  
07 关键验证指标  
08 决策闸门  
09 下一步行动  
10 什么会让我改变判断

模块名、顺序、表格列名、数量上限在 v3.0 中固定。

## 固定视觉结构

优先使用 **SVG / HTML 确定性渲染**，而不是每次让图片模型重新设计。

固定画布：1200 × 1800，2:3。

固定结构：

Hero → 决策结论 → 三列诊断区 → A/B/C方案 → 三阶段路线 → KPI → Gate → 下一步 → Footer。

固定品牌色：深海军蓝、白、浅灰、金色、推荐绿、风险红。

生成式图片模型只作为宿主无法程序化渲染时的 fallback。

## 文件

- [`SKILL.md`](./SKILL.md)：v3.0 核心协议
- [`schema/jn-decision-schema.json`](./schema/jn-decision-schema.json)：固定 Decision Schema
- [`renderer/README.md`](./renderer/README.md)：确定性视觉 Renderer 规范
- [`CHANGELOG.md`](./CHANGELOG.md)：版本历史

## 适用问题

增长、扩产、新市场、融资、第二曲线、新业务、数字化/AI投资、商业模式、并购、退出、创始人退出与传承、资本配置等企业价值问题。

## 方法边界

本项目严格区分：

- SOURCE-A：课程/著作明确内容
- SOURCE-B：从课程案例归纳的稳定思考方式
- ENGINE-C：为让 AI 稳定执行而加入的工程化规则

ENGINE-C 不应表述为贾宁老师本人提出或独创的方法。
