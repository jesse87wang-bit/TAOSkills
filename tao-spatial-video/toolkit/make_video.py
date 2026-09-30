#!/usr/bin/env python3
"""tao-spatial-video 命令行。所有步骤都从同一份分镜表 storyboard.json 出发。

  python3 make_video.py doctor                      检查环境（依赖、字体、模型、音效的版本和哈希）
  python3 make_video.py setup [--fonts] [--models]  下载并校验字体 / 模型
  python3 make_video.py probe  <原片>               看原片参数，给出分镜表 source 字段
  python3 make_video.py asr    <原片> <asr.json>    语音识别（逐字时间戳）
  python3 make_video.py align  <asr.json> <lines.txt> <lines.json>   校对字幕对齐（同时生成 lines_chars.json）
  python3 make_video.py validate <分镜表>           校验分镜表（红线词、同屏数量、时间）
  python3 make_video.py sprites  <分镜表>           渲染玻璃卡素材（Chromium）
  python3 make_video.py subs     <分镜表>           生成 4K 字幕贴图
  python3 make_video.py plan     <分镜表>           把分镜表翻译成时间轴（timeline.json）并列出卡点
  python3 make_video.py grab     <分镜表> 秒 ...       从原片抽 4K 静帧到 build/stills/（色调映射同成片）
  python3 make_video.py preview  <分镜表> 秒[:静帧.jpg] ...   4K 静帧预览（没给静帧就用 build/stills/ 里的，或现抽）
  python3 make_video.py render   <分镜表> [--range 起 止 | --list]  分段渲染（不带参数则逐段全部渲染、断点续跑；--list 列出分段）
  python3 make_video.py mix      <分镜表>           混音
  python3 make_video.py assemble <分镜表>           拼接 + 音轨 → 成片
  python3 make_video.py verify   <分镜表>           核对成片规格（分辨率/帧率/帧数/色彩）
  python3 make_video.py all      <分镜表>           单机一条龙：validate → sprites → subs → render → mix → assemble → verify
  python3 make_video.py selftest [--pixels] [--frames 起 止 --ref 基准]   基准回归测试（和第一条成片逐项/逐像素/逐帧比对）
"""
import argparse, os, sys, json, subprocess, math, re, time, shutil
KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
from sv import storyboard as SB

FPS = 60
DEFAULT_CHUNK = 450          # 每段帧数：在用户电脑上单段约 130–150 秒

def die(msg, code=1):
    print('✗ ' + msg, file=sys.stderr); sys.exit(code)

def P(sb):
    # 中间文件目录：默认分镜表旁的 build/；环境变量 SV_BUILD 可改到别处（例如分段视频不想写进同步盘）
    b = os.path.expanduser(os.environ.get('SV_BUILD') or os.path.join(sb['_dir'], sb.get('build', 'build')))
    return dict(build=b, sprites=os.path.join(b, 'sp3'), subs=os.path.join(b, 'sub4k'), chunks=os.path.join(b, 'chunks'),
                audio=os.path.join(b, 'audio.wav'), timeline=os.path.join(b, 'timeline.json'))

def output_path(sb):
    name = sb.get('output') or '成片_' + re.sub(r'[\\/:*?"<>|\s]+', '', sb.get('title', 'video')) + '_4K60.mp4'
    return name if os.path.isabs(name) else os.path.join(sb['_dir'], name)

def chunk_plan(sb, step=DEFAULT_CHUNK):
    b = sb.get('render', {}).get('chunks')
    T = SB.total_frames(sb)
    if b:
        if b[0] != 0 or b[-1] != T: die(f'render.chunks 必须从 0 开始、到总帧数 {T} 结束')
        return list(zip(b[:-1], b[1:]))
    return [(i, min(i+step, T)) for i in range(0, T, step)]

def chunk_file(sb, i0):
    return os.path.join(P(sb)['chunks'], f'c_{i0:05d}.mp4')

def count_frames(path):
    r = subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v','-show_entries','stream=nb_read_frames','-of','csv=p=0',path],
                       capture_output=True, text=True)
    try: return int(r.stdout.strip().splitlines()[-1])
    except Exception: return -1

def load_plan(sb, need_sprites=True):
    p = P(sb)
    if need_sprites and not os.path.isdir(p['sprites']):
        die(f'没有素材目录 {p["sprites"]}：先跑 sprites（分机器做时把 sp3/ 拷过来）')
    return SB.load(sb, sprite_dir=p['sprites'], subs_dir=p['subs'])

