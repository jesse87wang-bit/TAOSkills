# 4K 静帧预览：不用等整片渲染，就能看版式（字有没有被头挡、卡片有没有溢出、和字幕打不打架）
import subprocess
import numpy as np

def grab(mov, t, out_jpg, hdr=True):
    """从原片取一帧（与成片同样的色调映射），存成 jpg"""
    from . import comp4k
    vf = comp4k.TONEMAP if hdr else comp4k.SDR_VF
    subprocess.run(['ffmpeg','-v','error','-y','-ss',f'{t:.3f}','-i',mov,'-frames:v','1','-vf',vf,'-q:v','3',out_jpg], check=True)
    return out_jpg

def render(plan, stills, out_jpg, tile_w=540):
    """stills = [(秒, 静帧路径), ...] → 横向拼成一张预览图"""
    import cv2
    from . import comp4k
    class Enc:
        class stdin:
            buf = None
            @staticmethod
            def write(b): Enc.stdin.buf = b
    tiles = []
    for t, fr in stills:
        f = cv2.imread(fr); mt = comp4k.Matte()
        for _ in range(4): a = mt(f)
        comp4k.HEAD['l'] = None; comp4k.update_head(a)
        comp4k.render_frame(Enc, f, a, int(round(t*60)), plan['els'], plan['subs'], plan['fx'], plan['sub_index'])
        img = np.frombuffer(Enc.stdin.buf, np.uint8).reshape(comp4k.H, comp4k.W, 3)
        tile = cv2.resize(img, (tile_w, tile_w*16//9), interpolation=cv2.INTER_AREA)
        cv2.putText(tile, f'{t:.2f}s', (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 2, cv2.LINE_AA)
        tiles.append(tile)
    cv2.imwrite(out_jpg, np.hstack(tiles), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return out_jpg
