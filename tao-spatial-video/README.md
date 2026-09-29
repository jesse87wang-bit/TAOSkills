# tao-spatial-video

> **空间感口播包装** · v1.0.0

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

Agent 会依次完成：听写对齐字幕 → 按口播结构设计每一章的玻璃卡和卡点 → 渲染素材 → 4K 静帧自检 → 在你电脑上分段渲染 4K60 → 混音 → 核对规格后交付。2 分钟左右的片子约 1 小时（渲染约 40 分钟）。

## 运行要求

- Agent 能访问你电脑上的文件夹（Claude 桌面应用链接电脑），原片不上传云端
- 云端环境有 Chromium / Playwright（渲染玻璃卡素材）
- 音效需自备：见 [`toolkit/sfx/README.md`](toolkit/sfx/README.md)

## 目录

```text
tao-spatial-video/
├── SKILL.md            执行真源
├── manifest.json
├── INSTALL.md
├── CHANGELOG.md
└── toolkit/
    ├── device/         在电脑上跑：识别、对齐、HDR 色调映射、RVM 抠像、3D 玻璃卡合成、分段渲染、混音
    ├── container/      在云端跑：玻璃卡组件库、4K 字幕、静帧预览
    ├── templates/      完整示例：一条 2 分钟成片的时间轴和素材定义
    ├── sfx/            音效（不随仓库分发）
    └── fonts/          Poppins（首次运行自动下载）
```

## 第三方组件

- 人物抠像：[Robust Video Matting](https://github.com/PeterL1n/RobustVideoMatting)（运行时下载模型）
- 语音识别：[sherpa-onnx](https://github.com/k2-fsa/sherpa-onnx) + SenseVoice（运行时下载模型）
- 字体：Poppins（SIL OFL）、Noto Sans CJK（系统自带）