# ------------------------------------------------------------------ 环境
def cmd_doctor(a):
    from sv import assets
    ok = lambda b: '✓' if b else '✗'
    print('Python', sys.version.split()[0])
    pins = {}
    for l in open(os.path.join(KIT, 'requirements.txt')):
        m = re.match(r'([A-Za-z0-9_.-]+)==([^\s#]+)', l.strip())
        if m: pins[m.group(1).lower()] = m.group(2)
    mods = [('numpy','numpy'),('opencv-python-headless','cv2'),('onnxruntime','onnxruntime'),('sherpa-onnx','sherpa_onnx'),
            ('soundfile','soundfile'),('pillow','PIL'),('playwright','playwright')]
    from importlib import metadata
    def ver(dist, mod):
        __import__(mod)
        for d in ([dist, 'opencv-python', 'opencv-contrib-python'] if mod == 'cv2' else [dist]):
            try: return metadata.version(d)
            except metadata.PackageNotFoundError: pass
        return getattr(__import__(mod), '__version__', '?')
    for dist, mod in mods:
        try:
            v = ver(dist, mod); pin = pins.get(dist); same = pin is None or v == pin
            print(f'  {ok(True)} {dist:24s} {v}' + ('' if same else f'   ⚠ 基准是 {pin}（版本不同可能有细微像素差）'))
        except Exception:
            print(f'  {ok(False)} {dist:24s} 未安装')
    ff = shutil.which('ffmpeg')
    if ff:
        v = subprocess.run(['ffmpeg','-version'], capture_output=True, text=True).stdout.split('\n')[0]
        z = ' zscale ' in subprocess.run(['ffmpeg','-hide_banner','-filters'], capture_output=True, text=True).stdout
        print(f'  ✓ ffmpeg  {v}'); print(f'  {ok(z)} ffmpeg zscale（HDR 色调映射必需）')
    else:
        print('  ✗ ffmpeg 未安装')
    for name, m in assets.MANIFEST['fonts'].items():
        pth = os.path.join(assets.FONT_DIR, name); e = os.path.exists(pth)
        print(f'  {ok(e and assets.sha256(pth) == m["sha256"])} 字体 {name}' + ('' if e else '（缺，setup --fonts 下载）'))
    for name in ('rvm.onnx', 'silero_vad.onnx'):
        pth = os.path.join(assets.MODEL_DIR, name); e = os.path.exists(pth)
        print(f'  {ok(e and assets.sha256(pth) == assets.MANIFEST["models"][name]["sha256"])} 模型 {name}' + ('' if e else f'（缺，setup --models 下载到 {assets.MODEL_DIR}）'))
    miss, differ = assets.sfx_check()
    print(f'  {ok(not miss and not differ)} 音效 6 个' + (f'  缺：{miss}' if miss else '') + (f'  和基准不同：{differ}' if differ else ''))
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            b = p.chromium.launch(); print('  ✓ Chromium', b.version); b.close()
    except Exception as ex:
        print('  ✗ Chromium（渲染素材需要）：', str(ex).split('\n')[0][:120])

def cmd_setup(a):
    from sv import assets
    if a.fonts or not (a.fonts or a.models):
        for k, v in assets.fonts().items(): print('✓', k)
    if a.models or not (a.fonts or a.models):
        for k, v in assets.models().items(): print('✓', k, v)

def cmd_probe(a):
    r = subprocess.run(['ffprobe','-v','error','-print_format','json','-show_format','-show_streams',a.video], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout); v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    dur = float(v.get('duration') or d['format']['duration'])
    rot = 0
    for sd in v.get('side_data_list', []):
        if 'rotation' in sd: rot = int(sd['rotation'])
    w, h = int(v['width']), int(v['height'])
    if abs(rot) in (90, 270): w, h = h, w
    hdr = v.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    print(f'分辨率 {w}×{h}  帧率 {v.get("avg_frame_rate")}  时长 {dur:.3f}s  编码 {v.get("codec_name")} {v.get("pix_fmt")}  '
          f'color_transfer={v.get("color_transfer")}  → {"HDR（要色调映射）" if hdr else "SDR"}')
    if (w, h) != (2160, 3840):
        print('⚠ 不是 2160×3840 竖屏 4K：合成器按 4K 竖屏设计，先和用户确认')
    print('分镜表 source 字段：')
    print(json.dumps({'path': a.video, 'hdr': hdr, 'n_src': int(math.floor(dur*FPS))}, ensure_ascii=False))

