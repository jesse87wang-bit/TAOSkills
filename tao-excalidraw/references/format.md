# excalidraw_kit API 与 .excalidraw 格式速查

## 文件外壳

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "...",
  "elements": [ ... ],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

`Scene.save()` 已经处理好外壳，一般不用管。

## 每个元素的必填字段

漏掉任何一个，excalidraw.com 打开时会报 invalid element 或静默丢元素：

```
id type x y width height angle strokeColor backgroundColor fillStyle
strokeWidth strokeStyle roughness opacity groupIds frameId roundness
seed version versionNonce isDeleted boundElements updated link locked
```

`text` 额外需要：`text fontSize fontFamily textAlign verticalAlign
containerId originalText lineHeight`。
`arrow` / `line` 额外需要：`points startBinding endBinding startArrowhead
endArrowhead lastCommittedPoint`。

`points` 是**相对 `x`/`y` 的偏移**，第一个点恒为 `[0,0]`。整体平移图形时
只改 `x`/`y`，`points` 不动。

## API

### Scene(background="#ffffff", seed=20260819)

`seed` 固定随机种子，保证同一份脚本每次生成的文件字节一致（利于 git diff）。

### 图形

```python
s.box(x, y, w, h, label=None, font_size=20, **PALETTE["blue"])
s.ellipse(x, y, w, h, label=None, ...)
s.diamond(x, y, w, h, label=None, ...)
```

`label` 会作为 **bound text** 绑进容器（`containerId` + `boundElements`），
在 Excalidraw 里拖动图形时文字跟着走，双击可直接改。

通用关键字：`stroke` `bg` `fill_style` `stroke_width` `stroke_style`
（`solid|dashed|dotted`）`roughness`（0 建筑感 / 1 手绘 / 2 潦草）
`opacity` `roundness`（`None` 为直角）`group_ids`。

### 文字

```python
s.text(x, y, "多行\n文本", size=20, align="left|center|right", color="#1e1e1e")
s.title(cx, y, "大标题", sub="副标题")      # cx 是中心 x
```

`align="center"` 时 `x` 当作中心点。

### 连线

```python
s.arrow([(x1,y1), (x2,y2)], label="说明", dashed=False, curved=False,
        stroke="#1e1e1e", start_head=None, end_head="arrow")
s.line([(x1,y1), (x2,y2)], stroke="#dee2e6", dashed=True, stroke_width=1)
s.hrule(x1, x2, y)                            # 分隔线
```

三个以上的点 + `curved=True` 得到圆角折线，适合一对多的发散/收敛。

### 组合件

```python
s.card(x, y, w, h, "标题", "正文\n第二行", body_size=17, **PALETTE["green"])
s.sticky(x, y, w, h, "旁白金句", size=19)     # 默认淡黄便签
s.person(cx, cy, label="实习生", scale=1.0)   # 圆头 + 圆身
```

### 输出

```python
s.save("path.excalidraw")   # 返回 Path，自动建目录
s.bbox()                    # (minx, miny, maxx, maxy)
```

## 字体

`fontFamily`：`1` = Excalifont/Virgil 手绘体（`FONT_HAND`，默认），
`2` = Helvetica（`FONT_NORMAL`），`3` = Cascadia 等宽（`FONT_CODE`）。

手绘体不含 CJK 字形，中文会回退到系统 CJK 字体——所以中文看起来是规整的，
只有英文和数字带手绘感。这是 Excalidraw 的固有行为，不是 bug。

## 宽度估算

`text_width()` 按 CJK 1.0 字宽、ASCII 0.56 字宽估算。全角标点算 1.0，
emoji 实际渲染比估算宽，标题里带 emoji 时留 10% 余量。
