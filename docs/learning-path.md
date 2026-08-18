# Harness 学习路线：从零到用在自己项目里

原则：**不要先通读文档**。Harness 的每个组件都能独立产生价值，边做边学，每一步都以"在自己项目里跑通一个东西"为终点。

---

## Day 1（约 2 小时）：让 Claude 认识你的项目

**目标**：跑通 CLAUDE.md + 第一个 Skill。这两样能覆盖日常 70% 的收益。

### 步骤

1. **生成并精简 CLAUDE.md**（30 分钟）

   在你的项目根目录跑 `claude`，输入 `/init`。它会生成一份项目说明。
   **然后动手删**——删到只剩三类内容：项目是什么、目录约定、反直觉的规矩。
   删完通常只有 30-50 行。

2. **写第一个 Skill**（60 分钟）

   选一件你**这周至少手工重复了三次**的事。不要挑复杂的，挑烦的。
   典型候选：写提交信息、加一个新接口、跑发布前检查、生成某种样板代码。

   ```bash
   mkdir -p .claude/skills/my-first-skill
   ```

   照着 `starter-kit/claude/skills/pr-ready/SKILL.md` 改。重点打磨 `description`。

3. **验证触发**（30 分钟）

   两种方式各试一次：
   - 手动：`/my-first-skill`
   - 自动：用自然语言描述那个场景，看它会不会自己加载

   **自动触发不上，就是 `description` 写得不够具体**。回去改，再试。这个来回是必要的，别跳过。

**Day 1 验收**：你能用一句自然语言让 Claude 自动走完一套原来要手工交代的流程。

---

## Day 2（约 2 小时）：加上确定性

**目标**：理解"建议 vs 强制"的区别，配好权限和第一个 Hook。

### 步骤

1. **配权限**（30 分钟）

   把 `starter-kit/claude/settings.json` 里的 `permissions` 段拷进你项目的 `.claude/settings.json`，按你的项目改：
   - `allow`：你项目里安全的高频命令（测试、构建、lint）
   - `deny`：密钥文件、生成目录
   - `ask`：`git push`、部署这类不可逆操作

   改完重开会话，注意看有没有启动告警——写错的规则会在这里提示。

2. **挂第一个 Hook**（60 分钟）

   拷 `starter-kit/claude/hooks/format-after-edit.sh`，改成你项目的格式化命令。

   **先脱离 Claude Code 单独测**：

   ```bash
   echo '{"tool_input":{"file_path":"src/foo.ts"}}' | .claude/hooks/format-after-edit.sh
   echo "exit=$?"
   ```

   通了再写进 `settings.json` 的 `hooks.PostToolUse`，然后 `claude --debug` 看它有没有被触发。

3. **做一次对照实验**（30 分钟）

   在 CLAUDE.md 里写一句"每次改完代码都要格式化"，然后**把 hook 关掉**，让 Claude 改几个文件——观察它是否真的每次都格式化。再把 hook 打开重来一次。

   这个实验会让你彻底记住：**建议会被忘，Hook 不会**。

**Day 2 验收**：你能说清楚什么该放 CLAUDE.md、什么该放 Skill、什么必须做成 Hook。

---

## Week 1 剩下的时间：把日常流程搬进来

每天挑一件重复劳动，做成 Skill。目标是攒到 3-5 个真正会用的 Skill。

同时补两件事：

- **一个 Subagent**：照着 `starter-kit/claude/agents/test-runner.md` 改一个。用它跑一次大范围代码调研，对比一下主线上下文的占用（`/context`），体会"独立上下文"的价值。
- **一个 SessionStart Hook**：会话一开始就把当前分支、未提交改动、最近的失败测试注入进去。这类 hook 的收益被严重低估。

**判断 Skill 写得好不好，只看一个指标**：一周之后，你还在用它吗？没在用，要么是 `description` 不触发，要么是这件事本来就不值得自动化。两种情况都该删掉。

---

## Week 2：团队化

只有当你自己已经稳定用起来了，才做这一步。

1. **把 `.claude/` 提交进 git**。skills、agents、hooks、settings.json 都进版本控制，团队自动共享。
   注意：`settings.local.json` 是个人覆盖，应该进 `.gitignore`。

2. **跨项目复用的做成 Plugin**。多个仓库都要用的技能，别复制粘贴——打成插件，建一个 marketplace 仓库分发。

3. **建立评审习惯**。Skill 和 Hook 是会影响所有人工作方式的配置，改动应该走 PR 评审，和代码一样。

---

## 练习清单

按难度排序，做完这七个就算真正掌握了：

| # | 练习 | 考察点 |
|---|---|---|
| 1 | 写一个用 `` !`git diff` `` 注入真实 diff 的 Skill | 动态上下文注入 |
| 2 | 写一个 `description` 能被自然语言准确触发的 Skill | 触发词设计 |
| 3 | 用 `paths` 让 Skill 只在改某个目录时才加载 | 条件加载 |
| 4 | 写一个 PreToolUse Hook 拦截对某文件的修改 | 强制约束 + JSON 决策 |
| 5 | 写一个 SessionStart Hook 注入项目当前状态 | 上下文自动化 |
| 6 | 写一个 Subagent 并观察 `/context` 的差异 | 上下文隔离 |
| 7 | 把 2-3 个 Skill 打成 Plugin 并本地安装 | 打包分发 |

---

## 什么时候该停下来查文档

以下情况**不要凭记忆写**，一定去查（链接见主指南末尾）：

- 权限规则的精确语义（allow / deny 的匹配深度不一样，很反直觉）
- Hook 事件名和输入字段名（30 个事件，字段各不相同）
- Skill frontmatter 字段（有二十来个，且有版本差异）
- 要发布到 claude.ai / Skills API 时的字段限制（只允许 6 个字段，多写会**硬报错**而不是忽略）
