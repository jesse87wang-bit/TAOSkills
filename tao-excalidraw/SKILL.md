---
name: tao-excalidraw
description: 把口播稿、文案、教程、概念解释转成 Excalidraw 手绘风分镜图（.excalidraw + SVG/PNG 预览）。当用户要给一段稿子配图、做分镜、画概念图、出白板风格示意图，或直接点名 tao-excalidraw 时使用。也用于修改已生成的分镜。
---

# tao-excalidraw

把一段**讲给人听的稿子**，拆成一组**能一眼看懂的白板图**。

产出是 `.excalidraw` 文件——可以直接拖进 excalidraw.com 打开、继续手改、
导出 PNG/SVG，而不是一张改不动的图片。

## 什么时候用

- 口播稿 / 公众号文 / 课程脚本要配图
- 一个抽象概念要画成示意图（类比、流程、对比、前后变化）
- 已有分镜要调版式、改文案、换配色

## 工作流

### 1. 拆稿：先定分镜，再动手画

按稿子的**自然段落**切分镜，一段一图。切完先用一句话写出每张图的
**单一主张**——一张图只讲一件事，讲不完就拆成两张。

拆完先把分镜清单（编号 + 标题 + 主张 + 打算用什么图式）念给用户听，
确认后再生成。稿子超过 6 段时这一步不能省。

### 2. 选图式

主张的形状决定图式，不要每张都画成流程图：

| 稿子在说什么 | 用什么图式 |
| --- | --- |
| A 就是 B（类比、下定义） | 中心一个主体 + 左右两块属性卡 |
| 好指令 vs 烂指令（对比） | 上下两条并排管线，同一个中间件 |
| 多了少了刚好（程度） | 同一条量表画三行，填充比例不同 |
| 以前这样、现在那样（前后） | 一条横线分上下两带，或竖线分左右两栏 |
| 一步接一步（流程） | 横向链条 + 箭头，外面套虚线框表示"一个整体" |
| N 个东西的清单（总结） | 色块 + 破折号 + 说明，纵向对齐 |
| 一对多 vs 一对一（收敛） | 左边发散多根异色线，右边一根线进转接盒 |

### 3. 生成

用 `scripts/excalidraw_kit.py`，**不要手写 JSON**——漏字段会让
excalidraw.com 打不开文件。

```python
import sys; sys.path.insert(0, ".../tao-excalidraw/scripts")
from excalidraw_kit import Scene, PALETTE

s = Scene()
s.title(800, 40, "① LLM 大模型 = 刚入职的实习生")     # 居中大标题（x 是中心）
s.ellipse(80, 280, 340, 230, "全世界\n绝大部分的书", **PALETTE["violet"])
s.arrow([(440, 395), (620, 395)], label="全都读过")
s.person(800, 340, label="实习生")                      # 火柴人
s.card(1080, 250, 460, 150, "知识储备 ✅ 拉满",
       "上知天文下知地理\n能写方案，能分析问题", **PALETTE["green"])
s.sticky(300, 690, 940, 90, "ChatGPT、Claude、DeepSeek —— 全是这种人。")
s.save("01-llm.excalidraw")
```

把所有分镜写在一个 `build_scenes.py` 里，每张图一个函数，最后 `main()`
统一输出。**改图 = 改脚本重跑**，不要去手改生成出来的 JSON。

主要 API：`box` `ellipse` `diamond` `text` `title` `arrow` `line` `hrule`
`card`（标题+正文卡片）`sticky`（旁白便签）`person`（火柴人）`save`。
配色只用 `PALETTE`：`ink gray blue green yellow red violet`。
完整参数见 `references/format.md`。

### 4. 过稿：必须先看图再交付

```bash
python3 .../scripts/render_preview.py *.excalidraw -o previews/
CHR=/opt/pw-browsers/chromium-1194/chrome-linux/chrome   # 环境里的 chromium
for f in previews/*.svg; do
  $CHR --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --default-background-color=ffffff --window-size=1750,1050 \
    --screenshot="${f%.svg}.png" "file://$PWD/$f"
done
```

然后**用 Read 工具把 PNG 看一遍**。生成完不看图就交付，等于没做。
重点检查：文字有没有压到图形、结论文字有没有被示意块挡住、
标题是否居中于内容（不是居中于画布）、大片空白要收紧。

预览是近似渲染（没有手绘抖动），只用来验版式；定稿以 excalidraw.com 为准。

### 5. 交付

同时给出：`.excalidraw` 源文件、`previews/` 预览图、一份把
**原稿段落 ↔ 分镜编号**对起来的 README，方便录制时对着念。

## 版式约定

- 画布按 **1600×900** 布局，标题 `s.title(800, 40, ...)` 居中
- 标题 36 / 小节 20-22 / 图内标签 19-24 / 便签 18-20 / 注解 14-17
- 每张图**一个重点色**，其余用 `gray`；绿=好/现在，红=坏/以前，
  紫=核心新概念，黄=旁白与手册，蓝=人和输入
- 旁白句（稿子里的金句）统一放 `sticky`，压在画面底部
- 虚线框 = "这是一个整体"（比如把三步框成一个 Agent）
- 留白比塞满好，但四周不要留超过一屏的空白

## 常见坑

- **中文宽度**：`text_size()` 按 CJK 全宽估算，混排 emoji 会偏窄，
  文字压边时手动调 `x` 或加换行
- **箭头坐标**：`arrow(pts)` 传绝对坐标，内部转成相对 points；
  三点 + `curved=True` 画折线，两点画直线
- **`roundness`**：矩形默认圆角 `{"type":3}`，要直角传 `roundness=None`
- **合并总览图**：平移元素只改 `x`/`y`，`points` 是相对坐标不用动
