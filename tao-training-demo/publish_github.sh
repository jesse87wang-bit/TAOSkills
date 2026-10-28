#!/usr/bin/env bash
# 把 tao-training-demo 同步到 GitHub 镜像（jesse87wang-bit/TAOSkills 的 tao-training-demo/，main）并推送。
# 用法: bash publish_github.sh <本技能目录> <TAOSkills 仓库目录> ["提交说明"]
# 公开仓库：examples/ 下的客户原件摘录（只留 examples/README.md）、config.json、运行产物一律不进。
set -euo pipefail
SKILL="$(cd "$1" && pwd)"; REPO="$(cd "$2" && pwd)"; MSG="${3:-tao-training-demo: update}"
DST="$REPO/tao-training-demo"
VER=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$SKILL/manifest.json")
grep -q "^v$VER " "$SKILL/SKILL.md" || { echo "✗ SKILL.md 开头的版本号和 manifest.json（$VER）不一致，已停止"; exit 1; }
grep -q "## v$VER " "$SKILL/CHANGELOG.md" || { echo "✗ CHANGELOG.md 里没有 v$VER，已停止"; exit 1; }

cd "$REPO"
git fetch -q origin main && git checkout -q main && git reset -q --hard origin/main

mkdir -p "$DST"
find "$DST" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
( cd "$SKILL" && tar cf - \
    --exclude='./examples/*/*' --exclude='./examples/*_*' \
    --exclude='config.json' --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' \
    --exclude='*.zip' --exclude='data/runs' --exclude='data/state.json' . ) \
  | ( cd "$DST" && tar xf - )
# examples/ 只保留说明
find "$DST/examples" -mindepth 1 ! -name README.md -exec rm -rf {} + 2>/dev/null || true

git add -A tao-training-demo
LEAK=$(git diff --cached --name-only | grep -E '^tao-training-demo/examples/.+/|config\.json$|\.zip$' || true)
[ -z "$LEAK" ] || { echo "✗ 有客户摘录或密钥文件要进提交，已停止：$LEAK"; exit 1; }
if git diff --cached --quiet; then echo "GitHub 已是最新（v$VER），无需推送"; exit 0; fi

git -c user.name="${GIT_AUTHOR_NAME:-jesse87wang-bit}" -c user.email="${GIT_AUTHOR_EMAIL:-blumsteinwehe@gmail.com}" \
  commit -q -m "tao-training-demo v$VER" -m "$MSG"
git push -q origin main
echo "✓ 已推送 tao-training-demo v$VER → $(git rev-parse --short HEAD)"
