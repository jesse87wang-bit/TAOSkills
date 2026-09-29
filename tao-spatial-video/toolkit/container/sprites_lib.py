# tao-spatial-video 素材库（在云端容器里跑：Playwright + Chromium 渲染 3 倍透明 PNG）
# 组件都返回一段 HTML（最外层 class="el"），render_all() 逐个截图。
import os, sys, asyncio
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = KIT + '/fonts'
def _ensure_fonts():
    # Poppins（OFL 开源字体），缺了就从 google/fonts 仓库下载
    import urllib.request
    os.makedirs(FONT_DIR, exist_ok=True)
    for f in ['Poppins-BlackItalic.ttf', 'Poppins-SemiBold.ttf']:
        dst = os.path.join(FONT_DIR, f)
        if not os.path.exists(dst):
            urllib.request.urlretrieve('https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/'+f, dst)
_ensure_fonts()
DB = ("#06B6D4", "#3B82F6", "#0369A1")   # 产品 A（左侧、青蓝）
WB = ("#A855F7", "#6366F1", "#5B21B6")   # 产品 B（右侧、紫靛）
ICONS = {
 "doc": '<path d="M7 3h7l5 5v13H7z"/><path d="M14 3v5h5"/><path d="M9.5 13h6M9.5 17h6"/>',
 "users": '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20c0-3.3 2.5-5.5 5.5-5.5s5.5 2.2 5.5 5.5"/><circle cx="17" cy="9" r="2.6"/><path d="M16 14.6c2.6.2 4.5 2.2 4.5 5.1"/>',
 "flow": '<circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.3 11l7.4-4M8.3 13l7.4 4"/>',
 "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><circle cx="12" cy="12" r="0.9" fill="currentColor"/>',
 "image": '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="9" cy="10" r="1.8"/><path d="M4 18l5-5 4 4 3-3 4 4"/>',
 "video": '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="M16 10l5-3v10l-5-3z"/>',
 "funnel": '<path d="M4 5h16l-6 7.5V19l-4 1.5v-8z"/>',
 "chart": '<path d="M5 20V11M11 20V5M17 20v-6M3 20h18"/>',
 "link": '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 "lock": '<rect x="5" y="11" width="14" height="9.5" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
 "shield": '<path d="M12 3l7.5 3v5.5c0 4.6-3.2 8.3-7.5 9.5-4.3-1.2-7.5-4.9-7.5-9.5V6z"/><path d="M8.8 12.2l2.2 2.2 4.4-4.4"/>',
 "switch": '<path d="M4 8h14l-3.5-3.5M20 16H6l3.5 3.5"/>',
 "cpu": '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 3v4M14 3v4M10 17v4M14 17v4M3 10h4M3 14h4M17 10h4M17 14h4"/>',
 "chat": '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
 "book": '<path d="M4 5.5C6.5 4 9.5 4 12 5.5v14c-2.5-1.5-5.5-1.5-8 0z"/><path d="M20 5.5C17.5 4 14.5 4 12 5.5v14c2.5-1.5 5.5-1.5 8 0z"/>',
 "meeting": '<rect x="3" y="5" width="18" height="12" rx="2"/><path d="M8 21h8M12 17v4"/>',
 "coin": '<circle cx="12" cy="12" r="8.5"/><path d="M9 8l3 4 3-4M12 12v5M9.5 13.5h5"/>',
 "card": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="11" r="2.3"/><path d="M5.8 16c.6-1.6 1.8-2.4 3.2-2.4s2.6.8 3.2 2.4M14 10h4M14 13.5h3"/>',
 "task": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="M8 12l2.5 2.5L16 9"/>',
 "mega": '<path d="M4 10v4h3l7 4V6l-7 4z"/><path d="M17 9.5a3.5 3.5 0 0 1 0 5"/>',
 "db": '<ellipse cx="12" cy="6" rx="7" ry="2.8"/><path d="M5 6v12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8V6"/><path d="M5 12c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8"/>',
 "steps": '<path d="M4 18h5v-5h5V8h6"/>',
 "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
 "award": '<circle cx="12" cy="9" r="5.5"/><path d="M9 13.8L8 21l4-2 4 2-1-7.2"/>',
 "grid": '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
 "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5L18 18M6 18l2.5-2.5M15.5 8.5L18 6"/>',
 "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
 "warn": '<path d="M12 4l9 16H3z"/><path d="M12 10v4.5M12 17.2v.3"/>',
 "star": '<path d="M12 3.5l2.6 5.5 5.9.6-4.5 4 1.3 5.9-5.3-3-5.3 3 1.3-5.9-4.5-4 5.9-.6z"/>',
 "arrow": '<path d="M4 12h15M13 6l6 6-6 6"/>',
}

