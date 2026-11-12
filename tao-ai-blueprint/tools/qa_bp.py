"""蓝图页验收：python3 tools/qa_bp.py <蓝图.html> [截图目录]"""
import asyncio, sys, os, json
from playwright.async_api import async_playwright
path = os.path.abspath(sys.argv[1]); out = sys.argv[2] if len(sys.argv) > 2 else 'qa'; os.makedirs(out, exist_ok=True)
async def main():
    res = {'errors': [], 'checks': {}}
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome' if os.path.exists('/usr/bin/google-chrome') else None, args=['--no-sandbox'])
        for w, h in [(1440, 900), (390, 844)]:
            pg = await b.new_page(viewport={'width': w, 'height': h})
            pg.on('pageerror', lambda e: res['errors'].append(str(e)))
            await pg.route('**/fonts.googleapis.com/**', lambda r: r.abort())
            await pg.goto('file://' + path); await pg.wait_for_timeout(2000)
            ok = lambda k, v: res['checks'].__setitem__(f'{w}:{k}', bool(v))
            ok('9个板块', await pg.evaluate("document.querySelectorAll('main section').length") == 9)
            ok('业务地图可点', await pg.evaluate("document.querySelectorAll('#chain .link').length") >= 6)
            await pg.click('#chain .link:nth-child(2)'); ok('点击后详情变化', (await pg.text_content('#d-pain')).strip())
            await pg.click('#play'); await pg.wait_for_timeout(2600); ok('运行图播放', (await pg.text_content('#runcap')).strip())
            ok('矩阵有点', await pg.evaluate("document.querySelectorAll('#dots circle').length") >= 6)
            ok('路线图有关口线', await pg.evaluate("document.querySelectorAll('.gateline').length") >= 2)
            for sid in ['ideal', 'map', 'road', 'first']:
                el = await pg.query_selector('#' + sid); await el.screenshot(path=f'{out}/bp_{sid}_{w}.png')
            await pg.close()
        await b.close()
    res['pass'] = not res['errors'] and all(res['checks'].values())
    print(json.dumps(res, ensure_ascii=False, indent=1)); sys.exit(0 if res['pass'] else 1)
asyncio.run(main())
