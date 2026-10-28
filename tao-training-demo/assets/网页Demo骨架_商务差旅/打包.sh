#!/bin/bash
# 生成分发用的 zip：排除模型 Key（config.json）、演示状态和运行结果。问答缓存保留，便于断网回放。
cd "$(dirname "$0")"
NAME="商务差旅助手_网页演示版_$(date +%Y%m%d).zip"
python3 - "$NAME" <<'PY'
import os, sys, zipfile
name = sys.argv[1]
root = os.path.basename(os.getcwd())
skip_dirs = {"__pycache__", "runs"}
skip_files = {"config.json", "state.json", "state.json.tmp", ".DS_Store", name}
with zipfile.ZipFile(os.path.join("..", name), "w", zipfile.ZIP_DEFLATED) as z:
    for d, ds, fs in os.walk("."):
        ds[:] = [x for x in ds if x not in skip_dirs]
        for f in fs:
            if f in skip_files or f.endswith(".zip"):
                continue
            p = os.path.join(d, f)
            info = zipfile.ZipInfo.from_file(p, os.path.join(root, os.path.normpath(p)))
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(p, "rb") as fh:
                z.writestr(info, fh.read())
print("已生成：../%s" % name)
PY