def cmd_asr(a):
    from sv import speech; speech.asr(a.video, a.out)

def cmd_align(a):
    from sv import speech; speech.align(a.asr, a.lines_txt, a.out)

# ------------------------------------------------------------------ 设计
def cmd_validate(a):
    from sv import validate
    sb = SB.read(a.storyboard)
    E, W = validate.check(a.storyboard, P(sb)['sprites'])
    for w in W: print('⚠', w)
    for e in E: print('✗', e)
    print(f'校验：{len(E)} 个错误，{len(W)} 个提醒')
    if E: sys.exit(1)

def cmd_sprites(a):
    from sv import sprites
    sb = SB.read(a.storyboard); p = P(sb)
    try:
        items = SB.sprite_items(sb, a.only)
    except SB.StoryboardError as ex:
        die(str(ex))
    warn = sprites.render(items, p['sprites'])
    ofile = os.path.join(p['sprites'], 'overflow.json')
    old = json.load(open(ofile, encoding='utf-8')) if os.path.exists(ofile) and a.only else {}
    for k in items: old.pop(k, None)
    old.update(warn)
    json.dump(old, open(ofile, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in warn.items(): print(f'⚠ {k} 可能溢出：{v}')
    print(f'✓ {len(items)} 个素材 → {p["sprites"]}')

def cmd_subs(a):
    from sv import subs
    sb = SB.read(a.storyboard); p = P(sb)
    lines = json.load(open(SB.lines_path(sb), encoding='utf-8'))
    s, too_long = subs.make(lines, p['subs'], SB.total_sec(sb))
    for t in too_long: print('⚠ 字幕太宽，拆成两行：', t)
    print(f'✓ {len(s)} 行字幕 → {p["subs"]}')

def cmd_plan(a):
    sb = SB.read(a.storyboard); p = P(sb); plan = load_plan(sb)
    os.makedirs(p['build'], exist_ok=True)
    json.dump(SB.dump(plan), open(p['timeline'], 'w', encoding='utf-8'), ensure_ascii=False)
    sfx_at = {}
    for t, n, pan, g in plan['sfx']: sfx_at.setdefault(round(t+0.02, 2), []).append(n)
    print(f'{"出现":>7} {"退场":>7}  {"层":5} {"元素":14} 音效')
    for e, src in zip(plan['els'], sb['elements']):
        print(f'{e["in"]:7.2f} {e.get("out", float("nan")):7.2f}  {e["layer"]:5} {src["id"]:14} {",".join(sfx_at.get(round(e["in"],2), []))}')
    m = plan['meta']
    print(f'共 {len(plan["els"])} 个元素、{len(plan["sfx"])} 个音效；成片 {m["total_frames"]} 帧 = {m["total_sec"]:.3f} 秒 → {p["timeline"]}')

def cmd_preview(a):
    from sv import preview, comp4k, assets
    sb = SB.read(a.storyboard); p = P(sb); plan = load_plan(sb)
    comp4k.configure(sprites=p['sprites'], subs=p['subs'], mov=plan['meta']['mov'], hdr=plan['meta']['hdr'], rvm=assets.rvm_path())
    stills = []
    os.makedirs(os.path.join(p['build'], 'stills'), exist_ok=True)
    for arg in a.at:
        t, _, fr = arg.partition(':'); t = float(t)
        if not fr:
            fr = os.path.join(p['build'], 'stills', f'{t:.2f}.jpg')
            if not os.path.exists(fr):
                preview.grab(plan['meta']['mov'], t, fr, plan['meta']['hdr'])
        stills.append((t, fr))
    out = a.out or os.path.join(p['build'], 'preview.jpg')
    for i in range(0, len(stills), 6):
        o = out if len(stills) <= 6 else out.replace('.jpg', f'_{i//6+1}.jpg')
        preview.render(plan, stills[i:i+6], o); print('✓ 预览', o)

def cmd_grab(a):
    from sv import preview
    sb = SB.read(a.storyboard); p = P(sb); d = os.path.join(p['build'], 'stills'); os.makedirs(d, exist_ok=True)
    mov = SB.src_path(sb); hdr = sb['source'].get('hdr', True)
    for t in a.at:
        out = os.path.join(d, f'{t:.2f}.jpg'); preview.grab(mov, t, out, hdr); print('✓', out)

# ------------------------------------------------------------------ 渲染
def cmd_render(a):
    sb = SB.read(a.storyboard)
    if a.range:
        i0, i1 = a.range
        return render_one(sb, i0, i1)
    plan = chunk_plan(sb, a.chunk)
    if a.list:
        for i0, i1 in plan:
            f = chunk_file(sb, i0); done = os.path.exists(f) and count_frames(f) == i1-i0
            print(f'{"✓" if done else "·"} --range {i0} {i1}')
        return
    for i0, i1 in plan:
        f = chunk_file(sb, i0)
        if os.path.exists(f) and count_frames(f) == i1-i0 and not a.force:
            print(f'chunk {i0}-{i1} 已完成，跳过'); continue
        # 每段单独一个进程：和基准一致（人头位置平滑、抠像循环状态都从这一段的预热帧开始）
        r = subprocess.run([sys.executable, os.path.abspath(__file__), 'render', a.storyboard, '--range', str(i0), str(i1)])
        if r.returncode: die(f'chunk {i0}-{i1} 失败')
    print(f'✓ 全部 {len(plan)} 段完成')

def render_one(sb, i0, i1):
    from sv import comp4k, assets
    p = P(sb); plan = load_plan(sb)
    if not os.path.exists(os.path.join(p['subs'], 'subs.json')): die('没有字幕贴图：先跑 subs')
    m = plan['meta']
    if not os.path.exists(m['mov']): die(f'找不到原片 {m["mov"]}')
    comp4k.configure(sprites=p['sprites'], subs=p['subs'], mov=m['mov'], hdr=m['hdr'], rvm=assets.rvm_path())
    os.makedirs(p['chunks'], exist_ok=True); out = chunk_file(sb, i0); t0 = time.time()
    comp4k.render_chunk(plan, out, 0.0, i0, i1, n_src=m['n_src'])
    n = count_frames(out)
    print(f'chunk {i0}-{i1} frames={n} expected={i1-i0} time={time.time()-t0:.0f}s', flush=True)
    if n != i1-i0: die('帧数不对：把这一段拆小重跑')

def cmd_mix(a):
    from sv import mix, assets
    sb = SB.read(a.storyboard); p = P(sb); plan = load_plan(sb)
    miss, differ = assets.sfx_check()
    if differ: print('⚠ 这些音效和基准不同，声音会不一样：', differ)
    n = mix.mix(plan, p['audio'])
    print(f'✓ 混音 {n} 个音效 → {p["audio"]}')

def cmd_assemble(a):
    sb = SB.read(a.storyboard); p = P(sb); out = output_path(sb)
    plan = chunk_plan(sb, a.chunk)
    bad = [(i0, i1) for i0, i1 in plan if count_frames(chunk_file(sb, i0)) != i1-i0]
    if bad: die(f'这些段没渲染完或帧数不对：{bad}')
    if not os.path.exists(p['audio']): die('没有混音：先跑 mix')
    lst = os.path.join(p['chunks'], 'list.txt')
    with open(lst, 'w') as f:
        for i0, _ in plan: f.write(f"file '{os.path.basename(chunk_file(sb, i0))}'\n")
    subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',lst,'-i',p['audio'],'-map','0:v','-map','1:a','-c:v','copy',
                    '-c:a','aac','-b:a','320k','-ar','48000','-movflags','+faststart','-shortest',out], check=True)
    print('✓ 成片', out)

