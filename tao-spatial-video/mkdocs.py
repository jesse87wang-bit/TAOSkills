#!/usr/bin/env python3
"""从 lines.json + storyboard.json 的章节徽章生成 字幕.srt 和 口播稿.md（实录版）。
用法: python3 mkdocs.py <项目目录> <meta.json>
meta.json: {"id","title","column","biz_tier","cta","成品","分镜表","src_name","heads":{"开场":"…","B01":"…",...}}"""
import json, os, sys
d, meta = sys.argv[1], json.load(open(sys.argv[2], encoding='utf-8'))
L = json.load(open(os.path.join(d, 'lines.json'), encoding='utf-8'))
sb = json.load(open(os.path.join(d, 'storyboard.json'), encoding='utf-8'))

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'
with open(os.path.join(d, '字幕.srt'), 'w', encoding='utf-8') as f:
    for i, (a, b, t) in enumerate(L, 1):
        f.write(f'{i}\n{ts(a)} --> {ts(b)}\n{t}\n\n')

heads = meta.get('heads', {})
badges = sorted([e for e in sb['elements'] if e['type'] == 'badge'], key=lambda e: e['at'])
secs = [(-1, heads.get('开场', '开场'))]
for e in badges:
    num, txt = e['props']['num'], e['props']['text']
    h = heads.get(e['id'])
    if h is None:
        h = '结尾' if not num.isdigit() else f'{num} {txt}'
    st = e['at'] - 0.35
    if h == '结尾':   # 「关注我」一句归到结尾
        st = min([a for a, b, t in L if t.startswith('关注') and st - 4 < a < st] or [st])
    secs.append((st, h))
out = ['---', f"id: {meta['id']}", f"title: {meta['title']}", f"column: {meta['column']}", f"biz_tier: {meta['biz_tier']}",
       f"状态: recorded（实录版，按「{meta['src_name']}」听写校正）", f"cta: {meta['cta']}", f"成片: {meta['成品']}",
       f"分镜表: {meta['分镜表']}", '---', '', '# 口播稿（实录版）']
si = -1
for a, b, t in L:
    while si + 1 < len(secs) and a >= secs[si + 1][0]:
        si += 1; out += ['', f'## {secs[si][1]}']
    out.append(t)
open(os.path.join(d, '口播稿.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('✓ 字幕.srt', len(L), '行；口播稿.md', len(secs), '节')
