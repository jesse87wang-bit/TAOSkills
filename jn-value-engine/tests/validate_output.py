#!/usr/bin/env python3
import re, sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
errors=[]
heads=["01 决策结论","02 真正的问题","03 关键矛盾","04 方案对比","05 价值创造逻辑","06 建议路线图","07 关键验证指标","08 决策闸门","09 下一步行动 + 什么会让我改变判断"]

title = "企业价值引擎｜"
if title not in text: errors.append("TITLE")
else:
    prefix = text[:text.find(title)].replace("#", "").strip()
    if prefix: errors.append("USER_VISIBLE_PREAMBLE")
pos=[text.find(x) for x in heads]
for h,p in zip(heads,pos):
    if p<0: errors.append("MISSING:"+h)
if all(p>=0 for p in pos) and pos!=sorted(pos): errors.append("ORDER")

def section(a,b=None):
    s=text.find(a)
    if s<0:return ""
    e=text.find(b,s+len(a)) if b else len(text)
    return text[s:e if e>=0 else len(text)]

s4=section(heads[3],heads[4])
for x in ("A","B","C"):
    if not re.search(rf"(^|\n)\s*(?:方案\s*)?{x}(?:[：:、.\s]|$)",s4): errors.append("ABC:"+x)

s8=section(heads[7],heads[8])
gates=re.findall(r"(?:Gate|GATE|闸门)\s*[1-4]|[①②③④]",s8,re.I)
if len(set(gates))<4: errors.append("FOUR_GATES")

s9=section(heads[8])
if "下一步" not in s9: errors.append("NEXT_ACTION")
if not any(k in s9 for k in ["改变判断","反证","反转"]): errors.append("FALSIFICATION")

process_phrases = ["正在调用", "读取 Skill", "结构校验", "文字锁", "图片规范已锁定", "正在生成中", "完整交付已完成"]
for phrase in process_phrases:
    if phrase in text: errors.append("PROCESS_COMMENTARY:"+phrase)

print("PASS" if not errors else "FAIL\n"+"\n".join(errors))
sys.exit(0 if not errors else 1)
