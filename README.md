# TAOSkills

用于 TAO 系列 Skills 的存放。

## Skills

| Skill | 做什么 |
| --- | --- |
| [`tao-excalidraw`](./tao-excalidraw/) | 把口播稿 / 文案 / 概念解释转成 Excalidraw 手绘风分镜图 |

## 产出

`outputs/` 存放各 skill 跑出来的成品，一个选题一个目录。

| 目录 | 内容 |
| --- | --- |
| [`outputs/ai-concepts-framework`](./outputs/ai-concepts-framework/) | 《看完这篇，AI 圈再扔什么新词你都不会懵》8 张配图分镜 |

## 安装

把某个 skill 目录软链或复制到 `~/.claude/skills/` 即可：

```bash
ln -s "$PWD/tao-excalidraw" ~/.claude/skills/tao-excalidraw
```
