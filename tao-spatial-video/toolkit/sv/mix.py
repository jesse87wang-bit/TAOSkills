# 人声 + 音效混音 → loudnorm -16 LUFS 的 48k 立体声 wav（算法与第一条成片一致）
import os, wave, subprocess
import numpy as np
from . import assets

SR = 48000
SFX_DB = -8           # 音效相对人声 99.9 分位峰值的电平

def pcm(path):
    raw = subprocess.run(['ffmpeg','-v','error','-i',path,'-vn','-ac','2','-ar',str(SR),'-f','f32le','-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1,2).copy()

def mix(plan, out_wav, sfx_dir=None):
    sfx_dir = sfx_dir or assets.SFX_DIR
    need = sorted({name for _, name, _, _ in plan['sfx']})
    miss = [n for n in need if not os.path.exists(os.path.join(sfx_dir, n+'.wav'))]
    if miss:
        raise FileNotFoundError(f'缺音效：{miss}（放到 {sfx_dir}，见 toolkit/sfx/README.md）')
    clips = {}
    for name in need:
        y = pcm(os.path.join(sfx_dir, name+'.wav')); clips[name] = y/(np.abs(y).max()+1e-9)
    n = int(plan['meta']['total_sec']*SR)
    v = pcm(plan['meta']['mov']); voice = np.zeros((n,2), np.float32); voice[:min(n,len(v))] = v[:n]
    sfx = np.zeros((n,2), np.float32)
    for t, name, pan, g in plan['sfx']:
        y = clips[name]; s = int(t*SR); e = min(n, s+len(y))
        if s >= n: continue
        gl, gr = min(1, np.sqrt((1-pan)/2)*1.414), min(1, np.sqrt((1+pan)/2)*1.414)
        sfx[s:e,0] += y[:e-s,0]*g*gl; sfx[s:e,1] += y[:e-s,1]*g*gr
    vp = np.percentile(np.abs(voice), 99.9)+1e-9
    m = voice + sfx*vp*(10**(SFX_DB/20))
    m = m/max(1.0, np.abs(m).max()/0.97)
    tmp = out_wav + '.tmp.wav'
    w = wave.open(tmp,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(m,-1,1)*32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar',str(SR),out_wav], check=True)
    os.remove(tmp)
    return len(plan['sfx'])
