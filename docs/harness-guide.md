# Claude Code Harness 主指南

## 一、Harness 是什么

**Harness = 模型之外的一切。**

模型只负责"想"。它能看到什么上下文、能调哪些工具、什么时候被允许动手、动手之后自动发生什么——这些全部由 harness 决定。同一个模型，配置好的 harness 和裸用，产出差距非常大，而这个差距完全由你控制。

分层理解：

```
         你的项目
             │
   ┌─────────┴─────────┐
   │      Harness      │   ← 你要学的就是这一层
   │                   │
   │  CLAUDE.md   记忆：永远在上下文里的项目事实
   │  Skills      技能：按需加载的流程和知识
   │  Subagents   分身：独立上下文的专职 agent
   │  Hooks       钩子：确定性执行，模型无法绕过
   │  Permissions 权限：能做什么 / 要问 / 禁止
   │  MCP         外部系统接入
   │  Plugins     把上面这些打包分发给团队
   └─────────┬─────────┘
             │
           模型
```

一句话记住每层的定位：

- **CLAUDE.md** 是"你必须知道的事"
- **Skill** 是"遇到这种情况就这么做"
- **Hook** 是"不管你怎么想，这件事一定会发生"
- **Subagent** 是"这活儿交给另一个人，别占我上下文"

---

## 二、最重要的一张表：我该用哪个机制

学 harness 最大的坑不是不会写配置，而是**用错机制**。先记住这张表，后面的细节都是补充。

| 你的需求 | 用什么 | 为什么不是别的 |
|---|---|---|
| 项目的技术栈、目录约定、命名规范 | `CLAUDE.md` | 这些每次都要知道，放 Skill 里就可能不加载 |
| 一套多步骤流程（发版、提 PR、写迁移） | **Skill** | 放 CLAUDE.md 会让上下文常年膨胀 |
| 一份很长的参考资料（错误码表、API 清单） | **Skill + 引用文件** | 主文件只写摘要，正文按需再读 |
| "每次改完代码必须格式化" | **Hook**（PostToolUse） | Skill/CLAUDE.md 只是建议，模型可能忘 |
| "绝对不许改 .env" | **Hook + 权限 deny** | 同上，这是安全边界不是建议 |
| 大范围搜索、代码调研 | **Subagent** | 搜索会产生海量中间结果，别污染主上下文 |
| 需要独立、可并行的长任务 | **Subagent** | 独立上下文窗口 + 可后台跑 |
| 接数据库、Jira、内部 API | **MCP** | 这是工具接入，不是提示词问题 |
| 把以上配置分发给整个团队 | **Plugin** | 一次安装，全员一致 |

**判断口诀**：
> 要**知道** → CLAUDE.md ／ 要**会做** → Skill ／ 要**必须做** → Hook ／ 要**分开做** → Subagent

---

## 三、七个组件

### 1. CLAUDE.md —— 记忆

放在项目根目录。每次会话自动进上下文。

只放三类内容：
- 项目是什么、用什么技术栈
- 目录结构和文件放置约定
- 反直觉的约定（"这个项目不用 npm，用 pnpm"、"测试必须跑 `make test` 不能直接 pytest"）

**不要放**：长篇流程、代码示例、很少用到的参考资料。这些进 Skill。

> 判断标准：如果这条内容 90% 的会话都用不上，它就不该在 CLAUDE.md 里。

用 `/init` 可以让 Claude 自动生成一份初版，再手工删减。**删减这一步不能省**——自动生成的版本通常太长。

### 2. Skills —— 技能（投入产出比最高，优先学这个）

一个 Skill 就是一个目录，里面一个 `SKILL.md`：

```
.claude/skills/pr-ready/
├── SKILL.md              # 必需，入口
├── references/           # 可选，按需加载的长文档
│   └── error-codes.md
└── scripts/              # 可选，Claude 可以执行的脚本
    └── check.sh
```

