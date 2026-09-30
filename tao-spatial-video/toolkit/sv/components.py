# tao-spatial-video 玻璃卡组件库
# 每个组件返回一段 HTML（最外层 class="el"），由 sprites.py 用 Chromium 截成 3 倍透明 PNG。
# 这里的标记和 CSS 与第一条成片《WorkBuddy 还是豆包工作》逐字一致（golden 回归测试会校验），
# 改动任何一个字符都会让成片外观变化——要新样式请新增组件，不要改已有组件。
#
# 颜色：分镜表 palette 里的 A（左侧产品，默认青蓝）和 B（右侧产品，默认紫靛），每组 3 个色值：
#   [0] 渐变起点  [1] 渐变终点/强调  [2] 深色文字
import html as _html

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

# 基础 CSS（与第一条成片一致）。字体 @font-face 由 sprites.py 按 assets.json 注入（固定版本，保证各环境一致）。
BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:transparent;font-family:PopSB,'Noto Sans CJK SC';color:#171437;-webkit-font-smoothing:antialiased;padding:40px}
.cn{font-family:'Noto Sans CJK SC'}
.el{display:inline-block;position:relative}
/* 玻璃：半透明，让合成器里的虚化背景透出来 */
.glass{border-radius:34px;background:linear-gradient(155deg,rgba(255,255,255,.66) 0%,rgba(244,240,255,.50) 50%,rgba(226,220,255,.42) 100%);
  border:2.5px solid rgba(255,255,255,.92);box-shadow:inset 0 2px 0 rgba(255,255,255,1),inset 0 -30px 60px rgba(160,140,255,.18);position:relative;overflow:hidden}
