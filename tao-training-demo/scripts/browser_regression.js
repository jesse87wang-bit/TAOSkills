// 浏览器回归模板（商务差旅范例）：node browser_regression.js <截图目录> [http://127.0.0.1:端口]
// 先用 NO_BROWSER=1 在数据清空的副本里起服务。按课堂脚本点一遍、每步截图、断言关键文字；改选择器和断言即可复用。
// Playwright 和 Chromium 已预装：require('playwright') 直接可用，不要再 playwright install。
const { chromium } = require('playwright');
(async () => {
  const out = process.argv[2];
  const base = process.argv[3] || 'http://127.0.0.1:8768';
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await ctx.newPage();
  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push(String(e)));
  const shot = async name => p.screenshot({ path: `${out}/${name}.png`, fullPage: false });
  const go = async (h, name, wait) => { await p.goto(base + '/#/' + h); await p.waitForTimeout(wait || 900); if (name) await shot(name); };
  const role = async r => { await p.selectOption('#roleSel', r); await p.waitForTimeout(600); };
  const clickIf = async sel => { const el = await p.$(sel); if (el) { await el.click(); return true; } return false; };
  const checks = [];
  const expect = async (what, text) => { const t = await p.textContent('main'); const ok = t.includes(text); checks.push((ok ? 'PASS ' : 'FAIL ') + what + '：页面应出现“' + text + '”'); };
  await go('home', '01_工作台');
  await go('need', '02_出差需求');
  await p.click('#runPlan'); await p.waitForTimeout(3000); await shot('03_出方案运行记录');
  await go('plan', '04_方案对比', 1500);
  await expect('方案对比', '3,951'); await expect('方案对比', '3,748');
  await p.evaluate(() => window.scrollTo(0, 820)); await p.waitForTimeout(300); await shot('05_方案卡片');
  await p.evaluate(() => window.scrollTo(0, 0));
  await p.click('[data-dec="口径"][data-v="B"]'); await p.waitForTimeout(700); await shot('06_助理拍板被拦');
  checks.push(((await p.textContent('#toast')).includes('出行人') ? 'PASS ' : 'FAIL ') + '助理拍板被拦，提示要由出行人来做');
  await role('traveler');
  await go('plan', '07_出行人视角', 1200);
  await p.click('[data-dec="口径"][data-v="B"]'); await p.waitForTimeout(1500);
  await p.click('[data-dec="冲突"][data-v="线上参加"]'); await p.waitForTimeout(1500);
  await p.click('[data-dec="住法"][data-v="合住"]'); await p.waitForTimeout(1500);
  await p.click('[data-pick]'); await p.waitForTimeout(600); await shot('08_选定方案确认框');
  await p.click('#mOk'); await p.waitForTimeout(3500);
  await shot('09_待办与确认');
  await expect('行程包', '4,391'); await expect('行程包', '口径B');
  await p.click('[data-todo="T05"]'); await p.waitForTimeout(600); await shot('10_确认下单'); await p.click('#mOk'); await p.waitForTimeout(1500);
  for (const t of ['T03', 'T06', 'T07', 'T08', 'T09', 'T10', 'T12']) {
    if (await clickIf(`[data-todo="${t}"]`)) {
      await p.waitForTimeout(500);
      if (await p.isVisible('#modal:not(.hidden)')) await p.click('#mOk');
      await p.waitForTimeout(1200);
    }
  }
  await role('manager'); await go('package', '11_部门负责人视角', 1500);
  if (await clickIf('[data-todo="T03"]')) await p.waitForTimeout(1500);
  await p.click('[data-tab="行程单"]'); await p.waitForTimeout(800); await shot('12_行程单');
  await p.click('[data-tab="报备与通知草稿"]'); await p.waitForTimeout(800); await shot('13_报备草稿');
  await role('assistant');
  await go('brief', '14_早报页');
  await p.click('[data-d="2026-11-19"]'); await p.waitForTimeout(3000); await shot('15_早报');
  await go('change', '16_航班变动');
  await p.click('#runChange'); await p.waitForTimeout(3000); await shot('17_航班变动结果');
  await expect('航班变动', '只剩 10 分钟');
  await go('expense', '18_报销页');
  await p.click('#runExp'); await p.waitForTimeout(3000); await shot('19_报销检查');
  await expect('报销检查', '4,068'); await expect('报销检查', '705');
  await go('rules', '20_规则');
  await go('log', '21_日志');
  await go('settings', '22_设置');
  await p.click('#agentBtn'); await p.waitForTimeout(300);
  await p.fill('#agInput', '帮我把机票订了'); await p.press('#agInput', 'Enter'); await p.waitForTimeout(1500);
  await p.fill('#agInput', '为什么不推荐最便宜的？'); await p.press('#agInput', 'Enter'); await p.waitForTimeout(1500);
  await shot('23_问助理');
  const ag = await p.textContent('#agList'); checks.push((ag.includes('不能直接下单') ? 'PASS ' : 'FAIL ') + '问助理“帮我把机票订了”：回答不能直接下单');
  await p.click('#agClose');
  await go('home', '25_工作台_之后', 1500);
  await p.selectOption('#tripSel', 'cd'); await p.waitForTimeout(600);
  await go('need', null); await p.click('#runPlan'); await p.waitForTimeout(3000);
  await go('plan', '26_成都_方案对比', 1500);
  await expect('成都方案', '2,148');
  const m = await b.newContext({ viewport: { width: 390, height: 844 } }); const mp = await m.newPage();
  await mp.goto(base + '/#/plan'); await mp.waitForTimeout(1800); await mp.screenshot({ path: `${out}/24_手机宽度.png` });
  const sw = await mp.evaluate(() => document.documentElement.scrollWidth);
  console.log('mobile scrollWidth', sw);
  checks.push((sw <= 390 ? 'PASS ' : 'FAIL ') + '手机宽度 390 没有横向滚动（scrollWidth=' + sw + '）');
  console.log(checks.join('\n'));
  console.log('errors', JSON.stringify(errs));
  await b.close();
})();
