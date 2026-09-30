# tao-spatial-video 工具包 v1.1

一条命令行 `make_video.py`，从一份分镜表出发，把真人口播原片做成「真实背景里玻璃卡从人物身后浮出」的 4K60 成片。
分镜表怎么写见 [`STORYBOARD.md`](STORYBOARD.md)。

```
toolkit/
├── make_video.py        命令行入口（所有步骤）
├── STORYBOARD.md        分镜表格式说明
├── requirements.txt     固定版本
├── assets.json          字体 / 模型 / 音效的下载地址和 sha256
├── Dockerfile           参考运行环境
├── sv/                  实现
│   ├── components.py    玻璃卡组件（24 种，标记与第一条成片逐字一致）
│   ├── storyboard.py    分镜表 → 合成器时间轴 + 音效表（固定翻译规则）
│   ├── validate.py      校验（红线词、同屏数量、时间、溢出）
│   ├── sprites.py       Chromium 渲染素材（私有 fontconfig，只用固定版本字体）
│   ├── subs.py          4K 字幕贴图
│   ├── comp4k.py        合成器：HLG→SDR、RVM 抠像、3D 透视玻璃卡、人物遮挡（渲染核心，勿改）
│   ├── mix.py           人声 + 音效混音（-16 LUFS）
│   ├── speech.py        语音识别 + 字幕对齐
│   ├── preview.py       4K 静帧预览
│   ├── assets.py        下载与哈希校验
│   └── selftest.py      基准回归测试
├── golden/workbuddy/    基准：第一条成片的分镜表、字幕、时间轴、逐像素哈希
├── sfx/                 音效（自备，见 sfx/README.md）
└── fonts/               字体（setup 自动下载）
```

## 快速开始（单机）

```bash
pip install -r requirements.txt && python3 -m playwright install chromium   # ffmpeg 需自带 zscale（libzimg）
python3 make_video.py setup                 # 下载并校验字体、模型
python3 make_video.py doctor                # 环境自检
python3 make_video.py selftest --pixels     # 和第一条成片逐项/逐像素比对，全部 ✓ 再开始

python3 make_video.py probe 原片.MOV                       # → 分镜表 source 字段
python3 make_video.py asr   原片.MOV asr.json
#   对照口播稿写 lines.txt（实际念出来的字，一行一句）
python3 make_video.py align asr.json lines.txt lines.json  # 同时生成 lines_chars.json（关键词卡点）
#   写 storyboard.json（照 golden/workbuddy/storyboard.json）
python3 make_video.py validate storyboard.json
python3 make_video.py sprites  storyboard.json && python3 make_video.py validate storyboard.json   # 第二次校验包含溢出检查
python3 make_video.py preview  storyboard.json 20.5 70.2 100   # 4K 静帧预览，逐张看
python3 make_video.py all      storyboard.json               # 字幕 → 分段渲染 → 混音 → 拼接 → 核对
```

中间文件都在分镜表旁边的 `build/`：`sp3/`（素材）、`sub4k/`（字幕）、`stills/`（静帧）、`chunks/`（分段）、`audio.wav`、`timeline.json`。
环境变量：`SV_BUILD` 把 build 放到别处（分段视频很大，别写进同步盘）；`SV_MODELS` 模型目录（默认 `~/work/sv`）；`SV_SOURCE` 临时指定原片位置。

## 怎么保证「不同 Agent 做出来一模一样」

| 环节 | 做法 |
|---|---|
| 设计 | Agent 只写分镜表（内容 + 时间点 + 位置预设），不写坐标动画代码；组件库、位置预设、动画参数、音效规则都固定在工具包里 |
| 翻译 | `storyboard.py` 按固定规则把分镜表翻成时间轴；`plan` 命令会导出 `timeline.json` 可逐项核对 |
| 素材 | 组件标记固定；Chromium 只看得到 `fonts/` 里按 sha256 固定的字体（私有 fontconfig），渲染参数写死，不受本机字体影响 |
| 渲染 | 合成器源码固定（selftest 核对指纹）；抠像/识别模型按 sha256 校验；每段在独立进程里从段首预热 |
| 声音 | 音效文件按 sha256 核对；混音算法固定 |
| 回归 | `selftest` 拿第一条成片当尺子：时间轴逐项、素材和字幕逐像素、（有原片时）重渲分段逐帧 |

v1.1 发布前的回归结果（基准 = 第一条成片出片时的文件）：

- 分镜表翻译出的时间轴：58 个元素、82 个音效、扫光、光晕，与原始时间轴代码**逐项一致**
- 56 张玻璃卡素材、69 张字幕：**逐像素一致**
- 在用户电脑上用 v1.1 重渲第 420–870、3990–4410、7050–7268 帧：输出文件与原成片分段 **md5 完全相同**
- 混音：与原成片音轨 **md5 完全相同**；字幕对齐：与原 lines.json 完全相同

**版本不同时**：换了 Chromium / numpy / OpenCV / onnxruntime / ffmpeg 版本或 CPU 架构，成片的版式、动画、音效仍然一致，但可能出现肉眼看不出的像素级差异（抗锯齿、抠像边缘的浮点误差）。要逐像素一致，就用 `requirements.txt` 里的版本或 Docker 镜像，并跑 `selftest --pixels` 确认。

## 分机器工作（素材机 + 渲染机）

原片几百 MB 到几 GB，可以只在原片所在的机器上渲染，素材在另一台有 Chromium 的机器上做：

| 步骤 | 需要 |
|---|---|
| probe / asr / align / render / mix / assemble / verify | 原片、ffmpeg（zscale）、numpy、opencv、onnxruntime（asr 另需 sherpa-onnx、soundfile） |
| sprites / subs / validate / plan / preview | Playwright + Chromium（sprites）、Pillow（subs）；preview 另需 opencv + onnxruntime 和静帧 |

两边用同一份工具包和同一份分镜表，把素材机上的 `build/sp3/`、`build/sub4k/` 拷到渲染机分镜表旁的 `build/` 里即可。

**命令有时长限制的环境**（例如单次命令 180 秒）：不要用 `all`，先 `render --list` 看分段计划，再每次命令跑一段 `render --range 起 止`（每段 ≤450 帧，约 130–150 秒），最后 `mix` → `assemble` → `verify`。

## Docker

```bash
docker build -t tao-spatial-video toolkit/
docker run --rm -v "$PWD":/work -w /work tao-spatial-video all storyboard.json
```
镜像基于 `mcr.microsoft.com/playwright/python:v1.56.0-noble`，构建时会下载字体模型并跑 `selftest --pixels`。
说明：维护者的构建环境访问不了容器镜像仓库，这个 Dockerfile **还没有实际构建验证过**；镜像里的 ffmpeg 是 Ubuntu 24.04 的 6.1，和基准渲染机的 4.4.2 不同，出片效果一致，但不保证与基准逐像素一致。

## 渲染参数（已和用户确认，不要改）

2160×3840 · 60fps · H.264 High L5.2 · CRF 15 · yuv420p · bt709 · AAC 320k 48kHz；iPhone HLG/杜比视界原片用 zscale（linear, npl=100）→ hable → bt709 色调映射；原片像素只在卡片区域被改动。
