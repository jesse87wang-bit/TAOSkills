# 4K 字幕贴图（白字 + 深紫描边 + 柔和投影），和第一条成片逐像素一致
import os, json, math
from . import assets

SIZE, MIN_SIZE = 104, 80   # 字号（4K 像素）；太长的行在安全区模式下自动缩小，最小 80

def _render(FT, text, dy=0):
    from PIL import Image, ImageDraw, ImageFilter
    tw = int(FT.getlength(text))+80
    im = Image.new('RGBA', (tw, 210), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.text((40, 34+dy), text, font=FT, fill=(30,20,70,200), stroke_width=16, stroke_fill=(30,20,70,200))
    im = im.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(im); d.text((40, 34+dy), text, font=FT, fill=(255,255,255,255), stroke_width=5, stroke_fill=(25,15,60,255))
    return im, tw

def make(lines, out_dir, total_sec, safe_x=0):
    """lines = [[开始, 结束, 文字], ...]；最后一句延到片尾（向上取整到 0.1 秒）。
    safe_x>0：字幕宽度不超出平台安全区（左右各 safe_x 布局像素），超了先缩字号，缩到 80 还放不下就列为「要拆行」。
    返回 (subs, 要拆行的文字)"""
    from PIL import ImageFont
    os.makedirs(out_dir, exist_ok=True)
    font = assets.font('NotoSansCJKsc-Bold.otf'); FT = ImageFont.truetype(font, SIZE)
    max_w = int(round((1080 - 2*safe_x)*2)) if safe_x > 0 else 2100
    subs, too_long = [], []
    for i, (a, b, text) in enumerate(lines):
        im, tw = _render(FT, text)
        if tw > max_w and safe_x > 0:
            size = max(MIN_SIZE, int(SIZE*(max_w-80)/(tw-80)))
            im, tw = _render(ImageFont.truetype(font, size), text, (SIZE-size)//2)   # 缩小后保持垂直居中
        name = f'L{i:03d}.png'; im.save(os.path.join(out_dir, name)); subs.append([round(a,3), round(b,3), name])
        if tw > max_w:
            too_long.append(text)
    if subs:
        subs[-1][1] = math.ceil(total_sec*10)/10
    with open(os.path.join(out_dir, 'subs.json'), 'w', encoding='utf-8') as f:
        json.dump(subs, f, ensure_ascii=False)
    return subs, too_long
