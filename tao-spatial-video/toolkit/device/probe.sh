#!/bin/bash
# 看原片参数（是不是 HDR、帧率、时长）或核对成片。用法: probe.sh <视频>
ffprobe -v error -show_entries format=duration,bit_rate,size:stream=codec_name,profile,width,height,r_frame_rate,avg_frame_rate,pix_fmt,color_transfer,color_primaries,sample_rate,channels -of default=nw=1 "$1" | tr '\n' ' '; echo
echo "视频帧数: $(ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 "$1")"
