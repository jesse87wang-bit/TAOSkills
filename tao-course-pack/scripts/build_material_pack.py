#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tao-course-pack · 第一步产出：《讲师上课材料包》Word

用法：
    python3 build_material_pack.py course.json 输出.docx [--md 输出.md]

course.json 结构（字段都可选，除了 title、pages、modules）：
{
  "title": "《课程名》第X期·XX班（V1.0） 讲师上课材料包",
  "date_line": "2026年12月8—9日 · 地点 · 人数",
  "intro": ["本材料包按……编写……"],
  "urgent": {"title": "先办的一件事", "md": "……"},
  "pre_sections": [{"title": "11月24日新课件核对结果", "md": "……"}],
  "diff": {"title": "和上一版的不同", "head": [...], "rows": [[...]]},
  "audience": {"intro": "...", "head": [...], "rows": [[...]], "outro": "..."},
  "structure": {"head": [...], "rows": [[...]]},
  "numbering": "编号约定：……",
  "pages": [ {p,t,min,sec,type,say,act,assets:[{n,f,k}],task,fb,cold,fix,brk,start,end,time,day} ... ],
  "modules": [
     {"title": "讲师逐字讲稿·开场与模块一（8日14:00—15:00）", "goal": "这一小时要……",
      "train": "转训提示……",
      "sections": [{"no": "1.1", "title": "开场：……", "pages": [1, 2], "extra_md": "可选：本节附表"}]}
  ],
  "default_fb": "保留当前课件，按讲稿继续；台上不排障。",
  "after_part1_md": "开场逐字稿等附录（markdown）",
  "parts": [{"title": "第二部分 提示词全集", "md": "……"}]
}

排版规则（和上一版材料包一致）：
- 讲稿按小节写，一节覆盖几页 PPT；每节：【PPT】一行 → 口播（引用块，可直接念）→【学员】【演示/讲师动作】【素材】【翻车预案】【冷场】；
  每个模块末尾一句【转训提示】。
- 逐页的「课前核对」不散在讲稿里，统一收进第一部分末尾一张表。
- 时间轴按小节一行，课间单列。
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "assets", "reference.docx")


def jn(items):
    """拼接多段文字：前一段已以句末标点结尾就不再加分号。"""
    out = ""
    for t in dict.fromkeys(t.strip() for t in items if t and t.strip()):
        if out:
            out += "" if out[-1] in "。！？；）」”" else "；"
        out += t
    return out

def cell(x):
    return str(x).replace("|", "／").replace("\n", "<br>")


def table(head, rows):
    out = "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n"
    for r in rows:
        out += "| " + " | ".join(cell(c) for c in r) + " |\n"
    return out + "\n"


def speech_lines(say):
    """把讲稿拆成：动作行（【】开头且通篇是动作）和口播行（引用块）。"""
    out = []
    for ln in say.split("\n"):
        ln = ln.strip()
        if not ln:
            continue
        if ln.startswith("【") and "】" in ln and not re.search(r"[“”]", ln):  # 【】开头且不含引语：动作行
            out.append(("act", ln))
            continue
        if ln.startswith("“") and ln.endswith("”") and ln.count("“") == 1:
            ln = ln[1:-1]
        out.append(("say", ln))
    return out


