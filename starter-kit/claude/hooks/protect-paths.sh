#!/usr/bin/env bash
# PreToolUse hook —— 在 Edit/Write 真正落盘之前拦截受保护路径。
#
# 为什么用 Hook 而不是只写在 CLAUDE.md 里：
#   CLAUDE.md 是"建议"，模型可以忽略；Hook 由 harness 执行，是"强制"。
#
# 输入：stdin 收到一段 JSON（tool_name / tool_input / cwd / session_id ...）
# 输出：stdout 打印 JSON 决策；permissionDecision=deny 即拦截。
#      也可以用 exit 2 + stderr 拦截，此时 stderr 内容会作为拒绝理由回给模型。
set -uo pipefail

input=$(cat)

# 没有 jq 就直接放行，避免 hook 本身成为故障点
if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')

if [ -z "$path" ]; then
  exit 0
fi

# 在这里维护你项目的"禁止修改"清单
case "$path" in
  */.env|*/.env.*|*/secrets/*|*/node_modules/*|*/dist/*|*/build/*|*.lock|*/go.sum)
    jq -n --arg p "$path" '{
      hookSpecificOutput: {
        hookEventName: "PreToolUse",
        permissionDecision: "deny",
        permissionDecisionReason: ("受保护路径，禁止直接修改：" + $p + "。如需变更请改用生成它的工具或先征求人工确认。")
      }
    }'
    exit 0
    ;;
esac

exit 0
