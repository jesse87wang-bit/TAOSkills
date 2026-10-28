# 写分镜表的辅助脚本（v1.4.4）

把这几个文件复制到分镜表旁边（或容器里的工作目录），再写 `make_sb.py` 生成 `storyboard.json`：

- `helpers.py`：`add / LIST / FLOW / LOOP / BIG / GLOW / WARN / STRIKE / JUDGE / BADGE`，逐行揭开的 wipe 按 `heights.json` 自动算
- `sbhelp.py`：`GRID`（宫格）、`SVG`（svg_panel 自绘图解，`rv=[(画布内 y, 时刻), ...]` 按时间揭开）、`MK`（SVG 箭头）、`EN`
- `kw.py`：从 `lines_chars.json` 查关键词时刻：`python3 kw.py 品牌 技术 @50 规模`（`@秒` 表示从这之后找）
- `example_make_sb.py`：「AI 时代护城河」（2026-10-04）的完整分镜脚本，含 3 个自绘图解

顺序：写 make_sb.py → `python3 make_sb.py` → `make_video.py validate` → `sprites` → 看 overflow.json 改字 → 按 PNG 高度÷3 写 heights.json（`{"元素id": 高度}`）→ 再跑 make_sb.py → `subs` → 预览。
