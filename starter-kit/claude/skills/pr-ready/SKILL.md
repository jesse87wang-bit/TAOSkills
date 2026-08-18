---
name: pr-ready
description: 提交 PR 前的自检流程：跑测试和 lint、审查自己的 diff、生成符合仓库规范的提交信息。当用户说"要提 PR 了""帮我准备提交""检查一下再推"时使用。
allowed-tools:
  - Bash(git status *)
  - Bash(git diff *)
  - Bash(git log *)
  - Read
  - Grep
---

## 当前改动

!`git status --short`

## 与基线的 diff 概览

!`git diff HEAD --stat`

## 执行步骤

1. 跑项目自己的快检：先读 `package.json` / `Makefile` / `pyproject.toml` 找出 lint、typecheck、单测命令，再按顺序执行。任何一步失败就停下来修，不要跳过。
2. 用对抗性的眼光重读上面的 diff，逐项检查：
   - 调试残留（`console.log`、`print`、`TODO`、被注释掉的代码）
   - 硬编码的密钥、URL、绝对路径
   - 新增分支有没有对应测试
   - 错误路径是否有处理
3. 输出结论，固定格式：
   - **改了什么**：2-3 条要点
   - **风险**：具体到 `file:line`；没有就写"无"
   - **建议的提交信息**：一行标题（≤72 字符）+ 空行 + 要点说明

## 约束

- 不要自动执行 `git commit` 或 `git push`，只输出建议，由人来按。
- 如实汇报：测试失败就贴失败输出，不要粉饰。
