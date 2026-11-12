# 安装 tao-company-atlas

1. 把整个 `tao-company-atlas/` 目录交给 Agent（不要只拷 SKILL.md）。
2. 环境：Node 18+、Python 3 + Playwright（Chromium）。在目录里执行 `npm install`。
3. 跑一遍示例确认环境正常：
   ```bash
   node tools/lint.mjs configs/example-qinghe.js
   node tools/build.mjs configs/example-qinghe.js out
   python3 tools/qa.py out/青禾AI运转全景.html qa
   ```
4. 调用：「用 tao-company-atlas 给 <公司名> 做 AI 全貌」，可附上手头资料。
