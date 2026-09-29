# tao-spatial-video 合成器（在用户电脑的 Linux 环境里跑）
# 原片像素不动，只改玻璃卡/文字所在区域；人物用 RVM 抠像，卡片放在人物身后时会被人挡住。
# 坐标约定：时间轴里的 x/y 用 1080×1920 布局坐标，渲染时 ×K(=2) 到 4K；素材 PNG 是 3 倍 css 像素。
import cv2, numpy as np, math, sys, os, json, subprocess, time
cv2.setNumThreads(2)
W, H, FPS = 2160, 3840, 60
K = 2.0            # 1080 布局坐标 → 4K
SPR = 3.0          # 素材像素 / css 像素
BASE = os.path.dirname(os.path.abspath(__file__))
SP = os.environ.get('SV_SPRITES', BASE+'/sp3/')
SUBDIR = os.environ.get('SV_SUBS', BASE+'/sub4k/')
MOV = os.environ.get('SV_MOV', '')          # 由 render_chunk.py 设置
SRC_HDR = os.environ.get('SV_HDR', '1') == '1'   # iPhone HLG/杜比视界 → 1；普通 SDR 素材 → 0
SDR_VF = "scale=2160:3840:flags=lanczos,format=bgr24,fps=60"
TONEMAP = ("zscale=tin=arib-std-b67:min=bt2020nc:pin=bt2020:rin=tv:t=linear:npl=100,format=gbrpf32le,"
           "zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=bgr24,fps=60")

def bgr(h):
    h = h.lstrip('#'); return np.array([int(h[4:6],16), int(h[2:4],16), int(h[0:2],16)], np.float32)/255
CYAN, VIOLET, INDIGO = bgr('#22D3EE'), bgr('#8B5CF6'), bgr('#6366F1')

_spr = {}; _rs = {}
def sprite(n):
    if n not in _spr:
        im = cv2.imread(SP+n+'.png', cv2.IMREAD_UNCHANGED).astype(np.float32)/255.
        im[..., :3] *= im[..., 3:4]; _spr[n] = im
    return _spr[n]
def sprite_at(n, k):
    kq = round(k, 2); key = (n, kq)
    if key not in _rs:
        s = sprite(n)
        if kq < 0.97: s = cv2.resize(s, (max(2,int(s.shape[1]*kq)), max(2,int(s.shape[0]*kq))), interpolation=cv2.INTER_AREA)
        _rs[key] = s
        if len(_rs) > 6: _rs.pop(next(iter(_rs)))
    return _rs[key]

def ease_out_back(p, s=1.7): p -= 1; return p*p*((s+1)*p+s)+1
def ease_out_cubic(p): return 1-(1-p)**3
def ease_io(p): return 4*p**3 if p < .5 else 1-(-2*p+2)**3/2
def clamp(x, a=0., b=1.): return max(a, min(b, x))
def lerp(a, b, t): return a+(b-a)*t