`SKILL.md` = YAML frontmatter + Markdown 正文：

```markdown
---
name: pr-ready
description: 提交 PR 前的自检流程。当用户说"要提 PR 了""帮我准备提交"时使用。
allowed-tools:
  - Bash(git diff *)
  - Read
---

## 当前改动

!`git status --short`

## 步骤

1. 跑 lint 和测试
2. 逐项检查 diff
3. 输出提交信息建议
```

**三个关键点**：

1. **`description` 决定它会不会被触发**。写法是「做什么 + 什么时候用」，把最典型的场景放最前面。写"代码审查助手"没用，写"提交 PR 前的自检流程。当用户说'要提 PR 了'时使用"才有用。

2. **`` !`command` `` 是动态上下文注入**。Claude Code 会先执行这条命令，把输出替换进正文，模型看到的是**真实数据**而不是靠猜。这是 Skill 比纯提示词强的核心原因。

3. **正文越短越好**。Skill 一旦加载，内容会在后续对话里一直占着上下文。长资料放 `references/` 下，正文只写一句"详见 `references/xxx.md`，需要时再读"——这叫渐进式披露。

存放位置决定作用范围：

| 位置 | 作用范围 |
|---|---|
| `~/.claude/skills/<name>/SKILL.md` | 你的所有项目 |
| `.claude/skills/<name>/SKILL.md` | 当前项目（**建议提交进 git**） |
| `<plugin>/skills/<name>/SKILL.md` | 装了该插件的地方 |

常用 frontmatter 字段：

| 字段 | 用途 |
|---|---|
| `description` | 触发判断依据（最重要） |
| `when_to_use` | 补充触发短语，追加在 description 后 |
| `allowed-tools` | 本次调用免权限询问的工具 |
| `disable-model-invocation: true` | 只允许手敲 `/name`，模型不能自动调 |
| `user-invocable: false` | 只允许模型调，不进 `/` 菜单（适合背景知识类） |
| `paths` | 只在处理匹配的文件时才自动加载 |
| `context: fork` | 在独立 subagent 上下文里跑 |
| `model` / `effort` | 该 Skill 生效期间切换模型 / 思考强度 |

正文可用的变量：`$ARGUMENTS`、`$0`/`$1`、`${CLAUDE_SKILL_DIR}`、`${CLAUDE_PROJECT_DIR}`、`${CLAUDE_SESSION_ID}`。

> `.claude/commands/xxx.md` 是老写法，仍然可用，等价于 `/xxx`。新写的一律用 Skill——它多了支持文件、frontmatter 控制和自动触发。

### 3. Permissions —— 权限

配在 `.claude/settings.json`，三档：`allow`（不问直接做）／ `ask`（每次问）／ `deny`（禁止）。

