# tao-spatial-video v1.0.0 安装

## 安装

把整个 `tao-spatial-video/` 目录装进 Agent 的 skills 目录（不要只复制 SKILL.md，`toolkit/` 是必需的）。

发给支持 GitHub / Skills 的 Agent：

```text
请从 GitHub 安装并启用 tao-spatial-video：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/tao-spatial-video

请完整加载整个目录（包括 toolkit/）。安装后用「用 tao-spatial-video 把这条口播做成片」调用。
```

## 首次使用前

1. 按 `toolkit/sfx/README.md` 准备 6 个音效 wav，放进 `toolkit/sfx/`。
2. 电脑上的 Linux 环境第一次运行 `bash toolkit/device/prep.sh`，会装 sherpa-onnx、onnxruntime，并下载抠像和识别模型（约 200MB，放在 `~/work/sv`）。
3. 云端环境需要 Python Playwright + Chromium；字体会自动下载。
