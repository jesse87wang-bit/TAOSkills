# 分镜表格式 · storyboard@1.1

**Agent 只需要写两样东西：校对后的字幕 `lines.txt` 和这份分镜表 `storyboard.json`。**
版式坐标、动画曲线、玻璃卡样式、音效规则、渲染参数全部由工具包按固定规则翻译——两个 Agent 写出同一份分镜表，得到的就是同一条成片。

完整示例：[`golden/workbuddy/storyboard.json`](golden/workbuddy/storyboard.json)（第一条成片《WorkBuddy 还是豆包工作》，用它能逐帧复现原片）。

---

## 1. 顶层字段

| 字段 | 必填 | 说明 |
|---|---|---|
| `schema` | ✓ | 固定写 `"tao-spatial-video/storyboard@1.1"` |
| `title` | ✓ | 短标题，默认成片名 `成片_<title>_4K60.mp4` |
| `source` | ✓ | `{"path": 原片路径, "hdr": true/false, "n_src": 60fps 帧数}`，直接抄 `make_video.py probe` 的输出。路径可以是绝对路径、`~/…` 或相对分镜表 |
| `lines` | ✓ | 字幕文件（`align` 生成的 `lines.json`），相对分镜表 |
| `palette` | ✓ | `{"A": [起, 终, 深色字], "B": [...]}`：A = 左侧/第一个对象（默认青蓝），B = 右侧/第二个对象（默认紫靛）。**全片固定** |
| `elements` | ✓ | 画面元素列表，**顺序 = 同一层里的叠放顺序**（后面的盖在前面上） |
| `hold` | | 片尾定格秒数，默认 1.5 |
| `hold_frames` | | 片尾定格帧数（精确值，优先于 hold） |
| `output` | | 成片文件名（相对分镜表） |
| `rows` | | 横排组（见 §6） |
| `sfx` | | 不属于某个元素的额外音效 `[[秒, 音效, 声像, 增益], ...]`（重音、碰撞） |
| `boosts` | | 重音光晕 `[[秒, 强度], ...]`：所有玻璃卡光晕闪一下（0.7 秒衰减），强度 0.6–1.2 |
| `pulse_from` | | 从这一秒起光晕缓慢呼吸（片尾定格用，一般写原片结束的秒数） |
| `streaks` | | 扫光 `[[秒, y, 时长], ...]`：一道光从左扫到右，章节切换/大标题出现时用，时长 0.45 |
| `lines_chars` | | 关键词卡点用的逐字时间文件，默认 `lines_chars.json`（`align` 自动生成） |
| `render` | | `{"chunks": [0, 450, ..., 总帧数]}` 固定分段边界（只在要逐帧复现旧片时用） |
| `glow` | | 改位置预设的光晕色，如 `{"L": "#22D3EE", "R": "#8B5CF6"}` |

## 2. 元素字段

```json
{"id": "P_FEISHU", "type": "list_panel", "slot": "L", "at": 12.37, "out": 30.30,
 "props": {"color": "A", "glyph": "grid", "title": "飞书重度用户", "sub": "大量工作都在飞书里",
           "rows": [["doc", "文档"], ["book", "知识库"], ["meeting", "会议"], ["users", "协作"]]},
 "set": {"wipe": 4.2}, "ticks": [15.0, 15.55, 16.15, 16.69]}
```

| 字段 | 说明 |
|---|---|
| `id` | 唯一名字，也是素材 PNG 的文件名 |
| `type` + `props` | 用哪个组件、填什么内容（§4） |
| `use` | 代替 type/props：复用前面某个元素的素材，如 `{"id": "P_WB_again", "use": "P_WB", "slot": "R", ...}` |
| `slot` | 位置预设：`L` `R` `F` `TOP` `custom`（§3） |
| `at` | 出现时刻：秒，或关键词 `{"kw": "飞书", "n": 1, "offset": 0}`（§5） |
| `out` | 退场时刻（同上）；`null` = 一直留到片尾 |
| `row` | 加入某个横排组（仅 slot=F） |
| `set` | 覆盖位置预设的动画参数（§3 末） |
| `sfx` | 覆盖默认音效：`{"name":..,"pan":..,"gain":..,"dt":..}` 任选几项；`"ui"` 这种字符串 = 只换音效；`null` = 不要音效 |
| `ticks` | 列表逐行亮起的音效时刻（秒或关键词），每个一声轻点击 |