.glass::before{content:'';position:absolute;left:30px;right:30px;top:0;height:5px;border-radius:0 0 6px 6px;background:linear-gradient(90deg,transparent,var(--a1),var(--a2),transparent)}
.glass::after{content:'';position:absolute;inset:0;background:linear-gradient(115deg,rgba(255,255,255,.35) 0%,rgba(255,255,255,0) 32%);pointer-events:none}
.tile{display:inline-flex;align-items:center;justify-content:center;border-radius:28%;background:linear-gradient(145deg,var(--a1),var(--a2));box-shadow:inset 0 2px 0 rgba(255,255,255,.6),0 8px 20px rgba(40,30,120,.25);color:#fff}
.row{display:flex;align-items:center;gap:16px;padding:14px 16px;border-radius:20px;background:rgba(255,255,255,.62);border:1.5px solid rgba(255,255,255,.9);margin-top:12px}
.ic{display:inline-flex;align-items:center;justify-content:center;width:54px;height:54px;border-radius:16px;background:linear-gradient(145deg,rgba(255,255,255,.95),rgba(236,232,255,.85));color:var(--a3)}
.glowtxt{color:#fff;text-shadow:0 3px 0 rgba(40,25,120,.9),0 0 18px rgba(170,140,255,.95),0 0 40px rgba(120,90,255,.7)}
.skew{display:inline-block;transform:skewX(-9deg)}
"""
DEFAULT_PALETTE = {"A": ("#06B6D4", "#3B82F6", "#0369A1"), "B": ("#A855F7", "#6366F1", "#5B21B6")}

def V(a): return f"--a1:{a[0]};--a2:{a[1]};--a3:{a[2]}"
def _t(s):   # 纯文本转义（分镜表里的文字一律按纯文本处理）
    return _html.escape(str(s), quote=False)

# ------------------------------------------------------------------ 侧边玻璃卡（L/R 位）
def product_panel(P, color, name, sub, rows, glyph, en=False):
    """产品卡：图标 + 产品名 + 副标题 + 4 行能力。rows=[[图标,文字],...]"""
    a = P[color]; name, sub = _t(name), _t(sub)
    nm = f'<div style="font-family:PopBI;font-size:46px;line-height:1.15;color:{a[2]};white-space:nowrap">{name}</div>' if en else f'<div class="cn" style="font-size:66px;font-weight:900;line-height:1.1;color:{a[2]}">{name}</div>'
    rr = "".join(f'<div class="row"><span class="ic">{icon(i,32)}</span><span class="cn" style="font-size:34px;font-weight:700">{_t(t)}</span><span style="margin-left:auto;width:12px;height:12px;border-radius:50%;background:{a[1]};box-shadow:0 0 10px {a[1]}"></span></div>' for i,t in rows)
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:34px 30px 30px">
      <div style="display:flex;align-items:center;gap:20px"><span class="tile" style="width:96px;height:96px;flex-shrink:0">{icon(glyph,54,'#fff',2)}</span>
      <div>{nm}<div class="cn" style="font-size:30px;color:#4F4A78;margin-top:6px">{sub}</div></div></div>
      <div style="height:1.5px;background:linear-gradient(90deg,{a[1]}66,transparent);margin:22px 0 6px"></div>{rr}</div>'''

def list_panel(P, color, glyph, title, sub, rows, footer=None, footer_small=False, en=False, tsize=52):
    """列表卡：标题 + 副标题 + 3–4 行（配 wipe 逐行亮起）+ 可选底注。标题 ≤7 个汉字，长了调小 tsize。"""
    a = P[color]; title, sub = _t(title), _t(sub)
    nm = f'<div style="font-family:PopBI;font-size:{tsize-6}px;line-height:1.15;color:{a[2]};white-space:nowrap">{title}</div>' if en else f'<div class="cn" style="font-size:{tsize}px;font-weight:900;line-height:1.12;color:{a[2]};white-space:nowrap">{title}</div>'
    rr = "".join(f'<div class="row"><span class="ic">{icon(i,32)}</span><span class="cn" style="font-size:33px;font-weight:700">{_t(t)}</span><span style="margin-left:auto;width:12px;height:12px;border-radius:50%;background:{a[1]};box-shadow:0 0 10px {a[1]}"></span></div>' for i,t in rows)
    if footer and footer_small:
        footer = f'<span style="font-size:22px;color:#6B6596;font-weight:500">{_t(footer)}</span>'
    elif footer:
        footer = _t(footer)
    ft = f'<div class="cn" style="text-align:center;font-size:30px;font-weight:900;color:{a[2]};margin-top:18px">{footer}</div>' if footer else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:32px 28px 28px">
      <div style="display:flex;align-items:center;gap:18px"><span class="tile" style="width:92px;height:92px;flex-shrink:0">{icon(glyph,52,'#fff',2)}</span>
      <div>{nm}<div class="cn" style="font-size:28px;color:#4F4A78;margin-top:6px;white-space:nowrap">{sub}</div></div></div>
      <div style="height:1.5px;background:linear-gradient(90deg,{a[1]}66,transparent);margin:20px 0 4px"></div>{rr}{ft}</div>'''

def big_card(P, color, name, big, sub, pill=None, foot=None, en=False, bsize=98):
    """大字卡：产品名 + 标签 + 一个大词（4 个汉字最佳，长了调小 bsize）+ 一句解释 + 可选脚注。"""
    a = P[color]; name, big, sub = _t(name), _t(big), _t(sub)
    nm = f'<span style="font-family:PopBI;font-size:42px;color:{a[2]}">{name}</span>' if en else f'<span class="cn" style="font-size:44px;font-weight:900;color:{a[2]}">{name}</span>'
    pl = f'<span class="cn" style="font-size:28px;font-weight:700;color:#fff;padding:6px 18px;border-radius:999px;background:linear-gradient(90deg,{a[0]},{a[1]})">{_t(pill)}</span>' if pill else ''
    ft = f'<div class="cn" style="font-size:22px;color:#6B6596;margin-top:16px">{_t(foot)}</div>' if foot else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:34px 32px">
      <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap">{nm}{pl}</div>
      <div class="cn" style="font-size:{bsize}px;font-weight:900;line-height:1.05;margin:28px 0 16px;background:linear-gradient(90deg,{a[2]},{a[1]});-webkit-background-clip:text;color:transparent;white-space:nowrap">{big}</div>
      <div class="cn" style="font-size:36px;color:#3F3A68;font-weight:700">{sub}</div>{ft}</div>'''

def small_card(P, color, glyph, title, sub, sub_icon):
    """小名片：图标 + 标题 + 带小图标的一句话（如「企业微信 · 连接客户」）"""
    a = P[color]
    return f'''<div class="el glass" style="{V(a)};width:400px;padding:30px 28px;display:flex;align-items:center;gap:20px">
  <span class="tile" style="width:96px;height:96px;flex-shrink:0">{icon(glyph,54,'#fff',2)}</span>
  <div><div class="cn" style="font-size:46px;font-weight:900;color:{a[2]}">{_t(title)}</div><div class="cn" style="font-size:32px;color:#3F3A68;font-weight:700;margin-top:6px;display:flex;align-items:center;gap:8px">{icon(sub_icon,30,a[2])}{_t(sub)}</div></div></div>'''

def progress_card(P, color, glyph, title, sub, left, right, source=None):
    """流程卡：英文标题 + 副标题 + 一条从 left 到 right 的发光进度条（如「线索 → 回款」）"""
    a = P[color]; A = P['A']
    src = f'\n  <div class="cn" style="font-size:22px;color:#6B6596;margin-top:14px">{_t(source)}</div>' if source else ''
    return f'''<div class="el glass" style="{V(a)};width:460px;padding:32px 30px">
  <div style="display:flex;align-items:center;gap:18px"><span class="tile" style="width:92px;height:92px;flex-shrink:0">{icon(glyph,52,'#fff',2)}</span>
   <div><div style="font-family:PopBI;font-size:44px;color:{a[2]};white-space:nowrap">{_t(title)}</div><div class="cn" style="font-size:30px;color:#3F3A68;font-weight:700;margin-top:4px">{_t(sub)}</div></div></div>
  <div style="position:relative;margin-top:40px;height:22px;border-radius:11px;background:rgba(140,115,255,.2)"><div style="position:absolute;inset:0;border-radius:11px;background:linear-gradient(90deg,{A[0]},{a[0]},{a[1]});box-shadow:0 0 18px {a[1]}AA"></div></div>
  <div style="display:flex;justify-content:space-between;margin-top:14px"><span class="cn" style="font-size:38px;font-weight:900">{_t(left)}</span><span class="cn" style="font-size:38px;font-weight:900;color:{a[2]}">{_t(right)}</span></div>{src}</div>'''

def rating_panel(P, dims, title="评测维度", tag="示例", sub="用你自己的业务来打分", color="B"):
    """评分面板：空星（不写假分数）。dims=[[图标,维度],...]"""
    a = P[color]
    return f'''<div class="el glass" style="{V(a)};width:470px;padding:30px 28px">
  <div class="cn" style="font-size:42px;font-weight:900">{_t(title)} <span style="font-size:28px;color:#5A5488;font-weight:600">{_t(tag)}</span></div>
  <div class="cn" style="font-size:26px;color:#5A5488;margin:4px 0 8px">{_t(sub)}</div>
  {''.join(f"""<div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1.5px solid rgba(255,255,255,.6)"><span class="ic" style="width:48px;height:48px">{icon(i,28)}</span>
     <span class="cn" style="font-size:31px;font-weight:700;flex:1">{_t(t)}</span><span style="display:flex;gap:2px">{''.join(icon('star',27,'#6B5BD6',2.3) for _ in range(5))}</span></div>""" for i,t in dims)}</div>'''

def laptop(P, tasks, metrics, title="真实业务评测", tag="示意", note="用真实业务数据测试中…"):
    """电脑屏幕（示意界面）。tasks=[{color,name,job,pct:[3个百分比],en}] 两个；metrics=[4 个指标名]"""
    def task(a, nm, job, pct, en):
        return f'''<div style="flex:1;border-radius:18px;background:rgba(255,255,255,.08);border:1.5px solid rgba(255,255,255,.18);padding:18px">
      <div style="display:flex;align-items:center;gap:10px"><span class="tile" style="{V(a)};width:40px;height:40px;border-radius:12px">{icon('spark',22,'#fff')}</span>
      <span style="font-family:{'PopSB' if en else "'Noto Sans CJK SC'"};font-size:28px;font-weight:700;color:#fff">{_t(nm)}</span></div>
      <div class="cn" style="font-size:24px;color:#C9C3F0;margin:16px 0 10px">任务：{_t(job)}</div>
      {''.join(f'<div style="height:12px;border-radius:6px;background:rgba(255,255,255,.14);margin:10px 0"><div style="width:{w}%;height:100%;border-radius:6px;background:linear-gradient(90deg,{a[0]},{a[1]})"></div></div>' for w in pct)}
      <div class="cn" style="font-size:22px;color:#A9A3D8;margin-top:12px">{_t(note)}</div></div>'''
    tk = ''.join(task(P[x['color']], x['name'], x['job'], x['pct'], x.get('en', False)) for x in tasks)
    return f'''<div class="el" style="width:1000px">
    <div style="width:900px;height:570px;margin-left:50px;border-radius:30px;background:#0E0B24;border:3px solid #3A3566;padding:20px;box-shadow:inset 0 0 0 2px #1d1840">
     <div style="width:100%;height:100%;border-radius:16px;background:linear-gradient(160deg,#1B1545,#241a5c 60%,#2a1f6e);padding:24px;position:relative;overflow:hidden">
      <div style="position:absolute;right:-120px;top:-120px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(140,110,255,.45),transparent 70%)"></div>
      <div style="display:flex;align-items:center;justify-content:space-between"><span class="cn" style="font-size:34px;font-weight:900;color:#fff">{_t(title)}</span>
        <span class="cn" style="font-size:20px;color:#fff;background:rgba(255,255,255,.18);border-radius:8px;padding:4px 12px">{_t(tag)}</span></div>
      <div style="display:flex;gap:18px;margin-top:20px">{tk}</div>
      <div style="display:flex;gap:14px;margin-top:18px">{''.join(f'<div style="flex:1;border-radius:14px;background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.16);padding:12px 14px"><div class="cn" style="font-size:21px;color:#B9B2E8">{_t(k)}</div><div style="font-family:PopSB;font-size:30px;color:#fff;margin-top:4px">— <span class="cn" style="font-size:18px;color:#9F98D0">待测</span></div></div>' for k in metrics)}</div>
     </div></div>
    <div style="width:1000px;height:34px;border-radius:0 0 40px 40px;background:linear-gradient(180deg,#CFCBE6,#8F8AB5);box-shadow:inset 0 3px 0 #fff"></div></div>'''

# ------------------------------------------------------------------ 顶部 / 前景（F 位）
def badge(P, num, text):
    """顶部章节标：01 生态"""
    A, B = P['A'], P['B']
    return f'''<div class="el glass" style="{V(B)};padding:14px 34px;border-radius:999px;display:inline-flex;align-items:center;gap:16px">
      <span style="font-family:PopBI;font-size:48px;background:linear-gradient(140deg,{A[0]},{B[0]});-webkit-background-clip:text;color:transparent">{_t(num)}</span><span class="cn" style="font-size:44px;font-weight:900">{_t(text)}</span></div>'''

def glow_text(P, text, size, pad="10px 30px", en=False, letter_spacing=None, nowrap=False):
    """发光大字（胸前金句/标题）。en=True 用 Poppins 粗斜体（英文产品名）"""
    text = _t(text)
    if en:
        return f'<div class="el glowtxt" style="font-family:PopBI;font-size:{size}px;padding:{pad}">{text}</div>'
    extra = (f';letter-spacing:{letter_spacing}px' if letter_spacing else '') + (';white-space:nowrap' if nowrap else '')
    return f'<div class="el glowtxt cn" style="font-size:{size}px;font-weight:900;padding:{pad}{extra}"><span class="skew">{text}</span></div>'

def vs_text(P, text="VS"):
    A, B = P['A'], P['B']
    return f'<div class="el" style="font-family:PopBI;font-size:110px;padding:10px 24px;background:linear-gradient(90deg,{A[0]},#fff 50%,{B[0]});-webkit-background-clip:text;color:transparent;filter:drop-shadow(0 3px 0 rgba(40,25,120,.9)) drop-shadow(0 0 16px rgba(170,140,255,.95))">{_t(text)}</div>'

def dim_text(P, text, size=96):
    """暗一点的大字（常配 strike 划掉）"""
    return f'<div class="el cn" style="font-size:{size}px;font-weight:900;padding:10px 26px;color:#EEEAFF;text-shadow:0 3px 0 rgba(40,25,120,.9),0 0 20px rgba(120,90,255,.7)"><span class="skew">{_t(text)}</span></div>'

def strike(P):
    """红色手绘划线（盖在 dim_text 上）"""
    return '<div class="el" style="padding:10px"><svg width="520" height="60"><path d="M8 38 C 150 18, 330 44, 510 20" stroke="#FF3D71" stroke-width="13" stroke-linecap="round" fill="none"/></svg></div>'

def chapter_title(P, title, sub):
    """开场后的章节大标题 + 一行副标题（压在胸前）"""
    return f'''<div class="el" style="padding:10px 20px"><div class="cn glowtxt" style="font-size:104px;font-weight:900;line-height:1.1"><span class="skew">{_t(title)}</span></div>
  <div class="cn glowtxt" style="font-size:42px;font-weight:700;margin-top:10px;text-shadow:0 2px 0 rgba(40,25,120,.9),0 0 14px rgba(140,110,255,.9)">{_t(sub)}</div></div>'''

def verdict(P, color, pre, name, en=False):
    """结论条：「飞书重度用户 → 先看 豆包工作 ✓」"""
    a = P[color]; name = _t(name)
    nm = f'<span style="font-family:PopBI;font-size:56px">{name}</span>' if en else f'<span class="cn" style="font-weight:900;font-size:56px">{name}</span>'
    return f'''<div class="el" style="padding:6px"><div style="display:flex;align-items:center;gap:18px;padding:22px 40px;border-radius:32px;background:linear-gradient(90deg,{a[0]},{a[1]});border:2.5px solid rgba(255,255,255,.92);color:#fff;box-shadow:inset 0 2px 0 rgba(255,255,255,.5)">
      <span class="cn" style="font-size:42px;font-weight:700;white-space:nowrap">{_t(pre)}</span>{icon('arrow',44,'#fff',2.6)}<span class="cn" style="font-size:42px;font-weight:700">先看</span>{nm}
      <span style="width:56px;height:56px;border-radius:50%;background:#fff;display:inline-flex;align-items:center;justify-content:center">{icon('check',36,a[2],3)}</span></div></div>'''

def judge(P, color, cond, name, en=False):
    """判断行：「销售驱动 · 客户管理重 → WorkBuddy」（玻璃长条，960 宽）"""
    a = P[color]; name = _t(name)
    nm = f'<span style="font-family:PopBI;font-size:50px">{name}</span>' if en else f'<span class="cn" style="font-weight:900;font-size:50px">{name}</span>'
    return f'''<div class="el glass" style="{V(a)};width:960px;padding:22px 30px;display:flex;align-items:center;gap:18px">
      <span class="cn" style="font-size:44px;font-weight:900;flex:1;white-space:nowrap">{_t(cond)}</span>{icon('arrow',50,a[1],2.6)}
      <span style="padding:12px 28px;border-radius:24px;background:linear-gradient(90deg,{a[0]},{a[1]});color:#fff">{nm}</span></div>'''

def pill(P, text, color="B"):
    """胶囊标签：「第一步」"""
    a = P[color]
    return f'<div class="el" style="padding:4px"><span class="cn" style="display:inline-block;font-size:44px;font-weight:900;color:#fff;padding:10px 34px;border-radius:999px;background:linear-gradient(90deg,{a[0]},{a[1]});border:2px solid rgba(255,255,255,.9)">{_t(text)}</span></div>'

def chip(P, glyph, text, color="B"):
    """白底描边小标签（一排 2–3 个，用 row 排版）"""
    a = P[color]
    return f'''<div class="el" style="padding:4px"><div style="display:inline-flex;align-items:center;gap:12px;padding:16px 32px;border-radius:999px;background:rgba(255,255,255,.95);border:2.5px solid {a[1]};color:{a[2]};box-shadow:0 6px 16px rgba(80,60,200,.18)">
      {icon(glyph,42,a[2])}<span class="cn" style="font-size:44px;font-weight:900">{_t(text)}</span></div></div>'''

def warn_chip(P, text):
    """橙色提醒条：「这点很多公司会忽略」"""
    return f'''<div class="el" style="padding:4px"><div style="display:inline-flex;align-items:center;gap:14px;padding:16px 36px;border-radius:999px;background:rgba(255,255,255,.95);border:3px solid #FF7A45;color:#C2410C">
  {icon('warn',46,'#C2410C')}<span class="cn" style="font-size:46px;font-weight:900">{_t(text)}</span></div></div>'''

def stamp(P, text):
    """红色印章：「硬指标」（3 个汉字）"""
    return f'''<div class="el" style="padding:30px"><div style="width:480px;height:190px;transform:rotate(-8deg);border:10px solid #E0245E;border-radius:26px;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,.18)">
  <span class="cn" style="font-size:122px;font-weight:900;color:#E0245E;letter-spacing:10px">{_t(text)}</span></div></div>'''

def chat_bar(P, text, sub, tag="示意", color="B"):
    """对话输入条（900 宽）：「一句话 · 企业微信接入以后」"""
    a = P[color]
    return f'''<div class="el glass" style="{V(a)};width:900px;padding:22px 30px;border-radius:30px;display:flex;align-items:center;gap:20px">
  <span style="width:76px;height:76px;border-radius:50%;background:linear-gradient(135deg,{a[0]},{a[1]});display:inline-flex;align-items:center;justify-content:center">{icon('chat',40,'#fff')}</span>
  <span class="cn" style="font-size:48px;font-weight:900">{_t(text)}</span><span class="cn" style="font-size:32px;color:#4F4A78">{_t(sub)}</span>
  <span class="cn" style="margin-left:auto;font-size:24px;color:#fff;background:#8C86B8;border-radius:10px;padding:4px 12px">{_t(tag)}</span></div>'''

# ------------------------------------------------------------------ 小图标 / 小方块
def float_icon(P, color, glyph, size=96):
    """漂浮的 App 图标（开场点缀）"""
    return f'<div class="el" style="padding:6px"><span class="tile" style="{V(P[color])};width:{size}px;height:{size}px;border-radius:26px;border:2px solid rgba(255,255,255,.8)">{icon(glyph,int(size*0.55),"#fff",2)}</span></div>'

def number_tile(P, num, text, glyph):
    """编号方块：01 生态（开场目录）"""
    A, B = P['A'], P['B']
    return f'''<div class="el glass" style="{V(B)};width:250px;height:280px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px">
      <div style="font-family:PopBI;font-size:84px;line-height:1;background:linear-gradient(140deg,{A[0]},{B[0]} 70%);-webkit-background-clip:text;color:transparent">{_t(num)}</div>
      <span class="ic" style="width:60px;height:60px">{icon(glyph,36)}</span>
      <div class="cn" style="font-size:46px;font-weight:900">{_t(text)}</div></div>'''

def icon_tile(P, color, glyph, text):
    """图标方块（220×220）：海报 / 视频"""
    return f'''<div class="el glass" style="{V(P[color])};width:220px;height:220px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
      <span class="tile" style="width:96px;height:96px">{icon(glyph,54,'#fff',2)}</span><span class="cn" style="font-size:40px;font-weight:900">{_t(text)}</span></div>'''

def result_tile(P, glyph, text, color="B"):
    """结果方块（280×230）：客户画像 / 跟进任务"""
    return f'''<div class="el glass" style="{V(P[color])};width:280px;height:230px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px">
      <span class="ic" style="width:88px;height:88px;border-radius:26px">{icon(glyph,50)}</span><span class="cn" style="font-size:40px;font-weight:900">{_t(text)}</span></div>'''

# 组件注册表：分镜表里的 type → 函数；kind 决定默认音效和并发规则
COMPONENTS = {
    'product_panel': (product_panel, 'panel'), 'list_panel': (list_panel, 'panel'), 'big_card': (big_card, 'panel'),
    'small_card': (small_card, 'panel'), 'progress_card': (progress_card, 'panel'), 'rating_panel': (rating_panel, 'panel'),
    'laptop': (laptop, 'panel'),
    'badge': (badge, 'badge'),
    'glow_text': (glow_text, 'text'), 'dim_text': (dim_text, 'text'), 'chapter_title': (chapter_title, 'text'),
    'verdict': (verdict, 'text'), 'judge': (judge, 'text'), 'chat_bar': (chat_bar, 'text'),
    'vs_text': (vs_text, 'decor'), 'strike': (strike, 'decor'), 'stamp': (stamp, 'decor'),
    'pill': (pill, 'label'), 'chip': (chip, 'decor'), 'warn_chip': (warn_chip, 'label'),
    'float_icon': (float_icon, 'decor'), 'number_tile': (number_tile, 'tile'), 'icon_tile': (icon_tile, 'decor'),
    'result_tile': (result_tile, 'decor'),
}

def build(el, palette=None):
    """分镜表里的一个元素 → HTML"""
    P = {k: tuple(v) for k, v in (palette or DEFAULT_PALETTE).items()}
    fn, _ = COMPONENTS[el['type']]
    return fn(P, **el.get('props', {}))
