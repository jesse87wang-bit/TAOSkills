# 分镜表校验：结构、文字红线、时间、同屏数量、版式禁区
import os, json, inspect, re
from . import storyboard as SB
from .components import COMPONENTS, ICONS

SCHEMA = 'tao-spatial-video/storyboard@1.1'
# 平台红线（引导评论/私信）+ 账号宪法（不用这些词称呼观众）——出现在屏幕文字或字幕里都算错
FORBIDDEN = [(re.compile(r'评论区'), '平台不允许引导评论（字幕里口播说到「评论区」也要删掉这三个字）'),
             (re.compile(r'私信'), '平台不允许引导私信'),
             (re.compile(r'扣\s*[「“"\'0-9一二三四五六七八九十]'), '平台不允许「扣xx」引导'),
             (re.compile(r'老板|高管|管理者'), '账号宪法：不用「老板/高管/管理者」称呼观众，换个说法')]
TEXT_KINDS = ('text', 'label')

def _texts(v):
    if isinstance(v, str):
        yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from _texts(x)
    elif isinstance(v, (list, tuple)):
        for x in v: yield from _texts(x)

def _glyphs(typ, props):
    for k in ('glyph', 'sub_icon'):
        if k in props: yield props[k]
    for k in ('rows', 'dims'):
        for r in props.get(k, []): yield r[0]

def _cjk_len(s):
    return sum(1 for c in s if '一' <= c <= '鿿') + sum(1 for c in s if c.isascii() and c.strip())/2