def icon(name, size=40, color="currentColor", sw=2.1):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICONS[name]}</svg>'
def V(a): return f"--a1:{a[0]};--a2:{a[1]};--a3:{a[2]}"
BASE = f"""
@font-face{{font-family:LongCangX;src:url(file://{FONT_DIR}/LongCangX-Regular.ttf)}}
@font-face{{font-family:PopBI;src:url(file://{FONT_DIR}/Poppins-BlackItalic.ttf)}}
@font-face{{font-family:PopSB;src:url(file://{FONT_DIR}/Poppins-SemiBold.ttf)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:transparent;font-family:PopSB,'Noto Sans CJK SC';color:#171437;-webkit-font-smoothing:antialiased;padding:40px}}
.cn{{font-family:'Noto Sans CJK SC'}}
.el{{display:inline-block;position:relative}}
/* 玻璃：半透明，让合成器里的虚化背景透出来 */
.glass{{border-radius:34px;background:linear-gradient(155deg,rgba(255,255,255,.66) 0%,rgba(244,240,255,.50) 50%,rgba(226,220,255,.42) 100%);
  border:2.5px solid rgba(255,255,255,.92);box-shadow:inset 0 2px 0 rgba(255,255,255,1),inset 0 -30px 60px rgba(160,140,255,.18);position:relative;overflow:hidden}}
.glass::before{{content:'';position:absolute;left:30px;right:30px;top:0;height:5px;border-radius:0 0 6px 6px;background:linear-gradient(90deg,transparent,var(--a1),var(--a2),transparent)}}
.glass::after{{content:'';position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.35) 0%,rgba(255,255,255,0) 32%);pointer-events:none}}
.tile{{display:inline-flex;align-items:center;justify-content:center;border-radius:28%;background:linear-gradient(145deg,var(--a1),var(--a2));box-shadow:inset 0 2px 0 rgba(255,255,255,.6),0 8px 20px rgba(40,30,120,.25);color:#fff}}
.row{{display:flex;align-items:center;gap:16px;padding:14px 16px;border-radius:20px;background:rgba(255,255,255,.62);border:1.5px solid rgba(255,255,255,.9);margin-top:12px}}
.ic{{display:inline-flex;align-items:center;justify-content:center;width:54px;height:54px;border-radius:16px;background:linear-gradient(145deg,rgba(255,255,255,.95),rgba(236,232,255,.85));color:var(--a3)}}
.glowtxt{{color:#fff;text-shadow:0 3px 0 rgba(40,25,120,.9),0 0 18px rgba(170,140,255,.95),0 0 40px rgba(120,90,255,.7)}}
.skew{{display:inline-block;transform:skewX(-9deg)}}
"""

