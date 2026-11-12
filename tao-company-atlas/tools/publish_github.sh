#!/usr/bin/env bash
# 把工具包推到 GitHub：bash tools/publish_github.sh <工具包目录> <TAOSkills 仓库目录> "<提交说明>"
# 白名单拷贝：只推下面列出的引擎、工具、文档、虚构示例和示例截图。其他任何文件（客户配置、研究笔记、产物、发布副本）一律不进仓库。
set -euo pipefail
SRC=$(cd "$1" && pwd); REPO=$(cd "$2" && pwd); MSG="$3"; DST="$REPO/tao-company-atlas"
rm -rf "$DST"; mkdir -p "$DST"
cd "$SRC"
FILES=( *.md manifest.json package.json .gitignore
  engine/engine3d.js engine/template3d.html engine/blueprint.js engine/template-blueprint.html
  tools/build.mjs tools/lint.mjs tools/qa.py tools/qa_bp.py tools/snap.py tools/publish_github.sh
  configs/example-*.js examples/*.png )
for f in "${FILES[@]}"; do [ -e "$f" ] && install -D -m 644 "$f" "$DST/$f"; done
chmod +x "$DST/tools/publish_github.sh"
# 推送前核对：客户名黑名单（用户在本地 ~/.atlas_denylist 里一行一个；没有就只做结构检查）
DENY="${ATLAS_DENYLIST:-$HOME/.atlas_denylist}"
if [ -f "$DENY" ] && grep -rlF -f "$DENY" "$DST"; then echo "仓库内容里出现了客户名（见上），停止"; exit 1; fi
cd "$REPO"; git add -A tao-company-atlas; git commit -m "$MSG" || echo "没有变化"; git push origin HEAD:main
