/* 商务差旅助手 · 网页演示版前端（原生 JS，不依赖外部库） */
'use strict';
let META = null, ROLE = 'assistant', TRIP = 'sh', CACHE = {};
const $ = s => document.querySelector(s);
const main = () => $('#main');
function lsGet(k, d) { try { return localStorage.getItem(k) || d; } catch (e) { return d; } }
function lsSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 浏览器不让存就算了 */ } }
function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function yuan(x) { return x == null ? '【待补】' : Number(x).toLocaleString('zh-CN') + ' 元'; }
function dur(m) { m = Math.round(m); const h = Math.floor(m / 60), r = m % 60; return h ? `${h}小时${String(r).padStart(2, '0')}分` : `${r}分钟`; }
function hm(iso) { return iso ? iso.slice(11, 16) : ''; }
function md2(iso) { if (!iso) return ''; const d = new Date(iso.slice(0, 10) + 'T00:00'); return `${d.getMonth() + 1}月${d.getDate()}日`; }
function roleLabel(k) { return META ? META.roles[k].label : k; }

async function api(path, body) {
  const opt = { headers: { 'X-Role': ROLE } };
  if (body !== undefined) { opt.method = 'POST'; opt.headers['Content-Type'] = 'application/json'; opt.body = JSON.stringify(body); }
  let r;
  try { r = await fetch('/api/' + path, opt); } catch (e) { throw new Error('连不上本地服务：请确认“启动.command”的窗口还开着'); }
  const j = await r.json().catch(() => ({ error: '服务返回了看不懂的内容' }));
  if (!r.ok) { const e = new Error(j.error || ('出错了：' + r.status)); e.denied = j.denied; e.status = r.status; throw e; }
  return j;
}
function toast(msg, err) {
  const d = document.createElement('div'); d.textContent = msg; if (err) d.className = 'err';
  $('#toast').appendChild(d); setTimeout(() => d.remove(), err ? 6500 : 3200);
}
async function act(fn, okMsg) {
  try { const r = await fn(); if (okMsg) toast(okMsg); return r; }
  catch (e) { toast(e.message, true); return null; }
}
function confirmBox(html, okText) {
  return new Promise(res => {
    $('#mbody').innerHTML = html; $('#mOk').textContent = okText || '确认';
    $('#modal').classList.remove('hidden');
    const done = v => { $('#modal').classList.add('hidden'); $('#mOk').onclick = $('#mCancel').onclick = null; res(v); };
    $('#mOk').onclick = () => done(true); $('#mCancel').onclick = () => done(false);
  });
}
function copyText(t) {
  const fallback = () => { const a = document.createElement('textarea'); a.value = t; document.body.appendChild(a); a.select(); try { document.execCommand('copy'); } catch (e) { /* */ } a.remove(); };
  if (navigator.clipboard) navigator.clipboard.writeText(t).then(() => toast('已复制'), () => { fallback(); toast('已复制'); }); else { fallback(); toast('已复制'); }
}

