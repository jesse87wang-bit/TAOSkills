# -*- coding: utf-8 -*-
"""口播稿《看完这篇，AI 圈再扔什么新词你都不会懵》→ Excalidraw 分镜。

    python3 build_scenes.py
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "tao-excalidraw" / "scripts"))

from excalidraw_kit import PALETTE, Scene, text_size  # noqa: E402

INK, GRAY = "#1e1e1e", "#5c5f66"
MUTED = "#868e96"
OUT = HERE


def cover():
    s = Scene()
    s.title(800, 60, "AI 圈的六个词，一家公司讲明白",
            sub="LLM · Prompt · Context · Agent · Skill · MCP")

    frame = s.box(55, 240, 1490, 300, stroke="#adb5bd", bg="transparent",
                  stroke_style="dashed")
    frame["strokeWidth"] = 1
    s.text(85, 260, "你的 AI 公司", size=20, color=MUTED)

    chips = [
        ("LLM", "实习生", "violet"),
        ("Prompt", "任务指令", "blue"),
        ("Context", "背景资料", "blue"),
        ("Agent", "助理", "green"),
        ("Skill", "操作手册", "yellow"),
        ("MCP", "万能转接头", "red"),
    ]
    x = 80
    for name, role, color in chips:
        s.box(x, 320, 220, 110, name, font_size=26, **PALETTE[color])
        s.text(x + 110, 445, role, size=17, align="center", color=GRAY)
        x += 245

    s.sticky(430, 600, 740, 90,
             "一个朋友看了三个月 AI 内容，到现在没搞明白这些词什么意思。\n"
             "我说这样，你把它想象成一家公司。", size=18)
    return s


def scene_llm():
    s = Scene()
    s.title(800, 40, "① LLM 大模型 = 刚入职的实习生")

    s.ellipse(80, 280, 340, 230, "全世界\n绝大部分的书", font_size=22,
              **PALETTE["violet"])
    s.arrow([(440, 395), (620, 395)], label="全都读过", label_size=16)

    s.person(800, 340, scale=1.0, label="实习生", label_size=22,
             bg=PALETTE["yellow"]["bg"], stroke=PALETTE["yellow"]["stroke"])

    s.card(1080, 250, 460, 150, "知识储备 ✅ 拉满",
           "上知天文下知地理\n能写方案，能分析问题", body_size=17, **PALETTE["green"])
    s.card(1080, 440, 460, 180, "工作经验 ❌ 为零",
           "不了解你的业务\n不认识你的客户\n不知道你怎么做事", body_size=17, **PALETTE["red"])

    s.sticky(300, 690, 940, 90,
             "ChatGPT、Claude、DeepSeek —— 全是这种人。", size=20)
    return s


def scene_prompt():
    s = Scene()
    s.title(800, 40, "② Prompt 提示词 = 你下的任务指令")

    s.box(80, 220, 420, 130, "「写个方案」", font_size=24, **PALETTE["red"])
    s.arrow([(510, 285), (640, 285)])
    s.box(650, 225, 300, 120, "同一个 LLM", font_size=20, **PALETTE["gray"])
    s.arrow([(960, 285), (1090, 285)])
    s.box(1100, 220, 420, 130, "一堆废话", font_size=24, **PALETTE["red"])

    s.box(80, 450, 420, 190, "「500 字\n三个竞品对比\n一个行动建议」",
          font_size=22, **PALETTE["green"])
    s.arrow([(510, 545), (640, 545)])
    s.box(650, 485, 300, 120, "同一个 LLM", font_size=20, **PALETTE["gray"])
    s.arrow([(960, 545), (1090, 545)])
    s.box(1100, 480, 420, 130, "像模像样的方案", font_size=24,
          **PALETTE["green"])

    s.hrule(80, 1520, 400)
    s.sticky(300, 710, 1000, 100,
             "垃圾指令进，垃圾结果出。\n未来一个很重要的能力，就是把问题说清楚。",
             size=20)
    return s


def scene_context():
    s = Scene()
    s.title(800, 40, "③ Context 上下文 = 你给的背景资料",
            sub="去年的数据 · 竞品的官网 · 之前的讨论记录")

    bar_x, bar_w, bar_h = 380, 700, 76
    rows = [
        ("资料给少了", 0.28, "它不懂你", "red"),
        ("资料刚刚好", 1.00, "结果最好", "green"),
        ("资料给太多", 1.34, "前面的它就忘了", "red"),
    ]
    y = 220
    for label, ratio, verdict, color in rows:
        s.text(340, y + 24, label, size=20, align="right", color=INK)
        s.box(bar_x, y, bar_w, bar_h, stroke="#adb5bd", bg="transparent")
        fill_w = min(ratio, 1.0) * bar_w
        s.box(bar_x + 2, y + 2, fill_w - 4, bar_h - 4, **PALETTE[color])
        if ratio > 1.0:
            over = s.box(bar_x + bar_w + 10, y + 2, (ratio - 1.0) * bar_w,
                         bar_h - 4, stroke="#e03131", bg="#ffc9c9",
                         stroke_style="dashed", opacity=55)
            over["strokeWidth"] = 1
            s.text(bar_x + bar_w + 20 + (ratio - 1.0) * bar_w / 2, y + bar_h + 14,
                   "溢出 = 忘掉", size=15, align="center", color="#e03131")
        s.text(1380, y + 24, "→  " + verdict, size=20, color=GRAY)
        y += 150

    s.text(bar_x + bar_w / 2, 180, "AI 一次能记住的上下文是有限的", size=18,
           align="center", color=MUTED)
    s.sticky(300, 700, 1000, 100,
             "很多时候 AI 做不好，不是它不聪明，是信息没给够。", size=20)
    return s


def scene_agent():
    s = Scene()
    s.title(800, 40, "④ Agent 智能体 = 实习生 + 工具 + 权限")

    # --- 以前 ---
    s.text(80, 170, "以前：你一步一步盯着", size=22, color=MUTED)
    s.box(120, 230, 150, 100, "你", font_size=24, **PALETTE["blue"])
    s.box(520, 230, 200, 100, "实习生", font_size=22, **PALETTE["yellow"])
    for i, step in enumerate(("第 1 步", "第 2 步", "第 3 步")):
        yy = 250 + i * 30
        s.arrow([(280, yy), (510, yy)], label=None)
        s.text(395, yy - 22, step, size=14, align="center", color=MUTED)
    s.sticky(800, 235, 620, 90, "每一步都得在旁边说 —— 太累了。", size=19,
             bg="#ffe3e3", stroke="#ffa8a8")
    s.hrule(80, 1520, 400)

    # --- 现在 ---
    s.text(80, 440, "现在：给他电脑、软件、权限", size=22, color=MUTED)
    s.box(120, 560, 150, 100, "你", font_size=24, **PALETTE["blue"])
    s.arrow([(280, 610), (470, 610)])
    s.text(375, 566, "「帮我分析竞争对手」", size=15, align="center", color=GRAY)

    agent = s.box(480, 490, 780, 250, stroke="#2f9e44", bg="#ebfbee",
                  stroke_style="dashed")
    agent["strokeWidth"] = 1
    s.text(510, 508, "Agent", size=22, color="#2f9e44")
    s.box(520, 570, 200, 90, "自己搜索", font_size=19, **PALETTE["green"])
    s.arrow([(730, 615), (790, 615)])
    s.box(800, 570, 200, 90, "自己整理", font_size=19, **PALETTE["green"])
    s.arrow([(1010, 615), (1070, 615)])
    s.box(1080, 570, 160, 90, "出报告", font_size=19, **PALETTE["green"])
    s.arrow([(1270, 610), (1370, 610)])
    s.box(1380, 560, 150, 100, "报告", font_size=22, **PALETTE["gray"])
    s.text(870, 700, "全程不烦你", size=17, align="center", color="#2f9e44")

    s.sticky(230, 790, 1140, 100,
             "大模型是「我知道很多」，Agent 是「我帮你把事做完」。\n"
             "过去是人使用软件，未来越来越像人管理 AI 员工。", size=19)
    return s


def scene_skill():
    s = Scene()
    s.title(800, 40, "⑤ Skill 技能 = 助理的标准操作手册")

    s.text(240, 170, "反复出现的任务类型", size=20, align="center", color=MUTED)
    for i, name in enumerate(("市场分析", "客户跟进", "周报")):
        s.box(90, 220 + i * 110, 300, 84, name, font_size=21, **PALETTE["gray"])

    s.arrow([(420, 350), (620, 350)], curved=False)
    s.text(520, 300, "花一个下午\n写成 SOP", size=16, align="center", color=GRAY)

    s.text(940, 170, "写下来的手册", size=20, align="center", color=MUTED)
    books = ("《市场分析怎么做》", "《客户跟进怎么处理》", "《周报怎么生成》")
    for i, name in enumerate(books):
        s.box(660, 220 + i * 110, 560, 84, name, font_size=21,
              **PALETTE["yellow"])

    s.box(300, 580, 220, 100, "Agent", font_size=24, **PALETTE["green"])
    s.arrow([(530, 630), (640, 630)], label="接到任务", label_size=15)
    s.sticky(650, 575, 680, 110,
             "翻开手册照着做：\n不用你重复教，不会漏步骤。", size=19)
    return s


def scene_mcp():
    s = Scene()
    s.title(800, 40, "⑥ MCP = 万能转接头")

    div = s.line([(800, 150), (800, 830)], stroke="#dee2e6", dashed=True)
    div["strokeWidth"] = 1

    # --- 以前 ---
    s.text(400, 165, "以前：一个系统一根线", size=22, align="center",
           color=MUTED)
    s.box(60, 340, 190, 100, "Agent", font_size=22, **PALETTE["green"])
    sys_left = (("携程系统", 220, "red"), ("邮箱", 340, "blue"),
                ("搜索引擎", 460, "violet"))
    for name, yy, color in sys_left:
        s.box(540, yy, 200, 84, name, font_size=19, **PALETTE[color])
        a = s.arrow([(260, 390), (400, yy + 42), (530, yy + 42)],
                    stroke=PALETTE[color]["stroke"], curved=True)
        a["strokeStyle"] = "dashed" if color == "blue" else "solid"
        a["strokeWidth"] = 3 if color == "violet" else 2
    s.sticky(60, 600, 680, 130,
             "每个系统接口都不一样，\n每接一个都得重新开发 ——\n"
             "像出差带了五根不同的充电线。", size=18,
             bg="#ffe3e3", stroke="#ffa8a8")

    # --- 现在 ---
    s.text(1200, 165, "现在：一根线插所有设备", size=22, align="center",
           color=MUTED)
    s.box(850, 340, 180, 100, "Agent", font_size=22, **PALETTE["green"])
    s.arrow([(1040, 390), (1120, 390)], stroke="#6741d9")
    s.box(1130, 330, 170, 120, "MCP", font_size=26, **PALETTE["violet"])
    for name, yy, _c in sys_left:
        s.box(1400, yy, 160, 84, name, font_size=18, **PALETTE["gray"])
        s.arrow([(1310, 390), (1360, yy + 42), (1390, yy + 42)],
                stroke="#6741d9", curved=True)
    s.sticky(850, 600, 690, 130,
             "Agent 不需要知道每个系统怎么运作，\n它只跟 MCP 对话 ——\n"
             "订机票、发邮件、查数据，一个接口搞定。", size=18)
    return s


def scene_summary():
    s = Scene()
    s.title(800, 50, "一家公司，六个角色",
            sub="装进脑子里，以后再扔什么新词，你都能自己往里套")

    rows = [
        ("LLM", "读遍天下书的实习生", "violet"),
        ("Prompt", "你下的指令", "blue"),
        ("Context", "你给的背景资料", "blue"),
        ("Agent", "升级成能独当一面的助理", "green"),
        ("Skill", "助理的标准操作手册", "yellow"),
        ("MCP", "连接所有外部工具的万能转接头", "red"),
    ]
    y = 200
    for name, desc, color in rows:
        s.box(380, y, 250, 84, name, font_size=24, **PALETTE[color])
        s.text(660, y + 26, "—  " + desc, size=24, color=INK)
        y += 105

    s.sticky(380, 850, 900, 80, "下期聊聊：这些角色怎么改变一家公司的组织和生意。",
             size=19)
    return s


SCENES = [
    ("00-cover", "封面 · 把 AI 想象成一家公司", cover),
    ("01-llm", "LLM = 刚入职的实习生", scene_llm),
    ("02-prompt", "Prompt = 你下的任务指令", scene_prompt),
    ("03-context", "Context = 你给的背景资料", scene_context),
    ("04-agent", "Agent = 实习生 + 工具 + 权限", scene_agent),
    ("05-skill", "Skill = 标准操作手册", scene_skill),
    ("06-mcp", "MCP = 万能转接头", scene_mcp),
    ("07-summary", "总结 · 六个角色", scene_summary),
]

COLS, GAP = 2, 240


def build_combined(paths):
    """把各分镜平铺到一张总画布上，方便整体过稿。"""
    scenes = [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]
    merged, cursor_y, row_h = [], 0.0, 0.0
    col_w = 0.0
    for sc in scenes:
        els = sc["elements"]
        col_w = max(col_w, max(e["x"] + e["width"] for e in els)
                    - min(e["x"] for e in els))
    for i, (sc, (slug, caption, _)) in enumerate(zip(scenes, SCENES)):
        els = sc["elements"]
        minx = min(e["x"] for e in els)
        miny = min(e["y"] for e in els)
        maxy = max(e["y"] + e["height"] for e in els)
        col, row = i % COLS, i // COLS
        if col == 0 and i:
            cursor_y += row_h + GAP
            row_h = 0.0
        row_h = max(row_h, maxy - miny + 90)
        dx = col * (col_w + GAP) - minx
        dy = cursor_y + 90 - miny
        for e in els:
            e["x"] += dx
            e["y"] += dy
            if e["type"] in ("arrow", "line"):
                pass  # points 是相对坐标，随 x/y 平移即可
            merged.append(e)
        head = Scene()
        head.text(col * (col_w + GAP), cursor_y + 10,
                  f"{slug}  ·  {caption}", size=26, color="#868e96")
        merged.extend(head.elements)
    out = {
        "type": "excalidraw", "version": 2,
        "source": "https://github.com/jesse87wang-bit/TAOSkills",
        "elements": merged,
        "appState": {"gridSize": None, "gridStep": 5, "gridModeEnabled": False,
                     "viewBackgroundColor": "#ffffff"},
        "files": {},
    }
    p = OUT / "all-scenes.excalidraw"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def main():
    paths = []
    for slug, caption, fn in SCENES:
        p = fn().save(OUT / f"{slug}.excalidraw")
        paths.append(p)
        print(f"  {p.name:26} {caption}")
    print(f"  {build_combined(paths).name:26} 全部分镜（总览）")


if __name__ == "__main__":
    main()
