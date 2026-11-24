# Changelog

## v1.0.0（2026-11-24）

- 第一次进仓库。交付顺序固定：先出《讲师上课材料包》Word，再出授课台等工具产出。
- 新增 `scripts/build_material_pack.py`：course.json → 材料包 docx。格式按讲师认可的上一版：按模块→小节写逐字讲稿（不按页写），时间轴一节一行，逐页课前核对收进一张表，表格列宽按内容分配，不加目录页。
- 新增 `assets/reference.docx`（材料包样式）、`templates/`（授课台与投屏窗口）、`scripts/diff_slides.py`（新旧课件逐页比对）、`examples/course.example.json`（虚构示例）、`publish_github.sh`。
