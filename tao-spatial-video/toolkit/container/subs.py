# 4K 字幕贴图。用法: python3 subs.py <lines.json> <输出目录> [片尾定格后的总秒数]
# lines.json = [[开始,结束,文字],...]（align.py 输出，已人工校对）；最后一句延长到片尾
import sys, os, json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
L = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
FT = ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', 104, index=2)
subs = []
for i, (a, b, text) in enumerate(L):
    tw = int(FT.getlength(text))+80
    im = Image.new('RGBA', (tw, 210), (0,0,0,0)); d = ImageDraw.Draw(im)
    d.text((40, 34), text, font=FT, fill=(30,20,70,200), stroke_width=16, stroke_fill=(30,20,70,200))
    im = im.filter(ImageFilter.GaussianBlur(10))
    d = ImageDraw.Draw(im); d.text((40, 34), text, font=FT, fill=(255,255,255,255), stroke_width=5, stroke_fill=(25,15,60,255))
    name = f'L{i:03d}.png'; im.save(os.path.join(out, name)); subs.append([round(a,3), round(b,3), name])
    if tw > 2100: print('⚠ 字幕太长，请拆行:', text)
if len(sys.argv) > 3: subs[-1][1] = float(sys.argv[3])
json.dump(subs, open(os.path.join(out, 'subs.json'),'w'), ensure_ascii=False)
print(len(subs), 'subs')
