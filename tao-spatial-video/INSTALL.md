# tao-spatial-video v1.4.5 安装

## 装成 skill

把整个 `tao-spatial-video/` 目录装进 Agent 的 skills 目录（不要只复制 SKILL.md）。

```text
请从 GitHub 安装并启用 tao-spatial-video：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/tao-spatial-video
请完整加载整个目录。安装后用「用 tao-spatial-video 把这条口播做成片」调用。
```

## 首次使用前

1. 按 `sfx/README.md` 准备 6 个音效 wav，放进 `sfx/`（剪映音效，需自有授权，不随仓库分发）。
2. 云端（做素材）：`python3 make_video.py setup` 自动下载并校验字体和模型，`python3 make_video.py doctor` 自检。
3. 电脑端（Claude 桌面版 Linux 工作区，做渲染）：`bash setup_device.sh deps` → `bash setup_device.sh models` → `bash setup_device.sh check`。
4. 可选：`python3 make_video.py selftest --pixels` 与第一条成片逐项比对。

详细流程见 `SKILL.md`、`README.md`、`STORYBOARD.md`。