def project(w, h, cx, cy, ry, D=1700*K):
    c, s = math.cos(math.radians(ry)), math.sin(math.radians(ry)); pts = []
    for x, y in [(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]:
        X, Z = x*c, x*s; f = D/(D+Z); pts.append((cx+X*f, cy+y*f))
    return np.array(pts, np.float32)

def warp(n, w, h, cx, cy, ry):
    dst = project(w, h, cx, cy, ry); s0 = sprite(n)
    k = w/s0.shape[1]; s = sprite_at(n, k*1.12 if k < 0.85 else 1.0)
    sh, sw = s.shape[:2]
    x0, y0 = np.floor(dst.min(0)).astype(int); x1, y1 = np.ceil(dst.max(0)).astype(int)
    x0c, y0c, x1c, y1c = max(x0,0), max(y0,0), min(x1,W), min(y1,H)
    if x1c-x0c < 2 or y1c-y0c < 2: return None
    M = cv2.getPerspectiveTransform(np.array([(0,0),(sw,0),(sw,sh),(0,sh)], np.float32), dst-np.array([x0c,y0c],np.float32))
    out = cv2.warpPerspective(s, M, (x1c-x0c, y1c-y0c), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return out, x0c, y0c

def fast_blur(img, sigma):
    f = 4 if sigma > 12 else 2; h, w = img.shape[:2]
    sm = cv2.resize(img, (max(1,w//f), max(1,h//f)), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0,0), sigma/f)
    return cv2.resize(sm, (w, h), interpolation=cv2.INTER_LINEAR)

def state(e, t):
    if t < e['in']: return None
    p = clamp((t-e['in'])/e.get('dur', .55))
    tx, ty, ts, tr = e['x'], e['y'], e['s'], e.get('ry', 0)
    fx, fy, fs, fr = e.get('from', (tx, ty, ts*0.5, tr))
    eo = ease_out_cubic(p); eb = ease_out_back(p, e.get('back', 1.6))
    st = dict(x=lerp(fx,tx,eo), y=lerp(fy,ty,eo), s=lerp(fs,ts,eb), ry=lerp(fr,tr,eo), op=clamp(p*2.2), layer=e['layer'], reveal=1.0)
    for (m0, m1, tgt) in e.get('moves', []):
        if t >= m0:
            q = ease_io(clamp((t-m0)/(m1-m0)))
            for k2, v in tgt.items():
                if k2 == 'layer': st['layer'] = v
                else: st[k2] = lerp(st[k2], v, q)
    if 'out' in e and t >= e['out']:
        q = clamp((t-e['out'])/e.get('odur', .35)); qe = ease_io(q)
        ox, oy = e.get('to', (st['x'], st['y']))
        st['x'] = lerp(st['x'], ox, qe); st['y'] = lerp(st['y'], oy, qe); st['s'] *= (1-0.35*qe); st['op'] *= (1-q)
        if q >= 1: return None
    amp = e.get('float', 0)
    if amp:
        ph = e.get('ph', 0); st['y'] += amp*math.sin(2*math.pi*t/3.2+ph); st['ry'] += 1.4*math.sin(2*math.pi*t/4.1+ph)
    if 'wipe' in e:
        wf = e.get('wipe_from', e['in']+0.15); r0 = e.get('reveal0', 0.0)
        st['reveal'] = r0 + (1-r0)*clamp((t-wf)/e['wipe'])
    return st

class Matte:
    def __init__(self):
        import onnxruntime as ort
        so = ort.SessionOptions(); so.intra_op_num_threads = 3
        self.s = ort.InferenceSession(os.environ.get('SV_RVM', os.path.expanduser('~/work/sv/rvm.onnx')), so, providers=['CPUExecutionProvider'])
        self.rec = [np.zeros([1,1,1,1], np.float32)]*4; self.dr = np.array([0.25], np.float32)
    def __call__(self, f4k):
        sm = cv2.resize(f4k, (1080, 1920), interpolation=cv2.INTER_AREA)
        x = cv2.cvtColor(sm, cv2.COLOR_BGR2RGB).astype(np.float32).transpose(2,0,1)[None]/255.
        fgr, pha, *self.rec = self.s.run(None, {'src': x, 'r1i': self.rec[0], 'r2i': self.rec[1], 'r3i': self.rec[2], 'r4i': self.rec[3], 'downsample_ratio': self.dr})
        return pha[0,0]
HEAD = {'l': None, 'r': None}
def update_head(a1080):
    band = a1080[470:990] > 0.5
    cols = np.where(band.any(0))[0]
    if len(cols) == 0: return
    l, r = float(cols.min()), float(cols.max())
    if HEAD['l'] is None: HEAD['l'], HEAD['r'] = l, r
    else:
        HEAD['l'] += (l-HEAD['l'])*0.06; HEAD['r'] += (r-HEAD['r'])*0.06
def adjust_side(e, st):
    if HEAD['l'] is None: return
    wc = sprite(e['sp']).shape[1]/SPR
    s = st['s']
    if e['x'] > 540:
        r = HEAD['r']
        smax = (1070-r)/max(1.0, wc-45)
        if s > smax: s = max(min(s, 0.62), smax)
        hw = wc*s/2
        x = max(st['x'], r + hw - 20*s + 10)
        x = min(x, 1080 + 25*s - hw)
    else:
        l = HEAD['l']
        smax = (l-10)/max(1.0, wc-45)
        if s > smax: s = max(min(s, 0.62), smax)
        hw = wc*s/2
        x = min(st['x'], l - hw + 20*s - 10)
        x = max(x, -25*s + hw)
    st['x'], st['s'] = x, s

def alpha_region(a1080, x0, y0, x1, y1):
    X0, Y0 = max(0, x0//2-2), max(0, y0//2-2); X1, Y1 = min(1080, x1//2+3), min(1920, y1//2+3)
    sub = a1080[Y0:Y1, X0:X1]
    up = cv2.resize(sub, ((X1-X0)*2, (Y1-Y0)*2), interpolation=cv2.INTER_LINEAR)
    ox, oy = x0-X0*2, y0-Y0*2
    a = up[oy:oy+(y1-y0), ox:ox+(x1-x0)]
    return np.clip((a-0.18)/0.8, 0, 1)[..., None]

def draw(out, f, a1080, e, st, boost=0.):
    s0 = sprite(e['sp']); w = s0.shape[1]/SPR*st['s']*K; h = s0.shape[0]/SPR*st['s']*K
    r = warp(e['sp'], w, h, st['x']*K, st['y']*K, st['ry'])
    if r is None: return
    img, sx0, sy0 = r
    if st['reveal'] < 1:
        hh = img.shape[0]; cut = int(hh*st['reveal'])
        img = img*np.clip((cut-np.arange(hh))/80., 0, 1)[:, None, None].astype(np.float32)
    op = st['op']; A = img[..., 3:4]; sh, sw = A.shape[:2]
    back = st['layer'] == 'back'
    pad = 150 if (back or e.get('glow') is not None) else 0
    X0, Y0 = max(0, sx0-pad), max(0, sy0-pad); X1, Y1 = min(W, sx0+sw+pad), min(H, sy0+sh+pad)
    cur = out[Y0:Y1, X0:X1].astype(np.float32)/255.
    ox, oy = sx0-X0, sy0-Y0
    if pad:
        canvas = np.zeros((Y1-Y0, X1-X0), np.float32); canvas[oy:oy+sh, ox:ox+sw] = A[..., 0]
    if back and e.get('shadow', True):
        g = fast_blur(np.clip(canvas*2, 0, 1), 48)
        g = np.roll(np.roll(g, 76, 0), 52, 1)
        cur *= (1-0.30*op*g)[..., None]
    gc = e.get('glow')
    if gc is not None:
        g = fast_blur(canvas, 52)[..., None]
        cur += g*gc*(e.get('gk', .8)*0.45+boost*0.6)*op
    sub = cur[oy:oy+sh, ox:ox+sw]
    if e.get('glass'):
        fr = f[Y0:Y1, X0:X1].astype(np.float32)/255.
        frost = fast_blur(fr, 60)[oy:oy+sh, ox:ox+sw]*1.0+0.035
        m = np.clip(A*2.2, 0, 1)*op
        sub[:] = sub*(1-m) + frost*m
    if e.get('blur'): img = cv2.GaussianBlur(img, (0,0), e['blur']*K)
    sub[:] = sub*(1-A*op) + img[..., :3]*op
    if back:
        fr = f[Y0:Y1, X0:X1].astype(np.float32)/255.
        a = alpha_region(a1080, X0, Y0, X1, Y1)
        cur = fr*a + cur*(1-a)
    out[Y0:Y1, X0:X1] = np.clip(cur*255+0.5, 0, 255).astype(np.uint8)

_sub = {}
def sub_png(name):
    if name not in _sub:
        im = cv2.imread(SUBDIR+name, cv2.IMREAD_UNCHANGED).astype(np.float32)/255.
        im[..., :3] *= im[..., 3:4]; _sub[name] = im
    return _sub[name]
def over_png(out, im, x0, y0):
    h, w = im.shape[:2]; x1, y1 = min(W, x0+w), min(H, y0+h); xs, ys = max(0,x0), max(0,y0)
    s = im[ys-y0:y1-y0, xs-x0:x1-x0]; d = out[ys:y1, xs:x1].astype(np.float32)/255.
    d = d*(1-s[..., 3:4]) + s[..., :3]
    out[ys:y1, xs:x1] = np.clip(d*255+.5, 0, 255).astype(np.uint8)

def streak(out, cx, y):
    h = 120; y0 = int(y-h/2); y0 = max(0, min(H-h, y0))
    reg = out[y0:y0+h].astype(np.float32)/255.
    sl = np.zeros((h, W, 3), np.float32)
    cv2.line(sl, (int(cx-840), h//2), (int(cx+120), h//2), (1,1,1), 5, cv2.LINE_AA)
    sl = cv2.GaussianBlur(sl, (0,0), 3) + cv2.GaussianBlur(sl, (0,0), 18)*VIOLET*2.2
    out[y0:y0+h] = np.clip((reg+sl)*255+.5, 0, 255).astype(np.uint8)

def render_chunk(seq, out_mp4, seg_start, i0, i1, n_src, preroll=24):
    """渲染第 i0..i1 帧（相对片段起点），超出源片的帧重复最后一帧（片尾定格）"""
    els, subs, fx, sub_index = seq['els'], seq['subs'], seq['fx'], seq['sub_index']
    p0 = max(0, i0-preroll)
    src_end = min(i1, n_src)
    nread = max(0, src_end-p0)
    if i0 >= n_src:   # 纯定格段：只取最后一帧
        p0 = n_src-1-preroll if n_src-1-preroll > 0 else 0; nread = n_src-p0
    dec = subprocess.Popen(['ffmpeg','-v','error','-threads','2','-filter_threads','1','-ss',f'{seg_start+p0/FPS:.4f}','-i',MOV,'-frames:v',str(nread),'-vf',TONEMAP if SRC_HDR else SDR_VF,
                            '-f','rawvideo','-pix_fmt','bgr24','-'], stdout=subprocess.PIPE, bufsize=W*H*3*2)
    enc = subprocess.Popen(['ffmpeg','-v','warning','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
                '-c:v','libx264','-preset','medium','-crf','15','-profile:v','high','-level','5.2','-pix_fmt','yuv420p','-threads','3',
                '-x264-params','rc-lookahead=12:sync-lookahead=0',
                '-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709', out_mp4], stdin=subprocess.PIPE)
    matte = Matte(); f = None; a1080 = None; t0 = time.time(); last = p0-1
    for j in range(nread):
        buf = dec.stdout.read(W*H*3)
        if len(buf) < W*H*3: break
        f = np.frombuffer(buf, np.uint8).reshape(H, W, 3); a1080 = matte(f); update_head(a1080)
        i = p0+j; last = i
        if i < i0: continue
        render_frame(enc, f, a1080, i, els, subs, fx, sub_index)
    for i in range(max(i0, last+1), i1):   # 定格
        render_frame(enc, f, a1080, i, els, subs, fx, sub_index)
    enc.stdin.close(); enc.wait(); dec.kill()
    print('chunk', i0, i1, f'{time.time()-t0:.1f}s', flush=True)

def render_frame(enc, f, a1080, i, els, subs, fx, sub_index):
    t = i/FPS
    out = f.copy()
    boost = fx['boost'](t) if 'boost' in fx else 0.
    for layer in ('back', 'front'):
        for e in els:
            st = state(e, t)
            if st and st['layer'] == layer:
                if layer == 'back': adjust_side(e, st)
                draw(out, f, a1080, e, st, boost)
    for (ts, y, d) in fx.get('streaks', []):
        if ts <= t < ts+d:
            p = (t-ts)/d; streak(out, lerp(-600, W+600, ease_io(p)), y*K)
    for (s0, s1, text) in subs:
        if s0 <= t < s1:
            im = sub_png(sub_index[text]); over_png(out, im, (W-im.shape[1])//2, int(1478*K)); break
    enc.stdin.write(out.tobytes())
