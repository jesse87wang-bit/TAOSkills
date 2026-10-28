# 外部文件（字体、模型、音效）的下载与 sha256 校验
import os, json, hashlib, urllib.request, tarfile, shutil

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = json.load(open(os.path.join(KIT, 'assets.json'), encoding='utf-8'))
FONT_DIR = os.environ.get('SV_FONTS', os.path.join(KIT, 'fonts'))
SFX_DIR = os.environ.get('SV_SFX', os.path.join(KIT, 'sfx'))
MODEL_DIR = os.path.expanduser(os.environ.get('SV_MODELS', '~/work/sv'))

class AssetError(RuntimeError):
    pass

def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()

def _download(url, dst, tries=8):
    """断点续传：连接中途断开时从已下载的位置接着下（慢网络、代理常见）"""
    tmp = dst + '.part'
    total = None
    for _ in range(tries):
        have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
        req = urllib.request.Request(url, headers={'Range': f'bytes={have}-'} if have else {})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                if have and r.status != 206:      # 服务器不支持续传：从头来
                    have = 0
                if total is None:
                    cr = r.headers.get('Content-Range')
                    total = int(cr.split('/')[-1]) if cr and '/' in cr else (int(r.headers['Content-Length']) + have if r.headers.get('Content-Length') else None)
                with open(tmp, 'ab' if have else 'wb') as f:
                    shutil.copyfileobj(r, f)
        except OSError as ex:
            print('  网络中断，续传…', type(ex).__name__, flush=True)
        if total is not None and os.path.exists(tmp) and os.path.getsize(tmp) >= total:
            break
    os.replace(tmp, dst)

def _ensure(path, url, want):
    if os.path.exists(path) and sha256(path) == want:
        return path
    if os.path.exists(path):
        raise AssetError(f'{path} 的 sha256 与 assets.json 不符（版本不同会导致成片不一致）。删掉它让工具重新下载，或换成正确版本。')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print('下载', os.path.basename(path), '…', flush=True)
    _download(url, path)
    got = sha256(path)
    if got != want:
        os.rename(path, path + '.bad')
        raise AssetError(f'下载的 {os.path.basename(path)} 哈希不符：{got}（期望 {want}）')
    return path

def _from_zip(name, m):
    """备用来源：主地址下不了时，从官方发布包（zip）里取同一个文件，照样按 sha256 校验（v1.4.5）"""
    import zipfile
    path = os.path.join(FONT_DIR, name)
    os.makedirs(FONT_DIR, exist_ok=True)
    zp = os.path.join(FONT_DIR, '_' + os.path.basename(m['zip']))
    if not os.path.exists(zp):
        print('主地址不可用，改从官方发布包下载', os.path.basename(m['zip']), '…', flush=True)
        _download(m['zip'], zp)
    with zipfile.ZipFile(zp) as z:
        member = next(i for i in z.namelist() if os.path.basename(i) == name)
        with z.open(member) as src, open(path, 'wb') as dst:
            shutil.copyfileobj(src, dst)
    got = sha256(path)
    if got != m['sha256']:
        os.rename(path, path + '.bad')
        raise AssetError(f'发布包里的 {name} 哈希不符：{got}（期望 {m["sha256"]}）')
    return path

def _ensure_font(name, m):
    path = os.path.join(FONT_DIR, name)
    try:
        return _ensure(path, m['url'], m['sha256'])
    except AssetError:
        if not m.get('zip') or os.path.exists(path):
            raise
    except OSError:
        if not m.get('zip'):
            raise
    return _from_zip(name, m)

def _cleanup_font_zips():
    if os.path.isdir(FONT_DIR):
        for f in os.listdir(FONT_DIR):
            if f.startswith('_') and f.endswith('.zip'):
                os.remove(os.path.join(FONT_DIR, f))

def fonts():
    """确保字体齐全并校验，返回 {文件名: 绝对路径}"""
    out = {name: _ensure_font(name, m) for name, m in MANIFEST['fonts'].items()}
    _cleanup_font_zips()
    return out

def font(name):
    return _ensure_font(name, MANIFEST['fonts'][name])

def models():
    """确保抠像/识别模型齐全并校验（放在 SV_MODELS，默认 ~/work/sv），返回路径表"""
    M = MANIFEST['models']; out = {}
    for name in ('rvm.onnx', 'silero_vad.onnx'):
        out[name] = _ensure(os.path.join(MODEL_DIR, name), M[name]['url'], M[name]['sha256'])
    sv = M['sense-voice']; d = os.path.join(MODEL_DIR, sv['dir'])
    ok = all(os.path.exists(os.path.join(d, f)) and sha256(os.path.join(d, f)) == h for f, h in sv['files'].items())
    if not ok:
        os.makedirs(MODEL_DIR, exist_ok=True)
        tb = os.path.join(MODEL_DIR, 'sense-voice.tar.bz2')
        print('下载 SenseVoice 模型 …', flush=True)
        _download(sv['url'], tb)
        with tarfile.open(tb) as t:
            t.extractall(MODEL_DIR)
        os.remove(tb)
        for f, h in sv['files'].items():
            if sha256(os.path.join(d, f)) != h:
                raise AssetError(f'SenseVoice {f} 哈希不符')
    out['sense-voice'] = d
    return out

def rvm_path():
    p = os.environ.get('SV_RVM')
    if p:
        return os.path.expanduser(p)
    m = MANIFEST['models']['rvm.onnx']
    return _ensure(os.path.join(MODEL_DIR, 'rvm.onnx'), m['url'], m['sha256'])

def sfx_check():
    """核对 6 个音效；返回 (缺失列表, 哈希不符列表)"""
    missing, differ = [], []
    for name, want in MANIFEST['sfx'].items():
        if name.startswith('_'):
            continue
        p = os.path.join(SFX_DIR, name)
        if not os.path.exists(p):
            missing.append(name)
        elif sha256(p) != want:
            differ.append(name)
    return missing, differ
