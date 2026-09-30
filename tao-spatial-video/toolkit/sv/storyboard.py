# 分镜表（storyboard.json）→ 合成器时间轴 + 音效表
# 规则都写死在这里：同一份分镜表在任何环境里翻译出来的时间轴都一样。
import os, json, math, re, struct
import numpy as np

FPS = 60
SPR = 3.0            # 素材 PNG 像素 / css 像素
LX, RX, PY = 222, 890, 760
NAMED_GLOW = {'cyan': '#22D3EE', 'violet': '#8B5CF6', 'indigo': '#6366F1'}
SLOTS = ('L', 'R', 'F', 'TOP', 'custom')

# 默认音效：组件类型 → (音效, 声像规则, 增益, 相对出现时刻的偏移)
#   声像规则 side：左侧 -0.5 / 右侧 +0.5；side4：离中线 100 以上 ±0.4，否则 0；0：居中
SFX_DEFAULT = {
    'product_panel': ('deng', 'side', 1, -0.02), 'list_panel': ('deng', 'side', 1, -0.02),
    'big_card': ('deng', 'side', 1, -0.02), 'small_card': ('deng', 'side', 1, -0.02),
    'progress_card': ('deng', 'side', 1, -0.02), 'rating_panel': ('deng', 'side', 1, -0.02),
    'laptop': ('deng', 'side', 1, -0.02), 'number_tile': ('deng', 'side', 0.85, -0.02),
    'badge': ('xp', 0, 0.9, -0.02),
    'glow_text': ('tone', 0, 1, -0.02), 'dim_text': ('tone', 0, 1, -0.02), 'chapter_title': ('tone', 0, 1, -0.02),
    'verdict': ('tone', 0, 1, -0.02), 'judge': ('tone', 0, 1, -0.02), 'chat_bar': ('tone', 0, 1, -0.02),
    'pill': ('ui', 0, 0.9, -0.02), 'warn_chip': ('ui', 0, 0.9, -0.02),
    'vs_text': ('app', 0, 0.8, -0.02),
    'float_icon': ('app', 'side4', 0.7, -0.02), 'icon_tile': ('app', 'side4', 0.7, -0.02),
    'result_tile': ('app', 'side4', 0.7, -0.02), 'chip': ('app', 'side4', 0.7, -0.02),
    'strike': ('ding3', 0, 0.9, 0.0), 'stamp': ('ding3', 0, 1, -0.02),
}
TICK = ('app', 0.5)          # 列表卡逐行亮起的音效和增益
SFX_NAMES = ('deng', 'ding3', 'app', 'tone', 'xp', 'ui')

class StoryboardError(ValueError):
    pass

def bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16)], np.float32)/255

def png_size(path):
    with open(path, 'rb') as f:
        head = f.read(24)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise StoryboardError(f'不是 PNG：{path}')
    return struct.unpack('>II', head[16:24])

def read(path):
    with open(path, encoding='utf-8') as f:
        sb = json.load(f)
    sb['_dir'] = os.path.dirname(os.path.abspath(path))
    return sb

def src_path(sb):
    # SV_SOURCE：临时指定原片位置（例如回归测试时原片不在分镜表写的路径）
    p = os.path.expanduser(os.environ.get('SV_SOURCE') or sb['source']['path'])
    return p if os.path.isabs(p) else os.path.join(sb['_dir'], p)

def lines_path(sb):
    return os.path.join(sb['_dir'], sb.get('lines', 'lines.json'))

def total_frames(sb):
    # 片尾定格：hold_frames（精确帧数）优先，否则 hold 秒数 ×60
    hf = sb.get('hold_frames')
    return sb['source']['n_src'] + (int(hf) if hf is not None else int(round(sb.get('hold', 1.5)*FPS)))

def total_sec(sb):
    return total_frames(sb)/FPS

# ---------------------------------------------------------------- 关键词卡点
class Keywords:
    _P = re.compile(r"[\s，。？、；！：“”,?!.]")
    def __init__(self, sb):
        self.chars = None
        p = os.path.join(sb['_dir'], sb.get('lines_chars', os.path.splitext(sb.get('lines', 'lines.json'))[0] + '_chars.json'))
        if os.path.exists(p):
            with open(p, encoding='utf-8') as f:
                d = json.load(f)
            self.chars, self.times = d['chars'], d['times']
    def find(self, kw, n=1):
        if self.chars is None:
            raise StoryboardError(f'用了关键词卡点「{kw}」，但没有 lines_chars.json（align 步骤会生成）')
        k = ''.join(c for c in kw.lower() if not self._P.match(c)); i = -1
        for _ in range(n):
            i = self.chars.find(k, i+1)
            if i < 0:
                raise StoryboardError(f'口播里找不到第 {n} 次出现的关键词「{kw}」')
        return self.times[i]

