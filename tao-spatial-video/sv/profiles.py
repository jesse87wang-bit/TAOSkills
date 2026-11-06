"""Output adapter; the established 4K spatial composition core stays unchanged."""
import os, subprocess
DEFAULT = dict(width=2160, height=3840, fps=60)
SUPPORTED = ((2160,3840,60),(1080,1920,30))
def get(sb):
    p = sb.get('output_profile', DEFAULT)
    if not isinstance(p,dict) or set(p) != set(DEFAULT) or any(type(p[k]) is not int for k in DEFAULT):
        raise ValueError('output_profile 需要整数 width、height、fps')
    if tuple(p[k] for k in DEFAULT) not in SUPPORTED:
        raise ValueError('仅支持 2160×3840 60fps 或 1080×1920 30fps')
    return dict(p)
def configure(sb):
    from . import comp4k
    p = get(sb)
    if not hasattr(comp4k,'_profile_original'):
        comp4k._profile_original=(comp4k.SDR_VF,comp4k.TONEMAP)
    sdr,hdr=comp4k._profile_original
    comp4k.FPS=p['fps']
    comp4k.SDR_VF=sdr.replace('fps=60',f"fps={p['fps']}")
    comp4k.TONEMAP=hdr.replace('fps=60',f"fps={p['fps']}")
    if p != DEFAULT:
        comp4k.TONEMAP=comp4k.TONEMAP.replace('format=bgr24','scale=2160:3840:flags=lanczos,format=bgr24')
    return p

def render(sb,comp4k,plan,out,i0,i1,n_src):
    p=configure(sb)
    if p==DEFAULT:
        return comp4k.render_chunk(plan,out,0.0,i0,i1,n_src=n_src)
    canvas=out+'.canvas.mp4'; partial=out+'.part.mp4'
    try:
        comp4k.render_chunk(plan,canvas,0.0,i0,i1,n_src=n_src)
        subprocess.run(['ffmpeg','-v','error','-y','-i',canvas,'-an','-vf',f"scale={p['width']}:{p['height']}:flags=lanczos,setsar=1",
                        '-c:v','libx264','-preset','medium','-crf','15','-profile:v','high','-pix_fmt','yuv420p','-threads','3',
                        '-filter_threads','1','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',partial],check=True)
        tag_bt709(partial,out)
    finally:
        for f in (canvas,partial):
            if os.path.exists(f):os.remove(f)

def tag_bt709(source,destination):
    """Write H.264 VUI tags for already tone-mapped bt709 frames; stream copy, no color transform."""
    subprocess.run(['ffmpeg','-v','error','-y','-i',source,'-map','0','-c','copy',
                    '-bsf:v','h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1',
                    '-movflags','+faststart',destination],check=True)
