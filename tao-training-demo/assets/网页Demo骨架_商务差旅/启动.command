#!/bin/bash
# 商务差旅助手（网页演示版）——双击启动
cd "$(dirname "$0")"
if ! command -v python3 >/dev/null 2>&1; then
  echo "没有找到 python3。请在终端运行：xcode-select --install ，安装完成后再双击本文件。"
  read -n 1 -s -r -p "按任意键关闭"
  exit 1
fi
export PYTHONDONTWRITEBYTECODE=1
python3 app/server.py
