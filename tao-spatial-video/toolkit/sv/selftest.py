# 基准回归测试：拿第一条成片《WorkBuddy 还是豆包工作》当尺子
#   1 合成器源码指纹    —— 渲染核心和出片时逐行一致
#   2 组件 HTML         —— 56 个素材的标记和出片时一致
#   3 时间轴            —— 分镜表翻译出的时间轴 == 从原始代码直接导出的 timeline.json（元素/音效/扫光/光晕逐项）
#   4 素材/字幕像素     —— (--pixels) 重新渲染，和出片时的 PNG 逐像素比对（哈希）
#   5 成片逐帧          —— (--frames) 在有原片的电脑上重渲一段，和基准成片逐帧比对
import os, sys, json, hashlib, inspect, tempfile, subprocess, shutil
import numpy as np
from . import storyboard as SB

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD = os.path.join(KIT, 'golden', 'workbuddy')
CORE = ['bgr', 'sprite', 'sprite_at', 'ease_out_back', 'ease_out_cubic', 'ease_io', 'clamp', 'lerp', 'project', 'warp',
        'fast_blur', 'state', 'update_head', 'adjust_side', 'alpha_region', 'draw', 'over_png', 'streak', 'render_frame', 'render_chunk']

def h(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode('utf-8')).hexdigest()

def px_hash(path):
    from PIL import Image
    a = np.ascontiguousarray(np.array(Image.open(path).convert('RGBA')))
    return h(a.tobytes() + str(a.shape).encode())

def fingerprint():
    from . import comp4k
    fp = {n: h(inspect.getsource(getattr(comp4k, n))) for n in CORE}
    fp['Matte.__call__'] = h(inspect.getsource(comp4k.Matte.__call__))
    fp['CONST'] = h(repr((comp4k.W, comp4k.H, comp4k.FPS, comp4k.K, comp4k.SPR, comp4k.TONEMAP,
                          comp4k.CYAN.tolist(), comp4k.VIOLET.tolist(), comp4k.INDIGO.tolist())))
    return fp

def expected():
    with open(os.path.join(GOLD, 'expect.json'), encoding='utf-8') as f:
        return json.load(f)

class R:
    def __init__(self): self.fail = 0
    def ok(self, cond, msg, detail=''):
        print(('  ✓ ' if cond else '  ✗ ') + msg + (f'  {detail}' if detail else ''), flush=True)
        if not cond: self.fail += 1

def run(pixels=False, frames=None, ref=None):
    X = expected(); r = R()
    sb = SB.read(os.path.join(GOLD, 'storyboard.json'))
    print('1 合成器源码指纹')
    try:
        fp = fingerprint(); bad = [k for k in X['compositor'] if fp.get(k) != X['compositor'][k]]
        r.ok(not bad, f'{len(X["compositor"])-len(bad)}/{len(X["compositor"])} 个函数与基准一致', f'不一致：{bad}' if bad else '')
    except ImportError as ex:
        print('  - 跳过（缺依赖：', ex, '）')
    print('2 组件 HTML')
    items = SB.sprite_items(sb); bad = [k for k, v in items.items() if h(v) != X['html'].get(k)]
    r.ok(not bad and len(items) == len(X['html']), f'{len(items)-len(bad)}/{len(X["html"])} 个素材标记一致', f'不一致：{bad}' if bad else '')
    print('3 分镜表 → 时间轴')
    plan = SB.load(sb, sizes={k: tuple(v) for k, v in X['sizes'].items()})
    got = json.loads(json.dumps(SB.dump(plan)))
    with open(os.path.join(GOLD, 'timeline.json'), encoding='utf-8') as f:
        want = json.load(f)
    ne = sum(a != b for a, b in zip(got['els'], want['els'])) + abs(len(got['els']) - len(want['els']))
    r.ok(ne == 0, f'元素 {len(got["els"])}/{len(want["els"])} 逐项一致' if ne == 0 else f'{ne} 个元素不一致')
    r.ok(got['sfx'] == want['sfx'], f'音效 {len(got["sfx"])} 个逐项一致' if got['sfx'] == want['sfx'] else '音效表不一致')
    r.ok(got['streaks'] == want['streaks'] and got['boost'] == want['boost'], '扫光 / 光晕逐帧一致')
    r.ok(got['meta'] == want['meta'], f'总帧数 {got["meta"]["total_frames"]}、片长 {got["meta"]["total_sec"]:.3f}s')
    if pixels:
        print('4 素材 / 字幕逐像素')
        tmp = tempfile.mkdtemp(prefix='sv_selftest_')
        try:
            try:
                import playwright  # noqa
                from . import sprites as SP
                SP.render(items, os.path.join(tmp, 'sp3'), check=False)
                bad = [k for k in items if px_hash(os.path.join(tmp, 'sp3', k + '.png')) != X['sprite_px'][k]]
                r.ok(not bad, f'素材 {len(items)-len(bad)}/{len(items)} 张逐像素一致', f'不一致：{bad}' if bad else '')
            except ImportError:
                print('  - 素材跳过（这台机器没有 Playwright/Chromium）')
            try:
                from . import subs as SU
                with open(os.path.join(GOLD, 'lines.json'), encoding='utf-8') as f:
                    lines = json.load(f)
                subs, _ = SU.make(lines, os.path.join(tmp, 'sub4k'), SB.total_sec(sb))
                bad = [i for i, s in enumerate(subs) if px_hash(os.path.join(tmp, 'sub4k', s[2])) != X['subs_px'][i]]
                r.ok(not bad and len(subs) == len(X['subs_px']), f'字幕 {len(subs)-len(bad)}/{len(X["subs_px"])} 张逐像素一致', f'不一致：第 {bad} 行' if bad else '')
                r.ok([s[:2] for s in subs] == X['subs_times'], '字幕时间一致')
            except ImportError:
                print('  - 字幕跳过（这台机器没有 Pillow）')
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if frames:
        print('5 成片逐帧（重渲一段，和基准成片比）')
        r.ok(*frame_test(sb, frames[0], frames[1], ref))
    print('通过' if r.fail == 0 else f'有 {r.fail} 项不一致')
    return 1 if r.fail else 0

