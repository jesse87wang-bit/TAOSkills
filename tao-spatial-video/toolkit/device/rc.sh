#!/bin/bash
# 渲染一段并核对帧数。用法: rc.sh <工作目录> <时间轴.py> <起始帧> <结束帧>
# 每次调用都在 175 秒内结束（用户电脑的命令超过 180 秒会被杀，后台进程也活不过一次调用）
KIT="$(cd "$(dirname "$0")" && pwd)"
WD="$1"; SEQ="$2"; n=$(printf %05d $3)
mkdir -p "$WD/chunks"; S=$(date +%s)
timeout 175 python3 "$KIT/render_chunk.py" "$SEQ" $3 $4 "$WD/chunks/c_$n.mp4" > "$WD/chunks/log_$n.txt" 2>&1
c=$(ffprobe -v error -count_frames -show_entries stream=nb_read_frames -of csv=p=0 "$WD/chunks/c_$n.mp4" 2>/dev/null | tail -1)
echo "chunk $3-$4 frames=$c expected=$(( $4-$3 )) time=$(( $(date +%s)-S ))s"
