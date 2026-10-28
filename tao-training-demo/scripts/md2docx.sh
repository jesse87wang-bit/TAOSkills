#!/bin/bash
# 用法：bash md2docx.sh 文件1.md [文件2.md ...]   在同目录生成 .docx（中文字体、代码块底色和边框）
HERE="$(cd "$(dirname "$0")" && pwd)"
for f in "$@"; do
  pandoc "$f" -o "${f%.md}.docx" --reference-doc="$HERE/ref_cn.docx" --columns=40 --no-highlight && echo "已生成 ${f%.md}.docx"
done
