#!/usr/bin/env bash
# 把本技能同步到 GitHub jesse87wang-bit/TAOSkills 的 tao-course-pack/（main）
# 只推送通用部分：SKILL.md、scripts/、assets/、templates/、examples/（虚构示例）。
# 任何一期课的课件、讲稿、学员名单、素材、course.json 都不进仓库。
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="${TAOSKILLS_DIR:-$HOME/TAOSkills}"
[ -d "$REPO/.git" ] || git clone https://github.com/jesse87wang-bit/TAOSkills.git "$REPO"
cd "$REPO" && git pull --ff-only origin main
mkdir -p tao-course-pack
rsync -a --delete --exclude '.DS_Store' --exclude '__pycache__' \
  --include 'SKILL.md' --include 'README.md' --include 'INSTALL.md' --include 'CHANGELOG.md' --include 'publish_github.sh' \
  --include 'scripts/***' --include 'assets/***' --include 'templates/***' --include 'examples/***' \
  --exclude '*' "$HERE/" tao-course-pack/
git add tao-course-pack
git diff --cached --quiet && { echo "没有改动"; exit 0; }
git commit -m "tao-course-pack: ${1:-更新}"
git push origin main