def when(v, kws, what):
    """时间字段：数字（秒）或 {"kw": "关键词", "n": 第几次, "offset": 秒}"""
    if v is None or isinstance(v, (int, float)):
        return v
    if isinstance(v, dict) and 'kw' in v:
        return round(kws.find(v['kw'], v.get('n', 1)) + v.get('offset', 0.0), 3)
    raise StoryboardError(f'{what} 的时间写法不对：{v!r}')

# ---------------------------------------------------------------- 元素 → 合成器参数
DEFAULT_GLOW = {'L': 'cyan', 'R': 'violet', 'TOP': 'violet'}

def _glow(v, sb):
    if v is None or isinstance(v, np.ndarray):
        return v
    g = {**DEFAULT_GLOW, **sb.get('glow', {})}
    v = g.get(v, v)
    return bgr(NAMED_GLOW.get(v, v))

def _tup(v):
    return tuple(v) if isinstance(v, list) else v

def _finish(d, sb):
    for k in ('from', 'to'):
        if k in d:
            d[k] = _tup(d[k])
    if 'moves' in d:
        d['moves'] = [(m[0], m[1], dict(m[2])) for m in d['moves']]
    if 'glow' in d:
        d['glow'] = _glow(d['glow'], sb)
    if d.get('out', 0) is None:
        del d['out']
    return d

def element(e, tin, tout, sb, row_pos=None):
    slot = e['slot']; sp = e.get('use', e['id']); kw = dict(e.get('set', {}))
    if slot == 'L':
        d = dict(sp=sp, layer='back', x=LX, y=PY, s=0.92, ry=26, dur=.65, glow='L', gk=.9, glass=True, float=7, ph=0.3, out=tout, to=(460, 780))
        d['in'] = tin; d['from'] = (460, 790, 0.45, 55); d.update(kw)
    elif slot == 'R':
        d = dict(sp=sp, layer='back', x=RX, y=PY, s=0.92, ry=-26, dur=.65, glow='R', gk=.9, glass=True, float=7, ph=1.3, out=tout, to=(640, 780))
        d['in'] = tin; d['from'] = (640, 790, 0.45, -55); d.update(kw)
    elif slot == 'F':
        x, y, s = kw.pop('x', 540), kw.pop('y', 1195), kw.pop('s', 1.0)
        if row_pos is not None:
            x, y, s = row_pos
        pop = kw.pop('pop', 1.5)
        d = dict(sp=sp, layer='front', x=x, y=y, s=s, dur=.4, back=1.2, out=tout)
        d['in'] = tin; d['from'] = (x, y, s*pop, 0); d.update(kw)
    elif slot == 'TOP':
        d = dict(sp=sp, layer='front', x=540, y=330, s=1.15, dur=.45, glass=True, glow='TOP', gk=.6, out=tout)
        d['in'] = tin; d['from'] = (540, 300, .5, 0); d.update(kw)
    elif slot == 'custom':
        d = dict(sp=sp, **kw); d['in'] = tin; d['out'] = tout
        d.setdefault('layer', 'back')
    else:
        raise StoryboardError(f'{e["id"]}: 未知 slot {slot!r}（可选 {SLOTS}）')
    return _finish(d, sb)

def _rows(sb, els, size_of):
    """row 排版：fit=总宽度（按素材宽度等比缩放）或 s+gap（固定缩放、居中、间距）"""
    pos = {}
    for rname, r in sb.get('rows', {}).items():
        members = [e for e in els if e.get('row') == rname]
        if not members:
            continue
        ws = [size_of(e.get('use', e['id']))[0] for e in members]
        y = r['y']
        if 'fit' in r:
            k = r['fit']/sum(ws); x = (1080-r['fit'])/2
            for e, w in zip(members, ws):
                pos[e['id']] = (x+w*k/2, y, k); x += w*k
        else:
            s, gap = r['s'], r.get('gap', 10)
            tot = sum(ws)*s + gap*(len(ws)-1); x = (1080-tot)/2
            for e, w in zip(members, ws):
                pos[e['id']] = (x+w*s/2, y, s); x += w*s+gap
    return pos

def _pan(rule, d, slot):
    if not isinstance(rule, str):
        return rule
    x = d['x']
    if rule == 'side':
        if slot in ('L', 'R'):
            return -0.5 if slot == 'L' else 0.5
        return -0.5 if x < 540 else 0.5
    if rule == 'side4':
        return 0 if abs(x-540) < 100 else (-0.4 if x < 540 else 0.4)
    raise StoryboardError(f'未知声像规则 {rule}')