## 3. 位置预设 slot（坐标是 1080×1920 布局，合成时自动 ×2 到 4K）

| slot | 位置 | 默认参数 |
|---|---|---|
| `L` | 左侧玻璃卡，在**人物身后** | x=222 y=760 s=0.92 ry=+26°，从人物身后 (460,790) 转出，dur 0.65，青色光晕，毛玻璃，轻微漂浮，墙上投影 |
| `R` | 右侧玻璃卡，在人物身后 | x=890 ry=−26°，从 (640,790) 转出，紫色光晕，其余同 L |
| `F` | 胸前前景（压在人物前面） | x=540 y=1195 s=1.0，放大 pop=1.5 倍后回弹落下，dur 0.4 |
| `TOP` | 顶部章节标 | x=540 y=330 s=1.15，毛玻璃，紫色光晕 |
| `custom` | 自己写全部参数 | `set` 里必须有 `layer`（back/front）`x` `y` `s` |

合成器会按人头的实时位置**自动缩小、外移** L/R 卡片，保证字不被头挡住，不用手调。

`set` 里能改的参数：

| 参数 | 含义 |
|---|---|
| `x` `y` `s` `ry` | 最终位置、缩放、绕竖轴转角（度） |
| `pop` | （仅 F）出现时从几倍大小落下，1.0 = 不放大 |
| `dur` `back` | 出现动画时长；回弹强度（1.0 轻 – 1.6 重） |
| `from` / `to` | 出现起点 `[x, y, s, ry]` / 退场终点 `[x, y]` |
| `float` `ph` | 漂浮幅度（px）和相位（错开多张卡的节奏） |
| `glow` `gk` | 光晕色（`cyan` `violet` `indigo` 或 `#hex`）和强度 |
| `glass` | 毛玻璃（背景虚化透出） |
| `blur` | 景深虚化（前景小图标用 0.8–1.2） |
| `wipe` `wipe_from` `reveal0` | 从上往下逐行显现：用时、开始时刻（默认 at+0.15）、一开始就露出的比例 |
| `moves` | 中途移动 `[[开始秒, 结束秒, {"x":..,"y":..,"s":..,"ry":..,"layer":"front"}]]`（可以从身后移到胸前） |
| `odur` `shadow` | 退场时长（默认 0.35）；是否画墙面投影（back 层默认 true） |

## 4. 组件

颜色 `color` 只能写 `"A"` 或 `"B"`。图标 `glyph`：
`doc users flow target image video funnel chart link lock shield switch cpu chat book meeting coin card task mega db steps clock award grid spark check warn star arrow`

**侧边玻璃卡（放 L / R）**

| type | props | 用途 |
|---|---|---|
| `product_panel` | color, name, sub, rows(4 行), glyph, en | 产品卡：名字 + 一句定位 + 4 项能力 |
| `list_panel` | color, glyph, title, sub, rows(3–4 行), footer, footer_small, en, tsize=52 | 列表卡，配 `wipe` + `ticks` 逐行亮起。标题 ≤7 个汉字，长了调小 tsize |
| `big_card` | color, name, big, sub, pill, foot, en, bsize=98 | 大字卡：一个关键词（4 个汉字最佳，长了调小 bsize） |
| `small_card` | color, glyph, title, sub, sub_icon | 小名片 |
| `progress_card` | color, glyph, title(英文), sub, left, right, source | 发光进度条（线索 → 回款） |
| `rating_panel` | dims([[图标,维度],...]), title, tag, sub, color | 评分面板，**空星，不写假分数** |
| `laptop` | tasks(2 个 {color,name,job,pct,en}), metrics(4 个), title, tag="示意" | 电脑屏幕（示意界面，必须标「示意」） |
| `number_tile` | num, text, glyph | 编号方块（开场目录 01/02/03…） |

**顶部（TOP）**：`badge` — num, text（章节标「01 生态」，整章常驻）

**胸前（F）**