/* ---------- 极简 Markdown 渲染（标题、表格、引用、列表、粗体） ---------- */
function inline(s) { return esc(s).replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>').replace(/`([^`]+)`/g, '<code>$1</code>'); }
function md(text, opts) {
  opts = opts || {};
  const L = String(text || '').split('\n'); let out = [], i = 0;
  while (i < L.length) {
    const l = L[i];
    if (/^\s*$/.test(l)) { i++; continue; }
    let m = l.match(/^(#{1,3})\s+(.*)/);
    if (m) { out.push(`<h${m[1].length}>${inline(m[2])}</h${m[1].length}>`); i++; continue; }
    if (l.startsWith('|')) {
      const rows = []; while (i < L.length && L[i].startsWith('|')) { rows.push(L[i]); i++; }
      const cells = r => r.replace(/^\|/, '').replace(/\|\s*$/, '').split('|').map(c => c.trim());
      const head = cells(rows[0]); const body = rows.slice(2).map(cells);
      out.push('<div class="tw"><table><thead><tr>' + head.map(h => `<th>${inline(h)}</th>`).join('') + '</tr></thead><tbody>' +
        body.map(r => '<tr>' + r.map(c => `<td>${inline(c).replace(/&lt;br&gt;/g, '<br>')}</td>`).join('') + '</tr>').join('') + '</tbody></table></div>');
      continue;
    }
    if (l.startsWith('>')) {
      const q = []; while (i < L.length && L[i].startsWith('>')) { q.push(L[i].replace(/^>\s?/, '')); i++; }
      const raw = q.join('\n');
      out.push(`<blockquote>${inline(raw).replace(/\n/g, '<br>')}${opts.copy ? `<button class="ghost sm copy" data-copy="${esc(raw)}">复制</button>` : ''}</blockquote>`);
      continue;
    }
    if (/^- /.test(l)) {
      const li = []; while (i < L.length && /^- /.test(L[i])) { li.push(L[i].slice(2)); i++; }
      out.push('<ul>' + li.map(x => `<li>${inline(x)}</li>`).join('') + '</ul>'); continue;
    }
    const p = []; while (i < L.length && L[i].trim() && !/^(#|\||>|- )/.test(L[i])) { p.push(L[i]); i++; }
    out.push(`<p>${inline(p.join(' '))}</p>`);
  }
  return `<div class="md">${out.join('')}</div>`;
}
document.addEventListener('click', e => { const b = e.target.closest('[data-copy]'); if (b) copyText(b.dataset.copy); });

/* ---------- 启动与框架 ---------- */
async function loadMeta() { META = await api('meta'); return META; }
function tripMeta() { return META.trips[TRIP]; }
function tripState() { return META.states[TRIP]; }
function header(title, sub) { return `<h1>${esc(title)}</h1><p class="sub">${sub || esc(tripMeta().label + ' · ' + tripMeta().dates)}</p>`; }
function needPlanHtml(what) { return `<div class="card empty">${esc(what)}<br><br><a href="#/need"><button>去 ① 出差需求</button></a></div>`; }
function needPkgHtml(what) { return `<div class="card empty">${esc(what)}<br><br><a href="#/plan"><button>去 ② 方案对比</button></a></div>`; }

async function boot() {
  ROLE = lsGet('travel_role', 'assistant'); TRIP = lsGet('travel_trip', 'sh');
  try { await loadMeta(); } catch (e) { main().innerHTML = `<div class="card empty">${esc(e.message)}</div>`; return; }
  if (!META.trips[TRIP]) TRIP = 'sh';
  if (!META.roles[ROLE]) ROLE = 'assistant';
  $('#tripSel').innerHTML = Object.values(META.trips).map(t => `<option value="${t.id}">${esc(t.label)}（${esc(t.dates)}）</option>`).join('');
  $('#roleSel').innerHTML = Object.entries(META.roles).map(([k, v]) => `<option value="${k}">${esc(v.label)}</option>`).join('');
  $('#tripSel').value = TRIP; $('#roleSel').value = ROLE;
  $('#tripSel').onchange = e => { TRIP = e.target.value; lsSet('travel_trip', TRIP); CACHE = {}; renderChips(); route(); };
  $('#roleSel').onchange = e => { ROLE = e.target.value; lsSet('travel_role', ROLE); updateSide(); toast('当前身份：' + roleLabel(ROLE) + '。' + META.roles[ROLE].desc); route(); };
  $('#dataPill').textContent = '样例数据 · 演示模式'; $('#dataPill').title = META.label;
  $('#menuBtn').onclick = () => $('#side').classList.toggle('open');
  updateModel(META.model); updateSide(); renderChips();
  window.addEventListener('hashchange', route);
  route();
}
function updateModel(m) { $('#modelPill').textContent = m.online ? '在线 · ' + m.label : '离线 · 程序摘要'; $('#modelPill').className = 'pill ' + (m.online ? 'ok' : ''); $('#agMode').textContent = $('#modelPill').textContent; }
function updateSide() { $('#sideFoot').innerHTML = `当前身份：<b>${esc(roleLabel(ROLE))}</b><br>${esc(META.roles[ROLE].desc)}<br><br>${esc(META.label)}`; }

const PAGES = { home, need, plan, package: pkg, brief, change, expense, rules, log, settings };
async function refresh() { const y = window.scrollY; await loadMeta(); const p = (location.hash.replace('#/', '') || 'home').split('?')[0]; await (PAGES[p] || home)(); window.scrollTo(0, y); }
async function route() {
  const p = (location.hash.replace('#/', '') || 'home').split('?')[0];
  document.querySelectorAll('#nav a').forEach(a => a.classList.toggle('cur', a.dataset.p === p));
  $('#side').classList.remove('open');
  main().innerHTML = '<div class="loading">加载中…</div>';
  try { await loadMeta(); await (PAGES[p] || home)(); } catch (e) { main().innerHTML = `<div class="card empty">${esc(e.message)}</div>`; }
  window.scrollTo(0, 0);
}

/* ---------- 今日工作台 ---------- */
const STAGES = ['需求', '已出方案', '已选定', '已报销检查'];
const STAGE_LABEL = { '需求': '需求', '已出方案': '方案', '已选定': '行程包', '已报销检查': '报销' };
async function home() {
  let html = `<h1>今日工作台</h1><p class="sub">假设今天是 2026 年 11 月 12 日。${esc(META.label)}</p>`;
  const mine = [];
  for (const t of Object.values(META.trips)) {
    const st = META.states[t.id];
    const idx = STAGES.indexOf(st.stage);
    html += `<div class="card"><div class="row"><h3>${esc(t.label)}</h3><span class="pill acc">${esc(t.dates)}</span><span class="sp"></span>
      <button class="ghost sm" data-go="${t.id}" data-to="${st.package_ready ? 'package' : st.plan_ready ? 'plan' : 'need'}">打开</button></div>
      <div class="steps">${STAGES.map((s, i) => `<span class="${i < idx ? 'done' : i === idx ? 'now' : ''}">${STAGE_LABEL[s]}</span>`).join('')}</div>`;
    if (st.plan_ready) {
      const r = await api(`trip/${t.id}/plan`).catch(() => null);
      if (r) {
        const c = { 高: 0, 中: 0, 低: 0 }; r.res['问题清单'].forEach(i => c[i['级别']]++);
        html += `<div class="note">问题 ${r.res['问题清单'].length} 条（高 ${c['高']}、中 ${c['中']}、低 ${c['低']}）；必须先拍板 ${r.res['必须先拍板'].length} 件</div>`;
        if (ROLE === 'traveler' && !st.package_ready) mine.push(`<li>${esc(t.label)}：在“② 方案对比”里拍板并选定方案</li>`);
      }
    } else { html += `<div class="note">还没出方案。下一步：在“① 出差需求”里点“出方案”。</div>`; }
    if (st.package_ready) {
      const p = await api(`trip/${t.id}/package`).catch(() => null);
      if (p) {
        const pend = p.todos.filter(x => x['状态'] !== '完成');
        html += `<div class="note">待办 ${p.todos.length} 件，未完成 ${pend.length} 件；费用预估 ${yuan(p.pkg['费用预估']['合计'])}</div>`;
        pend.filter(x => x['谁来确认_key'] === ROLE).forEach(x => mine.push(`<li>${esc(t.label)}：${esc(x['事项'])}（截止 ${esc(x['截止'])}）</li>`));
        const next = (p.pkg['提醒计划'] || []).slice(0, 3).map(r => `${r['时间'].replace('T', ' ')} ${r['内容']}`);
        if (next.length) html += `<div class="note">接下来的提醒：${esc(next.join('；'))}</div>`;
      }
    }
    html += `</div>`;
  }
  html += `<div class="card"><h3>要“${esc(roleLabel(ROLE))}”处理的事</h3>${mine.length ? '<ul>' + mine.join('') + '</ul>' : '<p class="note">现在没有。切换右上角身份，看不同的人各要做什么。</p>'}</div>`;
  main().innerHTML = html;
  main().querySelectorAll('[data-go]').forEach(b => b.onclick = () => { TRIP = b.dataset.go; lsSet('travel_trip', TRIP); $('#tripSel').value = TRIP; location.hash = '#/' + b.dataset.to; });
}

/* ---------- ① 出差需求 ---------- */
async function need() {
  const info = await api(`trip/${TRIP}/info`);
  const req = info['需求'];
  const ppl = Object.entries(info['出行人']).map(([k, p]) => `<div class="tile"><b style="font-size:16px">${esc(p.name)}</b><span>${esc(p.title)} · ${esc(p.level)} · ${esc(p.gender)}</span>
    <div class="chips">${Object.entries(p.prefs || {}).map(([a, b]) => `<span class="pill">${esc(prefLabel(a))}：${esc(Array.isArray(b) ? b.join('、') : b)}</span>`).join('') || '<span class="note">没有特别偏好</span>'}</div></div>`).join('');
  const ev = req.events.map(e => `<tr><td>${esc(e.id)}</td><td>${esc(e.title)}</td><td class="nw">${md2(e.start)} ${hm(e.start)}—${hm(e.end)}</td><td>${esc(e.place)}</td><td>${e.external ? '外部客户' : '内部'}</td><td>${esc(e.contact || '')}</td></tr>`).join('');
  const legs = req.legs.map(l => `<tr><td>${esc(l.id)}</td><td>${esc(l.from)} → ${esc(l.to)}</td><td>${esc(l.next_event ? '赶 ' + l.next_event : l.prev_event ? l.prev_event + ' 结束后出发' : '')}${l.prev_hotel ? '；从酒店出发' : ''}</td><td>${l.requested_seat ? esc(Object.entries(l.requested_seat).map(([k, v]) => info['出行人'][k].name + v).join('、')) : '按各自差标'}</td><td>${(info['候选'][l.id] || []).length} 个</td></tr>`).join('');
  const stays = (req.stays || []).map(s => `<tr><td>${esc(s.city)}</td><td>${md2(s.check_in)}—${md2(s.check_out)}</td><td>${(info['候选'][s.id] || []).length} 家</td></tr>`).join('');
  const cal = info['日程'].map(c => `<tr><td>${esc(info['出行人'][c.owner] ? info['出行人'][c.owner].name : '')}</td><td>${esc(c.title)}</td><td class="nw">${md2(c.start)} ${hm(c.start)}—${hm(c.end)}</td><td>${c.online ? '<span class="pill acc">线上</span>' : '<span class="pill">线下</span>'}</td></tr>`).join('');
  const st = info.state;
  main().innerHTML = header('① 出差需求') + `
    <div class="card"><h3>原话</h3>${md('> ' + info['原话'].trim().split('\n').join('\n> '))}<p class="note">助理把原话整理成结构化需求（下面几张表，文件：需求.json）。原话里没说的不猜，缺什么一次问完。</p></div>
    <h2>出行人与偏好</h2><div class="grid g3">${ppl}</div>
    <h2>要赶的活动</h2><div class="card tw"><table><thead><tr><th>编号</th><th>活动</th><th>时间</th><th>地点</th><th>类型</th><th>对接人</th></tr></thead><tbody>${ev}</tbody></table></div>
    <div class="grid g2"><div class="card tw"><h3>交通段与候选</h3><table><thead><tr><th>段</th><th>路线</th><th>约束</th><th>指定席别</th><th>候选</th></tr></thead><tbody>${legs}</tbody></table></div>
    <div class="card tw"><h3>住宿与候选</h3><table><thead><tr><th>城市</th><th>日期</th><th>候选</th></tr></thead><tbody>${stays || '<tr><td colspan="3">不住宿</td></tr>'}</tbody></table><p class="note">${esc(info['来源'])}</p></div></div>
    <h2>出行人这几天的日程</h2><div class="card tw"><table><thead><tr><th>谁</th><th>日程</th><th>时间</th><th>方式</th></tr></thead><tbody>${cal || '<tr><td colspan="4">没有</td></tr>'}</tbody></table></div>
    <div class="card"><div class="row"><div><h3>出方案</h3><div class="note">运行 工具/方案计算.py：按差旅规则卡把所有交通、酒店、住法组合起来，逐条核对差标、时间、日程和偏好。数字全由程序算。</div></div><span class="sp"></span>
      <button id="runPlan">${st.plan_ready ? '重新出方案' : '出方案'}</button></div><div id="runLog"></div></div>`;
  $('#runPlan').onclick = async () => {
    $('#runPlan').disabled = true; $('#runLog').innerHTML = '<div class="log">正在运行 python3 工具/方案计算.py …</div>';
    const r = await act(() => api(`trip/${TRIP}/plan`, {}), '方案已算好');
    $('#runPlan').disabled = false;
    if (r) { $('#runLog').innerHTML = `<div class="log">$ python3 工具/方案计算.py --trip … --output …\n${esc(r.log)}</div><p><a href="#/plan"><button>看 ② 方案对比</button></a></p>`; }
    else $('#runLog').innerHTML = '';
  };
}
function prefLabel(k) { return { seat: '座位', earliest_departure: '最早出发', latest_departure: '最晚出发', airport_pref: '机场', buffer_before_external_min: '见客户前留(分钟)', room: '住宿' }[k] || k; }

/* ---------- ② 方案对比 ---------- */
let PLAN_FILTER = '全部';
async function plan() {
  const st = tripState();
  if (!st.plan_ready) { main().innerHTML = header('② 方案对比') + needPlanHtml('这趟出差还没出方案。'); return; }
  const { res } = await api(`trip/${TRIP}/plan`);
  const idx = {}; res['问题清单'].forEach(i => idx[i['编号']] = i);
  const c = { 高: 0, 中: 0, 低: 0 }; res['问题清单'].forEach(i => c[i['级别']]++);
  const s = res['组合统计'];
  let html = header('② 方案对比') + `<div class="grid g4">
    <div class="tile"><b>${s['总组合']}</b><span>种组合（交通 × 酒店 × 住法）</span></div>
    <div class="tile ok"><b>${s['可选']}</b><span>种可选（排除 ${s['排除']} 种硬伤）</span></div>
    <div class="tile hi"><b>${c['高']}</b><span>条高级问题（不解决不能订）</span></div>
    <div class="tile mid"><b>${c['中'] + c['低']}</b><span>条中低级（审批 / 提醒）</span></div></div>
    <p class="note">${esc(res['数据来源'])}。${esc(res['第七条口径']['说明'])}。<a href="/api/trip/${TRIP}/file?kind=${encodeURIComponent('方案')}&name=${encodeURIComponent('方案对比.html')}&inline=1" target="_blank">打开程序原始输出 方案对比.html</a></p>`;
  html += `<div class="card decide"><h3>必须先拍板的事</h3><p class="note">这些事 AI 不替人决定。拍板人：出行人（口径怎么准备、住法、冲突、超标）；财务（确认口径）。</p>${res['必须先拍板'].map(x => decideHtml(x, st)).join('')}</div>`;
  const decided = st.mode_confirmed || (st.decisions || {})['口径'];
  html += `<h2>方案</h2>`;
  if (decided && !st.mode_confirmed) html += `<p class="note">出行人已定先按口径${decided}准备，下面只列口径${decided}下的推荐；另一种口径的推荐，改选口径就能看到。</p>`;
  const order = Object.entries(res['方案']).filter(([n]) => !decided || !/[AB]$/.test(n) || n.endsWith(decided));
  for (const [name, p] of order) html += planCard(name, p, res, idx, st);
  html += `<h2>问题清单（${res['问题清单'].length} 条）</h2><div class="chips" id="pf">${['全部', '高', '中', '低'].map(k => `<button class="${k === PLAN_FILTER ? 'cur' : ''}" data-f="${k}">${k}</button>`).join('')}</div>
    <div class="card tw"><table><thead><tr><th>编号</th><th>级别</th><th>对象</th><th>问题</th><th>证据</th><th>建议</th><th>口径</th></tr></thead><tbody>
    ${res['问题清单'].filter(i => PLAN_FILTER === '全部' || i['级别'] === PLAN_FILTER).map(i => `<tr><td>${esc(i['编号'])}</td><td><span class="lv ${i['级别']}">${i['级别']}</span></td><td>${esc(i['对象'])}</td><td>${esc(i['问题'])}</td><td>${esc(i['证据'])}</td><td>${esc(i['建议'])}</td><td>${esc(i['适用口径'])}</td></tr>`).join('')}</tbody></table></div>
    <details class="card"><summary><b>各选项核对（${res['选项核对'].length} 个）</b></summary><div class="tw"><table><thead><tr><th>段</th><th>选项</th><th>内容</th><th>出门</th><th>到场/到家</th><th>费用</th><th>结论</th><th>问题</th></tr></thead><tbody>
    ${res['选项核对'].map(r => `<tr class="${r['结论'] === '排除' ? 'ex' : ''}"><td>${esc(r['段'])}</td><td>${esc(r['选项'])}</td><td>${esc(r['内容'])}</td><td>${esc(r['出门'])}</td><td>${esc(r['到场/到家'])}</td><td class="nw">${yuan(r['费用'])}</td><td>${esc(r['结论'])}</td><td>${esc(r['问题'])}</td></tr>`).join('')}</tbody></table></div></details>`;
  main().innerHTML = html;
  main().querySelectorAll('#pf button').forEach(b => b.onclick = () => { PLAN_FILTER = b.dataset.f; refresh(); });
  main().querySelectorAll('[data-dec]').forEach(b => b.onclick = async () => {
    const r = await act(() => api(`trip/${TRIP}/decide`, { key: b.dataset.dec, value: b.dataset.v }), '已记录：' + b.dataset.dec + ' → ' + b.dataset.v);
    if (r) refresh();
  });
  main().querySelectorAll('[data-pick]').forEach(b => b.onclick = async () => {
    const ok = await confirmBox(`<h3>选定方案：${esc(b.dataset.title)}</h3><p>${esc(b.dataset.desc)}</p><p class="note">选定后生成行程包：行程单、日历文件、待办与确认清单、报备与通知草稿、提醒计划。不会下单，也不会发消息。</p>`, '选定并生成行程包');
    if (!ok) return;
    const r = await act(() => api(`trip/${TRIP}/choose`, { pick: b.dataset.pick, mode: b.dataset.mode || undefined }), '行程包已生成');
    if (r) location.hash = '#/package';
  });
}
function decideHtml(x, st) {
  const d = st.decisions || {};
  const btns = (key, vals, roleKey) => vals.map(v => `<button class="sm ${d[key] === v ? 'on' : 'ghost'}" data-dec="${key}" data-v="${v}">${v}</button>`).join(' ') + ` <span class="who">由${esc(roleLabel(roleKey))}拍板</span>`;
  let ctl = '';
  if (x['事项'] === '日程冲突') ctl = btns('冲突', ['改期', '请人代开', '线上参加'], 'traveler');
  else if (x['事项'] === '第七条口径') {
    ctl = st.mode_confirmed ? `<span class="pill ok">财务已确认：口径${st.mode_confirmed}</span>` :
      `<div>先按哪种准备：${btns('口径', ['A', 'B'], 'traveler')}</div><div style="margin-top:4px">财务确认：<button class="sm ghost" data-dec="口径确认" data-v="A">确认口径A</button> <button class="sm ghost" data-dec="口径确认" data-v="B">确认口径B</button> <span class="who">由财务确认，确认后按一种口径重算</span></div>`;
  } else if (x['事项'] === '合住还是分住') ctl = btns('住法', ['合住', '分住'], 'traveler');
  else if (x['事项'] === '超标') ctl = st.seat_fix ? '<span class="pill ok">已改订标准席别，方案已重算</span>' : btns('超标', ['申请超标审批', '改订标准席别'], 'traveler');
  return `<div class="ditem"><div class="t">${esc(x['事项'])}：${esc(x['说明'])}</div><div class="d">${esc(x['细节'])}。建议：${esc(x['建议'])}</div>${ctl}</div>`;
}
function planCard(name, p, res, idx, st) {
  const rec = name.startsWith('推荐');
  const mode = /[AB]$/.test(name) ? name.slice(-1) : '';
  const title = { 推荐A: '推荐 · 口径A（只看起飞）', 推荐B: '推荐 · 口径B（起降都在时段内）', 推荐: '推荐', 最省钱: '最省钱', 最省时: '最省时' }[name] || name.replace(/([AB])$/, ' · 口径$1');
  const pick = name.startsWith('推荐') ? '推荐' : name;
  const legs = p['交通'].map(x => `<tr><td>${esc(x['段'])}</td><td>${esc(x['方式'])} ${esc(x['班次'])}<br><span class="note">${esc(x['出发站'])} → ${esc(x['到达站'])}</span></td><td class="nw">${md2(x['出发'])} ${hm(x['出发'])}—${hm(x['到达'])}</td><td>${hm(x['出门'])} 出门 → ${hm(x['到场'])} 到${esc(x['到达后去'])}</td><td>${Object.entries(x['席别']).map(([n, s]) => `${esc(n)} ${esc(s['席别'])} ${yuan(s['票价'])}${s['超标'] ? `<span class="pill hi">超 ${yuan(s['超标'])}</span>` : ''}`).join('<br>')}</td></tr>`).join('') +
    p['住宿'].map(h => `<tr><td>住宿</td><td>${esc(h['酒店'])}</td><td class="nw">${md2(h['入住'])} 起 ${h['晚数']} 晚</td><td>${esc(h['住法'])} ${h['间数']} 间</td><td>${yuan(h['房价'])} × ${h['间数']} = ${yuan(h['合计'])}</td></tr>`).join('');
  const qs = (p['问题'] || []).map(q => idx[q] ? `<span class="q ${idx[q]['级别']}" title="${esc(idx[q]['证据'])}">${q} ${esc(idx[q]['问题'])}</span>` : '').join('');
  const why = (res['推荐理由'][name] || []).map(r => `<li>${esc(r)}</li>`).join('');
  const desc = p['交通'].map(x => `${x['段']} ${x['班次']}`).join('，') + (p['住宿'].length ? '，住 ' + p['住宿'].map(h => h['酒店'] + '（' + h['住法'] + '）').join('、') : '') + '，合计 ' + yuan(p['费用']['合计']);
  return `<div class="card plan ${rec ? 'rec' : ''}"><div class="row"><h3>${esc(title)}</h3><span class="sp"></span><span class="big">${yuan(p['费用']['合计'])}</span></div>
    <div class="note">交通 ${yuan(p['费用']['交通'])} + 住宿 ${yuan(p['费用']['住宿'])} · 在途 ${dur(p['在途分钟'])} · 综合成本 ${yuan(p['综合成本'])} · 伙食补助另计 ${yuan(p['伙食补助']['合计'])}</div>
    <div class="tw"><table><thead><tr><th>段</th><th>班次 / 酒店</th><th>时间</th><th>出门 → 到场</th><th>席别与票价</th></tr></thead><tbody>${legs}</tbody></table></div>
    ${qs ? `<div style="margin-top:8px">${qs}</div>` : '<div class="note" style="margin-top:8px">没有问题</div>'}
    ${why ? `<ul>${why}</ul>` : ''}
    <div class="row" style="margin-top:10px"><span class="sp"></span><button class="sm ${rec ? '' : 'ghost'}" data-pick="${esc(pick === '推荐' ? '推荐' : name)}" data-mode="${mode}" data-title="${esc(title)}" data-desc="${esc(desc)}">选定这个方案</button><span class="who">由出行人拍板</span></div></div>`;
}

/* ---------- ③ 行程包与确认 ---------- */
let PKG_TAB = '待办与确认';
async function pkg() {
  const st = tripState();
  if (!st.package_ready) { main().innerHTML = header('③ 行程包与确认') + needPkgHtml('还没有选定方案。出行人在“② 方案对比”里选定后，这里会出行程单、日历、待办、报备草稿和提醒计划。'); return; }
  const r = await api(`trip/${TRIP}/package`);
  const P = r.pkg, f = P['费用预估'];
  const pend = r.todos.filter(x => x['状态'] !== '完成').length;
  const tabs = ['待办与确认', '行程单', '报备与通知草稿', '提醒计划', '下载'];
  let body = '';
  if (PKG_TAB === '待办与确认') {
    body = `<p class="note">🔒 = 要本人确认后再办。一次确认只办一件；演示系统不连接订票平台、不发消息、不改日历。切换右上角身份试试：助理点“确认”会被系统拦下。</p>
      <div class="tw"><table><thead><tr><th>编号</th><th>事项</th><th>截止</th><th>状态</th><th>谁来确认</th><th></th></tr></thead><tbody>${r.todos.map(t => {
        const done = t['状态'] === '完成';
        const label = t['事项'].startsWith('提交 OA') ? (t['状态'] === '待办' ? '提交' : '审批通过') : '确认';
        return `<tr><td>${esc(t['编号'])}</td><td>${t['需本人确认'] ? '🔒 ' : ''}${esc(t['事项'])}<div class="note">${esc(t['说明'])}</div></td><td class="nw">${esc(t['截止'])}</td>
          <td class="nw">${done ? '<span class="pill ok">完成</span>' : t['状态'] === '待办' ? '<span class="pill warn">待办</span>' : `<span class="pill acc">${esc(t['状态'])}</span>`}${t['确认人'] && done ? `<div class="note">${esc(t['确认人'])} ${esc(t['确认时间'] || '')}</div>` : ''}</td>
          <td class="nw">${esc(t['谁来确认'])}</td><td>${done || !t['需本人确认'] ? '' : `<button class="sm ${t['谁来确认_key'] === ROLE ? '' : 'ghost'}" data-todo="${esc(t['编号'])}">${label}</button>`}</td></tr>`;
      }).join('')}</tbody></table></div>`;
  } else if (PKG_TAB === '行程单') body = md(r.texts['行程单.md']);
  else if (PKG_TAB === '报备与通知草稿') body = md(r.texts['报备与通知草稿.md'], { copy: true });
  else if (PKG_TAB === '提醒计划') body = md(r.texts['提醒计划.md']) + `<p class="note">正式使用时：“定时任务”用 WorkBuddy 的定时任务或企业日历建；“日历提醒”导入 行程.ics 后由日历自己提醒。演示时请导入一个单独建的“差旅演示”日历，演示完删掉。</p>`;
  else {
    const files = [['行程单.docx', 'Word 行程单'], ['行程.ics', '日历文件（双击导入，出门前 15 分钟、会议前 30 分钟提醒）'], ['行程单.md', '行程单 Markdown'], ['待办清单.json', '待办状态'], ['报备与通知草稿.md', '报备与通知草稿'], ['提醒计划.md', '提醒计划'], ['行程.json', '给早报、航班变动、报销检查用的数据']];
    body = '<ul>' + files.map(([n, d]) => `<li><a href="/api/trip/${TRIP}/file?kind=${encodeURIComponent('行程包')}&name=${encodeURIComponent(n)}">${esc(n)}</a> <span class="note">${esc(d)}</span></li>`).join('') + '</ul>';
  }
  main().innerHTML = header('③ 行程包与确认') + `<div class="grid g4">
    <div class="tile"><b style="font-size:16px">${esc(P['方案名'])}</b><span>${esc(P['方案']['id'])}</span></div>
    <div class="tile"><b>${yuan(f['合计'])}</b><span>费用预估（交通 ${yuan(f['交通'])} + 住宿 ${yuan(f['住宿'])} + 伙食补助 ${yuan(f['伙食补助'])}）</span></div>
    <div class="tile ${pend ? 'mid' : 'ok'}"><b>${pend}</b><span>件待办未完成（共 ${r.todos.length} 件）</span></div>
    <div class="tile"><b>${(P['提醒计划'] || []).length}</b><span>条提醒；报销截止 ${esc(P['报销截止'])}</span></div></div>
    <div class="card"><div class="tabs">${tabs.map(t => `<button class="${t === PKG_TAB ? 'cur' : ''}" data-tab="${t}">${t}</button>`).join('')}</div>${body}</div>`;
  main().querySelectorAll('[data-tab]').forEach(b => b.onclick = () => { PKG_TAB = b.dataset.tab; pkg(); });
  main().querySelectorAll('[data-todo]').forEach(b => b.onclick = async () => {
    const t = r.todos.find(x => x['编号'] === b.dataset.todo);
    if (t['事项'].startsWith('订')) {
      const ok = await confirmBox(`<h3>确认下单</h3><p>${esc(t['事项'])}</p><p>${esc(t['说明'])}</p><p class="note">演示系统没有连接订票平台：确认后只记录“本人已同意”，不会产生订单，也不会付款。正式使用时付款由本人在订票平台完成。</p>`, '本人确认');
      if (!ok) return;
    }
    const x = await act(() => api(`trip/${TRIP}/todo`, { id: t['编号'] }), '已记录');
    if (x) refresh();
  });
}

/* ---------- ④ 早报与提醒 ---------- */
async function brief() {
  const st = tripState();
  if (!st.package_ready) { main().innerHTML = header('④ 早报与提醒') + needPkgHtml('先选定方案、生成行程包，才有早报和提醒。'); return; }
  const list = await api(`trip/${TRIP}/briefs`);
  const dates = tripMeta().brief_dates;
  main().innerHTML = header('④ 早报与提醒') + `<div class="card"><div class="row"><div><h3>生成早报</h3><div class="note">出发前一天出“明日出行提醒”，出行当天出早报。航班动态、天气只用发出时间之前查到的数据；没有就写“出发前再查一次”。</div></div></div>
    <div class="chips" style="margin-top:8px">${dates.map(d => `<button data-d="${d}">${md2(d + 'T00:00')}${list.some(x => x.date === d) ? ' ✓' : ''}</button>`).join('')}</div>
    <p class="note">小提示：先在“③ 行程包与确认”里把订票、出差申请等标成完成，早报只会提醒没办完的事。</p></div>
    ${list.length ? list.map(x => `<div class="card"><div class="row"><h3>${md2(x.date + 'T00:00')}</h3><span class="sp"></span><button class="ghost sm" data-copy="${esc(x.sms)}">复制短信版</button></div>${md(x.md)}<h3 style="margin-top:10px">短信版（企业微信 / 短信可直接粘贴）</h3><div class="sms">${esc(x.sms)}</div></div>`).join('') : '<div class="card empty">还没有生成早报</div>'}`;
  main().querySelectorAll('[data-d]').forEach(b => b.onclick = async () => {
    b.disabled = true;
    const r = await act(() => api(`trip/${TRIP}/brief`, { date: b.dataset.d }), '早报已生成');
    if (r) refresh(); else b.disabled = false;
  });
}

/* ---------- ⑤ 航班变动 ---------- */
async function change() {
  const st = tripState();
  if (!tripMeta().change) { main().innerHTML = header('⑤ 航班变动') + '<div class="card empty">这趟出差没有航班变动样例。换到“林总、张工 · 上海 / 苏州”看。</div>'; return; }
  if (!st.package_ready) { main().innerHTML = header('⑤ 航班变动') + needPkgHtml('先选定方案、生成行程包，才能算航班变动的影响。'); return; }
  const n = await api(`trip/${TRIP}/notice`);
  let html = header('⑤ 航班变动') + `<div class="card"><h3>收到通知（样例）</h3><p>${md2(n.notified_at)} ${hm(n.notified_at)}：<b>${esc(n.no)} ${esc(n.status)}</b>，原因：${esc(n.reason)}；预计 ${hm(n.new_dep)} 起飞、${hm(n.new_arr)} 到达。</p>
    <button id="runChange">${st.change_ready ? '重新算影响' : '算影响'}</button> <span class="note">运行 工具/航班变动处理.py</span></div>`;
  if (st.change_ready) {
    const c = await api(`trip/${TRIP}/change`);
    const opts = (c.md.match(/^\| ✓ [^|]+/gm) || []).map(x => x.replace('| ✓ ', '').trim());
    html += `<div class="card">${md(c.md, { copy: true })}</div><div class="card"><h3>出行人选办法</h3><div class="chips">${opts.map(o => `<button class="${st.change_choice === o ? 'cur' : ''}" data-ch="${esc(o)}">${esc(o)}</button>`).join('')}</div><p class="note">改签、退票、付款都由本人在平台完成；这里只记录选择。${st.change_choice ? '已选择：' + esc(st.change_choice) : ''}</p></div>`;
  }
  main().innerHTML = html;
  $('#runChange').onclick = async () => { const r = await act(() => api(`trip/${TRIP}/change`, {}), '已算好'); if (r) refresh(); };
  main().querySelectorAll('[data-ch]').forEach(b => b.onclick = async () => { const r = await act(() => api(`trip/${TRIP}/change`, { choice: b.dataset.ch }), '已记录选择'); if (r) refresh(); });
}

/* ---------- ⑥ 报销检查 ---------- */
async function expense() {
  const st = tripState();
  if (!tripMeta().invoices) { main().innerHTML = header('⑥ 报销检查') + '<div class="card empty">这趟出差没有发票样例。换到“林总、张工 · 上海 / 苏州”看。</div>'; return; }
  if (!st.package_ready) { main().innerHTML = header('⑥ 报销检查') + needPkgHtml('先选定方案、生成行程包，报销检查要拿发票和确认的行程对照。'); return; }
  let html = header('⑥ 报销检查') + `<div class="card"><div class="row"><div><h3>检查发票</h3><div class="note">出差回来后，把发票识别结果（样例：票据识别结果.json，11 张）交给程序逐张核对。超标审批、招待报备办没办，以“③ 待办与确认”里的状态为准。</div></div><span class="sp"></span><button id="runExp">${st.expense_ready ? '重新检查' : '检查发票'}</button></div></div>`;
  if (st.expense_ready) {
    const e = await api(`trip/${TRIP}/expense`);
    const sum = k => e.rows.reduce((a, r) => a + Number(r[k] || 0), 0);
    const bySt = s => e.rows.filter(r => r['结论'] === s).reduce((a, r) => a + Number(r['金额']), 0);
    html += `<div class="grid g4"><div class="tile ok"><b>${yuan(sum('可报'))}</b><span>可报</span></div><div class="tile mid"><b>${yuan(bySt('需处理'))}</b><span>需处理（补材料或重开后可报）</span></div>
      <div class="tile hi"><b>${yuan(sum('个人承担或不能报'))}</b><span>个人承担或不能报</span></div><div class="tile"><b>${e.rows.length}</b><span>张票据</span></div></div>
      <p class="note">${esc(e.summary)}　<a href="/api/trip/${TRIP}/file?kind=${encodeURIComponent('报销检查')}&name=${encodeURIComponent('报销检查.docx')}">下载 报销检查.docx</a>　<a href="/api/trip/${TRIP}/file?kind=${encodeURIComponent('报销检查')}&name=${encodeURIComponent('报销清单.csv')}">下载 报销清单.csv</a></p>
      <div class="card tw"><table><thead><tr><th>编号</th><th>类型</th><th>人</th><th>内容</th><th>金额</th><th>结论</th><th>原因</th><th>要做什么</th></tr></thead><tbody>${e.rows.map(r => `<tr><td>${esc(r['编号'])}</td><td>${esc(r['类型'])}</td><td>${esc(r['人'])}</td><td>${esc(r['内容'])}</td><td class="nw">${yuan(r['金额'])}</td><td class="nw"><span class="pill ${r['结论'] === '可报' ? 'ok' : r['结论'] === '不能报' ? 'hi' : 'warn'}">${esc(r['结论'])}</span></td><td>${esc(r['原因'])}</td><td>${esc(r['要做什么'])}</td></tr>`).join('')}</tbody></table></div>
      <details class="card"><summary><b>完整报告（报销检查.md）</b></summary>${md(e.md)}</details>`;
  }
  main().innerHTML = html;
  $('#runExp').onclick = async () => { const r = await act(() => api(`trip/${TRIP}/expense`, {}), '已检查'); if (r) refresh(); };
}

/* ---------- 规则与制度 ---------- */
let DOC_TAB = '规则卡';
async function rules() {
  const tabs = ['规则卡', '差旅管理办法', '差旅标准', '偏好档案', '提醒规则', '报销规则', '输入格式'];
  const d = await api('doc?name=' + encodeURIComponent(DOC_TAB));
  const body = d.path.endsWith('.json') ? `<pre class="log" style="max-height:none">${esc(d.text)}</pre>` : md(d.text);
  main().innerHTML = `<h1>规则与制度</h1><p class="sub">规矩是人给的：规则卡写清检查什么、怎么判定、轻重和依据；程序只读 差旅标准.json 里的数字。</p>
    <div class="card"><div class="tabs">${tabs.map(t => `<button class="${t === DOC_TAB ? 'cur' : ''}" data-tab="${t}">${t}</button>`).join('')}</div><p class="note">文件：${esc(d.path)}</p>${body}</div>`;
  main().querySelectorAll('[data-tab]').forEach(b => b.onclick = () => { DOC_TAB = b.dataset.tab; rules(); });
}

/* ---------- 操作日志 ---------- */
async function log() {
  const a = await api('audit');
  main().innerHTML = `<h1>操作日志</h1><p class="sub">谁、在什么身份下、做了什么决定。被权限拦下的操作不会写进来。</p><div class="card tw"><table><thead><tr><th>时间</th><th>身份</th><th>行程</th><th>操作</th><th>说明</th></tr></thead><tbody>
    ${a.map(x => `<tr><td class="nw">${esc(x['时间'])}</td><td class="nw">${esc(x['身份'])}</td><td>${esc(x['行程'])}</td><td>${esc(x['操作'])}</td><td>${esc(x['说明'])}</td></tr>`).join('') || '<tr><td colspan="5">还没有操作</td></tr>'}</tbody></table></div>`;
}

/* ---------- 设置与身份 ---------- */
async function settings() {
  const cfg = await api('settings');
  main().innerHTML = `<h1>设置与身份</h1><p class="sub">${esc(META.label)}</p>
    <div class="card"><h3>四种身份</h3><p class="note">右上角切换。权限由后端检查：换个身份点按钮，没权限的会被拦下并说明原因。</p><div class="tw"><table><thead><tr><th>身份</th><th>能做什么</th></tr></thead><tbody>${Object.values(META.roles).map(r => `<tr><td class="nw">${esc(r.label)}</td><td>${esc(r.desc)}</td></tr>`).join('')}</tbody></table></div></div>
    <div class="card"><h3>大模型（可选）</h3><p class="note">不接模型也能完整演示：Agent 用程序结果回答。接了模型后，回答由模型组织语言，程序核对数字和“已下单/已发送”之类的说法；在线问过的问题会缓存，断网时回放。选外部模型时，问题和程序结果（样例数据）会发给服务商。</p>
      <div class="grid g2"><label>服务商<br><select id="pv">${cfg.providers.map(p => `<option value="${p.key}" ${p.key === cfg.key ? 'selected' : ''}>${esc(p.label)}</option>`).join('')}</select></label>
      <label>模型名（以服务商控制台为准）<br><input id="pm" value="${esc(cfg.model)}"></label>
      <label>接口地址<br><input id="pu" value="${esc(cfg.base_url)}"></label>
      <label>API Key ${cfg.has_key ? '<span class="pill ok">已保存</span>' : ''}<br><input id="pk" type="password" placeholder="${cfg.has_key ? '不改就留空' : '粘贴 Key'}"></label></div>
      <div class="row" style="margin-top:10px"><button id="ps">保存</button><button class="ghost" id="pt">测试连接</button><span class="note" id="pr"></span></div>
      <p class="note">Key 只保存在本机 config.json。只有“差旅助理”身份能改设置。</p></div>
    <div class="card"><div class="row"><div><h3>重置演示状态</h3><div class="note">清空两趟出差的方案、行程包、早报、航班变动、报销结果、所有决定和待办状态；模型设置和问答缓存保留。彩排后、上课前点一次。只有“差旅助理”能重置。</div></div><span class="sp"></span><button id="rs">重置</button></div></div>`;
  $('#pv').onchange = e => { const p = cfg.providers.find(x => x.key === e.target.value); $('#pm').value = p.model; $('#pu').value = p.base_url; };
  $('#ps').onclick = async () => { const r = await act(() => api('settings', { key: $('#pv').value, model: $('#pm').value, base_url: $('#pu').value, api_key: $('#pk').value }), '已保存'); if (r) { updateModel(r); settings(); } };
  $('#pt').onclick = async () => { $('#pr').textContent = '测试中…'; const r = await act(() => api('settings/test', {})); if (r) $('#pr').textContent = r.text; };
  $('#rs').onclick = async () => { const ok = await confirmBox('<h3>重置演示状态？</h3><p>两趟出差回到“需求”这一步。</p>', '重置'); if (!ok) return; const r = await act(() => api('reset', {}), '已重置'); if (r) { location.hash = '#/home'; route(); } };
}

/* ---------- Agent ---------- */
const CHIPS = {
  sh: ['为什么不推荐最便宜的？', '两种口径差多少？', '林总想单住要多花多少？', '评审会怎么办？', '有哪些超标？', '帮我把机票订了', '早报几点发？', '航班延误了怎么办？', '报销还差什么？'],
  cd: ['为什么不推荐最便宜的？', '两种口径差多少？', '出差申请什么时候交？', '预算会能参加吗？', '有哪些超标？', '帮我订票'],
};
function renderChips() { $('#agChips').innerHTML = (CHIPS[TRIP] || []).map(q => `<button>${esc(q)}</button>`).join(''); $('#agChips').querySelectorAll('button').forEach(b => b.onclick = () => ask(b.textContent)); }
function addMsg(html, me) { const d = document.createElement('div'); d.className = 'msg' + (me ? ' me' : ''); d.innerHTML = html; $('#agList').appendChild(d); $('#agList').scrollTop = 1e9; return d; }
async function ask(q) {
  if (!q.trim()) return;
  addMsg(`<div class="b">${esc(q)}</div>`, true);
  const w = addMsg('<div class="b">正在查程序结果…</div>');
  try {
    const r = await api('agent', { trip: TRIP, question: q });
    w.innerHTML = `<div class="b">${esc(r.text)}</div><div class="m">${esc(r.mode)}${r.sources && r.sources.length ? ' · 依据：' + esc(r.sources.join('、')) : ''}</div>${(r.notes || []).map(n => `<div class="n">程序核对：${esc(n)}</div>`).join('')}`;
  } catch (e) { w.innerHTML = `<div class="b">${esc(e.message)}</div>`; }
}
$('#agentBtn').onclick = () => $('#agent').classList.toggle('hidden');
$('#agClose').onclick = () => $('#agent').classList.add('hidden');
$('#agForm').onsubmit = e => { e.preventDefault(); const v = $('#agInput').value; $('#agInput').value = ''; ask(v); };

boot();
