# spatial_video｜空间感玻璃卡口播成片工具包

配合 skill `tao-spatial-video` 使用。第一条成品：`30-口播稿/加更-WorkBuddy还是豆包工作/成片_WorkBuddy还是豆包工作_4K60.mp4`。

## 两处运行

| 在哪跑 | 做什么 | 目录 |
|---|---|---|
| **云端容器**（有 Chromium） | 渲染玻璃卡素材 PNG、字幕 PNG、静帧预览 | `container/` `templates/` |
| **用户电脑 Linux 环境**（原片在这） | 识别、对齐、调色抠像合成、编码、混音 | `device/` |

原片 4K 文件太大，不往云端传；素材和字幕是小文件，从云端传到电脑上。

## 目录

```
device/
  prep.sh          准备环境：装 sherpa-onnx / onnxruntime，下 RVM 抠像模型、SenseVoice 识别模型（放 ~/work/sv）
  probe.sh         看原片参数（HDR? 帧率? 时长?）/ 核对成片
  asr.py           语音识别（逐字时间戳）
  align.py         把校对后的字幕行对齐到识别时间 → lines.json（+ 逐字时间 _chars.json，用来卡点）
  comp4k.py        合成器：HDR→SDR 色调映射、RVM 抠像、3D 透视玻璃卡、人物遮挡、字幕、扫光
  render_chunk.py  渲染一段帧
  rc.sh            渲染一段并核对帧数（每段 ≤450 帧，175 秒内结束）
  mix.py           人声 + 音效混音，响度 -16 LUFS
container/
  sprites_lib.py   玻璃卡组件库（list_panel / big_card / badge / verdict / judge / chip / glow_text / laptop / rating_panel ...）
  subs.py          4K 字幕 PNG + subs.json
  preview.py       用 4K 静帧预览版式
templates/
  seq_example.py      时间轴示例（完整一条片子的写法）
  sprites_example.py  素材示例
sfx/   剪映音效（仓库里不带音频，按 sfx/README.md 自己准备）：deng 噔-楞 / ding3 三连叮 / app 短点击 / tone 柔和系统音 / xp 提示音 / ui 按钮点击
fonts/ Poppins（英文粗斜体，首次运行自动下载）
```

## 关键参数（已和用户确认过的标准）

- 输出 2160×3840、60fps、H.264 High、CRF 15、bt709；和原片同分辨率同帧率
- iPhone 原片是 HLG/杜比视界：必须用 comp4k.py 里的 `TONEMAP`（zscale + hable）转 SDR，直接转会发灰过曝
- 原片像素不动，只有卡片区域被改；不虚化背景、不调色
- 画面上不出现「评论区扣 xx」这类引导字样
