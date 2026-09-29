#!/bin/bash
# 用户电脑 Linux 环境准备（每个新会话跑一次，约 1–2 分钟）
mkdir -p ~/work/sv && cd ~/work/sv
python3 -c "import sherpa_onnx, soundfile" 2>/dev/null || python3 -m pip install --user -q sherpa-onnx soundfile
python3 -c "import cv2, onnxruntime, numpy" 2>/dev/null || python3 -m pip install --user -q opencv-python-headless onnxruntime numpy
[ -f rvm.onnx ] || curl -sL -o rvm.onnx https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx
[ -f silero_vad.onnx ] || curl -sL -o silero_vad.onnx https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx
[ -d sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09 ] || (curl -sL -o sv.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2 && tar xjf sv.tar.bz2 && rm sv.tar.bz2)
ls -la ~/work/sv
