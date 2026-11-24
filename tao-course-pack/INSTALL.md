# tao-course-pack v1.0.0 安装

## 装成 skill（Claude Code、Codex、WorkBuddy 等）

把整个 `tao-course-pack/` 目录装进 Agent 的 skills 目录，不要只复制 SKILL.md（scripts/、assets/、templates/ 会用到）。

```text
请从 GitHub 安装并启用 tao-course-pack：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/tao-course-pack
请完整加载整个目录。安装后用「用 tao-course-pack 帮我备课」调用，并附上课件 PDF、讲稿和日程。
```

## Claude（claude.ai / 桌面版）

Claude 账号里的技能只保存 SKILL.md。由 Claude 在对话里发技能卡片，点“保存”即可；scripts/、assets/、templates/ 在本机文件夹或本仓库里时会被读取。

## 前提

- Python 3.9+、pandoc（生成 Word）
- LibreOffice、poppler-utils（转 PDF 检查版式、课件转图、新旧课件比对）、Pillow、numpy
