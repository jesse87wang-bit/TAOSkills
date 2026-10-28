# tao-training-demo v3.0.0 安装

## 装成 skill（Claude Code、Codex、WorkBuddy 等）

把整个 `tao-training-demo/` 目录装进 Agent 的 skills 目录，不要只复制 SKILL.md（references/、scripts/、assets/ 会用到）。

```text
请从 GitHub 安装并启用 tao-training-demo：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/tao-training-demo
请完整加载整个目录。安装后用「用 tao-training-demo 做一个 XX 助手」调用。
```

## Claude（claude.ai / 桌面版）

Claude 账号里的技能只保存 SKILL.md。由 Claude 在对话里发技能卡片，点“保存”即可；SKILL.md 是自足的，references/ 等文件在本机文件夹或本仓库里时会被读取。新版本同样以卡片发出，点保存后生效。

## WorkBuddy

“技能 → 添加技能 → 上传技能”，选本目录打成的 zip（以当天界面为准）。

## 前提

- 做出来的 Demo 只依赖 Mac 自带的 Python 3.9+ 标准库
- 生成 Word 需要 pandoc；浏览器回归需要 Playwright + Chromium（只在制作时用，交付物不依赖）
