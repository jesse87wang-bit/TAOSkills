# 自动剪口误（v1.5.0 新增）
# 原片 → 转写（逐字时间戳）→ 剪辑计划 cut_plan.json（可人工/Agent 修改）→ 净剪片 + 剪后转写
#
# 规则（保守优先：宁可少剪，不剪坏句子）
#   1. 重录：某一句后面不久又重新说了一遍（开头相同或高度相似）→ 删前面那次，留最后一次
#   2. 结尾残句：片尾没说完、只重复开头的短句 → 删
#   3. 句首语气词：「嗯」「呃」「额」开头的单独语气词 → 删（句中的「啊」是说话节奏，默认保留）
#   4. 长停顿：两句之间超过 0.45 秒的空白 → 压到约 0.25 秒
#   5. 有文稿时（--script）：和文稿对不上的句子标「文稿外」，默认保留但在报告里列出来请人确认
import os, json, re, difflib, subprocess

FILLERS = set('啊嗯呃额哦唔')
LEAD_FILLERS = set('嗯呃额唔')
_PUNCT = re.compile(r"[\s，。？、；！：“”‘’,?!.;:'\"（）()《》\-—…]")

def _norm(s, drop_fillers=True):
    s = _PUNCT.sub('', s.lower())
    return ''.join(c for c in s if not (drop_fillers and c in FILLERS))

def _probe(video):
    r = subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_format', '-show_streams', video],
                       capture_output=True, text=True, check=True)
    d = json.loads(r.stdout)
    v = next((s for s in d['streams'] if s['codec_type'] == 'video'), None)
    if v is None:   # 只有音频（测试用）
        return dict(fps=30.0, dur=float(d['format']['duration']), hdr=False, transfer=None, codec=None)
    num, den = (v.get('avg_frame_rate') or v.get('r_frame_rate') or '30/1').split('/')
    fps = float(num) / float(den or 1)
    dur = float(v.get('duration') or d['format']['duration'])
    hdr = v.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    w, h = int(v['width']), int(v['height']); rot = 0
    for sd in v.get('side_data_list', []):
        if 'rotation' in sd: rot = int(sd['rotation'])
    if abs(rot) in (90, 270): w, h = h, w
    return dict(fps=fps, dur=dur, hdr=hdr, transfer=v.get('color_transfer'), codec=v.get('codec_name'), w=w, h=h)

TARGET = (2160, 3840)   # 包装引擎按竖屏 4K 设计：剪辑时顺便把别的尺寸放大/缩到这个尺寸

def _read_script(path):
    txt = open(path, encoding='utf-8').read()
    if txt.startswith('---'):                       # 去掉 front matter
        parts = txt.split('---', 2)
        txt = parts[2] if len(parts) == 3 else txt
    lines = [l for l in txt.splitlines() if l.strip() and not l.lstrip().startswith('#')]
    return _norm(''.join(lines))

def _coverage(phrase, script):
    if not phrase: return 1.0
    sm = difflib.SequenceMatcher(None, phrase, script, autojunk=False)
    return sum(b.size for b in sm.get_matching_blocks()) / len(phrase)