def _md5s(cmd):
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    return [l.split(',')[-1].strip() for l in out.splitlines() if l and not l.startswith('#')]

def _ref_frames(ref, i0, i1):
    """基准可以是分段目录（c_0000.mp4 这类文件）或整条成片"""
    if os.path.isdir(ref):
        for name in (f'c_{i0:05d}.mp4', f'c_{i0:04d}.mp4'):
            if os.path.exists(os.path.join(ref, name)):
                return ['-i', os.path.join(ref, name)]
        raise FileNotFoundError(f'{ref} 里没有从第 {i0} 帧开始的分段')
    return ['-ss', f'{(i0-0.25)/60:.6f}', '-i', ref]

def frame_test(sb, i0, i1, ref):
    """需要：原片（分镜表 source.path，或环境变量 SV_SOURCE）、golden 的 build/sp3 与 build/sub4k、基准（--ref 成片或分段目录）。
    这一段还没渲染就先渲染（约 150 秒）；已渲染过就只比对。"""
    if not ref or not os.path.exists(ref):
        return False, '需要 --ref（基准成片，或基准分段所在目录）'
    bounds = sb['render']['chunks']
    if i0 not in bounds or i1 not in bounds:
        return False, f'起止帧要用基准的分段边界 {bounds}（抠像预热从段首开始，边界不同结果会有细微差别）'
    build = os.path.expanduser(os.environ.get('SV_BUILD') or os.path.join(GOLD, 'build'))
    new = os.path.join(build, 'chunks', f'c_{i0:05d}.mp4')
    if not os.path.exists(new):
        r = subprocess.run([sys.executable, os.path.join(KIT, 'make_video.py'), 'render', os.path.join(GOLD, 'storyboard.json'), '--range', str(i0), str(i1)])
        if r.returncode:
            return False, '渲染失败'
    rf = _ref_frames(ref, i0, i1)
    a = _md5s(['ffmpeg', '-v', 'error', '-i', new, '-map', '0:v', '-f', 'framemd5', '-'])
    b = _md5s(['ffmpeg', '-v', 'error'] + rf + ['-map', '0:v', '-frames:v', str(i1-i0), '-f', 'framemd5', '-'])
    same = sum(x == y for x, y in zip(a, b))
    if same == len(a) == len(b) == i1-i0:
        return True, f'第 {i0}–{i1} 帧：{same}/{i1-i0} 帧与基准逐像素一致'
    p = subprocess.run(['ffmpeg', '-v', 'info', '-i', new] + rf + ['-filter_complex', '[0:v][1:v]psnr', '-frames:v', str(i1-i0), '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    psnr = [l for l in p.splitlines() if 'PSNR' in l]
    return False, f'第 {i0}–{i1} 帧：{same}/{i1-i0} 帧逐像素一致（新 {len(a)} 帧 / 基准 {len(b)} 帧）；{psnr[-1].split("PSNR")[-1].strip() if psnr else ""}'