| type | props | 用途 |
|---|---|---|
| `glow_text` | text, size, pad, en, letter_spacing, nowrap | 发光大字：金句、标题（size 46–124；一行放不下加 nowrap 并调小 size） |
| `dim_text` | text, size | 偏暗的大字（后面常跟 strike 划掉） |
| `strike` | — | 红色手绘划线 |
| `chapter_title` | title, sub | 章节大标题 + 副标题 |
| `verdict` | color, pre, name, en | 结论条「A 情况 → 先看 X ✓」 |
| `judge` | color, cond, name, en | 判断行「条件 → X」 |
| `pill` | text, color | 胶囊标签「第一步」 |
| `warn_chip` | text | 橙色提醒条 |
| `chip` | glyph, text, color | 白底小标签，2–3 个用 `row` 排成一排 |
| `stamp` | text | 红色印章（3 个汉字） |
| `chat_bar` | text, sub, tag, color | 对话输入条（900 宽） |
| `vs_text` | text="VS" | 渐变 VS |
| `float_icon` | color, glyph, size | 漂浮 App 图标（点缀，配 blur） |
| `icon_tile` | color, glyph, text | 图标方块 220×220 |
| `result_tile` | glyph, text, color | 结果方块 280×230 |

`en: true` = 名字用 Poppins 粗斜体（英文产品名）。所有文字按纯文本处理。

## 5. 时间：秒 or 关键词

- 直接写秒：`"at": 12.37`
- 关键词卡点：`"at": {"kw": "飞书", "n": 1, "offset": -0.05}` —— 口播里第 n 次说到「飞书」的第一个字的时刻，再加 offset。英文不分大小写，标点空格忽略。
- `ticks`、`out`、顶层 `sfx` 的时间也都可以写关键词。
- 关键词来自 `align` 生成的 `lines_chars.json`（识别出的原话），所以要按**实际念出来的字**写。

## 6. 横排组 rows

```json
"rows": {"title": {"y": 1195, "fit": 1000},
         "chips": {"y": 1150, "s": 0.9, "gap": 10}}
```
- `fit`：组里元素按素材宽度等比缩放，总宽正好 = fit，水平居中（开场「WorkBuddy VS 豆包工作」）
- `s` + `gap`：固定缩放，间距 gap，整体居中（一排标签）

元素写 `"slot": "F", "row": "chips"`，x/y/s 由组算，`set` 里只写 pop/dur 等。

## 7. 音效

每个元素自动带一个音效，时刻 = 出现时刻 − 0.02 秒：

| 组件 | 音效 | 声像 | 增益 |
|---|---|---|---|
| 侧边玻璃卡（product/list/big/small/progress/rating/laptop） | `deng`「噔-楞」 | 左 −0.5 / 右 +0.5 | 1 |
| number_tile | `deng` | 按左右 | 0.85 |
| badge | `xp` 提示音 | 0 | 0.9 |
| glow_text / dim_text / chapter_title / verdict / judge / chat_bar | `tone` 柔和系统音 | 0 | 1 |
| pill / warn_chip | `ui` 按钮点击 | 0 | 0.9 |
| vs_text | `app` 短点击 | 0 | 0.8 |
| float_icon / icon_tile / result_tile / chip | `app` | 离中线远的 ±0.4 | 0.7 |
| strike | `ding3` 三连叮（时刻不提前） | 0 | 0.9 |
| stamp | `ding3` | 0 | 1 |
| `ticks` 每一个 | `app` | 跟卡片左右 | 0.5 |

- 同一时刻已经有卡片音效的（比如标题字和卡片同时出现），给字写 `"sfx": null`，别叠两个。
- 重音（boosts 那一下）配一个顶层 `sfx`：`[t, "ding3", 声像, 0.6]`。
- 音效文件要自备（剪映授权），见 [`sfx/README.md`](sfx/README.md)。

## 8. 校验规则（`make_video.py validate`，有错误不能渲染）

- 屏幕文字和字幕里不能有：**评论区、私信、扣 xx**（平台红线）；**老板 / 高管 / 管理者**（账号宪法，不这样称呼观众）
- 同侧玻璃卡同一时间最多 1 张（前一张 out 了下一张再 at）；章节标同时最多 1 个
- 胸前文字同时超过 3 行会提醒
- 前景元素 y 要在 220–1500 之间（顶部 0–220、底部 1500 以下是平台 UI）
- 素材渲染后文字溢出卡片 = 错误（调小 tsize/bsize/size 或缩短文字）
- 组件、图标、颜色、props 名字写错都会直接报出来
