"""逐步截图，检查每一步镜头有没有对准、标签有没有挤在一起：
python3 tools/snap.py <3D页面.html> [截图目录] [视图，默认 campus,org,ideal] [宽度，默认 1440]
每一步等镜头飞到位再截，输出 <视图>_<步>.png。看图标准见 README「镜头怎么调」。"""
import asyncio, sys, os
from playwright.async_api import async_playwright
path = os.path.abspath(sys.argv[1]); out = sys.argv[2] if len(sys.argv) > 2 else 'snap'
views = (sys.argv[3] if len(sys.argv) > 3 else 'campus,org,ideal').split(',')
W = int(sys.argv[4]) if len(sys.argv) > 4 else 1440
os.makedirs(out, exist_ok=True)
ARGS = ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=ARGS)
        pg = await b.new_page(viewport={'width': W, 'height': 860})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
        await pg.goto('file://' + path); await pg.wait_for_timeout(2500)
        for v in views:
            await pg.click(f'button[data-view={v}]'); await pg.wait_for_timeout(800)
            n = await pg.evaluate("document.querySelectorAll('#steps button').length")
            for i in range(n):
                await pg.click(f'#steps button:nth-child({i + 1})')
                await pg.wait_for_timeout(4500)
                await pg.screenshot(path=f'{out}/{v}_{i + 1}.png')
        await pg.click('button[data-view=cockpit]'); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{out}/cockpit.png', full_page=True)
        print('errors:', errs or '无'); print('已截图到', out)
        await b.close()
asyncio.run(main())
