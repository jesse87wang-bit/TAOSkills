# tao-spatial-video 参考运行环境（素材 + 渲染同一台机器）
# 说明：维护者的环境无法拉取容器镜像，此文件尚未实际构建验证；构建时会跑 selftest --pixels，不通过则构建失败。
FROM mcr.microsoft.com/playwright/python:v1.56.0-noble
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/tao-spatial-video
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SV_MODELS=/opt/sv-models
RUN python3 make_video.py setup \
 && python3 make_video.py selftest --pixels
ENTRYPOINT ["python3", "/opt/tao-spatial-video/make_video.py"]
