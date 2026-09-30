# 语音识别（SenseVoice + silero VAD，逐字时间戳）与字幕对齐
import os, json, re, difflib, subprocess
from . import assets

def asr(video, out_json):
    import numpy as np, soundfile as sf, sherpa_onnx
    m = assets.models(); M = m['sense-voice']
    wav = os.path.splitext(out_json)[0] + '_16k.wav'
    subprocess.run(['ffmpeg','-v','error','-y','-i',video,'-vn','-ac','1','-ar','16000',wav], check=True)
    rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f"{M}/model.int8.onnx", tokens=f"{M}/tokens.txt", language="zh", use_itn=True, num_threads=4)
    audio, sr = sf.read(wav, dtype="float32")
    cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = m['silero_vad.onnx']
    cfg.silero_vad.min_silence_duration = 0.25; cfg.silero_vad.min_speech_duration = 0.2; cfg.silero_vad.max_speech_duration = 12; cfg.sample_rate = sr
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=600)
    segs = []; i = 0; w = cfg.silero_vad.window_size
    while i < len(audio):
        vad.accept_waveform(audio[i:i+w]); i += w
        while not vad.empty(): segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
    vad.flush()
    while not vad.empty(): segs.append((vad.front.start, np.array(vad.front.samples))); vad.pop()
    out = []
    for st, s in segs:
        stm = rec.create_stream(); stm.accept_waveform(sr, s); rec.decode_stream(stm); r = stm.result; t0 = st/sr
        out.append(dict(start=round(t0,2), end=round(t0+len(s)/sr,2), text=r.text, tokens=list(r.tokens), ts=[round(t0+x,2) for x in r.timestamps]))
        print(f"[{t0:7.2f}] {r.text}", flush=True)
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False)
    os.remove(wav)
    return out

_P = re.compile(r"[\s，。？、；！：“”,?!.]")

def align(asr_json, lines_txt, out_json):
    """校对过的字幕行（一行一句，≤16 字）对齐到逐字时间戳 → lines.json [[开始,结束,文字],...]
    同时写 *_chars.json（整篇去标点的字 + 每个字的时间），分镜表里的关键词卡点用它。"""
    with open(asr_json, encoding='utf-8') as f:
        d = json.load(f)
    A, T, SEG = [], [], []
    for si, s in enumerate(d):
        for tok, t in zip(s['tokens'], s['ts']):
            for c in tok.strip().lower(): A.append(c); T.append(t); SEG.append(si)
    with open(lines_txt, encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    B, BL = [], []
    for li, l in enumerate(lines):
        for c in l:
            if not _P.match(c): B.append(c.lower()); BL.append(li)
    sm = difflib.SequenceMatcher(None, A, B, autojunk=False); bt = [None]*len(B); bs = [None]*len(B)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n): bt[b+k] = T[a+k]; bs[b+k] = SEG[a+k]
    idx = [i for i, x in enumerate(bt) if x is not None]
    for i in range(len(bt)):
        if bt[i] is None:
            prev = max([j for j in idx if j < i], default=None); nxt = min([j for j in idx if j > i], default=None)
            if prev is None: bt[i], bs[i] = bt[nxt], bs[nxt]
            elif nxt is None: bt[i], bs[i] = bt[prev]+0.15*(i-prev), bs[prev]
            else: bt[i], bs[i] = bt[prev]+(bt[nxt]-bt[prev])*(i-prev)/(nxt-prev), bs[prev]
    out = []
    for li, l in enumerate(lines):
        ii = [i for i, x in enumerate(BL) if x == li]
        out.append([bt[ii[0]], min(bt[ii[-1]]+0.3, d[bs[ii[-1]]]['end']), l])
    for i in range(len(out)-1):
        if out[i][1] > out[i+1][0]-0.02 or out[i+1][0]-out[i][1] < 0.35: out[i][1] = out[i+1][0]-0.02
    out[0][0] = max(0, out[0][0]-0.1); out[-1][1] = d[-1]['end']+0.3
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump([[round(a,3), round(b,3), t] for a, b, t in out], f, ensure_ascii=False)
    with open(os.path.splitext(out_json)[0] + '_chars.json', 'w', encoding='utf-8') as f:
        json.dump({'chars': "".join(B), 'times': [round(x,3) for x in bt]}, f, ensure_ascii=False)
    for a, b, t in out: print(f"{a:7.2f}-{b:7.2f}  {t}")
    return out