# ---------------- 组件 ----------------
def product_panel(a, name, sub, rows, glyph, en=False):
    """开场产品卡：图标 + 产品名 + 一行说明 + 4 行标签"""
    nm = f'<div style="font-family:PopBI;font-size:46px;line-height:1.15;color:{a[2]};white-space:nowrap">{name}</div>' if en else f'<div class="cn" style="font-size:66px;font-weight:900;line-height:1.1;color:{a[2]}">{name}</div>'
    rr = "".join(f'<div class="row"><span class="ic">{icon(i,32)}</span><span class="cn" style="font-size:34px;font-weight:700">{t}</span><span style="margin-left:auto;width:12px;height:12px;border-radius:50%;background:{a[1]};box-shadow:0 0 10px {a[1]}"></span></div>' for i,t in rows)
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:34px 30px 30px">
      <div style="display:flex;align-items:center;gap:20px"><span class="tile" style="width:96px;height:96px;flex-shrink:0">{icon(glyph,54,'#fff',2)}</span>
      <div>{nm}<div class="cn" style="font-size:30px;color:#4F4A78;margin-top:6px">{sub}</div></div></div>
      <div style="height:1.5px;background:linear-gradient(90deg,{a[1]}66,transparent);margin:22px 0 6px"></div>{rr}</div>'''
def list_panel(a, glyph, title, sub, rows, footer=None, en=False, tsize=52):
    """侧边列表卡（最常用）：标题 ≤7 个汉字，行 ≤8 个汉字，3–4 行"""
    nm = f'<div style="font-family:PopBI;font-size:{tsize-6}px;line-height:1.15;color:{a[2]};white-space:nowrap">{title}</div>' if en else f'<div class="cn" style="font-size:{tsize}px;font-weight:900;line-height:1.12;color:{a[2]};white-space:nowrap">{title}</div>'
    rr = "".join(f'<div class="row"><span class="ic">{icon(i,32)}</span><span class="cn" style="font-size:33px;font-weight:700">{t}</span><span style="margin-left:auto;width:12px;height:12px;border-radius:50%;background:{a[1]};box-shadow:0 0 10px {a[1]}"></span></div>' for i,t in rows)
    ft = f'<div class="cn" style="text-align:center;font-size:30px;font-weight:900;color:{a[2]};margin-top:18px">{footer}</div>' if footer else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:32px 28px 28px">
      <div style="display:flex;align-items:center;gap:18px"><span class="tile" style="width:92px;height:92px;flex-shrink:0">{icon(glyph,52,'#fff',2)}</span>
      <div>{nm}<div class="cn" style="font-size:28px;color:#4F4A78;margin-top:6px;white-space:nowrap">{sub}</div></div></div>
      <div style="height:1.5px;background:linear-gradient(90deg,{a[1]}66,transparent);margin:20px 0 4px"></div>{rr}{ft}</div>'''
def big_card(a, name, pill, big, sub, foot=None, en=False, bsize=98):
    """侧边大字卡：一个大结论（4 个汉字最佳，长了调小 bsize）"""
    nm = f'<span style="font-family:PopBI;font-size:42px;color:{a[2]}">{name}</span>' if en else f'<span class="cn" style="font-size:44px;font-weight:900;color:{a[2]}">{name}</span>'
    pl = f'<span class="cn" style="font-size:28px;font-weight:700;color:#fff;padding:6px 18px;border-radius:999px;background:linear-gradient(90deg,{a[0]},{a[1]})">{pill}</span>' if pill else ''
    ft = f'<div class="cn" style="font-size:22px;color:#6B6596;margin-top:16px">{foot}</div>' if foot else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:34px 32px">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">{nm}{pl}</div>
      <div class="cn" style="font-size:{bsize}px;font-weight:900;line-height:1.05;margin:28px 0 16px;background:linear-gradient(90deg,{a[2]},{a[1]});-webkit-background-clip:text;color:transparent;white-space:nowrap">{big}</div>
      <div class="cn" style="font-size:36px;color:#3F3A68;font-weight:700">{sub}</div>{ft}</div>'''
def small_card(a, glyph, title, sub):
    return f'''<div class="el glass" style="{V(a)};width:400px;padding:30px 28px;display:flex;align-items:center;gap:20px">
      <span class="tile" style="width:96px;height:96px;flex-shrink:0">{icon(glyph,54,'#fff',2)}</span>
      <div><div class="cn" style="font-size:46px;font-weight:900;color:{a[2]}">{title}</div><div class="cn" style="font-size:32px;color:#3F3A68;font-weight:700;margin-top:6px">{sub}</div></div></div>'''
def progress_card(a, title, sub, left, right, source=None):
    src = f'<div class="cn" style="font-size:22px;color:#6B6596;margin-top:14px">来源：{source}</div>' if source else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:32px 30px">
      <div style="display:flex;align-items:center;gap:18px"><span class="tile" style="width:92px;height:92px;flex-shrink:0">{icon('grid',52,'#fff',2)}</span>
       <div><div style="font-family:PopBI;font-size:44px;color:{a[2]};white-space:nowrap">{title}</div><div class="cn" style="font-size:30px;color:#3F3A68;font-weight:700;margin-top:4px">{sub}</div></div></div>
      <div style="position:relative;margin-top:40px;height:22px;border-radius:11px;background:rgba(140,115,255,.2)"><div style="position:absolute;inset:0;border-radius:11px;background:linear-gradient(90deg,{DB[0]},{WB[0]},{WB[1]})"></div></div>
      <div style="display:flex;justify-content:space-between;margin-top:14px"><span class="cn" style="font-size:38px;font-weight:900">{left}</span><span class="cn" style="font-size:38px;font-weight:900;color:{a[2]}">{right}</span></div>{src}</div>'''