def cmd_verify(a):
    sb = SB.read(a.storyboard); out = a.file or output_path(sb)
    r = subprocess.run(['ffprobe','-v','error','-print_format','json','-show_format','-show_streams',out], capture_output=True, text=True, check=True)
    d = json.loads(r.stdout); v = next(s for s in d['streams'] if s['codec_type'] == 'video')
    au = [s for s in d['streams'] if s['codec_type'] == 'audio']
    n = count_frames(out); want = SB.total_frames(sb)
    checks = [('分辨率 2160×3840', (v['width'], v['height']) == (2160, 3840), f'{v["width"]}×{v["height"]}'),
              ('帧率 60/1', v['r_frame_rate'] == '60/1', v['r_frame_rate']),
              (f'帧数 {want}', n == want, n),
              ('H.264 High', v['codec_name'] == 'h264' and v.get('profile') == 'High', f'{v["codec_name"]} {v.get("profile")}'),
              ('bt709', v.get('color_transfer') == 'bt709' and v.get('color_primaries') == 'bt709', f'{v.get("color_primaries")}/{v.get("color_transfer")}'),
              ('音轨 AAC 48k 立体声', bool(au) and au[0]['codec_name'] == 'aac' and au[0]['sample_rate'] == '48000' and au[0]['channels'] == 2,
               f'{au[0]["codec_name"]} {au[0]["sample_rate"]} {au[0]["channels"]}ch' if au else '无')]
    for name, good, got in checks: print(f'{"✓" if good else "✗"} {name}：{got}')
    print(f'  时长 {float(d["format"]["duration"]):.3f}s  码率 {int(d["format"]["bit_rate"])/1e6:.1f} Mbps  {int(d["format"]["size"])/1e6:.0f} MB')
    if not all(g for _, g, _ in checks): sys.exit(1)

