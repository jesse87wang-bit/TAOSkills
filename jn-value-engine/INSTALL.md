# jn-value-engine 安装与使用

> **企业价值引擎**
>
> 公开仓库：`jesse87wang-bit/TAOSkills`
> Skill 目录：`jn-value-engine/`

## 最快安装方式

把下面这段话原样发给支持 GitHub / Skills 的 Agent：

```text
请从 GitHub 安装并启用 jn-value-engine：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/jn-value-engine

要求：
1. 必须读取并保留整个 jn-value-engine 目录，不要只复制 SKILL.md 的一小段；
2. 将 SKILL.md 作为入口协议，同时读取同目录下的 DELIVERY-CONTRACT、schema、renderer、README、CHANGELOG 及视觉规范等相关文件；
3. 不得擅自改写 Skill 的交付顺序、九段文字结构、Decision Schema 或 JN 视觉规范；
4. 安装后先做一次自检，确认默认交付为：对话窗口内九段文字分析 → 同源 JN 企业价值路线图；
5. 自检通过后告诉我“jn-value-engine 已加载”，并等待我提问。
```

如果 Agent 能直接访问公开 GitHub，这通常是最省事的方式。

---

## Git 安装

```bash
git clone https://github.com/jesse87wang-bit/TAOSkills.git
cd TAOSkills
```

完整 Skill 位于：

```text
TAOSkills/jn-value-engine/
```

**不要只复制 `SKILL.md`。** 为了让不同 Agent 尽量保持一致，应该把整个 `jn-value-engine` 文件夹作为一个整体加载。

---

## 不同 Agent 怎么用

### 1. Codex

推荐方式：

1. 把 `TAOSkills` 克隆到 Codex 当前 workspace；
2. 告诉 Codex：

```text
把 ./jn-value-engine 作为项目 Skill 加载。
执行任何 jn-value-engine 请求前，先读取该目录的 SKILL.md 和相关协议文件，严格遵守交付与视觉规范。
```

如果当前 Codex 环境提供原生 Skills 目录，也可以把**整个 `jn-value-engine` 文件夹**复制到该 Skills 目录；具体路径以当前 Codex 产品版本显示的 Skill / workspace 规则为准。

### 2. Claude Code / Cowork

如果当前版本支持 Agent Skills：把整个 `jn-value-engine` 目录放入该项目可识别的 Skills 位置，再要求 Claude 读取 `SKILL.md` 作为入口。

如果当前环境没有原生 Skill 安装入口，则：

1. 将仓库克隆到项目目录；
2. 在会话开头发送：

```text
本项目使用 ./jn-value-engine 作为企业价值决策 Skill。
每次调用前读取其 SKILL.md 及相关协议文件，不得自行改写输出结构和视觉规范。
```

### 3. Cursor

Cursor 不一定把任意 GitHub 目录自动识别为“Skill”。最稳妥的方法是：

1. 将 `TAOSkills` 克隆进项目或作为相邻目录；
2. 在项目 Rules / Instructions 中写入：

```text
涉及企业经营、投资、融资、增长、商业模式、数字化、并购、资本配置等决策问题时，优先读取 ./jn-value-engine/SKILL.md，并把整个 ./jn-value-engine 目录视为完整 Skill 协议。
```

重点仍然是：**加载整个目录，而不是把它降级成一段 Prompt。**

### 4. ChatGPT

如果当前 ChatGPT 会话/工作区能够读取 GitHub：直接发送本文最上面的“最快安装方式”提示词。

如果当前环境没有“安装 GitHub Skill”的原生入口，可以把 `jn-value-engine` 目录作为项目文件/知识文件提供给 ChatGPT，并明确要求：

```text
以后我说“用 jn-value-engine 回答”时，先读取并遵守 jn-value-engine/SKILL.md 与相关协议文件。
```

注意：是否能在不同新会话中持续生效，取决于具体 ChatGPT 工作区/项目的文件与指令持久化能力。

### 5. OpenClaw 及其他 Agent

只要该 Agent 支持以下任一能力，就可以使用：

- 从 GitHub 读取目录；
- 加载 Agent Skills / `SKILL.md`；
- 将项目目录作为长期 instructions / knowledge；
- 在 workspace 中读取本地仓库。

安装原则统一为：**整个 `jn-value-engine` 目录一起加载，`SKILL.md` 为入口，相关协议文件共同生效。**

不同产品的 Skill 目录名称、命令和 UI 可能变化，因此本项目不把某个厂商的临时安装路径写死；以该 Agent 当前版本的官方 Skill / workspace 机制为准。

---

## 安装后自检

建议安装完成后直接测试：

```text
用 jn-value-engine 回答：
新能源设备公司订单和客户都不错，但下游回款太慢，导致拖欠供应商500多万元、资金链断了。应该继续融资还是缩业务？
```

合格结果应满足：

1. 先在对话窗口出现完整九段文字分析；
2. 九段内容包含决策结论、真正的问题、关键矛盾、方案对比、价值创造逻辑、建议路线图、关键指标、决策闸门、下一步与反转条件；
3. 文字之后紧接一张 JN 企业价值路线图；
4. 路线图与文字结论同源；
5. 路线图视觉遵循仓库中冻结的 canonical visual reference，不应由不同 Agent 自由改版；
6. 正式输出不应出现 HOLD、LEVEL、ENGINE-C、Router、confidence 等内部工程术语。

如果只出现普通 ChatGPT 式建议、只有图、只有文字，或者视觉风格明显漂移，说明该 Agent 没有完整加载整个 Skill。

---

## 使用方式

安装后只需要这样问：

```text
用 jn-value-engine 回答：<你的企业问题>
```

例如：

```text
用 jn-value-engine 回答：
公司现金流很好，现在有1亿元闲置资金，是回购股份、还债、扩产还是做第二曲线？
```

适用于增长、扩产、融资、资本结构、商业模式、第二曲线、数字化/AI投资、并购、退出、资本配置等企业价值问题。

---

## 分享给别人的最短版本

只需要把下面两行发给对方：

```text
安装这个公开 Skill：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/jn-value-engine

请完整加载整个 jn-value-engine 目录，不要只复制 Prompt。安装后用“用 jn-value-engine 回答：……”调用。
```
