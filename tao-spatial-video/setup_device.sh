#!/usr/bin/env bash
# tao-spatial-video 电脑端（Claude 桌面版的 Linux 工作区）一次性安装，v1.4.5。
# 单次命令有 180 秒上限，所以分三步跑，每步都可以重复执行（已装好的会跳过，下载会续传）：
#   bash setup_device.sh deps     # ffmpeg 检查 + Python 依赖（numpy / opencv / onnxruntime / sherpa-onnx / soundfile / pillow）
#   bash setup_device.sh models   # 抠像 + 语音识别模型 → ~/work/sv（约 250MB，没下完就再跑一次）
#   bash setup_device.sh check    # doctor 环境自检 + selftest 基准回归（电脑端不渲染素材，素材在云端做）
# 电脑端不需要 Playwright/Chromium：sprites / subs / preview 在云端容器做。
set -u
KIT="$(cd "$(dirname "$0")" && pwd)"
case "${1:-check}" in
  deps)
    if command -v ffmpeg >/dev/null; then
      ffmpeg -hide_banner -filters 2>/dev/null | grep -q zscale && echo "✓ ffmpeg 带 zscale" || echo "✗ ffmpeg 没有 zscale（iPhone HDR 原片色调映射必需）"
    else
      echo "✗ 没有 ffmpeg：sudo apt-get install -y ffmpeg"
    fi
    PIP="python3 -m pip install --user -q"
    python3 -m pip install --help 2>/dev/null | grep -q break-system-packages && PIP="$PIP --break-system-packages"
    WH="$KIT/_离线模型/wheels"
    if ls "$WH"/*.whl >/dev/null 2>&1; then   # 先用离线安装包（云端下好传过来的），不依赖电脑端网络
      timeout 170 $PIP --no-index --find-links "$WH" sherpa-onnx==1.13.8 soundfile==0.14.0 && echo "✓ 离线安装 sherpa-onnx / soundfile"
    fi
    timeout 170 $PIP numpy==2.2.6 opencv-python-headless==5.0.0.93 onnxruntime==1.23.2 \
      sherpa-onnx==1.13.8 soundfile==0.14.0 pillow==12.2.0 && echo "✓ Python 依赖" || echo "… 没装完（超时或网络），再跑一次 deps"
    ;;
  models)
    # 优先用工具包里的离线备份（_离线模型/sv-models.tar.part*，云端打包传过来的），电脑端联不了网也能装
    OFF="$KIT/_离线模型"; MD="${SV_MODELS:-$HOME/work/sv}"
    if ls "$OFF"/sv-models.tar.part* >/dev/null 2>&1; then
      mkdir -p "$MD"
      if [ -f "$OFF/sv-models.tar.md5" ]; then
        GOT=$(cat "$OFF"/sv-models.tar.part* | md5sum | cut -d' ' -f1); WANT=$(cut -d' ' -f1 "$OFF/sv-models.tar.md5")
        [ "$GOT" = "$WANT" ] || { echo "✗ 离线备份 md5 不符（$GOT ≠ $WANT），改走在线下载"; OFF=""; }
      fi
      [ -n "$OFF" ] && cat "$OFF"/sv-models.tar.part* | tar xf - -C "$MD" && echo "✓ 已从离线备份解出模型到 $MD"
    fi
    cd "$KIT" && timeout 170 python3 make_video.py setup --models || echo "… 没装完，再跑一次 models（会续传）"
    ;;
  check)
    cd "$KIT" && python3 make_video.py doctor && timeout 170 python3 make_video.py selftest
    ;;
  *) echo "用法: bash setup_device.sh deps|models|check"; exit 1 ;;
esac
