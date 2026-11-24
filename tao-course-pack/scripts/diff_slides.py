# -*- coding: utf-8 -*-
"""新旧两版课件逐页比对（图片型 PDF 也适用）：整页渲染后做像素差，列出改动的页和改动面积。

用法：python3 diff_slides.py 旧课件.pdf 新课件.pdf [--dpi 60] [--out diff_dir]
输出：每页一行「页码 改动占比」，改动页另存左右对照图到 diff_dir，供人工逐页看。
依赖：poppler-utils（pdftoppm）、Pillow、numpy。
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image


def render(pdf, dpi, d):
    subprocess.run(["pdftoppm", "-r", str(dpi), "-png", pdf, os.path.join(d, "p")], check=True)
    return sorted(os.path.join(d, f) for f in os.listdir(d) if f.endswith(".png"))


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    old, new = sys.argv[1], sys.argv[2]
    dpi = int(sys.argv[sys.argv.index("--dpi") + 1]) if "--dpi" in sys.argv else 60
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "diff_dir"
    os.makedirs(out, exist_ok=True)
    a, b = tempfile.mkdtemp(), tempfile.mkdtemp()
    pa, pb = render(old, dpi, a), render(new, dpi, b)
    if len(pa) != len(pb):
        print("页数不同：旧 %d 页，新 %d 页（下面按页序对齐比较，插页后会整体错位）" % (len(pa), len(pb)))
    changed = 0
    for i, (x, y) in enumerate(zip(pa, pb), 1):
        ia, ib = Image.open(x).convert("L"), Image.open(y).convert("L")
        if ia.size != ib.size:
            ib = ib.resize(ia.size)
        d = np.abs(np.asarray(ia, dtype=int) - np.asarray(ib, dtype=int)) > 40
        r = d.mean()
        if r > 0.0005:
            changed += 1
            print("P%02d 改动 %.1f%%" % (i, r * 100))
            w, h = ia.size
            c = Image.new("RGB", (w * 2 + 10, h), "white")
            c.paste(Image.open(x).convert("RGB"), (0, 0)); c.paste(Image.open(y).convert("RGB").resize((w, h)), (w + 10, 0))
            c.save(os.path.join(out, "P%02d_旧左_新右.jpg" % i), quality=80)
    print("共 %d 页有改动，对照图在 %s/" % (changed, out))


if __name__ == "__main__":
    main()
