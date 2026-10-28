# tao-spatial-video 工具包 v1.4.5

一条命令行 `make_video.py`，从一份分镜表出发，把真人口播原片做成「真实背景里玻璃卡从人物身后浮出」的 4K60 成片。
分镜表怎么写见 [`STORYBOARD.md`](STORYBOARD.md)；用 Python 生成分镜表的辅助脚本和完整示例在 [`authoring/`](authoring/README.md)。

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

## v1.4.5 更新

- `setup` 下载中文字体时，主地址（raw.githubusercontent.com）不可用会自动改从 Noto 官方发布包（GitHub releases）取，照样按 sha256 校验。
- 新增 `setup_device.sh`：Claude 桌面版 Linux 工作区的分步安装（`deps` → `models` → `check`），适配单次命令 180 秒上限。
- `30-口播稿/_next_chunk.sh`、`_finish.sh` 同时支持 `~/mnt/自媒体`（单独连接自媒体文件夹）和 `~/mnt/Desktop/自媒体`（连接整个桌面）。

## 快速开始（单机）

```bash
pip install -r requirements.txt && python3 -m playwright install chromium   # ffmpeg 需自带 zscale（libzimg）
python3 make_video.py setup                 # 下载并校验字体、模型
python3 make_video.py doctor                # 环境自检
python3 make_video.py selftest --pixels     # 和第一条成片逐项/逐像素比对，全部 ✓ 再开始

python3 make_video.py probe 原片.MOV                       # → 分镜表 source 字段
python3 make_video.py framing 原片.MOV                     # 取景检查：留安全区时侧卡能放多大（不合格先问用户）
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

**命令有时长限制的环境**（例如单次命令 180 秒）：不要用 `all`，先 `render --list` 看分段计划，再每次命令跑一段 `render --range 起 止`，最后 `mix` → `assemble` → `verify`。分镜表 `render.chunks` 写成每段 **220 帧**（`list(range(0, N, 220)) + [N]`）：4K HEVC 原片 280 帧一段偶尔要 150 秒以上，220 帧稳定在 60–75 秒；一次命令里上一段不到 95 秒就接着跑下一段。拼接后核对帧数 = n_src、片尾 3 秒 `freezedetect` 为 0、1 秒一帧总览图从头看到尾。

## Docker

```bash
docker build -t tao-spatial-video toolkit/
docker run --rm -v "$PWD":/work -w /work tao-spatial-video all storyboard.json
```
镜像基于 `mcr.microsoft.com/playwright/python:v1.56.0-noble`，构建时会下载字体模型并跑 `selftest --pixels`。
说明：维护者的构建环境访问不了容器镜像仓库，这个 Dockerfile **还没有实际构建验证过**；镜像里的 ffmpeg 是 Ubuntu 24.04 的 6.1，和基准渲染机的 4.4.2 不同，出片效果一致，但不保证与基准逐像素一致。

## 平台安全区与取景（v1.4：默认留安全区）

用户 2026-10-02 确认的规则：
- **保留安全区**：默认 `safe_x = 90`（左右各留 90 布局像素 ≈ 8%，视频号长屏手机不会裁到玻璃框和字）。
- **信息不能因为安全区打折**：侧边照样放完整的列表卡、循环图、六宫格、流程图，不再把列表挪到胸前小标签；需要别的图解就用 `svg_panel` 自己画。
- **片尾不加静帧**：`hold` 默认 0，原片结束成片就结束。
- 侧卡能放多大只取决于**人在画面里占多宽**。用户以后会离镜头远一些。拿到原片先跑 `framing`：
  - ✓ 合格（侧卡 ≥0.68 倍，和「有了 WorkBuddy」那两条一样大）→ 正常做；
  - ⚠ 偏近（0.55–0.68）→ 照常用图解卡，列表最多 4 行、每行 ≤8 字；
  - ✗ 太近（<0.55）→ **先问用户**：这条不留安全区（`safe_x: 0`），还是留安全区、侧卡只放大字卡和短列表。
- 参考：2026-10 那批原片头肩宽度约占画面 40%、人偏右 3%，留安全区时右侧卡只有 0.44 倍；要达到 0.68 倍，头肩宽度需 ≤26% 且人站正中（约离镜头远 1.5 倍）。

- **侧卡让位只量头肩主体（v1.4.2，用户 2026-10-04 确认：必须保持，不要改回去）**：留安全区时，抬到脸旁边的手不算进人物宽度——以前手一抬，侧卡就被压到 0.5 倍、跟着手势忽大忽小；现在稳定在取景决定的大小（约 0.6 倍）。实现在 `sv/comp4k.py` 的 `update_head_core`，`configure(safe_x>0)` 时启用；`safe_x: 0` 仍用原算法（旧片逐位一致、selftest 指纹不变）。

`safe_x: 0` 的合成行为和 v1.0/v1.1 逐位相同（卡片最小 0.62 倍、可略出画 25px），只用于用户同意不留安全区的片子和复现旧片。
v1.3 加回的图解卡：`loop_panel` 循环图、`grid_panel` 宫格（3–6 格）、`flow_panel` 流程图；v1.4 新增 `svg_panel` 自绘图解卡，见 STORYBOARD.md §4。

## 字幕和实录版口播稿（v1.4.4）

`python3 mkdocs.py <项目文件夹> meta.json` 从 `lines.json` + 分镜表的章节标生成 `字幕.srt` 和 `口播稿.md`（实录版，按章节标分节）。
meta.json：`{"id","title","column","biz_tier","cta","成品","分镜表","src_name","heads":{"开场":"…","B01":"01 …"}}`；`heads` 不写就用「序号 + 章节标文字」，非数字序号（NEXT/LAST）记成「结尾」，「关注我」那句归到结尾。
`cta` 按录音写：实录里没有「关注我」就写「无」，不照抄文稿。

## 交付规则（v1.4.3：delivery.json，每个用户自己定）

成片做完后 `make_video.py deliver storyboard.json --src 成片.mp4`，按工具包目录下 `delivery.json` 命名并放进成品文件夹：

```json
{"root": "../../成品", "folder": "{MMDD} {name}", "file": "Final{name}{ext}", "tz": "Asia/Shanghai"}
```
- `{name}` = 分镜表的 `deliver_name`（用户怎么叫这条视频就怎么写，比如「AI 原生组织」，带空格照抄），没写就用原片文件名去掉扩展名
- `{MMDD}` = 交付当天的月日（按 `tz`），也可以用 `{YYYY}` `{MM}` `{DD}` `{title}`
- `root` 相对工具包目录，或写绝对路径
- **新用户第一次用、还没有 delivery.json**：deliver 会停下来提示——先问用户成片放哪、文件夹和文件怎么命名，写进 delivery.json 再交付

## 渲染参数（已和用户确认，不要改）

2160×3840 · 60fps · H.264 High L5.2 · CRF 15 · yuv420p · bt709 · AAC 320k 48kHz；iPhone HLG/杜比视界原片用 zscale（linear, npl=100）→ hable → bt709 色调映射；原片像素只在卡片区域被改动。