def badge(n, t):
    """顶部章节标：01 生态"""
    return f'''<div class="el glass" style="{V(WB)};padding:14px 34px;border-radius:999px;display:inline-flex;align-items:center;gap:16px">
      <span style="font-family:PopBI;font-size:48px;background:linear-gradient(140deg,{DB[0]},{WB[0]});-webkit-background-clip:text;color:transparent">{n}</span><span class="cn" style="font-size:44px;font-weight:900">{t}</span></div>'''
def glow_text(text, size=96, en=False):
    """压在胸前的发光大字"""
    fam = "font-family:PopBI" if en else "font-family:'Noto Sans CJK SC';font-weight:900"
    return f'<div class="el glowtxt" style="{fam};font-size:{size}px;padding:10px 28px;white-space:nowrap"><span class="skew">{text}</span></div>'
def dim_text(text, size=96):
    return f'<div class="el cn" style="font-size:{size}px;font-weight:900;padding:10px 26px;color:#EEEAFF;text-shadow:0 3px 0 rgba(40,25,120,.9),0 0 20px rgba(120,90,255,.7)"><span class="skew">{text}</span></div>'
def strike():
    return '<div class="el" style="padding:10px"><svg width="520" height="60"><path d="M8 38 C 150 18, 330 44, 510 20" stroke="#FF3D71" stroke-width="13" stroke-linecap="round" fill="none"/></svg></div>'
def pill(text, a=WB, size=44):
    return f'<div class="el" style="padding:4px"><span class="cn" style="display:inline-block;font-size:{size}px;font-weight:900;color:#fff;padding:10px 34px;border-radius:999px;background:linear-gradient(90deg,{a[0]},{a[1]});border:2px solid rgba(255,255,255,.9)">{text}</span></div>'
def verdict(a, pre, name, en=False):
    """结论条：xx → 先看 产品 ✓"""
    nm = f'<span style="font-family:PopBI;font-size:56px">{name}</span>' if en else f'<span class="cn" style="font-weight:900;font-size:56px">{name}</span>'
    return f'''<div class="el" style="padding:6px"><div style="display:flex;align-items:center;gap:18px;padding:22px 40px;border-radius:32px;background:linear-gradient(90deg,{a[0]},{a[1]});border:2.5px solid rgba(255,255,255,.92);color:#fff;box-shadow:inset 0 2px 0 rgba(255,255,255,.5)">
      <span class="cn" style="font-size:42px;font-weight:700;white-space:nowrap">{pre}</span>{icon('arrow',44,'#fff',2.6)}<span class="cn" style="font-size:42px;font-weight:700">先看</span>{nm}
      <span style="width:56px;height:56px;border-radius:50%;background:#fff;display:inline-flex;align-items:center;justify-content:center">{icon('check',36,a[2],3)}</span></div></div>'''
def judge(a, cond, name, en=False):
    """判断行：条件 → 产品"""
    nm = f'<span style="font-family:PopBI;font-size:50px">{name}</span>' if en else f'<span class="cn" style="font-weight:900;font-size:50px">{name}</span>'
    return f'''<div class="el glass" style="{V(a)};width:960px;padding:22px 30px;display:flex;align-items:center;gap:18px">
      <span class="cn" style="font-size:44px;font-weight:900;flex:1;white-space:nowrap">{cond}</span>{icon('arrow',50,a[1],2.6)}
      <span style="padding:12px 28px;border-radius:24px;background:linear-gradient(90deg,{a[0]},{a[1]});color:#fff">{nm}</span></div>'''
