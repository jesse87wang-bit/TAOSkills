# tao-spatial-video

> **空间感口播包装** · v1.1.0

把一条真人口播原片（iPhone 竖拍 4K HDR）和口播稿，做成像 AI 产品发布会一样的科技感成片：

- 人物始终居中，**背景是真实房间**，原片画质不动
- **玻璃拟态卡片从人物身后两侧浮出**，带 3D 透视，内侧被人的头和肩挡住，人和 UI 在同一个空间里
- 每张卡、每行字都**卡着口播关键词弹出**，配科技感提示音
- 输出和原片同规格：**2160×3840 · 60fps**

## 怎么用

装好后，对 Agent 说：

```text
用 tao-spatial-video 把这条口播做成片：
原片：~/Desktop/自媒体/xxx.MOV
口播稿：（贴上来）
```

Agent 会：听写对齐字幕 → 按口播结构写一份**分镜表** → 渲染玻璃卡素材并自动校验 → 4K 静帧自检 → 分段渲染 4K60 → 混音 → 核对规格后交付。2 分钟左右的片子约 1 小时（渲染约 40 分钟）。

## 换 Agent 也一样（v1.1）

v1.1 把「做法」固定成了工具包：Agent 只写分镜表 `storyboard.json`（哪句话出什么卡、放左边还是右边），
玻璃卡样式、坐标动画、音效规则、字体、模型、渲染参数全部由 `toolkit/make_video.py` 按固定规则生成，并按 sha256 锁定版本。
Claude、Codex、WorkBuddy 等任何能跑 Python 的 Agent 装上后，同一份分镜表出来的是同一条片子。

自带回归测试：`python3 toolkit/make_video.py selftest --pixels`，拿第一条成片《WorkBuddy 还是豆包工作》逐项、逐像素比对。
v1.1 发布时的结果：时间轴 58 个元素 / 82 个音效逐项一致，56 张素材 + 69 张字幕逐像素一致，在原机器上重渲的分段和原成片 **md5 完全相同**。

## 运行要求

- Python 3.10+、ffmpeg（带 zscale）、Playwright + Chromium；依赖版本见 `toolkit/requirements.txt`（也可用 `toolkit/Dockerfile`）
- 字体和模型首次运行自动下载并校验
- 音效需自备（剪映授权）：见 [`toolkit/sfx/README.md`](toolkit/sfx/README.md)
- 原片可以不离开你的电脑：素材可以在另一台机器做，渲染在原片所在的机器上跑（见 `toolkit/README.md`）

## 目录

```text
tao-spatial-video/
├── SKILL.md                 Agent 执行流程（真源）
├── manifest.json
├── INSTALL.md
├── CHANGELOG.md
└── toolkit/
    ├── make_video.py        命令行：probe / asr / align / validate / sprites / subs / preview / render / mix / assemble / verify / selftest
    ├── STORYBOARD.md        分镜表格式
    ├── README.md            环境、分机器、一致性说明
    ├── sv/                  组件库、分镜表翻译、校验、合成器、混音…
    ├── golden/workbuddy/    第一条成片的完整分镜表 + 回归基准
    ├── requirements.txt · assets.json · Dockerfile
    ├── sfx/                 音效（不随仓库分发）
    └── fonts/               字体（自动下载）
```

## 第三方组件

- 人物抠像：[Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting)（GPL-3.0，运行时下载模型）
- 语音识别：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) + SenseVoice（运行时下载模型）
- 字体：Poppins、Noto Sans CJK SC 2.004（SIL OFL，运行时下载）
