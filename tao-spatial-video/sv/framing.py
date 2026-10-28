# 取景检查（v1.4）：拿到原片先量一下「留安全区时，侧边玻璃卡能放多大」。
# 用和合成器完全相同的抠像与人头带（1080 布局坐标第 470–990 行）量人物左右边界，
# 按合成器 adjust_side 的公式预测左右侧卡的缩放，给出能不能「留安全区 + 完整侧卡」的结论和录制建议。
import os, tempfile, statistics
import numpy as np

CARD_W = 460            # 侧卡标准宽度（css 像素）：list_panel / big_card / loop_panel / flow_panel 都是 460，grid_panel 470
DESIGN_S = 0.92         # 侧卡设计缩放（L/R 位默认）
GOOD = 0.68             # ≥0.68：和「有了 WorkBuddy」「WorkBuddy 还是豆包」两条成片的侧卡一样大
OK = 0.55               # 0.55–0.68：偏小，列表最多 4 行；<0.55：太小，会被压到 0.5 倍下限、内侧压到人头后面
BAND = (470, 990)       # 与 comp4k.update_head 相同

def _geom(safe):
    bleed = 0 if safe > 0 else 25
    return bleed, CARD_W - (20 + bleed)

def side_scale(l, r, safe):
    """合成器给左右侧卡留出的最大缩放（未截断）"""
    _, den = _geom(safe)
    return (l - 10 - safe)/max(1.0, den), (1070 - safe - r)/max(1.0, den)

def effective(smax, safe):
    """合成器实际用的缩放：放得下就用设计值，放不下就缩，但不低于下限（低于下限时卡片内侧会压到人后面）"""
    floor = 0.5 if safe > 0 else 0.62
    if smax >= DESIGN_S: return DESIGN_S, False
    return max(floor, smax), smax < floor

def max_width(safe, s=GOOD):
    """要让两侧卡片都达到缩放 s，人头带最宽多少（1080 布局像素）"""
    _, den = _geom(safe)
    return 1080 - 2*(s*den + safe + 10)

def core_lr(band):
    """和 comp4k.update_head_core 相同：只取和头肩连成一体的部分（v1.4.2）"""
    top = band[:band.shape[0]//3]; ct = np.where(top.any(0))[0]
    if len(ct) == 0: ct = np.where(band.any(0))[0]
    if len(ct) == 0: return (None, None)
    c = int(np.median(ct)); L, R = [], []
    for row in band[::4]:
        if not row[c]: continue
        zl = np.where(~row[:c])[0]; zr = np.where(~row[c:])[0]
        L.append(zl.max()+1 if len(zl) else 0); R.append(c+zr.min()-1 if len(zr) else band.shape[1]-1)
    return (float(min(L)), float(max(R))) if L else (None, None)

def measure(mov, hdr, dur, n=6):
    from . import comp4k, preview
    import cv2
    ts = [dur*(0.08 + 0.84*i/max(1, n-1)) for i in range(n)]
    out = []
    with tempfile.TemporaryDirectory() as d:
        for t in ts:
            f = os.path.join(d, f'{t:.2f}.jpg'); preview.grab(mov, t, f, hdr)
            im = cv2.imread(f); m = comp4k.Matte()
            for _ in range(3): a = m(im)
            band = a[BAND[0]:BAND[1]] > 0.5; cols = np.where(band.any(0))[0]
            cl, cr = core_lr(band)
            rows = np.where((a > 0.5).any(1))[0]
            if len(cols) == 0: continue
            out.append(dict(t=round(t, 2), l=float(cols.min()), r=float(cols.max()), cl=cl, cr=cr, top=float(rows.min()) if len(rows) else None))
    return out

def report(ms, safe):
    if not ms:
        return '✗ 没量到人物（抠像没找到人），请人工看一下原片', 'fail'
    kl, kr = ('cl', 'cr') if safe > 0 and all(m.get('cl') is not None for m in ms) else ('l', 'r')   # 留安全区时合成器只量头肩主体
    l = statistics.median(m[kl] for m in ms); r = statistics.median(m[kr] for m in ms)
    tops = [m['top'] for m in ms if m['top'] is not None]; top = statistics.median(tops) if tops else None
    w = r - l; c = (l + r)/2 - 540
    sl, sr = side_scale(l, r, safe); el, ol = effective(sl, safe); er, orr = effective(sr, safe)
    worst = min(0.0 if ol else el, 0.0 if orr else er)    # 放不下（压到人后面）按 0 算
    need = max_width(safe)
    L = []
    L.append(f'安全区 safe_x={safe:g}（左右各 {safe/10.8:.1f}%）  抽 {len(ms)} 帧')
    L.append(f'人物头肩宽度 {w:.0f}/1080 = {w/10.8:.0f}% 画面宽   中心偏{"右" if c > 0 else "左"} {abs(c):.0f} 像素'
             + (f'   头顶在画面 {top/19.2:.0f}% 高度' if top is not None else ''))
    L.append(f'侧卡缩放预测：左 {el:.2f} 倍{"（放不下，内侧压到人后面）" if ol else ""}   右 {er:.2f} 倍{"（放不下，内侧压到人后面）" if orr else ""}'
             f'   （目标 ≥{GOOD}，和「有了 WorkBuddy」那两条一样大）')
    if worst >= GOOD and abs(c) <= 40:
        L.append('✓ 取景合格：' + ('留安全区也能' if safe > 0 else '侧卡能') + '放完整的列表卡、循环图、宫格（和参考成片一样大）')
        verdict = 'good'
    elif worst >= OK:
        L.append('⚠ 偏近：卡片会比参考成片小一些。列表卡最多 4 行、每行 ≤8 字；图解卡照常用')
        verdict = 'tight'
    else:
        L.append('✗ 太近：留安全区时侧卡会被压到 0.5 倍左右，小字在手机上看不清。先问用户：①这条不留安全区（safe_x: 0）'
                 '②留安全区、侧卡只放大字卡和短列表')
        verdict = 'close'
    if worst < GOOD or abs(c) > 40:
        tip = []
        if w > need: tip.append(f'头肩宽度降到 ≤{need:.0f} 像素（≈{need/10.8:.0f}% 画面宽），大约离镜头再远 {w/need:.1f} 倍')
        if abs(c) > 20: tip.append(f'人往{"左" if c > 0 else "右"}挪，站到画面正中（现在偏 {abs(c)/10.8:.0f}%）')
        if tip: L.append('录制建议：' + '；'.join(tip) + '；镜头高度不变，头顶保持在画面 25%–40% 高度')
    return '\n'.join(L), verdict