def chip(g, t, a=WB):
    return f'''<div class="el" style="padding:4px"><div style="display:inline-flex;align-items:center;gap:12px;padding:16px 32px;border-radius:999px;background:rgba(255,255,255,.95);border:2.5px solid {a[1]};color:{a[2]}">
      {icon(g,42,a[2])}<span class="cn" style="font-size:44px;font-weight:900">{t}</span></div></div>'''
def warn_chip(t):
    return f'''<div class="el" style="padding:4px"><div style="display:inline-flex;align-items:center;gap:14px;padding:16px 36px;border-radius:999px;background:rgba(255,255,255,.95);border:3px solid #FF7A45;color:#C2410C">
      {icon('warn',46,'#C2410C')}<span class="cn" style="font-size:46px;font-weight:900">{t}</span></div></div>'''
def icon_tile(a, g, t=None, size=220):
    lab = f'<span class="cn" style="font-size:40px;font-weight:900">{t}</span>' if t else ''
    return f'''<div class="el glass" style="{V(a)};width:{size}px;height:{size}px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
      <span class="tile" style="width:96px;height:96px">{icon(g,54,'#fff',2)}</span>{lab}</div>'''
def float_icon(a, g, s=96):
    """装饰小图标（前景，可轻微虚化）"""
    return f'<div class="el" style="padding:6px"><span class="tile" style="{V(a)};width:{s}px;height:{s}px;border-radius:26px;border:2px solid rgba(255,255,255,.8)">{icon(g,int(s*0.55),"#fff",2)}</span></div>'
def number_tile(n, t, g):
    """路线图方块：01 + 图标 + 两个字"""
    return f'''<div class="el glass" style="{V(WB)};width:250px;height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">
      <div style="font-family:PopBI;font-size:84px;line-height:1;background:linear-gradient(140deg,{DB[0]},{WB[0]} 70%);-webkit-background-clip:text;color:transparent">{n}</div>
      <span class="ic" style="width:60px;height:60px">{icon(g,36)}</span><div class="cn" style="font-size:46px;font-weight:900">{t}</div></div>'''
def chat_bar(t, sub, tag='示意'):
    return f'''<div class="el glass" style="{V(WB)};width:900px;padding:22px 30px;border-radius:30px;display:flex;align-items:center;gap:20px">
      <span style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,{WB[0]},{WB[1]});display:inline-flex;align-items:center;justify-content:center">{icon('chat',40,'#fff')}</span>
      <span class="cn" style="font-size:48px;font-weight:900">{t}</span><span class="cn" style="font-size:32px;color:#4F4A78">{sub}</span>
      <span class="cn" style="margin-left:auto;font-size:24px;color:#fff;background:#8C86B8;border-radius:10px;padding:4px 12px">{tag}</span></div>'''
def result_tile(g, t):
    return f'''<div class="el glass" style="{V(WB)};width:280px;height:230px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
      <span class="ic" style="width:88px;height:88px;border-radius:26px">{icon(g,50)}</span><span class="cn" style="font-size:40px;font-weight:900">{t}</span></div>'''
def stamp(t):
    return f'''<div class="el" style="padding:30px"><div style="width:480px;height:190px;transform:rotate(-8deg);border:10px solid #E0245E;border-radius:26px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.18)">
      <span class="cn" style="font-size:122px;font-weight:900;color:#E0245E;letter-spacing:10px">{t}</span></div></div>'''
