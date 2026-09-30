# 把分镜表里的组件渲染成 3 倍透明 PNG（Playwright + Chromium）
# 字体全部来自 assets.json 里固定版本的文件，不依赖系统字体：
#   Linux：Poppins 走 @font-face，中文走私有 fontconfig（与第一条成片的渲染路径完全相同 → 逐像素一致）
#   macOS/Windows：Chromium 不读 fontconfig，中文改走 @font-face（字形相同，抗锯齿有细微差别；要逐像素一致请在 Linux/Docker 里跑）
import os, sys, asyncio, pathlib
from . import assets
from .components import BASE_CSS

# 溢出检查：nowrap 文字或固定宽度容器被撑破时报出来
_OVERFLOW_JS = """
() => {
  // 每段文字都要完整落在卡片里、且不被任何 overflow:hidden 的容器裁掉
  const out = [];
  const root = document.querySelector('.el');
  const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const t = n.textContent.trim(); if (!t) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    const r = rg.getBoundingClientRect();
    for (let a = n.parentElement; a; a = a.parentElement) {
      const cs = getComputedStyle(a);
      if (a === root || cs.overflowX !== 'visible' || cs.overflowY !== 'visible') {
        const b = a.getBoundingClientRect();
        if (r.left < b.left - 1 || r.right > b.right + 1) { out.push('文字超出/被裁切：' + t.slice(0, 24)); break; }
      }
      if (a === root) break;
    }
  }
  return [...new Set(out)];
}
"""

def font_css():
    f = assets.fonts()
    u = lambda n: pathlib.Path(f[n]).resolve().as_uri()
    css = (f"@font-face{{font-family:PopBI;src:url({u('Poppins-BlackItalic.ttf')})}}\n"
           f"@font-face{{font-family:PopSB;src:url({u('Poppins-SemiBold.ttf')})}}\n")
    if not sys.platform.startswith('linux'):
        css += ''.join(f"@font-face{{font-family:'Noto Sans CJK SC';src:url({u(n)});font-weight:{w}}}\n"
                       for n, w in [('NotoSansCJKsc-Regular.otf', 400), ('NotoSansCJKsc-Medium.otf', 500),
                                    ('NotoSansCJKsc-Bold.otf', 700), ('NotoSansCJKsc-Black.otf', 900)])
    return css

# 私有 fontconfig：Chromium 只看得到 toolkit/fonts 里固定版本的字体，渲染参数也写死
# （与基准环境一致：灰度抗锯齿 + hintslight），所以不受本机装了什么字体、什么字体配置影响。
FONTS_CONF = """<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>{fonts}</dir>
  <cachedir>{cache}</cachedir>
  <match target="font">
    <edit name="antialias" mode="assign"><bool>true</bool></edit>
    <edit name="hinting" mode="assign"><bool>true</bool></edit>
    <edit name="hintstyle" mode="assign"><const>hintslight</const></edit>
    <edit name="autohint" mode="assign"><bool>false</bool></edit>
    <edit name="rgba" mode="assign"><const>rgb</const></edit>
    <edit name="lcdfilter" mode="assign"><const>lcddefault</const></edit>
    <edit name="embeddedbitmap" mode="assign"><bool>true</bool></edit>
  </match>
</fontconfig>
"""

def fontconfig_file():
    assets.fonts()
    d = os.path.join(assets.FONT_DIR, '.fontconfig'); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, 'fonts.conf')
    with open(p, 'w') as f:
        f.write(FONTS_CONF.format(fonts=os.path.abspath(assets.FONT_DIR), cache=os.path.join(d, 'cache')))
    return p

def page(html, fcss):
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{fcss}{BASE_CSS}</style></head><body>{html}</body></html>"

async def _render(items, out_dir, tmp_html, check):
    from playwright.async_api import async_playwright
    fcss = font_css(); warn = {}
    if not sys.platform.startswith('linux'):
        print('⚠ 非 Linux：素材和基准会有肉眼看不出的抗锯齿差异；要逐像素一致请在 Linux 或 Docker 里跑 sprites', flush=True)
    os.makedirs(out_dir, exist_ok=True)
    async with async_playwright() as p:
        env = dict(os.environ, FONTCONFIG_FILE=fontconfig_file())
        b = await p.chromium.launch(env=env)
        pg = await b.new_page(viewport={'width': 1400, 'height': 1400}, device_scale_factor=3)
        for name, html in items.items():
            with open(tmp_html, 'w', encoding='utf-8') as f:
                f.write(page(html, fcss))
            await pg.goto(pathlib.Path(tmp_html).resolve().as_uri())
            await pg.evaluate('document.fonts.ready')
            await pg.wait_for_timeout(100)
            if check:
                w = await pg.evaluate(_OVERFLOW_JS)
                if w:
                    warn[name] = w
            await pg.locator('.el').first.screenshot(path=os.path.join(out_dir, name + '.png'), omit_background=True)
            print('ok', name, flush=True)
        await b.close()
    os.remove(tmp_html)
    return warn

def render(items, out_dir, check=True):
    """items = {素材名: html}；返回 {素材名: [溢出警告]}"""
    return asyncio.run(_render(items, out_dir, os.path.join(out_dir, '_render.html'), check))