def plan(asr_json, video, out_json, script=None, pause=0.45, keep_gap=0.25, window=25.0):
    info = _probe(video)
    asr = json.load(open(asr_json, encoding='utf-8'))
    ph = []
    for i, s in enumerate(asr):
        toks = [(t, ts) for t, ts in zip(s['tokens'], s['ts'])]
        # 句首语气词
        lead = 0
        while lead < len(toks) and toks[lead][0].strip() and all(c in LEAD_FILLERS for c in toks[lead][0].strip()):
            lead += 1
        start = toks[lead][1] if lead < len(toks) else s['start']
        last = toks[-1][1] if toks else s['end']
        end = min(s['end'], last + 0.35)
        ph.append(dict(i=i, start=round(start, 3), end=round(end, 3), vad=[s['start'], s['end']], text=s['text'],
                       norm=_norm(s['text']), lead_filler=lead > 0, keep=True, reason=''))
    # 1. 重录：留最后一次
    for i, p in enumerate(ph):
        if len(p['norm']) < 3: continue
        later = ''
        for q in ph[i+1:]:
            if q['start'] - p['end'] > window: break
            later += q['norm']
            if len(later) >= len(p['norm']) + 6: break
        if not later: continue
        head = later[:len(p['norm']) + 3]
        r = difflib.SequenceMatcher(None, p['norm'], head, autojunk=False).ratio()
        if r >= 0.72:
            p['keep'] = False; p['reason'] = f'重录（后面重新说了一遍，相似度 {r:.2f}），留后一次'
    # 2. 结尾残句：片尾的短句，且它被重录过（说了好几次都没说完）
    dropped_norms = [p['norm'] for p in ph if not p['keep']]
    for p in reversed(ph):
        if not p['keep']: continue
        if len(p['norm']) <= 8 and any(d.startswith(p['norm'][:3]) for d in dropped_norms if d):
            p['keep'] = False; p['reason'] = '片尾残句（重复起头、没说完）'
            continue
        break
    # 5. 文稿外
    if script:
        sc = _read_script(script)
        for p in ph:
            cov = _coverage(p['norm'], sc)
            p['script_cov'] = round(cov, 2)
            if cov < 0.5 and p['keep']:
                if p is ph[-1] or all(not q['keep'] for q in ph[ph.index(p)+1:]):
                    p['keep'] = False; p['reason'] = f'片尾文稿外（和文稿重合 {cov:.0%}）'
                else:
                    p['flag'] = f'文稿外（和文稿重合 {cov:.0%}），默认保留，请确认'
    # 3/4. 区间：留下的句子 + 前后余量，相邻句之间的空白超过 pause 就压到 keep_gap
    fr = 1.0 / info['fps']
    snap = lambda t: round(round(t / fr) * fr, 4)
    keep = []
    pre, post = 0.12, 0.10
    for p in ph:
        if not p['keep']: continue
        a, b = max(0.0, p['start'] - pre), min(info['dur'], p['end'] + post)
        if keep:
            gap = a - keep[-1][1]
            if gap <= pause - pre - post:          # 原本的停顿不长：连起来，保留自然节奏
                keep[-1][1] = b; continue
            if gap < keep_gap - pre - post:        # 余量重叠
                keep[-1][1] = b; continue
            extra = max(0.0, keep_gap - pre - post) / 2
            keep[-1][1] = min(keep[-1][1] + extra, a); a = max(a - extra, keep[-1][1])
        keep.append([a, b])
    keep = [[snap(a), snap(b)] for a, b in keep if b - a > 2 * fr]
    kept = sum(b - a for a, b in keep)
    out = dict(version='1.5.0', source=os.path.abspath(video), fps=info['fps'], dur=round(info['dur'], 3),
               hdr=info['hdr'], script=os.path.abspath(script) if script else None,
               keep=keep, kept_dur=round(kept, 3), phrases=ph)
    json.dump(out, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    report(out_json)
    return out

def report(plan_json, out_md=None):
    d = json.load(open(plan_json, encoding='utf-8'))
    L = [f"# 剪辑计划：{os.path.basename(d['source'])}", '',
         f"原片 {d['dur']:.1f} 秒 → 净剪 {d['kept_dur']:.1f} 秒（剪掉 {d['dur'] - d['kept_dur']:.1f} 秒，{len(d['keep'])} 段）", '',
         '| 时间 | 处理 | 内容 |', '|---|---|---|']
    for p in d['phrases']:
        act = '保留' if p['keep'] else '**删除**'
        note = p['reason'] or p.get('flag', '')
        if p['keep'] and p.get('lead_filler'): note = (note + '；' if note else '') + '去掉句首语气词'
        L.append(f"| {p['start']:.1f}–{p['end']:.1f} | {act}{'：' + note if note else ''} | {p['text']} |")
    L += ['', '保留区间（秒）：' + '、'.join(f'{a:.2f}–{b:.2f}' for a, b in d['keep']), '',
          '要改的话：直接改 cut_plan.json 里 phrases[].keep（true/false），再运行 `make_video.py cutapply cut_plan.json`（会按 phrases 重新算区间）。']
    txt = '\n'.join(L)
    out_md = out_md or os.path.splitext(plan_json)[0] + '_报告.md'
    open(out_md, 'w', encoding='utf-8').write(txt)
    print(txt)
    return out_md

def _rebuild_keep(d):
    """phrases 被人工改过 keep 时，按同样规则重算区间"""
    fr = 1.0 / d['fps']; snap = lambda t: round(round(t / fr) * fr, 4)
    keep = []; pre, post, pause, keep_gap = 0.12, 0.10, 0.45, 0.25
    for p in d['phrases']:
        if not p['keep']: continue
        a, b = max(0.0, p['start'] - pre), min(d['dur'], p['end'] + post)
        if keep:
            gap = a - keep[-1][1]
            if gap <= pause - pre - post or gap < keep_gap - pre - post:
                keep[-1][1] = b; continue
            extra = max(0.0, keep_gap - pre - post) / 2
            keep[-1][1] = min(keep[-1][1] + extra, a); a = max(a - extra, keep[-1][1])
        keep.append([a, b])
    return [[snap(a), snap(b)] for a, b in keep if b - a > 2 * fr]

def apply(plan_json, out_video=None, rebuild=True):
    d = json.load(open(plan_json, encoding='utf-8'))
    if rebuild:
        d['keep'] = _rebuild_keep(d); d['kept_dur'] = round(sum(b - a for a, b in d['keep']), 3)
        json.dump(d, open(plan_json, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    src = d['source']
    if not d['keep']: raise ValueError('没有保留区间')
    from .profiles import get as output_profile
    target_profile=output_profile(d) if 'output_profile' in d else None
    target=(target_profile['width'],target_profile['height']) if target_profile else TARGET
    last=0
    for a,b in d['keep']:
        if not (0 <= a < b <= d['dur']+.001 and a >= last): raise ValueError('剪辑区间无效或重叠')
        last=b
    out_video = out_video or os.path.join(os.path.dirname(os.path.abspath(plan_json)), '净剪_' + os.path.splitext(os.path.basename(src))[0] + '.mov')
    parts, labels = [], []
    for k, (a, b) in enumerate(d['keep']):
        f = 0.012
        parts.append(f"[0:v]trim=start={a}:end={b},setpts=PTS-STARTPTS[v{k}];"
                     f"[0:a]atrim=start={a}:end={b},asetpts=PTS-STARTPTS,afade=t=in:d={f},afade=t=out:st={max(0, b - a - f):.4f}:d={f}[a{k}];")
        labels.append(f'[v{k}][a{k}]')
    info = _probe(src)
    if info['w'] > info['h']:
        raise SystemExit(f"原片是横屏 {info['w']}×{info['h']}：口播工作台只做竖屏，先和用户确认（可以先裁成竖屏再做）")
    scale = ''
    if (info['w'], info['h']) != target:
        scale = f"[vc]scale={target[0]}:{target[1]}:flags=lanczos:force_original_aspect_ratio=increase,crop={target[0]}:{target[1]}[v]"
        print(f"原片 {info['w']}×{info['h']} → 输出竖屏规格 {target[0]}×{target[1]}（不增加细节，只是统一尺寸）")
    vout = '[vc]' if scale else '[v]'
    fc = ''.join(parts) + ''.join(labels) + f"concat=n={len(d['keep'])}:v=1:a=1{vout}[a]" + (';' + scale if scale else '')
    fcf = os.path.splitext(out_video)[0] + '_filter.txt'
    open(fcf, 'w').write(fc)
    if d['hdr']:   # 保留 HLG：10-bit HEVC + 原色彩标记，后面的包装照常做色调映射
        venc = ['-c:v', 'libx265', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p10le', '-tag:v', 'hvc1',
                '-x265-params', 'pools=4:frame-threads=2:log-level=error:colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc',
                '-color_primaries', 'bt2020', '-color_trc', 'arib-std-b67', '-colorspace', 'bt2020nc']
    else:
        venc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '12', '-pix_fmt', 'yuv420p',
                '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709']
    tmp = os.path.splitext(out_video)[0] + '.part' + os.path.splitext(out_video)[1]
    cmd = ['ffmpeg', '-v', 'error', '-y', '-threads', '2', '-filter_complex_threads', '1', '-i', src, '-filter_complex_script', fcf, '-map', '[v]', '-map', '[a]',
           '-r', str(target_profile['fps']) if target_profile else f"{d['fps']:.6g}", *venc, '-c:a', 'aac', '-b:a', '320k', '-ar', '48000', '-movflags', '+faststart', tmp]
    subprocess.run(cmd, check=True)
    os.replace(tmp, out_video); os.remove(fcf)
    # 剪后转写：把原转写的逐字时间映射到新时间轴，包装时不用再转写一遍
    asr_src = os.path.splitext(plan_json)[0].replace('cut_plan', 'asr') + '.json'
    print(f"✓ 净剪片 {out_video}  （{d['kept_dur']:.2f} 秒，{len(d['keep'])} 段）")
    return out_video

def normalize(video, out_video=None):
    """不剪辑，只统一成竖屏 4K（原片不是 2160×3840 时，包装前先跑这个）"""
    info = _probe(video)
    out_video = out_video or os.path.join(os.path.dirname(os.path.abspath(video)), '4K_' + os.path.splitext(os.path.basename(video))[0] + '.mov')
    plan_json = os.path.splitext(out_video)[0] + '_plan.json'
    json.dump(dict(source=os.path.abspath(video), fps=info['fps'], dur=info['dur'], hdr=info['hdr'],
                   keep=[[0.0, round(info['dur'], 4)]], kept_dur=round(info['dur'], 3), phrases=[]),
              open(plan_json, 'w', encoding='utf-8'), ensure_ascii=False)
    v = apply(plan_json, out_video, rebuild=False); os.remove(plan_json); return v

def remap_asr(plan_json, asr_json, out_json):
    """原片转写 → 净剪片时间轴（只保留留下来的句子）"""
    d = json.load(open(plan_json, encoding='utf-8')); asr = json.load(open(asr_json, encoding='utf-8'))
    off, segs = 0.0, []
    for a, b in d['keep']:
        segs.append((a, b, off)); off += b - a
    def m(t):
        for a, b, o in segs:
            if a - 1e-6 <= t <= b + 1e-6: return round(o + t - a, 3)
        return None
    keep_i = {p['i'] for p in d['phrases'] if p['keep']}
    out = []
    for i, s in enumerate(asr):
        if i not in keep_i: continue
        toks, ts = [], []
        for t, x in zip(s['tokens'], s['ts']):
            y = m(x)
            if y is not None: toks.append(t); ts.append(y)
        if not toks: continue
        st = m(max(s['start'], segs[0][0])) or ts[0]
        en = m(min(s['end'], d['keep'][-1][1])) or ts[-1] + 0.3
        out.append(dict(start=round(min(st, ts[0]), 3), end=round(max(en, ts[-1]), 3), text=''.join(toks), tokens=toks, ts=ts))
    json.dump(out, open(out_json, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'✓ 剪后转写 {out_json}（{len(out)} 句）')
    return out
