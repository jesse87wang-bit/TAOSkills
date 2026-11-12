#!/usr/bin/env bash
# 把工具包推到 GitHub：bash tools/publish_github.sh <工具包目录> <TAOSkills 仓库目录> "<提交说明>"
# 只推引擎、工具、文档和虚构示例。客户配置、研究笔记、产物、截图、原始参考件一律不进仓库。
set -euo pipefail
SRC=$(cd "$1" && pwd); REPO=$(cd "$2" && pwd); MSG="$3"; DST="$REPO/tao-ai-blueprint"
rm -rf "$DST"; mkdir -p "$DST"
# 不依赖 rsync：用 tar 按排除清单拷贝
tar -C "$SRC" -cf - \
  --exclude=node_modules --exclude='./out*' --exclude='./qa*' --exclude='./snap*' --exclude=./research \
  --exclude='./configs' --exclude='./engine/_*' --exclude='./tools/_*' --exclude=.git --exclude=__pycache__ . | tar -C "$DST" -xf -
mkdir -p "$DST/configs"; cp "$SRC"/configs/example-*.js "$DST/configs/"
# 推送前核对：除示例外不能有任何配置，不能有 _ 开头的原始参考件
if find "$DST/configs" -type f ! -name 'example-*' | grep -q .; then echo "有客户配置混进来了，停止"; exit 1; fi
if find "$DST" -name '_*' | grep -q .; then echo "有原始参考件混进来了，停止"; exit 1; fi
cd "$REPO"; git add tao-ai-blueprint; git commit -m "$MSG" || echo "没有变化"; git push origin HEAD:main