def check(path, sprite_dir=None):
    E, W = [], []
    try:
        sb = SB.read(path)
    except Exception as ex:
        return [f'读不了分镜表：{ex}'], []
    if sb.get('schema') != SCHEMA:
        E.append(f'schema 应为 "{SCHEMA}"')
    src = sb.get('source', {})
    if not isinstance(src.get('n_src'), int) or src.get('n_src', 0) <= 0:
        E.append('source.n_src 必须是正整数（probe 给出的 60fps 帧数）')
    if 'path' not in src:
        E.append('source.path 缺失')
    elif not os.path.exists(SB.src_path(sb)):
        W.append(f'找不到原片 {SB.src_path(sb)}（在没有原片的机器上做素材可以忽略）')
    pal = sb.get('palette', {})
    for k in ('A', 'B'):
        if k not in pal or len(pal[k]) != 3:
            E.append(f'palette.{k} 需要 3 个颜色')
    total = SB.total_sec(sb) if not any('n_src' in e for e in E) else 1e9

    # 字幕
    lp = SB.lines_path(sb); lines = []
    if not os.path.exists(lp):
        E.append(f'找不到字幕 {lp}')
    else:
        with open(lp, encoding='utf-8') as f:
            lines = json.load(f)
        prev = -1
        for i, l in enumerate(lines):
            if len(l) != 3 or not l[2]:
                E.append(f'字幕第 {i+1} 行格式不对'); continue
            a, b, t = l
            if not a < b: E.append(f'字幕第 {i+1} 行 开始≥结束')
            if a < prev - 1e-6: E.append(f'字幕第 {i+1} 行 时间倒退')
            prev = a
            for rx, why in FORBIDDEN:
                if rx.search(t): E.append(f'字幕第 {i+1} 行「{t}」：{why}')

    # 元素
    kws = SB.Keywords(sb); ids = {}; rows = sb.get('rows', {}); spans = []
    for n, e in enumerate(sb.get('elements', [])):
        eid = e.get('id', f'#{n}'); tag = f'元素 {eid}'
        if 'id' not in e: E.append(f'{tag}：缺 id'); continue
        if eid in ids: E.append(f'{tag}：id 重复')
        ids[eid] = e
        if 'use' in e:
            if e['use'] not in ids or 'type' not in ids[e['use']]:
                E.append(f'{tag}：use 必须引用前面出现过、带 type 的元素'); continue
            typ = ids[e['use']]['type']
        else:
            typ = e.get('type')
            if typ not in COMPONENTS:
                E.append(f'{tag}：未知组件 {typ!r}'); continue
            fn = COMPONENTS[typ][0]; sig = inspect.signature(fn); props = e.get('props', {})
            params = list(sig.parameters)[1:]
            for p in params:
                if sig.parameters[p].default is inspect.Parameter.empty and p not in props:
                    E.append(f'{tag}（{typ}）：缺 props.{p}')
            for p in props:
                if p not in params: E.append(f'{tag}（{typ}）：不认识的 props.{p}')
            for c in [props.get('color')] + [x.get('color') for x in props.get('tasks', [])]:
                if c is not None and c not in pal: E.append(f'{tag}：color 只能是 palette 里的 {list(pal)}')
            for g in _glyphs(typ, props):
                if g not in ICONS: E.append(f'{tag}：没有图标 {g!r}（可选：{" ".join(ICONS)}）')
            for t in _texts(props):
                for rx, why in FORBIDDEN:
                    if rx.search(t): E.append(f'{tag}「{t}」：{why}')
            if typ == 'list_panel' and _cjk_len(props.get('title', '')) > 7 and props.get('tsize', 52) >= 52:
                W.append(f'{tag}：标题超过 7 个字，可能溢出（调小 tsize，或看 sprites 的溢出检查）')
            if typ == 'big_card' and _cjk_len(props.get('big', '')) > 4 and props.get('bsize', 98) >= 98:
                W.append(f'{tag}：大字超过 4 个字，可能溢出（调小 bsize）')
        kind = COMPONENTS[typ][1]
        slot = e.get('slot')
        if slot not in SB.SLOTS:
            E.append(f'{tag}：slot 只能是 {SB.SLOTS}'); continue
        st = e.get('set', {})
        if slot == 'custom':
            for k in ('layer', 'x', 'y', 's'):
                if k not in st: E.append(f'{tag}：slot=custom 时 set 里必须写 {k}')
        if 'row' in e and (slot != 'F' or e['row'] not in rows):
            E.append(f'{tag}：row 只能用于 slot=F，且要在 rows 里定义')
        try:
            tin = SB.when(e.get('at'), kws, eid+'.at'); tout = SB.when(e.get('out'), kws, eid+'.out')
        except SB.StoryboardError as ex:
            E.append(f'{tag}：{ex}'); continue
        if tin is None: E.append(f'{tag}：缺 at'); continue
        if not 0 <= tin < total: E.append(f'{tag}：at={tin} 超出片长 {total:.2f}s')
        if tout is not None:
            if tout <= tin + 0.3: E.append(f'{tag}：out 必须晚于 at 至少 0.3 秒')
            elif tout - tin < 0.6: W.append(f'{tag}：只停留 {tout-tin:.2f} 秒，观众可能看不清')
            if tout > total: E.append(f'{tag}：out 超出片长')
        for k in ('wipe_from',):
            if k in st and st[k] < tin: E.append(f'{tag}：{k} 早于出现时间')
        ov = e.get('sfx', {})
        if isinstance(ov, str): ov = {'name': ov}
        if ov:
            if ov.get('name', 'deng') not in SB.SFX_NAMES: E.append(f'{tag}：音效只能是 {SB.SFX_NAMES}')
            if not -1 <= ov.get('pan', 0) <= 1: E.append(f'{tag}：pan 范围 -1~1')
            if not 0 < ov.get('gain', 1) <= 1.5: E.append(f'{tag}：gain 范围 0~1.5')
        for tk in e.get('ticks', []):
            try: SB.when(tk, kws, eid+'.ticks')
            except SB.StoryboardError as ex: E.append(f'{tag}：{ex}')
        layer = st.get('layer', 'front' if slot in ('F', 'TOP') else 'back')
        x = st.get('x', {'L': SB.LX, 'R': SB.RX}.get(slot, 540)); y = st.get('y', {'TOP': 330, 'L': SB.PY, 'R': SB.PY}.get(slot, 1195))
        if 'row' in e: y = rows[e['row']]['y']
        if layer == 'front' and slot != 'TOP' and not 220 <= y <= 1500:
            W.append(f'{tag}：y={y} 在平台 UI 区（顶部 0–220 / 底部 1500 以下）')
        side = slot if slot in ('L', 'R') else ('L' if x < 540 else 'R')
        spans.append((eid, kind, slot, layer, side, tin, tout if tout is not None else total))
    for t, name, pan, gain in sb.get('sfx', []):
        if name not in SB.SFX_NAMES: E.append(f'sfx {t}：音效只能是 {SB.SFX_NAMES}')

    # 同屏数量：同侧玻璃卡 ≤1、胸前文字 ≤3、顶部章节标 ≤1
    t = 0.0
    seen = set()
    while t < total:
        on = [s for s in spans if s[5] <= t < s[6]]
        for side in ('L', 'R'):
            p = [s[0] for s in on if s[1] == 'panel' and s[3] == 'back' and s[4] == side]
            if len(p) > 1 and tuple(p) not in seen:
                seen.add(tuple(p)); E.append(f'{t:.2f}s：{"左" if side == "L" else "右"}侧同时有 {len(p)} 张卡 {p}，先让前一张 out')
        f = [s[0] for s in on if s[1] in TEXT_KINDS and s[3] == 'front']
        if len(f) > 3 and tuple(f) not in seen:
            seen.add(tuple(f)); W.append(f'{t:.2f}s：胸前同时有 {len(f)} 行字 {f}，太挤')
        b = [s[0] for s in on if s[2] == 'TOP']
        if len(b) > 1 and tuple(b) not in seen:
            seen.add(tuple(b)); E.append(f'{t:.2f}s：同时有两个章节标 {b}')
        t = round(t + 0.05, 2)

    # 素材溢出检查结果（sprites 步骤写的）
    if sprite_dir and os.path.exists(os.path.join(sprite_dir, 'overflow.json')):
        with open(os.path.join(sprite_dir, 'overflow.json'), encoding='utf-8') as f:
            for k, v in json.load(f).items():
                E.append(f'素材 {k} 文字溢出：{v}（调小 tsize/bsize/size 或缩短文字，再跑 sprites）')
    return E, W