def build_md(c):
    P = {x["p"]: x for x in c["pages"]}
    dfb = c.get("default_fb", "保留当前课件，按讲稿继续；台上不排障。")
    o = []
    o.append("---\ntitle: %s\nsubtitle: %s\n---\n\n" % (json.dumps(c["title"], ensure_ascii=False), json.dumps(c.get("date_line", ""), ensure_ascii=False)))

    # ---------- 使用说明 ----------
    o.append("# 使用说明、受众差异与课堂时间轴\n\n")
    for para in c.get("intro", []):
        o.append(para + "\n\n")
    if c.get("urgent"):
        o.append("## %s\n\n%s\n\n" % (c["urgent"]["title"], c["urgent"]["md"]))
    for s in c.get("pre_sections", []):
        o.append("## %s\n\n%s\n\n" % (s["title"], s["md"]))
    if c.get("diff"):
        d = c["diff"]; o.append("## %s\n\n" % d["title"] + table(d["head"], d["rows"]))
    if c.get("audience"):
        a = c["audience"]
        o.append("## 受众画像与说话方式\n\n%s\n\n" % a.get("intro", "") + table(a["head"], a["rows"]) + a.get("outro", "") + "\n\n")
    if c.get("structure"):
        s = c["structure"]; o.append("## 材料包结构\n\n" + table(s["head"], s["rows"]))

    # 时间轴：按小节
    rows = []
    for m in c["modules"]:
        for s in m["sections"]:
            a, b = s["pages"][0], s["pages"][-1]
            pa, pb = P[a], P[b]
            if a in c.get("day_starts", []):
                rows.append(("", "**%s**" % pa["day"], "", ""))
            tasks = jn(P[i]["task"] for i in range(a, b + 1) if P[i].get("task")) or "听／看"
            mats = "、".join(dict.fromkeys(x["n"].split("（")[0] for i in range(a, b + 1) for x in P[i]["assets"])) or "PPT"
            rows.append(("%s—%s" % (pa["start"], pb["end"]), "%s %s" % (s["no"], s["title"]), tasks, mats))
            for i in range(a, b + 1):
                if P[i].get("brkTime"):
                    rows.append((P[i]["brkTime"], "课间／机动", "—", "—"))
    o.append("## 分钟级课堂时间轴\n\n" + table(["时间", "环节（小节）", "学员在做什么", "材料"], rows))
    if c.get("numbering"):
        o.append(c["numbering"] + "\n\n")

    # ---------- 第一部分 讲稿 ----------
    checks = []
    o.append("# 第一部分 讲师逐字讲稿\n\n")
    for m in c["modules"]:
        o.append("## %s\n\n" % m["title"])
        if m.get("goal"):
            o.append(m["goal"] + "\n\n")
        for s in m["sections"]:
            a, b = s["pages"][0], s["pages"][-1]
            pages = [P[i] for i in range(a, b + 1)]
            prange = "P%d" % a if a == b else "P%d—P%d" % (a, b)
            o.append("### %s %s（%s—%s，%s）\n\n" % (s["no"], s["title"], pages[0]["start"], pages[-1]["end"], prange))
            o.append("【PPT】" + "；".join("P%d %s" % (x["p"], x["t"]) for x in pages) + "\n\n")
            for x in pages:
                if len(pages) > 1:
                    o.append("【翻到 P%d】\n\n" % x["p"])
                for kind, ln in speech_lines(x["say"]):
                    o.append(("> " + ln + "\n\n") if kind == "say" else (ln + "\n\n"))
                if x.get("task"):
                    o.append("【学员】%s\n\n" % x["task"])
                if x.get("act"):
                    o.append("【讲师动作】%s\n\n" % x["act"].replace("\n", "；"))
                if x.get("countdown"):
                    o.append("【计时】授课台点「投屏倒计时 %d 分钟」。\n\n" % x["countdown"])
                if x.get("brkTime"):
                    o.append("*课间／机动 %s*\n\n" % x["brkTime"])
            mats = [y for x in pages for y in x["assets"]]
            if mats:
                o.append("【素材】" + "；".join("%s（`%s`）" % (y["n"], y["f"]) for y in mats) + "\n\n")
            fbs = list(dict.fromkeys("P%d：%s" % (x["p"], x["fb"]) for x in pages if x.get("fb") and x["fb"] != dfb))
            if fbs:
                o.append("【翻车预案】" + ("；".join(f.rstrip("。；") for f in fbs) + "。" if len(fbs) > 1 else fbs[0].split("：", 1)[1]) + "\n\n")
            colds = [x["cold"] for x in pages if x.get("cold")]
            if colds:
                o.append("【冷场】" + jn(colds) + "\n\n")
            if s.get("extra_md"):
                o.append(s["extra_md"] + "\n\n")
            for x in pages:
                if x.get("fix"):
                    checks.append(("P%d" % x["p"], x["t"], x["fix"]))
        if m.get("train"):
            o.append("【转训提示】%s\n\n" % m["train"])
    if checks:
        o.append("## 本部分的课前核对\n\n" + table(["页", "标题", "要核对的事"], checks))
    if c.get("after_part1_md"):
        o.append(c["after_part1_md"] + "\n\n")

    for part in c.get("parts", []):
        o.append("# %s\n\n%s\n\n" % (part["title"], part["md"]))

    md = "".join(o)
    md = re.sub(r"_{2,}", lambda m: "＿" * len(m.group(0)), md)  # 填空横线，避免被当成斜体
    # 段落后紧跟列表时补空行，否则 pandoc 会把列表并进段落
    md = re.sub(r"(?m)^([^\n|>#\-\d\s][^\n]*)\n(- |\d+\. )", r"\1\n\n\2", md)
    return fit_tables(md)


def _w(text):
    """显示宽度：中文算2，英文数字算1。"""
    return sum(2 if ord(ch) > 0x2E80 else 1 for ch in text)


def fit_tables(md):
    """按每列内容的长短重排表格分隔行的横线数，pandoc 据此给列宽（内容多的列宽，短的窄）。"""
    lines = md.split("\n")
    i = 0
    while i < len(lines) - 1:
        if lines[i].startswith("|") and re.match(r"^\|(\s*:?-+:?\s*\|)+\s*$", lines[i + 1]):
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            rows = [[x.strip() for x in l.strip().strip("|").split("|")] for l in [lines[i]] + lines[i + 2:j]]
            n = len(rows[0])
            ws = []
            for k in range(n):
                vals = [_w(r[k]) for r in rows if k < len(r)]
                avg = sum(vals) / len(vals)
                ws.append(max(14.0, min(55.0, (avg + max(vals)) / 2)))
            tot = sum(ws)
            lines[i + 1] = "|" + "|".join("-" * max(3, round(w / tot * 100)) for w in ws) + "|"
            i = j
        else:
            i += 1
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    c = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    md = build_md(c)
    mdp = sys.argv[sys.argv.index("--md") + 1] if "--md" in sys.argv else out.rsplit(".", 1)[0] + ".md"
    open(mdp, "w", encoding="utf-8").write(md)
    # --columns 很小：让所有表格都按分隔行横线比例分配列宽、占满版心（和上一版材料包一致）；不加目录
    subprocess.run(["pandoc", mdp, "-f", "markdown-auto_identifiers", "-o", out, "--columns=20", "--reference-doc", REF], check=True)
    print("ok", out, len(md))


if __name__ == "__main__":
    main()