def cmd_all(a):
    me = [sys.executable, os.path.abspath(__file__)]
    for step in (['validate'], ['sprites'], ['validate'], ['subs'], ['plan'], ['render'], ['mix'], ['assemble'], ['verify']):
        print(f'==> {step[0]}', flush=True)
        r = subprocess.run(me + step + [a.storyboard])
        if r.returncode: die(f'{step[0]} 失败')

def cmd_selftest(a):
    from sv import selftest
    sys.exit(selftest.run(pixels=a.pixels, frames=a.frames, ref=a.ref))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('doctor').set_defaults(fn=cmd_doctor)
    s = sp.add_parser('setup'); s.add_argument('--fonts', action='store_true'); s.add_argument('--models', action='store_true'); s.set_defaults(fn=cmd_setup)
    s = sp.add_parser('probe'); s.add_argument('video'); s.set_defaults(fn=cmd_probe)
    s = sp.add_parser('asr'); s.add_argument('video'); s.add_argument('out'); s.set_defaults(fn=cmd_asr)
    s = sp.add_parser('align'); s.add_argument('asr'); s.add_argument('lines_txt'); s.add_argument('out'); s.set_defaults(fn=cmd_align)
    for name, fn in [('validate', cmd_validate), ('subs', cmd_subs), ('plan', cmd_plan), ('mix', cmd_mix), ('all', cmd_all)]:
        s = sp.add_parser(name); s.add_argument('storyboard'); s.set_defaults(fn=fn)
    s = sp.add_parser('sprites'); s.add_argument('storyboard'); s.add_argument('--only', nargs='*'); s.set_defaults(fn=cmd_sprites)
    s = sp.add_parser('grab'); s.add_argument('storyboard'); s.add_argument('at', nargs='+', type=float); s.set_defaults(fn=cmd_grab)
    s = sp.add_parser('preview'); s.add_argument('storyboard'); s.add_argument('at', nargs='+'); s.add_argument('--out'); s.set_defaults(fn=cmd_preview)
    s = sp.add_parser('render'); s.add_argument('storyboard'); s.add_argument('--range', nargs=2, type=int)
    s.add_argument('--chunk', type=int, default=DEFAULT_CHUNK); s.add_argument('--force', action='store_true')
    s.add_argument('--list', action='store_true', help='只列出分段计划和完成情况'); s.set_defaults(fn=cmd_render)
    s = sp.add_parser('assemble'); s.add_argument('storyboard'); s.add_argument('--chunk', type=int, default=DEFAULT_CHUNK); s.set_defaults(fn=cmd_assemble)
    s = sp.add_parser('verify'); s.add_argument('storyboard'); s.add_argument('--file'); s.set_defaults(fn=cmd_verify)
    s = sp.add_parser('selftest'); s.add_argument('--pixels', action='store_true', help='重新渲染素材和字幕，逐像素比对（素材需要 Chromium，字幕需要 Pillow）')
    s.add_argument('--frames', nargs=2, type=int, metavar=('起', '止'), help='在有原片的电脑上重渲一段，和基准成片逐帧比对')
    s.add_argument('--ref', help='基准成片或基准分段所在目录（--frames 用）'); s.set_defaults(fn=cmd_selftest)
    a = ap.parse_args(); a.fn(a)

if __name__ == '__main__':
    main()
