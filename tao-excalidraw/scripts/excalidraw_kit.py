"""Excalidraw 场景构建工具箱.

生成 .excalidraw 文件（schema version 2），可直接拖进 excalidraw.com 打开、
继续手改。所有元素都带完整字段，避免打开时报 "invalid element"。

用法::

    from excalidraw_kit import Scene, PALETTE

    s = Scene()
    s.title(0, 0, "标题")
    a = s.box(0, 100, 200, 80, "LLM", **PALETTE["blue"])
    b = s.box(320, 100, 200, 80, "Agent", **PALETTE["green"])
    s.connect(a, b, "加上工具")
    s.save("out.excalidraw")
"""

from __future__ import annotations

import json
import random
from pathlib import Path

# Excalidraw 手绘风默认色板：(stroke, background)
PALETTE = {
    "ink": {"stroke": "#1e1e1e", "bg": "transparent"},
    "gray": {"stroke": "#343a40", "bg": "#e9ecef"},
    "blue": {"stroke": "#1971c2", "bg": "#a5d8ff"},
    "green": {"stroke": "#2f9e44", "bg": "#b2f2bb"},
    "yellow": {"stroke": "#f08c00", "bg": "#ffec99"},
    "red": {"stroke": "#e03131", "bg": "#ffc9c9"},
    "violet": {"stroke": "#6741d9", "bg": "#d0bfff"},
}

FONT_HAND = 1   # Excalifont / Virgil，手绘体（中文自动回退到系统 CJK 字体）
FONT_NORMAL = 2  # Helvetica
FONT_CODE = 3   # Cascadia

LINE_HEIGHT = 1.25


def _rand() -> int:
    return random.randint(1, 2 ** 31 - 1)


def _id(prefix: str) -> str:
    return f"{prefix}-{random.randint(0, 2 ** 40):010x}"


def text_width(s: str, font_size: int) -> float:
    """粗略估算文本宽度：CJK 按 1 个字宽，ASCII 按 0.56 个字宽。"""
    width = 0.0
    for ch in s:
        width += 1.0 if ord(ch) > 0x2E7F else 0.56
    return width * font_size


def text_size(s: str, font_size: int) -> tuple[float, float]:
    lines = s.split("\n")
    w = max((text_width(line, font_size) for line in lines), default=0.0)
    h = len(lines) * font_size * LINE_HEIGHT
    return w, h