def rating_panel(title, dims, sub='用你自己的业务来打分'):
    """评分面板：dims=[(icon,'维度'),...] 空星，不写假分数"""
    rows = ''.join(f"""<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1.5px solid rgba(255,255,255,.6)"><span class="ic" style="width:48px;height:48px">{icon(i,28)}</span>
       <span class="cn" style="font-size:31px;font-weight:700;flex:1">{t}</span><span style="display:flex;gap:2px">{''.join(icon('star',27,'#6B5BD6',2.3) for _ in range(5))}</span></div>""" for i,t in dims)
    return f'''<div class="el glass" style="{V(WB)};width:470px;padding:30px 28px">
      <div class="cn" style="font-size:42px;font-weight:900">{title} <span style="font-size:28px;color:#5A5488;font-weight:600">示例</span></div>
      <div class="cn" style="font-size:26px;color:#5A5488;margin:4px 0 8px">{sub}</div>{rows}</div>'''
def laptop(title, left_name, left_job, right_name, right_job, metrics):
    """电脑屏幕（示意界面，标「示意」）"""
    task = lambda a, nm, job, pct: f'''<div style="flex:1;border-radius:18px;background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.18);padding:18px">
      <div style="display:flex;align-items:center;gap:10px"><span class="tile" style="{V(a)};width:40px;height:40px;border-radius:12px">{icon('spark',22,'#fff')}</span>
      <span class="cn" style="font-size:28px;font-weight:700;color:#fff">{nm}</span></div>
      <div class="cn" style="font-size:24px;color:#C9C3F0;margin:16px 0 10px">任务：{job}</div>
      {''.join(f'<div style="height:12px;border-radius:6px;background:rgba(255,255,255,.14);margin:10px 0"><div style="width:{w}%;height:100%;border-radius:6px;background:linear-gradient(90deg,{a[0]},{a[1]})"></div></div>' for w in pct)}
      <div class="cn" style="font-size:22px;color:#A9A3D8;margin-top:12px">用真实业务数据测试中…</div></div>'''
    mt = ''.join(f'<div style="flex:1;border-radius:14px;background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.16);padding:12px 14px"><div class="cn" style="font-size:21px;color:#B9B2E8">{k}</div><div style="font-family:PopSB;font-size:30px;color:#fff;margin-top:4px">— <span class="cn" style="font-size:18px;color:#9F98D0">待测</span></div></div>' for k in metrics)
    return f'''<div class="el" style="width:1000px">
    <div style="width:900px;height:570px;margin-left:50px;border-radius:30px;background:#0E0B24;border:3px solid #3A3566;padding:20px">
     <div style="width:100%;height:100%;border-radius:16px;background:linear-gradient(160deg,#1B1545,#241a5c 60%,#2a1f6e);padding:24px;position:relative;overflow:hidden">
      <div style="display:flex;align-items:center;justify-content:space-between"><span class="cn" style="font-size:34px;font-weight:900;color:#fff">{title}</span>
        <span class="cn" style="font-size:20px;color:#fff;background:rgba(255,255,255,.18);border-radius:8px;padding:4px 12px">示意</span></div>
      <div style="display:flex;gap:18px;margin-top:20px">{task(DB,left_name,left_job,[88,64,40])}{task(WB,right_name,right_job,[76,58,30])}</div>
      <div style="display:flex;gap:14px;margin-top:18px">{mt}</div></div></div>
    <div style="width:1000px;height:34px;border-radius:0 0 40px 40px;background:linear-gradient(180deg,#CFCBE6,#8F8AB5);box-shadow:inset 0 3px 0 #fff"></div></div>'''

# ---------------- 渲染 ----------------
async def _render(S, outdir, names, scale):
    from playwright.async_api import async_playwright
    os.makedirs(outdir, exist_ok=True); tmp = os.path.join(outdir, '_tmp.html')
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1400,'height':1400}, device_scale_factor=scale)
        for n, html in S.items():
            if names and n not in names: continue
            open(tmp,'w').write(f"<!doctype html><html><head><meta charset='utf-8'><style>{BASE}</style></head><body>{html}</body></html>")
            await pg.goto('file://'+tmp); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(100)
            await pg.locator('.el').first.screenshot(path=f'{outdir}/{n}.png', omit_background=True)
            print('ok', n)
        await b.close()
    os.remove(tmp)
def render_all(S, outdir, names=None, scale=3):
    """S = {'素材名': html}；输出 outdir/素材名.png（3 倍）"""
    asyncio.run(_render(S, outdir, names, scale))
