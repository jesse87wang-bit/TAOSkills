"""把 .excalidraw 渲染成 SVG 预览图（近似，用于快速过稿）。

不追求还原 Excalidraw 的手绘抖动，只保证版式、文字、连线位置准确，
方便在浏览器 / PR 里直接看分镜对不对。最终定稿仍以 excalidraw.com 打开为准。

    python3 render_preview.py scene.excalidraw            -> scene.svg
    python3 render_preview.py a.excalidraw b.excalidraw -o out/
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.sax.saxutils import escape

FONT_STACK = {
    1: "'Excalifont','Virgil','Segoe UI','PingFang SC','Hiragino Sans GB',"
       "'Microsoft YaHei',sans-serif",
    2: "'Helvetica Neue',Helvetica,'PingFang SC','Microsoft YaHei',sans-serif",
    3: "'Cascadia Code',Consolas,'Microsoft YaHei',monospace",
}
PAD = 48


def _stroke_dash(el: dict) -> str:
    style = el.get("strokeStyle", "solid")
    w = el.get("strokeWidth", 2)
    if style == "dashed":
        return f' stroke-dasharray="{w * 4},{w * 3}"'
    if style == "dotted":
        return f' stroke-dasharray="{w},{w * 2}"'
    return ""


def _fill(el: dict) -> str:
    bg = el.get("backgroundColor", "transparent")
    return "none" if bg in ("transparent", None) else bg


def _text_anchor(el: dict) -> tuple[str, float]:
    align = el.get("textAlign", "left")
    if align == "center":
        return "middle", el["x"] + el["width"] / 2
    if align == "right":
        return "end", el["x"] + el["width"]
    return "start", el["x"]


def render_elements(elements: list[dict], bg: str) -> str:
    live = [e for e in elements if not e.get("isDeleted")]
    if not live:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"/>'

    x0 = min(e["x"] for e in live) - PAD
    y0 = min(e["y"] for e in live) - PAD
    x1 = max(e["x"] + e["width"] for e in live) + PAD
    y1 = max(e["y"] + e["height"] for e in live) + PAD
    w, h = x1 - x0, y1 - y0

    out: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.1f} {y0:.1f} '
        f'{w:.1f} {h:.1f}" width="{w:.0f}" height="{h:.0f}">',
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0,1 L9,5 L0,9" fill="none" stroke="context-stroke" '
        'stroke-width="1.6"/></marker></defs>',
        f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'fill="{bg}"/>',
    ]

    for el in live:
        t = el["type"]
        sc = el.get("strokeColor", "#1e1e1e")
        sw = el.get("strokeWidth", 2)
        op = el.get("opacity", 100) / 100
        common = (f' stroke="{sc}" stroke-width="{sw}" opacity="{op}"'
                  f'{_stroke_dash(el)}')

        if t == "rectangle":
            r = 12 if el.get("roundness") else 0
            out.append(f'<rect x="{el["x"]:.1f}" y="{el["y"]:.1f}" '
                       f'width="{el["width"]:.1f}" height="{el["height"]:.1f}" '
                       f'rx="{r}" fill="{_fill(el)}"{common}/>')
        elif t == "ellipse":
            out.append(f'<ellipse cx="{el["x"] + el["width"] / 2:.1f}" '
                       f'cy="{el["y"] + el["height"] / 2:.1f}" '
                       f'rx="{el["width"] / 2:.1f}" ry="{el["height"] / 2:.1f}" '
                       f'fill="{_fill(el)}"{common}/>')
        elif t == "diamond":
            cx, cy = el["x"] + el["width"] / 2, el["y"] + el["height"] / 2
            pts = (f'{cx:.1f},{el["y"]:.1f} '
                   f'{el["x"] + el["width"]:.1f},{cy:.1f} '
                   f'{cx:.1f},{el["y"] + el["height"]:.1f} '
                   f'{el["x"]:.1f},{cy:.1f}')
            out.append(f'<polygon points="{pts}" fill="{_fill(el)}"{common}/>')
        elif t in ("arrow", "line"):
            pts = " ".join(f'{el["x"] + px:.1f},{el["y"] + py:.1f}'
                           for px, py in el.get("points", []))
            head = ' marker-end="url(#ah)"' if el.get("endArrowhead") else ""
            start = ' marker-start="url(#ah)"' if el.get("startArrowhead") else ""
            out.append(f'<polyline points="{pts}" fill="none"'
                       f'{common}{head}{start} stroke-linecap="round" '
                       f'stroke-linejoin="round"/>')
        elif t == "text":
            size = el.get("fontSize", 20)
            family = FONT_STACK.get(el.get("fontFamily", 1), FONT_STACK[1])
            anchor, tx = _text_anchor(el)
            lines = el.get("text", "").split("\n")
            # SVG 基线在字身底部，这里把首行基线放在文字块顶部往下 ~0.82em
            base = el["y"] + size * 0.82
            out.append(f'<text x="{tx:.1f}" y="{base:.1f}" fill="{sc}" '
                       f'font-family="{family}" font-size="{size}" '
                       f'text-anchor="{anchor}" opacity="{op}" '
                       f'style="white-space:pre">')
            for i, ln in enumerate(lines):
                dy = 0 if i == 0 else size * el.get("lineHeight", 1.25)
                out.append(f'<tspan x="{tx:.1f}" dy="{dy:.1f}">'
                           f'{escape(ln) or " "}</tspan>')
            out.append("</text>")

    out.append("</svg>")
    return "".join(out)


def render_file(src: Path, dst: Path) -> Path:
    data = json.loads(src.read_text(encoding="utf-8"))
    bg = data.get("appState", {}).get("viewBackgroundColor", "#ffffff")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render_elements(data["elements"], bg), encoding="utf-8")
    return dst


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+")
    ap.add_argument("-o", "--out-dir")
    args = ap.parse_args()
    for raw in args.inputs:
        src = Path(raw)
        out_dir = Path(args.out_dir) if args.out_dir else src.parent
        print(render_file(src, out_dir / (src.stem + ".svg")))


if __name__ == "__main__":
    main()
