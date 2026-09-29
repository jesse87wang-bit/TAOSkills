# 把「校对过的字幕行」对齐到识别的逐字时间戳，输出 lines.json [[开始,结束,文字],...]
# 用法: python3 align.py <asr.json> <字幕行.txt（一行一句，≤16字）> <输出lines.json>
import sys, json, difflib, re
d = json.load(open(sys.argv[1])); A=[]; T=[]; SEG=[]
for si, s in enumerate(d):
    for tok, t in zip(s['tokens'], s['ts']):
        for c in tok.strip().lower(): A.append(c); T.append(t); SEG.append(si)
lines = [l.strip() for l in open(sys.argv[2]) if l.strip()]
P = re.compile(r"[\s，。？、；！：“”,?!.]"); B=[]; BL=[]
for li, l in enumerate(lines):
    for c in l:
        if not P.match(c): B.append(c.lower()); BL.append(li)
sm = difflib.SequenceMatcher(None, A, B, autojunk=False); bt=[None]*len(B); bs=[None]*len(B)
for a, b, n in sm.get_matching_blocks():
    for k in range(n): bt[b+k] = T[a+k]; bs[b+k] = SEG[a+k]
idx = [i for i, x in enumerate(bt) if x is not None]
for i in range(len(bt)):
    if bt[i] is None:
        prev = max([j for j in idx if j < i], default=None); nxt = min([j for j in idx if j > i], default=None)
        if prev is None: bt[i], bs[i] = bt[nxt], bs[nxt]
        elif nxt is None: bt[i], bs[i] = bt[prev]+0.15*(i-prev), bs[prev]
        else: bt[i], bs[i] = bt[prev]+(bt[nxt]-bt[prev])*(i-prev)/(nxt-prev), bs[prev]
out = []
for li, l in enumerate(lines):
    ii = [i for i, x in enumerate(BL) if x == li]
    out.append([bt[ii[0]], min(bt[ii[-1]]+0.3, d[bs[ii[-1]]]['end']), l])
for i in range(len(out)-1):
    if out[i][1] > out[i+1][0]-0.02 or out[i+1][0]-out[i][1] < 0.35: out[i][1] = out[i+1][0]-0.02
out[0][0] = max(0, out[0][0]-0.1); out[-1][1] = d[-1]['end']+0.3
json.dump([[round(a,3), round(b,3), t] for a, b, t in out], open(sys.argv[3],'w'), ensure_ascii=False)
for a, b, t in out: print(f"{a:7.2f}-{b:7.2f}  {t}")
# 关键词时间：python3 -c "..." 查某个词第一次出现的秒数，用来卡点
full = "".join(B)
json.dump({'chars': full, 'times': [round(x,3) for x in bt]}, open(sys.argv[3].replace('.json','_chars.json'),'w'), ensure_ascii=False)