class Scene:
    """一张 Excalidraw 画布。"""

    def __init__(self, background: str = "#ffffff", seed: int = 20260819):
        random.seed(seed)
        self.elements: list[dict] = []
        self.background = background

    # ---------- 内部 ----------

    def _base(self, kind: str, x: float, y: float, w: float, h: float, **kw) -> dict:
        el = {
            "id": _id(kind[:4]),
            "type": kind,
            "x": round(x, 2),
            "y": round(y, 2),
            "width": round(w, 2),
            "height": round(h, 2),
            "angle": 0,
            "strokeColor": kw.get("stroke", "#1e1e1e"),
            "backgroundColor": kw.get("bg", "transparent"),
            "fillStyle": kw.get("fill_style", "solid"),
            "strokeWidth": kw.get("stroke_width", 2),
            "strokeStyle": kw.get("stroke_style", "solid"),
            "roughness": kw.get("roughness", 1),
            "opacity": kw.get("opacity", 100),
            "groupIds": list(kw.get("group_ids", [])),
            "frameId": None,
            "index": None,
            "roundness": kw.get("roundness", {"type": 3}),
            "seed": _rand(),
            "version": 1,
            "versionNonce": _rand(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
        }
        self.elements.append(el)
        return el

    def _label(self, container: dict, label: str, font_size: int,
               font_family: int, color: str) -> dict:
        w, h = text_size(label, font_size)
        el = {
            "id": _id("text"),
            "type": "text",
            "x": round(container["x"] + (container["width"] - w) / 2, 2),
            "y": round(container["y"] + (container["height"] - h) / 2, 2),
            "width": round(w, 2),
            "height": round(h, 2),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": 100,
            "groupIds": list(container["groupIds"]),
            "frameId": None,
            "index": None,
            "roundness": None,
            "seed": _rand(),
            "version": 1,
            "versionNonce": _rand(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "text": label,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": "center",
            "verticalAlign": "middle",
            "containerId": container["id"],
            "originalText": label,
            "lineHeight": LINE_HEIGHT,
            "autoResize": True,
        }
        container["boundElements"].append({"type": "text", "id": el["id"]})
        self.elements.append(el)
        return el

    # ---------- 图形 ----------

    def box(self, x, y, w, h, label=None, *, font_size=20,
            font_family=FONT_HAND, label_color="#1e1e1e", **kw) -> dict:
        el = self._base("rectangle", x, y, w, h, **kw)
        if label:
            self._label(el, label, font_size, font_family, label_color)
        return el

    def ellipse(self, x, y, w, h, label=None, *, font_size=20,
                font_family=FONT_HAND, label_color="#1e1e1e", **kw) -> dict:
        el = self._base("ellipse", x, y, w, h, **kw)
        if label:
            self._label(el, label, font_size, font_family, label_color)
        return el

    def diamond(self, x, y, w, h, label=None, *, font_size=18,
                font_family=FONT_HAND, label_color="#1e1e1e", **kw) -> dict:
        el = self._base("diamond", x, y, w, h, **kw)
        if label:
            self._label(el, label, font_size, font_family, label_color)
        return el

    # ---------- 文字 ----------

    def text(self, x, y, s, *, size=20, align="left", family=FONT_HAND,
             color="#1e1e1e", opacity=100, group_ids=()) -> dict:
        w, h = text_size(s, size)
        if align == "center":
            x -= w / 2
        elif align == "right":
            x -= w
        el = {
            "id": _id("text"),
            "type": "text",
            "x": round(x, 2),
            "y": round(y, 2),
            "width": round(w, 2),
            "height": round(h, 2),
            "angle": 0,
            "strokeColor": color,
            "backgroundColor": "transparent",
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": "solid",
            "roughness": 1,
            "opacity": opacity,
            "groupIds": list(group_ids),
            "frameId": None,
            "index": None,
            "roundness": None,
            "seed": _rand(),
            "version": 1,
            "versionNonce": _rand(),
            "isDeleted": False,
            "boundElements": [],
            "updated": 1,
            "link": None,
            "locked": False,
            "text": s,
            "fontSize": size,
            "fontFamily": family,
            "textAlign": align if align in ("left", "center", "right") else "left",
            "verticalAlign": "top",
            "containerId": None,
            "originalText": s,
            "lineHeight": LINE_HEIGHT,
            "autoResize": True,
        }
        self.elements.append(el)
        return el

    def title(self, x, y, s, *, size=36, sub=None, sub_size=18,
              color="#1e1e1e", sub_color="#5c5f66") -> None:
        self.text(x, y, s, size=size, align="center", color=color)
        if sub:
            self.text(x, y + size * LINE_HEIGHT + 12, sub,
                      size=sub_size, align="center", color=sub_color)

    # ---------- 连线 ----------

    def arrow(self, pts, *, label=None, label_size=16, dashed=False,
              stroke="#1e1e1e", label_color=None, curved=False,
              start_head=None, end_head="arrow", group_ids=()) -> dict:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x0, y0 = pts[0]
        el = self._base(
            "arrow", x0, y0, max(xs) - min(xs), max(ys) - min(ys),
            stroke=stroke, bg="transparent",
            stroke_style="dashed" if dashed else "solid",
            roundness={"type": 2} if curved else None,
            group_ids=group_ids,
        )
        el["points"] = [[round(p[0] - x0, 2), round(p[1] - y0, 2)] for p in pts]
        el["lastCommittedPoint"] = None
        el["startBinding"] = None
        el["endBinding"] = None
        el["startArrowhead"] = start_head
        el["endArrowhead"] = end_head
        el["elbowed"] = False
        if label:
            mid = pts[len(pts) // 2] if len(pts) > 2 else (
                (pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
            self.text(mid[0], mid[1] - label_size * 1.6, label,
                      size=label_size, align="center",
                      color=label_color or stroke, group_ids=group_ids)
        return el

    def line(self, pts, *, stroke="#adb5bd", dashed=False, stroke_width=2,
             group_ids=()) -> dict:
        el = self.arrow(pts, stroke=stroke, dashed=dashed, end_head=None,
                        group_ids=group_ids)
        el["type"] = "line"
        el["strokeWidth"] = stroke_width
        return el

    def hrule(self, x1, x2, y, *, stroke="#dee2e6", dashed=True) -> dict:
        el = self.arrow([(x1, y), (x2, y)], stroke=stroke, dashed=dashed,
                        end_head=None)
        el["strokeWidth"] = 1
        return el

    # ---------- 组合件 ----------

    def card(self, x, y, w, h, heading, body, *, heading_size=22,
             body_size=15, body_color="#495057", **kw) -> dict:
        """带标题和正文的卡片，正文左对齐排在标题下方。"""
        el = self._base("rectangle", x, y, w, h, **kw)
        self.text(x + w / 2, y + 16, heading, size=heading_size, align="center",
                  color=kw.get("stroke", "#1e1e1e"))
        self.text(x + 18, y + 16 + heading_size * LINE_HEIGHT + 10, body,
                  size=body_size, color=body_color)
        return el

    def person(self, cx, cy, *, scale=1.0, label=None, stroke="#1e1e1e",
               bg="#ffec99", label_size=18, label_color="#1e1e1e") -> dict:
        """火柴人 / 头像：一个圆脑袋加一个身体，用来表示「人」或「实习生」。"""
        gid = _id("grp")
        head_r = 44 * scale
        self._base("ellipse", cx - head_r, cy - head_r * 2.1, head_r * 2,
                   head_r * 2, stroke=stroke, bg=bg, group_ids=[gid])
        body = self._base("ellipse", cx - head_r * 1.55, cy + 2,
                          head_r * 3.1, head_r * 2.4, stroke=stroke, bg=bg,
                          group_ids=[gid])
        body["roundness"] = {"type": 2}
        if label:
            self.text(cx, cy + head_r * 2.6, label, size=label_size,
                      align="center", color=label_color, group_ids=[gid])
        return body

    def sticky(self, x, y, w, h, body, *, size=16, color="#1e1e1e", **kw) -> dict:
        """便签：淡色底 + 左对齐正文，用来放旁白/注解。"""
        kw.setdefault("bg", "#fff9db")
        kw.setdefault("stroke", "#f5c451")
        el = self._base("rectangle", x, y, w, h, **kw)
        _, th = text_size(body, size)
        self.text(x + 16, y + (h - th) / 2, body, size=size, color=color)
        return el

    # ---------- 输出 ----------

    def to_dict(self) -> dict:
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://github.com/jesse87wang-bit/TAOSkills",
            "elements": self.elements,
            "appState": {
                "gridSize": None,
                "gridStep": 5,
                "gridModeEnabled": False,
                "viewBackgroundColor": self.background,
            },
            "files": {},
        }

    def save(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(self.to_dict(), ensure_ascii=False, indent=2),
                     encoding="utf-8")
        return p

    def bbox(self) -> tuple[float, float, float, float]:
        xs, ys, xe, ye = [], [], [], []
        for el in self.elements:
            xs.append(el["x"])
            ys.append(el["y"])
            xe.append(el["x"] + el["width"])
            ye.append(el["y"] + el["height"])
        return min(xs), min(ys), max(xe), max(ye)
