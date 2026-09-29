# 用 4K 静帧预览版式（不用等整片渲染）。在云端容器跑，需要 onnxruntime、opencv。
# 用法: python3 preview.py <时间轴.py> <素材目录sp3> <字幕目录> <输出.jpg> 秒:静帧.jpg 秒:静帧.jpg ...
import sys, os, importlib.util, numpy as np, cv2
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
seq_path, sp, subdir, out = sys.argv[1:5]
os.environ['SV_SPRITES'] = os.path.abspath(sp)+'/'; os.environ['SV_SUBS'] = os.path.abspath(subdir)+'/'
os.environ.setdefault('SV_RVM', os.path.expanduser('~/sv/rvm.onnx'))
sys.path.insert(0, KIT+'/device'); import comp4k
spec = importlib.util.spec_from_file_location('seqmod', seq_path); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
S = m.seq()
class Enc:
    class stdin:
        buf = None
        @staticmethod
        def write(b): Enc.stdin.buf = b
tiles = []
for arg in sys.argv[5:]:
    t, fr = arg.split(':', 1); t = float(t)
    f = cv2.imread(fr); mt = comp4k.Matte()
    for _ in range(4): a = mt(f)
    comp4k.HEAD['l'] = None; comp4k.update_head(a)
    comp4k.render_frame(Enc, f, a, int(round(t*60)), S['els'], S['subs'], S['fx'], S['sub_index'])
    img = np.frombuffer(Enc.stdin.buf, np.uint8).reshape(3840, 2160, 3)
    tiles.append(cv2.resize(img, (540, 960), interpolation=cv2.INTER_AREA))
cv2.imwrite(out, np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 88]); print('preview ->', out)
