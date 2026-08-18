# Harness 起步套件

一套可以直接复制到自己项目里的最小可用配置。每个文件都带注释，改一改就能用。

> 注意目录名是 `claude/` 而不是 `.claude/`——刻意去掉了点号，这样它在本仓库里不会被 Claude Code 当成真实配置加载。**复制的时候改名**。

## 安装

```bash
cp -r starter-kit/claude /你的项目/.claude
cd /你的项目
chmod +x .claude/hooks/*.sh
```

然后按下面的清单逐项改。**不要原样照抄就跑**——权限和 hook 都跟你的项目强相关。

## 内容

| 文件 | 作用 | 你需要改什么 |
|---|---|---|
| `settings.json` | 权限规则 + hook 注册 | 换成你项目真实的构建/测试命令；补上你的密钥路径 |
| `hooks/protect-paths.sh` | PreToolUse：拦截对受保护文件的修改 | 改 `case` 里的路径清单 |
| `hooks/format-after-edit.sh` | PostToolUse：改完自动格式化 | 换成你项目的格式化工具 |
| `skills/pr-ready/SKILL.md` | 提 PR 前的自检流程 | 换成你项目的 lint/测试命令和提交规范 |
| `skills/api-conventions/SKILL.md` | 按路径自动加载的约定类 Skill | 换成你项目的实际约定和 `paths` |
| `agents/test-runner.md` | 跑测试并诊断失败的子 agent | 一般不用改 |

## 验证装对了

```bash
# 1. hook 脚本能独立跑通（拦截）
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"/x/.env"}}' \
  | .claude/hooks/protect-paths.sh
# 期望：输出一段带 "permissionDecision": "deny" 的 JSON

# 2. hook 脚本能独立跑通（放行）
echo '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"file_path":"/x/src/a.ts"}}' \
  | .claude/hooks/protect-paths.sh
# 期望：无输出，exit 0

# 3. 起会话看有没有配置告警
claude --debug
```

进会话后再确认三件事：

- `/hooks` 能看到两个 hook 已注册
- `/` 菜单里有 `/pr-ready`
- `/agents` 里有 `test-runner`

## 依赖

hook 脚本需要 `jq`。没装也不会出错——脚本会静默放行，但拦截功能不生效。

```bash
# macOS
brew install jq
# Debian/Ubuntu
sudo apt install jq
```

## 提交进 git

`.claude/` 里除 `settings.local.json` 外都建议提交，团队自动共享同一套配置：

```gitignore
.claude/settings.local.json
```
