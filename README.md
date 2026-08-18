# TAOSkills

用于 TAO 系列 Skills 的存放。

## Claude Code Harness 学习资料

**Harness = 模型之外的一切**——上下文里有什么、能调哪些工具、什么时候允许动手、动手之后自动发生什么。同一个模型，配好 harness 和裸用差距很大，而这个差距完全由你控制。

### 从哪开始

| 文档 | 内容 | 什么时候读 |
|---|---|---|
| [docs/learning-path.md](docs/learning-path.md) | Day 1 / Day 2 / Week 1 / Week 2 的具体动作和练习清单 | **先读这个**，边做边学 |
| [docs/harness-guide.md](docs/harness-guide.md) | 七个组件详解、决策表、六个常见坑 | 卡住了或想搞清原理时 |
| [docs/cheatsheet.md](docs/cheatsheet.md) | 全部 frontmatter 字段、hook 事件、权限语法 | 写配置时当字典查 |
| [starter-kit/](starter-kit/) | 可直接复制到自己项目的最小可用配置 | Day 1 就可以拷走 |

### 一分钟版本

要**知道** → `CLAUDE.md`
要**会做** → Skill
要**必须做** → Hook
要**分开做** → Subagent

最快的上手路径：在你的项目里跑 `/init` 生成 `CLAUDE.md` 并删到 30 行 → 挑一件本周重复了三次的事写成 Skill → 拷一个 hook 进去，体会"建议"和"强制"的区别。两个下午就能落地。

详细步骤见 [docs/learning-path.md](docs/learning-path.md)。
