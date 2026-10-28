import json, os

H = json.load(open('heights.json')) if os.path.exists('heights.json') else {}
E = []
def add(**k): E.append(k)

def wipe_list(eid, at, ticks, n):
    h = H.get(eid, 97*n + 183); hdr = h - 97*n - 33
    r0 = hdr/h; ends = [(hdr + 97*(i+1))/h + 0.06 for i in range(n)]
    t1, tn = ticks[0] + 0.12, ticks[-1] + 0.12
    w = (1-r0)*(tn-t1)/max(0.05, ends[-1]-ends[0]) if n > 1 else 0.6
    wf = t1 - (ends[0]-r0)*w/(1-r0)
    if wf < at:
        r_at = r0 + (1-r0)*(at-wf)/w; w = (1-r_at)*w/(1-r0); wf = at; r0 = r_at
    return {"wipe": round(w, 3), "wipe_from": round(wf, 3), "reveal0": round(r0, 3)}

def wipe_flow(eid, at, ticks, n):
    """flow_panel：标题区约 156，每步 95，步间箭头 34"""
    h = H.get(eid, 156 + 95*n + 34*(n-1) + 29); hdr = h - 29 - 95*n - 34*(n-1)
    r0 = hdr/h; ends = [(hdr + 95*(i+1) + 34*i)/h + 0.04 for i in range(n)]
    t1, tn = ticks[0] + 0.12, ticks[-1] + 0.12
    w = (1-r0)*(tn-t1)/max(0.05, ends[-1]-ends[0]); wf = t1 - (ends[0]-r0)*w/(1-r0)
    if wf < at:
        r_at = r0 + (1-r0)*(at-wf)/w; w = (1-r_at)*w/(1-r0); wf = at; r0 = r_at
    return {"wipe": round(w, 3), "wipe_from": round(wf, 3), "reveal0": round(r0, 3)}

def LIST(eid, slot, at, out, color, glyph, title, sub, rows, ticks, **props):
    add(id=eid, type="list_panel", slot=slot, at=at, out=out, ticks=ticks, set=wipe_list(eid, at, ticks, len(rows)),
        props={"color": color, "glyph": glyph, "title": title, "sub": sub, "rows": rows, **props})
def FLOW(eid, slot, at, out, color, glyph, title, sub, steps, ticks):
    add(id=eid, type="flow_panel", slot=slot, at=at, out=out, ticks=ticks, set=wipe_flow(eid, at, ticks, len(steps)),
        props={"color": color, "glyph": glyph, "title": title, "sub": sub, "steps": steps})
def LOOP(eid, slot, at, out, color, title, sub, nodes, center="spark"):
    add(id=eid, type="loop_panel", slot=slot, at=at, out=out,
        props={"color": color, "title": title, "sub": sub, "nodes": nodes, "center_glyph": center, "glyph": "flow"})
def BIG(eid, slot, at, out, color, name, big, sub, **props):
    add(id=eid, type="big_card", slot=slot, at=at, out=out, props={"color": color, "name": name, "big": big, "sub": sub, **props})
def GLOW(eid, at, out, text, size, y=None, **kw):
    add(id=eid, type="glow_text", slot="F", at=at, out=out, **({"set": {"y": y}} if y else {}), props={"text": text, "size": size}, **kw)
def WARN(eid, at, out, text, y=None):
    add(id=eid, type="warn_chip", slot="F", at=at, out=out, **({"set": {"y": y}} if y else {}), props={"text": text})
def STRIKE(eid, text, at, strike_at, out, size=88, s=1.0):
    add(id="D_"+eid, type="dim_text", slot="F", at=at, out=out, props={"text": text, "size": size})
    add(id="S_"+eid, type="strike", slot="F", at=strike_at, out=out, set={"y": 1200, "s": s, "pop": 1.0, "dur": 0.25})
def JUDGE(eid, at, out, color, cond, name, y=None):
    add(id=eid, type="judge", slot="F", at=at, out=out, **({"set": {"y": y}} if y else {}), props={"color": color, "cond": cond, "name": name})
def BADGE(eid, at, out, num, text):
    add(id=eid, type="badge", slot="TOP", at=at, out=out, props={"num": num, "text": text})

