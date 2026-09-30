# 4K 字幕贴图（白字 + 深紫描边 + 柔和投影），和第一条成片逐像素一致
import os, json, math
from . import assets

MAX_W = 2100          # 超过这个宽度（约 18 个汉字）要拆行

def make(lines, out_dir, total_sec):
    """lines = [[开始, 结束, 文字], ...]；最后一句延到片尾（向上取整到 0.1 秒）。返回 (subs, 过长的行)"""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    os.makedirs(out_dir, exist_ok=True)
    FT = ImageFont.truetype(assets.font('NotoSansCJKsc-Bold.otf'), 104)
    subs, too_long = [], []
    for i, (a, b, text) in enumerate(lines):
        tw = int(FT.getlength(text))+80
        im = Image.new('RGBA', (tw, 210), (0,0,0,0)); d = ImageDraw.Draw(im)
        d.text((40, 34), text, font=FT, fill=(30,20,70,200), stroke_width=16, stroke_fill=(30,20,70,200))
        im = im.filter(ImageFilter.GaussianBlur(10))
        d = ImageDraw.Draw(im); d.text((40, 34), text, font=FT, fill=(255,255,255,255), stroke_width=5, stroke_fill=(25,15,60,255))
        name = f'L{i:03d}.png'; im.save(os.path.join(out_dir, name)); subs.append([round(a,3), round(b,3), name])
        if tw > MAX_W:
            too_long.append(text)
    if subs:
        subs[-1][1] = math.ceil(total_sec*10)/10
    with open(os.path.join(out_dir, 'subs.json'), 'w', encoding='utf-8') as f:
        json.dump(subs, f, ensure_ascii=False)
    return subs, too_long
