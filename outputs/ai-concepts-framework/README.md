# 《看完这篇，AI 圈再扔什么新词你都不会懵》配图分镜

口播稿共 8 段，对应 8 张分镜。录制时按编号顺序切图即可。

## 分镜清单

| 编号 | 对应稿子段落 | 这张图的主张 | 图式 |
| --- | --- | --- | --- |
| `00-cover` | 开头「把它想象成一家公司」 | 六个词就是一家公司的六个角色 | 色块阵列 + 虚线公司框 |
| `01-llm` | 实习生读过全世界的书 | 知识拉满、经验为零 | 中心主体 + 左右属性卡 |
| `02-prompt` | 「写个方案」vs「500 字三个竞品对比」 | 同一个模型，指令决定结果 | 上下双管线对比 |
| `03-context` | 资料给少了 / 给多了 | 上下文窗口有限，多了会溢出 | 三行量表 + 溢出块 |
| `04-agent` | 配电脑、装软件、开权限 | 从「盯着做」到「交出去」 | 上下两带前后对比 |
| `05-skill` | 花一个下午写成操作手册 | 重复任务写成 SOP，不用重复教 | 左任务 → 右手册 |
| `06-mcp` | 五根充电线 vs 万能转接头 | N 个私有接口收敛成 1 个标准接口 | 左右分栏，发散 vs 收敛 |
| `07-summary` | 结尾六个角色列表 | 一套框架，以后新词自己往里套 | 色块清单 |

`all-scenes.excalidraw` 是把 8 张平铺在一张画布上的总览，用来整体过版式。

## 怎么用

**改文案 / 调版式**：改 `build_scenes.py`，然后

```bash
python3 build_scenes.py
python3 ../../tao-excalidraw/scripts/render_preview.py *.excalidraw -o previews/
```

不要直接手改 `.excalidraw` JSON——下次重跑会被覆盖。

**导出成图**：把 `.excalidraw` 拖进 <https://excalidraw.com> 打开，
`Ctrl/Cmd + Shift + E` 导出 PNG/SVG，可以选透明底、2x 分辨率。

**预览图**：`previews/*.svg` 和 `previews/*.png` 是近似渲染，
只用来快速过稿——没有 Excalidraw 的手绘抖动效果，定稿以 excalidraw.com 为准。

## 生成方式

由 [`tao-excalidraw`](../../tao-excalidraw/) skill 生成。
