# tao-spatial-video v1.1.0 安装

## 安装

把整个 `tao-spatial-video/` 目录装进 Agent 的 skills 目录（不要只复制 SKILL.md，`toolkit/` 是必需的）。

发给支持 GitHub / Skills 的 Agent：

```text
请从 GitHub 安装并启用 tao-spatial-video：
https://github.com/jesse87wang-bit/TAOSkills/tree/main/tao-spatial-video

请完整加载整个目录（包括 toolkit/），然后在 toolkit/ 里依次运行：
pip install -r requirements.txt && python3 -m playwright install chromium
python3 make_video.py setup
python3 make_video.py doctor
python3 make_video.py selftest --pixels
全部 ✓ 后，用「用 tao-spatial-video 把这条口播做成片」调用。
```

## 首次使用前

1. 按 `toolkit/sfx/README.md` 准备 6 个音效 wav，放进 `toolkit/sfx/`（`doctor` 会核对是否和基准一致）。
2. ffmpeg 需要带 zscale（`ffmpeg -filters | grep zscale` 有输出）；Ubuntu/Debian 的 apt 版、Homebrew 版都带。
3. `setup` 会下载字体（约 70MB）和抠像/识别模型（约 250MB，默认放 `~/work/sv`，可用环境变量 `SV_MODELS` 改）。网络慢时可重复运行，已下载且校验通过的会跳过。
4. `selftest --pixels` 全部 ✓，说明这台机器做出来的素材和第一条成片逐像素一致。

也可以直接用 Docker：`docker build -t tao-spatial-video toolkit/`（见 `toolkit/README.md`）。

## 从 v1.0 升级

v1.0 的 `seq.py` / `sprites.py` 写法不再使用，改为分镜表 `storyboard.json`（格式见 `toolkit/STORYBOARD.md`，完整示例 `toolkit/golden/workbuddy/storyboard.json`）。
v1.0.0 的代码保留在 Git 标签 `tao-spatial-video-v1.0.0`。
