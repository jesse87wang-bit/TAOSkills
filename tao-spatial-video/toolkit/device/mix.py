# 人声 + 剪映音效混音，输出 loudnorm 到 -16 LUFS 的 wav
# 用法: python3 mix.py <时间轴.py> <输出.wav>
# 时间轴文件需定义 MOV、TOTAL_SEC（成片总秒数，含片尾定格）、SFX = [(秒, 'deng'|'ding3'|'app'|'tone'|'xp'|'ui', 声像-1~1, 增益0~1), ...]
import sys, os, wave, subprocess, importlib.util, numpy as np
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SR = 48000
spec = importlib.util.spec_from_file_location('seqmod', sys.argv[1]); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.abspath(sys.argv[1])))
spec.loader.exec_module(m)
def pcm(path):
    raw = subprocess.run(['ffmpeg','-v','error','-i',path,'-vn','-ac','2','-ar',str(SR),'-f','f32le','-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1,2).copy()
clips = {}
for name in ['deng','ding3','app','tone','xp','ui']:
    y = pcm(f'{KIT}/sfx/{name}.wav'); clips[name] = y/(np.abs(y).max()+1e-9)
n = int(m.TOTAL_SEC*SR); voice = np.zeros((n,2), np.float32); v = pcm(os.path.expanduser(m.MOV)); voice[:min(n,len(v))] = v[:n]
sfx = np.zeros((n,2), np.float32)
for t, name, pan, g in m.SFX:
    y = clips[name]; s = int(t*SR); e = min(n, s+len(y))
    if s >= n: continue
    gl, gr = min(1, np.sqrt((1-pan)/2)*1.414), min(1, np.sqrt((1+pan)/2)*1.414)
    sfx[s:e,0] += y[:e-s,0]*g*gl; sfx[s:e,1] += y[:e-s,1]*g*gr
vp = np.percentile(np.abs(voice), 99.9)+1e-9
mix = voice + sfx*vp*(10**(getattr(m,'SFX_DB',-8)/20)); mix /= max(1.0, np.abs(mix).max()/0.97)
tmp = sys.argv[2]+'.tmp.wav'
w = wave.open(tmp,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(mix,-1,1)*32767).astype(np.int16).tobytes()); w.close()
subprocess.run(['ffmpeg','-v','error','-y','-i',tmp,'-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar',str(SR),sys.argv[2]], check=True); os.remove(tmp)
print('mix ok', len(m.SFX), 'sfx', round(m.TOTAL_SEC,2), 's')
