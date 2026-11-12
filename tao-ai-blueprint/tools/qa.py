"""验收脚本：python3 tools/qa.py <3D页面.html> [截图目录]
检查：无脚本错误、4 个视图可切换、步骤按钮和下一步有效、全屏按钮、驾驶舱图表与批准派发、
三种宽度（手机 390 / Claude 窗口 1180 / 宽屏 1600）截图；全程拦截谷歌字体，模拟国内离线环境。"""
import asyncio, sys, json, os
from playwright.async_api import async_playwright
page_path = os.path.abspath(sys.argv[1]); outdir = sys.argv[2] if len(sys.argv) > 2 else 'qa'
os.makedirs(outdir, exist_ok=True)
ARGS = ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
async def main():
    res = {'errors': [], 'checks': {}}
    async with async_playwright() as p:
        exe = '/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None
        b = await p.chromium.launch(executable_path=exe, args=ARGS)
        pg = await b.new_page(viewport={'width': 1600, 'height': 900})
        pg.on('pageerror', lambda e: res['errors'].append(str(e)))
        await pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
        await pg.goto('file://' + page_path); await pg.wait_for_timeout(2500)
        ok = lambda k, v: res['checks'].__setitem__(k, bool(v))
        ok('logo已填', (await pg.text_content('#logo')).strip())
        for v in ['campus', 'org', 'ideal']:
            await pg.click(f'button[data-view={v}]'); await pg.wait_for_timeout(500)
            n = await pg.evaluate("document.querySelectorAll('#steps button').length")
            await pg.click('#steps button:nth-child(3)'); await pg.wait_for_timeout(300)
            t3 = await pg.text_content('#s-title')
            await pg.click('#next'); await pg.wait_for_timeout(300)
            t4 = await pg.text_content('#s-title')
            ok(f'{v}:有8步', n == 8); ok(f'{v}:步骤和下一步可点', t3 and t4 and t3 != t4 and await pg.evaluate("document.querySelectorAll('#steps button')[3].classList.contains('on')"))
            await pg.wait_for_timeout(6000); await pg.screenshot(path=f'{outdir}/{v}_1600.png')
        await pg.click('button[data-view=campus]'); await pg.wait_for_timeout(300)
        await pg.click('#fs'); await pg.wait_for_timeout(400)
        ok('全屏按钮', await pg.evaluate("document.body.classList.contains('immersive')"))
        await pg.click('#fs'); await pg.wait_for_timeout(300)
        await pg.click('button[data-view=cockpit]'); await pg.wait_for_timeout(2500)
        ok('驾驶舱图表', await pg.evaluate("document.querySelectorAll('#cockpit svg').length") >= 6)
        ok('驾驶舱状态块', await pg.evaluate("document.querySelectorAll('#ck-tiles .tile').length") >= 8)
        await pg.click('#ck-decs .dec [data-act=ok]'); await pg.wait_for_timeout(2500)
        ok('批准即派发', await pg.evaluate("document.querySelectorAll('#ck-log li:not(.muted)').length") >= 1)
        await pg.click('#ck-stage [data-st="3"]'); await pg.wait_for_timeout(2500)
        ok('派发路径随阶段变化', await pg.evaluate("document.querySelectorAll('#ck-route .rn').length") >= 4)
        await pg.screenshot(path=f'{outdir}/cockpit_1600.png')
        await pg.close()
        for w, h in [(1180, 760), (390, 844)]:
            q = await b.new_page(viewport={'width': w, 'height': h})
            q.on('pageerror', lambda e: res['errors'].append(str(e)))
            await q.route('**/fonts.googleapis.com/**', lambda r: r.abort())
            await q.goto('file://' + page_path); await q.wait_for_timeout(2000)
            await q.click('button[data-view=cockpit]'); await q.wait_for_timeout(1500)
            panels = await q.evaluate("[...document.querySelectorAll('.ck-grid > .p')].map(e=>e.getBoundingClientRect().width)")
            ok(f'驾驶舱{w}宽面板不被挤窄', min(panels) > (w * 0.4 if w < 1000 else 300))
            await q.screenshot(path=f'{outdir}/cockpit_{w}.png', full_page=False)
            await q.click('button[data-view=campus]'); await q.wait_for_timeout(5000)
            await q.screenshot(path=f'{outdir}/campus_{w}.png')
            await q.close()
        await b.close()
    res['pass'] = not res['errors'] and all(res['checks'].values())
    print(json.dumps(res, ensure_ascii=False, indent=1))
    sys.exit(0 if res['pass'] else 1)
asyncio.run(main())
