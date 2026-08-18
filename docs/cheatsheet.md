# Harness 速查表

## 目录结构

```
项目根/
├── CLAUDE.md                        # 项目记忆，每次会话自动加载
└── .claude/
    ├── settings.json                # 权限 + hooks（提交进 git）
    ├── settings.local.json          # 个人覆盖（加进 .gitignore）
    ├── skills/<name>/SKILL.md       # 技能
    ├── agents/<name>.md             # 子 agent
    ├── hooks/*.sh                   # hook 脚本
    └── commands/<name>.md           # 老式命令（等价 Skill，新写用 Skill）
```

个人级同结构放 `~/.claude/`。优先级：企业 > 个人 > 项目。

## Skill frontmatter

```yaml
---
name: my-skill                    # 显示名；命令名来自目录名
description: 做什么 + 什么时候用    # 最重要，决定能否被自动触发
when_to_use: 补充触发短语          # 追加在 description 后
argument-hint: "[issue-number]"   # 自动补全提示
arguments: [issue, branch]        # 命名参数，正文用 $issue / $branch
allowed-tools:                    # 本轮免权限询问
  - Bash(git diff *)
  - Read
disallowed-tools: [AskUserQuestion]
disable-model-invocation: true    # 只能手敲 /name
user-invocable: false             # 只能模型调，不进 / 菜单
paths: ["src/api/**"]             # 只在处理匹配文件时自动加载
context: fork                     # 在独立 subagent 上下文里跑
agent: Explore                    # 配合 context: fork
background: false                 # 配合 context: fork，等结果
model: sonnet                     # 该 Skill 生效期间的模型
effort: high                      # low|medium|high|xhigh|max
hooks: {...}                      # 调用时注册 hook
---
```

`description` + `when_to_use` 合计超过 1536 字符会被截断，**把最关键的场景写在最前面**。

## Skill 正文里的变量

```
$ARGUMENTS          全部参数
$0 / $1             第 N 个参数（等价 $ARGUMENTS[0]）
$name               frontmatter arguments 声明的命名参数
${CLAUDE_SKILL_DIR}     SKILL.md 所在目录
${CLAUDE_PROJECT_DIR}   项目根
${CLAUDE_SESSION_ID}    会话 ID
${CLAUDE_EFFORT}        当前思考强度
${CLAUDE_PLUGIN_ROOT}   插件根（仅插件 Skill）
```

动态上下文注入（**Skill 最核心的能力**）：

```markdown
!`git diff HEAD`
```

命令先执行，输出替换进正文，模型看到的是真实数据。

## Subagent frontmatter

```yaml
---
name: test-runner                 # 必需
description: 何时委派给它            # 必需
tools: Read, Grep, Bash           # 不写 = 继承全部
disallowedTools: Write
model: sonnet                     # sonnet|opus|haiku|fable|inherit
permissionMode: default           # default|acceptEdits|auto|dontAsk|plan|bypassPermissions
maxTurns: 15
skills: [api-conventions]         # 预加载技能
isolation: worktree               # 独立 git worktree
background: true
effort: high
memory: project                   # user|project|local
color: green
---
```

## 权限规则

```json
{
  "permissions": {
    "allow": ["Bash(npm run *)", "Bash(git commit *)"],
    "ask":   ["Bash(git push *)"],
    "deny":  ["Read(./.env)", "Edit(./secrets/**)", "mcp__*"]
  }
}
```

路径锚点（gitignore 语法）：

| 写法 | 含义 |
|---|---|
| `//path` | 文件系统绝对路径 |
| `~/path` | 家目录 |
| `/path` | 相对配置文件所在的项目根 |
| `path` 或 `./path` | 相对当前目录 |

**三个必记的坑**：

- 文件规则只认 `Read` 和 `Edit`。`Write(...)` / `Glob(...)` / `NotebookEdit(...)` 会被接受但永不生效
- `Bash(command:rm *)` 无效（主内容字段不能用 `param:value`），要写 `Bash(rm *)`
- `:*` 只在模式**末尾**有效。`Bash(git:* push)` 匹配不上
- `Edit(src/**)` 作 allow 只匹配 `<cwd>/src`；作 deny/ask 匹配任意深度的 `src`

## Hook 配置

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/check.sh",
        "if": "Bash(git *)",
        "timeout": 600,
        "statusMessage": "检查中"
      }]
    }]
  }
}
```

`type` 可选：`command` | `http` | `mcp_tool` | `prompt` | `agent`

`matcher`：`*` | `Bash` | `Bash|Edit` | `^Notebook`（正则）| `mcp__memory__.*`

### 常用事件

| 事件 | 时机 |
|---|---|
| `SessionStart` / `SessionEnd` | 会话开始 / 结束 |
| `UserPromptSubmit` | 用户提交前（可改写提示词） |
| `PreToolUse` | 工具执行前（**可拦截**） |
| `PostToolUse` / `PostToolUseFailure` | 工具成功 / 失败后 |
| `Stop` / `StopFailure` | 一轮回答结束 |
| `SubagentStart` / `SubagentStop` | 子 agent 起止 |
| `PreCompact` / `PostCompact` | 上下文压缩前后 |
| `FileChanged` | 监视的文件变化 |
| `Notification` | 发通知时 |

### 输入（stdin JSON）

```json
{
  "session_id": "...",
  "cwd": "/path",
  "hook_event_name": "PreToolUse",
  "permission_mode": "default",
  "tool_name": "Bash",
  "tool_input": { "command": "npm test" },
  "tool_use_id": "toolu_..."
}
```

### 输出（stdout JSON）

```json
{
  "continue": true,
  "systemMessage": "给用户看的提示",
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow | deny | escalate",
    "permissionDecisionReason": "deny 时必填",
    "additionalContext": "补给模型的上下文",
    "updatedInput": { "command": "改写后的命令" }
  }
}
```

### 退出码

| 码 | 含义 |
|---|---|
| `0` | 成功；stdout 是合法 JSON 则按结构化控制解析 |
| `2` | **阻断；stderr 作为原因回给模型** |
| 其他 | 非阻断错误，动作照常进行 |

`UserPromptSubmit` / `SessionStart` 的 stdout 纯文本会直接给模型看。

## 插件

```
my-plugin/
├── .claude-plugin/plugin.json    # 只放这一个文件
├── skills/ agents/ commands/
├── hooks/hooks.json
├── .mcp.json
└── scripts/
```

```json
{ "name": "my-plugin", "version": "1.0.0", "description": "..." }
```

```bash
claude --plugin-dir /path/to/plugin      # 本地调试，仅当前会话
claude plugin install <name> --scope project
```

marketplace source 类型：`directory` | `github` | `npm` | `url` | `archive` | `git-subdir` | `command`

## 调试命令

```bash
claude --debug            # 看 hook 触发、skill 加载全过程
```

```
/hooks       当前生效的 hook
/agents      管理 subagent
/doctor      排查配置问题
/context     上下文占用（验证 Skill 是否过长）
/init        生成 CLAUDE.md 初版
/reload-plugins   插件的 hooks/agents/mcp 改动后重载
```

单独测 hook 脚本：

```bash
echo '{"tool_name":"Edit","tool_input":{"file_path":"/repo/.env"}}' | .claude/hooks/protect-paths.sh
```

## 发布到 claude.ai / Skills API 的限制

只允许这 6 个 frontmatter 字段，多写会**硬报错**：

```
name, description, license, compatibility, metadata, allowed-tools
```

且 `` !`command` `` 动态注入在 claude.ai 和 API 里**不生效**（那是 Claude Code 独有能力）。
