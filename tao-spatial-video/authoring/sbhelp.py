def reveal(eid, pts, hdr, tail, at):
    """pts=[(内容区内 y, 时刻), ...]：第一段在 at 时已露出，之后按时间匀速揭到最后一段"""
    tot = H.get(eid);
    if tot is None: return {}
    (y0, t0), (y1, t1) = pts[0], pts[-1]
    f0, f1 = (hdr + y0)/tot, (hdr + y1)/tot
    rate = (f1 - f0)/max(0.3, t1 - t0)
    return {"wipe": round((1 - f0)/rate, 3), "wipe_from": round(max(at, t0), 3), "reveal0": round(f0, 3)}

def GRID(eid, slot, at, out, color, title, sub, cells, times, glyph="grid"):
    """宫格：times = 每格出现时刻（按行揭开，每行取该行第一个格子的时刻）"""
    rows = [times[i] for i in range(0, len(times), 3)]
    pts = [(156*(r+1) + 12*r, t) for r, t in enumerate(rows)]
    e = dict(id=eid, type="grid_panel", slot=slot, at=at, out=out, ticks=times,
             props={"color": color, "title": title, "sub": sub, "cells": cells, "glyph": glyph})
    st = reveal(eid, pts, 160, 28, at)
    if st: e["set"] = st
    add(**e)

def SVG(eid, slot, at, out, color, title, sub, svg, glyph="grid", w=404, h=340, rv=None, ticks=None, tsize=52):
    e = dict(id=eid, type="svg_panel", slot=slot, at=at, out=out,
             props={"color": color, "title": title, "sub": sub, "svg": svg, "glyph": glyph, "w": w, "h": h, "tsize": tsize})
    if rv:
        tot = H.get(eid, 156 + h + 26); st = reveal(eid, rv, tot - 26 - h, 26, at)
        if st: e["set"] = st
    if ticks: e["ticks"] = ticks
    add(**e)

EN = ' class="en"'
EN = ' class="en"'
MK = lambda i, c: f'<marker id="{i}" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c}"/></marker>'
