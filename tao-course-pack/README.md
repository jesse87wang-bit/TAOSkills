# tao-course-pack

线下 AI 培训课的备课工具包：把「课件 + 讲稿 + 大纲」变成讲师拿去就能上课的一整套资料。

两步，顺序固定：

1. **《讲师上课材料包》Word**：`scripts/build_material_pack.py course.json 输出.docx`。按模块→小节写逐字讲稿（口播引用块＋【学员】【讲师动作】【素材】【翻车预案】【冷场】），前面是差异、受众、时间轴，后面是提示词、素材清单、学员表单、项目包、转训包、课前准备。
2. **授课台与其他产出**：`templates/00_授课台.html` + `投屏窗口.html`（读同目录 `lesson-data.js` 和 `01_课件/pNN.jpg`），以及提示词、离线卡、打印件、就绪检查表。

其他：`scripts/diff_slides.py 旧.pdf 新.pdf` 逐页比对两版课件。完整方法见 `SKILL.md`。

依赖：Python 3、pandoc、LibreOffice（检查渲染）、poppler-utils、Pillow、numpy。

`examples/course.example.json` 是虚构示例；真实课程的课件、讲稿、学员信息、素材不放进本仓库。