规则格式是 `Tool` 或 `Tool(specifier)`：

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git commit *)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Edit(./secrets/**)"]
  }
}
```

三条最容易踩的规则：

1. **Bash 前缀匹配用空格**：`Bash(git commit *)`。`Bash(ls:*)` 这种 `:*` 后缀等价，但**只在模式末尾**有效——`Bash(git:* push)` 里的冒号会被当普通字符，匹配不上。
2. **文件规则只认 `Read` 和 `Edit`**。写 `Write(docs/**)`、`NotebookEdit(...)`、`Glob(...)` 会被接受但**永远不生效**，还会在启动时告警。要拦写入就写 `Edit(docs/**)`。
3. **`Bash(command:rm *)` 这种参数匹配无效**。工具的主内容字段（Bash 的 `command`、Read/Edit 的 `file_path`、WebFetch 的 `url`）不能用 `param:value` 形式匹配，会被忽略并告警。直接写 `Bash(rm *)`。

路径规则用 gitignore 语法，四种锚点：`//绝对路径`、`~/家目录`、`/相对于配置文件所在项目根`、`path` 或 `./path` 相对当前目录。注意 allow 和 deny 的深度语义不同：`Edit(src/**)` 作为 allow 只匹配 `<cwd>/src`，作为 deny/ask 则匹配任意深度的 `src` 目录。

### 4. Hooks —— 钩子（唯一的"强制"机制）

Skill 和 CLAUDE.md 都是给模型看的**建议**，模型可以不听。Hook 由 harness 执行，模型绕不过去。凡是"必须每次都发生"的事，只能靠 Hook。

配置形状：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/protect-paths.sh",
            "statusMessage": "检查受保护路径"
          }
        ]
      }
    ]
  }
}
```

- `matcher` 匹配工具名，支持 `Bash`、`Bash|Edit`、`^Notebook`（正则）、`mcp__memory__.*`、`*`
- `type` 除 `command` 外还有 `http`、`mcp_tool`、`prompt`、`agent`
- `if` 可以再加一层条件：`"if": "Bash(git *)"`

最常用的几个事件（完整列表 30 个，一开始只需记这几个）：

| 事件 | 时机 | 典型用途 |
|---|---|---|
| `SessionStart` | 会话开始 | 注入当前分支、待办、环境状态 |
| `UserPromptSubmit` | 用户提交前 | 追加上下文、改写提示词 |
| `PreToolUse` | 工具执行前 | **拦截危险操作**（能 deny） |
| `PostToolUse` | 工具成功后 | 自动格式化、跑测试 |
| `Stop` | 一轮回答结束 | 收尾检查、通知 |
| `SessionEnd` | 会话结束 | 清理、归档 |

**脚本怎么写**：stdin 收 JSON，stdout 出 JSON。

输入里最常用的字段：`tool_name`、`tool_input`（如 `.tool_input.file_path`、`.tool_input.command`）、`cwd`、`session_id`、`permission_mode`。

拦截的两种写法：

```bash
# 写法一：JSON 决策（推荐，理由更清晰）
jq -n '{hookSpecificOutput:{hookEventName:"PreToolUse",
        permissionDecision:"deny",
        permissionDecisionReason:"受保护路径"}}'

# 写法二：exit 2，stderr 作为拒绝理由回给模型
echo "受保护路径" >&2; exit 2
```

退出码语义：
- `0` 成功；stdout 若是合法 JSON 就按结构化控制解析
- `2` 阻断；**stderr 才是给模型看的原因**（这点最常搞错）
- 其他 非阻断错误，动作照常进行

`PreToolUse` 的 `permissionDecision` 可取 `allow` / `deny` / `escalate`，还能用 `updatedInput` **改写**工具入参（比如把危险命令换成安全版本）。

> **写 Hook 的铁律**：hook 本身不能成为故障点。依赖的命令（`jq`、`prettier`）不存在时要静默放行，而不是让整个会话卡住。参考 `starter-kit/claude/hooks/` 里两个脚本的写法。

### 5. Subagents —— 分身

放 `.claude/agents/<name>.md`。它有**自己独立的上下文窗口**，跑完只把结论带回主线。

```markdown
---
name: test-runner
description: 跑测试套件、定位失败原因。当用户要求跑测试或 CI 变红时委派给它。
tools: Read, Grep, Glob, Bash
model: sonnet
maxTurns: 15
---

你是测试执行与失败诊断专员。被调用时：
1. 先识别项目的测试命令，不要猜
2. 执行测试，完整捕获输出
3. 判断是测试写错了还是代码写错了
```

常用字段：`tools`（不写则继承全部）、`disallowedTools`、`model`（`sonnet`/`opus`/`haiku`/`inherit`）、`permissionMode`、`maxTurns`、`skills`（预加载技能）、`isolation: worktree`（在独立 git worktree 里跑）、`background`。

**什么时候值得用**：
- 搜索/调研类任务——中间结果多，扔进 subagent 上下文里，主线只拿结论
- 可以并行的独立任务
- 需要不同模型或不同权限的任务

**什么时候不要用**：小任务。每次 spawn 都是冷启动，要重新建立上下文，比你自己直接做更慢更贵。

### 6. MCP —— 外部系统接入

需要 Claude 读写外部系统（数据库、Jira、Sentry、内部 API）时才用。配在 `.mcp.json` 或 settings 里。

学习顺序上放最后：大部分项目前期靠 Skill + Hook 已经够用，MCP 是"接得上外部数据"才有价值。

### 7. Plugins —— 打包分发

上面所有东西（skills / agents / hooks / MCP / commands）打成一个包：

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json      # 只放这一个文件
├── skills/
├── agents/
├── hooks/hooks.json
└── .mcp.json            # 其余目录都在插件根下
```

`plugin.json` 最小形态只需要 `name`：

```json
{
  "name": "tao-skills",
  "version": "0.1.0",
  "description": "TAO 系列通用技能包"
}
```

通过 marketplace 分发（`.claude-plugin/marketplace.json`，source 支持 `github` / `directory` / `npm` / `url` 等），团队成员 `claude plugin install <name> --scope project` 即可。

本地开发调试：`claude --plugin-dir /path/to/plugin`，只对当前会话生效。

---

## 四、六个最常见的坑

1. **把所有东西塞进 CLAUDE.md**。结果是上下文常年臃肿，真正重要的约定被淹没。→ 流程进 Skill，参考资料进 Skill 的 `references/`。

2. **指望 Skill 能"强制"执行**。Skill 是模型自己决定要不要用的。要保证 100% 发生，只有 Hook。

3. **`description` 写得含糊导致不触发**。「代码质量工具」不会被触发；「提交 PR 前的自检：跑测试、审 diff、生成提交信息。当用户说要提 PR 时使用」会。写完之后自己念一遍：模型只看这句话，判断得出该不该用吗？

4. **Skill 正文写太长**。加载后一直占上下文，每一行都是持续成本。正文写"做什么"，别写"为什么"和背景故事。

5. **Hook 用 exit 2 但把原因写到 stdout**。exit 2 时模型看到的是 **stderr**。写错地方模型就只知道被拒了、不知道为什么，然后原地重试。

6. **权限规则写了不生效**。三个高频错误：`Write(path)` 不生效（要用 `Edit`）、`Bash(command:rm *)` 不生效（要用 `Bash(rm *)`）、`Bash(git:* push)` 不生效（`:*` 只能放末尾）。启动时会有告警，注意看。

---

## 五、调试手段

| 手段 | 用途 |
|---|---|
| `claude --debug` | 看 hook 触发、skill 加载的完整过程 |
| `/hooks` | 查看当前生效的 hook 配置 |
| `/agents` | 查看/管理 subagent |
| `/doctor` | 排查配置问题 |
| `/context` | 看当前上下文占用，验证"Skill 是不是太长了" |
| 手动喂 JSON 给 hook 脚本 | 见下方 |

Hook 脚本可以脱离 Claude Code 单独测：

```bash
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"/repo/.env"}}' \
  | .claude/hooks/protect-paths.sh
```

写 hook 时**一定先这样测通再挂上去**——挂上去之后再调试，每次都要重开会话，非常慢。

Skill 改动会被实时监测，不用重启会话；但插件里的 `hooks/`、`agents/`、`.mcp.json` 改动需要 `/reload-plugins`。

---

## 六、官方文档定位

需要查准确定义时（不要凭记忆）：

- Skills：https://code.claude.com/docs/en/skills
- Hooks：https://code.claude.com/docs/en/hooks
- Subagents：https://code.claude.com/docs/en/sub-agents
- Permissions：https://code.claude.com/docs/en/permissions
- Settings：https://code.claude.com/docs/en/settings
- Plugins：https://code.claude.com/docs/en/plugins-reference
- 全部文档索引：https://code.claude.com/docs/llms.txt
