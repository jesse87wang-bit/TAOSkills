#!/bin/bash
# 运行验收测试（在临时副本中进行，不影响本目录的数据和状态）
cd "$(dirname "$0")"
export PYTHONDONTWRITEBYTECODE=1
python3 -m unittest discover -s tests -v
read -n 1 -s -r -p "测试结束，按任意键关闭"
