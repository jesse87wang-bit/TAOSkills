#!/usr/bin/env bash
# PostToolUse hook —— 每次 Edit/Write 之后自动格式化被改动的文件。
#
# 这类"每次都要做、做不做和模型的判断无关"的事情，就该放进 Hook，
# 而不是写进 CLAUDE.md 反复提醒模型"记得跑 prettier"。
#
# 本脚本永远 exit 0：格式化失败不应该打断 Claude 的工作流。
set -uo pipefail

input=$(cat)

if ! command -v jq >/dev/null 2>&1; then
  exit 0
fi

path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')

if [ -z "$path" ] || [ ! -f "$path" ]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-.}"

case "$path" in
  *.ts|*.tsx|*.js|*.jsx|*.mjs|*.cjs|*.json|*.css|*.scss|*.md)
    if [ -f "$project_dir/package.json" ] && command -v npx >/dev/null 2>&1; then
      npx --no-install prettier --write "$path" >/dev/null 2>&1 || true
    fi
    ;;
  *.py)
    if command -v ruff >/dev/null 2>&1; then
      ruff format "$path" >/dev/null 2>&1 || true
    elif command -v black >/dev/null 2>&1; then
      black -q "$path" >/dev/null 2>&1 || true
    fi
    ;;
  *.go)
    if command -v gofmt >/dev/null 2>&1; then
      gofmt -w "$path" >/dev/null 2>&1 || true
    fi
    ;;
  *.rs)
    if command -v rustfmt >/dev/null 2>&1; then
      rustfmt "$path" >/dev/null 2>&1 || true
    fi
    ;;
esac

exit 0