def type_of(e, by_id):
    return e['type'] if 'type' in e else by_id[e['use']]['type']

def load(path_or_sb, sprite_dir=None, sizes=None, subs_dir=None):
    """返回 dict(els, subs, fx, sub_index, sfx, meta)——els/fx/subs 直接交给 comp4k.render_chunk"""
    sb = read(path_or_sb) if isinstance(path_or_sb, str) else path_or_sb
    els = sb['elements']; by_id = {e['id']: e for e in els}; kws = Keywords(sb)
    def size_of(sp):
        if sizes is not None:
            w, h = sizes[sp]
        else:
            w, h = png_size(os.path.join(sprite_dir, sp + '.png'))
        return w/SPR, h/SPR
    rows = _rows(sb, els, size_of)
    E, SFX = [], []
    for e in els:
        tin = when(e['at'], kws, e['id']+'.at'); tout = when(e.get('out'), kws, e['id']+'.out')
        d = element(e, tin, tout, sb, rows.get(e['id']))
        E.append(d)
        typ = type_of(e, by_id)
        if 'sfx' in e and e['sfx'] is None:
            pass
        else:
            name, rule, gain, dt = SFX_DEFAULT[typ]
            ov = e.get('sfx') or {}
            if isinstance(ov, str):
                ov = {'name': ov}
            pan = ov['pan'] if 'pan' in ov else _pan(rule, d, e['slot'])
            SFX.append((round(tin + ov.get('dt', dt), 3), ov.get('name', name), pan, ov.get('gain', gain)))
        for tk in e.get('ticks', []):
            SFX.append((round(when(tk, kws, e['id']+'.ticks'), 3), TICK[0], _pan('side', d, e['slot']), TICK[1]))
    for t, name, pan, gain in sb.get('sfx', []):
        SFX.append((round(when(t, kws, 'sfx'), 3), name, pan, gain))
    SFX.sort(key=lambda x: x[0])
    boosts = [tuple(b) for b in sb.get('boosts', [])]; pulse = sb.get('pulse_from')
    def boost(t):
        b = 0.
        for (t0, amp) in boosts:
            if t0 <= t < t0+.7: b += amp*(1-(t-t0)/.7)
        if pulse is not None and t >= pulse: b += 0.25+0.25*math.sin((t-pulse)*4)
        return b
    fx = dict(boost=boost, streaks=[tuple(s) for s in sb.get('streaks', [])])
    subs = []
    if subs_dir and os.path.exists(os.path.join(subs_dir, 'subs.json')):
        with open(os.path.join(subs_dir, 'subs.json'), encoding='utf-8') as f:
            subs = [tuple(s) for s in json.load(f)]
    meta = dict(mov=src_path(sb), hdr=sb['source'].get('hdr', True), n_src=sb['source']['n_src'],
                hold=sb.get('hold', 1.5), total_frames=total_frames(sb), total_sec=total_sec(sb), title=sb.get('title', ''))
    return dict(els=E, subs=subs, fx=fx, sub_index={s[2]: s[2] for s in subs}, sfx=SFX, meta=meta)

def dump(plan):
    """时间轴的规范化 JSON（回归测试用：和 golden/*/timeline.json 逐项比对）"""
    def conv(v):
        if isinstance(v, np.ndarray): return [float(x) for x in v]
        if isinstance(v, (list, tuple)): return [conv(x) for x in v]
        if isinstance(v, dict): return {k: conv(x) for k, x in sorted(v.items())}
        return v
    m = plan['meta']
    return {'els': [conv(e) for e in plan['els']], 'sfx': [list(s) for s in plan['sfx']],
            'streaks': conv(plan['fx']['streaks']),
            'boost': [round(plan['fx']['boost'](i/FPS), 9) for i in range(m['total_frames'])],
            'meta': {'n_src': m['n_src'], 'total_frames': m['total_frames'], 'total_sec': m['total_sec'], 'hdr': m['hdr']}}

def sprite_items(sb, only=None):
    """需要渲染的素材：{素材名: html}（use 引用的元素不重复渲染）"""
    from .components import build
    pal = sb.get('palette'); out = {}
    for e in sb['elements']:
        if 'type' not in e or (only and e['id'] not in only):
            continue
        try:
            out[e['id']] = build(e, pal)
        except Exception as ex:
            raise StoryboardError(f'素材 {e["id"]}（{e["type"]}）生成失败：{type(ex).__name__} {ex}。先跑 validate 看具体问题') from None
    return out
