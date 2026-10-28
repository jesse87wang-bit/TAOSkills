#!/usr/bin/env bash
# 把工具包同步到 GitHub 镜像（jesse87wang-bit/TAOSkills 的 tao-spatial-video/）并推送。
# 用法: bash publish_github.sh <工具包目录> <TAOSkills 仓库目录> "<提交说明（可多行，末尾可带署名行）>"
# 只拷代码和文档；剪映音效（需自有授权）、字体、运行产物、旧版本备份一律不进仓库。
set -euo pipefail
KIT="$(cd "$1" && pwd)"; REPO="$(cd "$2" && pwd)"; MSG="${3:-tao-spatial-video: update}"
DST="$REPO/tao-spatial-video"
VER=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['version'])" "$KIT/manifest.json")

cd "$REPO"
git fetch -q origin main && git checkout -q main && git reset -q --hard origin/main

# 清空镜像目录（保留 .git 之外的一切由工具包重新生成）
find "$DST" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || mkdir -p "$DST"
( cd "$KIT" && tar cf - \
    --exclude='sfx/*.wav' --exclude='fonts/*.ttf' --exclude='fonts/*.otf' --exclude='fonts/.fontconfig' \
    --exclude='build' --exclude='_v1.*' --exclude='_patch_v1.4' --exclude='_离线模型' \
    --exclude='__pycache__' --exclude='*.pyc' --exclude='.DS_Store' --exclude='*.part' --exclude='*.bad' . ) \
  | ( cd "$DST" && tar xf - )

git add -A tao-spatial-video
LEAK=$(git diff --cached --name-only | grep -E '\.(wav|ttf|otf)$' || true)
[ -z "$LEAK" ] || { echo "✗ 有音效或字体要进提交，已停止：$LEAK"; exit 1; }
if git diff --cached --quiet; then echo "GitHub 已是最新（v$VER），无需推送"; exit 0; fi

git -c user.name="${GIT_AUTHOR_NAME:-jesse87wang-bit}" -c user.email="${GIT_AUTHOR_EMAIL:-blumsteinwehe@gmail.com}" \
  commit -q -m "tao-spatial-video v$VER" -m "$MSG"
git push -q origin main
echo "✓ 已推送 tao-spatial-video v$VER → $(git rev-parse --short HEAD)"
