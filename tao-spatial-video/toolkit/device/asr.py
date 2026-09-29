# 语音识别（带逐字时间戳）。用法: python3 asr.py <原片> <输出asr.json>
# 模型：sherpa-onnx SenseVoice int8 + silero VAD（都在 GitHub releases，环境里一般能下）
import sys, os, json, subprocess, numpy as np, soundfile as sf, sherpa_onnx
W = os.path.expanduser('~/work/sv'); M = W+'/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09'
wav = W+'/_asr.wav'
subprocess.run(['ffmpeg','-v','error','-y','-i',sys.argv[1],'-vn','-ac','1','-ar','16000',wav], check=True)
rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f"{M}/model.int8.onnx", tokens=f"{M}/tokens.txt", language="zh", use_itn=True, num_threads=4)
audio, sr = sf.read(wav, dtype="float32")
cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = W+"/silero_vad.onnx"
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
    print(f"[{t0:7.2f}] {r.text}")
json.dump(out, open(sys.argv[2],'w'), ensure_ascii=False)
