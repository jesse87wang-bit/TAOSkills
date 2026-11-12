// AI 全貌蓝图：9 个板块，全部从配置 CFG.blueprint 渲染。
export function render(CFG) {
  const B = CFG.blueprint, $ = s => document.querySelector(s);
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const esc = s => s; // 配置由我们自己写，允许内嵌 <b> 等标记

  // ---------------- 目录与页脚 ----------------
  const NAV = [['ideal', '01 理想态'], ['map', '02 全业务地图'], ['arch', '03 架构'], ['flow', '04 流程'], ['run', '05 运行'], ['prio', '06 先后顺序'], ['road', '07 路线图'], ['ipo', '08 ' + B.s08.nav], ['first', '09 第一步']];
  $('#nav').innerHTML = `<span class="brand">${CFG.shortName} AI 全貌</span>` + NAV.map(([id, t]) => `<a href="#${id}">${t}</a>`).join('');
  $('#foot').innerHTML = B.footer;

  const C = B.cover, S1 = B.s01, S2 = B.s02, S3 = B.s03, S4 = B.s04, S5 = B.s05, S6 = B.s06, S7 = B.s07, S8 = B.s08, S9 = B.s09;
  const GATES7 = [['选场景', '业务负责人认领，写清要解决什么'], ['定口径和基线', '现在多少工时、多少错误、多少成本'], ['离线评测', '用历史数据跑，达到准确率门槛'], ['影子运行', 'AI 跟着真实业务跑，不影响决策'], ['受控试用', '小范围用，人工复核每一条'], ['正式上线', '负责人签字，有回退办法'], ['月度复盘', '对比基线，决定扩大还是调整']];
  const money = CFG.page.money.rows, mcol = ['var(--cyan)', 'var(--violet)', '#5b6677', '#d95926'];

  $('#main').innerHTML = `
<header class="cover">
  <p class="eyebrow">${C.eyebrow}</p>
  <h1>${C.h1}<span>${C.h1b}</span></h1>
  <p class="lead">${C.lead}</p>
  ${C.link3d ? `<p style="margin:18px 0 0"><a class="go3d" href="${C.link3d}">${C.link3dText}</a></p>` : ''}
  <div class="oneline">${C.ideals.map(([n, b, s]) => `<div class="ol"><div class="n">${n}</div><b>${b}</b><span>${s}</span></div>`).join('')}</div>
</header>

<section id="ideal">
  <p class="eyebrow">01 · 理想态全貌</p>
  <h2>${S1.h2}</h2>
  <p class="lead">${S1.lead}</p>
  <div class="screen" role="img" aria-label="AI 运营中枢大屏示意">
    <div class="scr-head">
      <div class="scr-title">${S1.screenTitle}</div>
      <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="sim">概念示意 · 数据为模拟</span><span class="clock" id="clock">14:00:00</span></div>
    </div>
    <div class="scr-body">
      <div class="col">
        <div class="pane">
          <h4>${S1.kpiTitle} <span class="tag cy">实时</span></h4>
          <div class="kpis">${S1.kpis.map((k, i) => `<div class="kpi"><b id="kb${i}" style="color:${k.color}">${k.value}</b><span>${k.label}</span></div>`).join('')}</div>
        </div>
        <div class="pane bars">
          <h4>${S1.barsTitle}</h4>
          ${S1.bars.map(([n, v], i) => `<div class="row"><span>${n}</span><div class="track"><div class="fill" data-i="${i}" style="width:50%${i === S1.barsBest ? ';background:var(--ok)' : ''}"></div></div><span class="v" id="bv${i}">${v}</span></div>`).join('')}
          <p class="small" style="margin:8px 0 0">${S1.barsNote}</p>
        </div>
        <div class="pane">
          <h4>经营一句话问</h4>
          <p class="small" style="margin:0;color:var(--ink)">${S1.askQ}</p>
          <p class="small" style="margin:6px 0 0">→ ${S1.askA}</p>
        </div>
      </div>
      <div class="col">
        <div class="pane canvas-box" style="padding:6px">
          <canvas id="net" aria-hidden="true"></canvas>
          <div class="legend"><span><i style="background:var(--cyan)"></i>数据汇入中枢</span><span><i style="background:var(--amber)"></i>AI建议下发</span><span><i style="background:var(--warn)"></i>异常，推给人</span><span><i style="background:var(--ok)"></i>已处理</span></div>
        </div>
        <div class="pane">
          <h4>数字员工在岗 <span class="tag new">今日完成任务数</span></h4>
          <div class="agents">${S1.agents.map(([n, v, core], i) => `<div class="agent${core ? ' core' : ''}">${n} <b id="ag${i}">${v}</b></div>`).join('')}</div>
        </div>
      </div>
      <div class="col">
        <div class="pane"><h4>AI 已处理 <span class="tag ok">自动记录</span></h4><ul class="feed" id="feed"></ul></div>
        <div class="pane"><h4>待人确认 <span class="tag warn">推给人</span></h4><ul class="feed" id="todo" style="max-height:210px"></ul></div>
      </div>
    </div>
  </div>
  <div class="callouts">${S1.callouts.map(([b, s]) => `<div class="callout"><b>${b}</b><span>${s}</span></div>`).join('')}</div>
</section>

<section id="map">
  <p class="eyebrow">02 · 全公司、全业务 AI 地图</p>
  <h2>${S2.h2}</h2>
  <p class="lead">${S2.lead}</p>
  <div class="bizrow">
    <div class="card"><h3>${S2.moneyTitle}</h3>
      <div class="mixbar">${money.map((r, i) => `<i style="width:${r[1]}%;background:${mcol[i] || '#5b6677'}"></i>`).join('')}</div>
      <p class="small" style="margin:8px 0 0">${S2.moneyText}</p></div>
    <div class="card"><h3>${S2.modesTitle}</h3>
      <div class="modes3">${S2.modes.map(([a, b], i) => `<span${i === S2.modes.length - 1 ? ' class="to"' : ''}>${a}<small>${b}</small></span>`).join('')}</div></div>
  </div>
  <div class="chain" id="chain" style="grid-template-columns:repeat(${S2.biz.length},minmax(112px,1fr))"></div>
  <div class="support" id="support"><span class="lab">支撑部门：</span></div>
  <div class="detail" aria-live="polite">
    <div class="card"><h3>现在的难处</h3><p id="d-pain"></p></div>
    <div class="card"><h3>AI 怎么帮</h3><p id="d-how"></p></div>
    <div class="card"><h3>上哪些智能体 · 第几步</h3><div id="d-agent"></div></div>
  </div>
  <div class="keyrow">${S2.keyrow.map(([c, t]) => `<span class="chip ${c}">${t}</span>`).join('')}</div>
  <div class="matrix-wrap"><table class="matrix" id="matrix"><thead><tr><th>业务环节</th><th>现在的难处</th><th>AI 怎么帮</th><th>智能体 / 模型</th></tr></thead><tbody></tbody></table></div>
  <p class="small" style="margin-top:10px">${S2.note}</p>
</section>

<section id="arch">
  <p class="eyebrow">03 · 总体架构</p>
  <h2>${S3.h2}</h2>
  <p class="lead">${S3.lead}</p>
  <div class="arch">
    <div class="layers">${S3.layers.map(L => `<div class="layer ${L.cls}"><div class="lname"><b>${L.name}</b><span>${L.sub}</span></div>
        <div class="mods">${L.mods.map(([c, t, sm]) => `<span class="mod ${c}">${t}${sm ? `<small>${sm}</small>` : ''}</span>`).join('')}</div></div>`).join('')}</div>
    <aside class="gov" aria-label="治理"><h3>治理贯穿每一层</h3>${S3.gov.map(([a, b]) => `<div>${a}<small>${b}</small></div>`).join('')}</aside>
  </div>
  <div class="loopnote"><b>↻ 回流</b><span>${S3.loop}</span></div>
</section>

<section id="flow">
  <p class="eyebrow">04 · 流程图</p>
  <h2>${S4.h2}</h2>
  <p class="lead">${S4.lead}</p>
  <div class="flow">${S4.steps.map(([t, k, v, ev, hum], i) => `<div class="step${hum ? ' human' : ''}"><span class="no">${String(i + 1).padStart(2, '0')}</span><h3>${t}</h3><span class="k">${k}</span><span class="v ${hum ? 'hu' : 'ai'}">${v}</span><span class="k">留下</span><span class="v ev">${ev}</span></div>`).join('')}</div>
  <h3 style="margin-top:34px">每个场景上线，都走同一条路</h3>
  <p class="small" style="margin:6px 0 0">不管是哪个场景，都按这七关推进。哪一关不过，就停在那一关，不硬上。</p>
  <div style="overflow-x:auto"><div class="gatesrow">${GATES7.map(([b, s], i) => `<div class="gs"><span class="gt">关 ${i + 1}</span><b>${b}</b><small>${s}</small></div>`).join('')}</div></div>
</section>

<section id="run">
  <p class="eyebrow">05 · 运行图</p>
  <h2>${S5.h2}</h2>
  <p class="lead">${S5.lead}</p>
  <div class="runbar"><button id="play" type="button">▶ 播放</button><button id="reset" class="ghost" type="button">重置</button><span class="sim">情景示意 · 数字为模拟</span></div>
  <div class="runcap" id="runcap" aria-live="polite"></div>
  <div class="lanes-wrap"><div class="lanes" id="lanes">${S5.heads.map(t => `<div class="h">${t}</div>`).join('')}</div></div>
</section>

<section id="prio">
  <p class="eyebrow">06 · 先做什么</p>
  <h2>按“价值 × 好不好落地”排出先后</h2>
  <p class="lead">${S6.lead}</p>
  <div class="prio">
    <div class="card quad">
      <svg viewBox="0 0 560 440" role="img" aria-label="场景价值与落地难度矩阵">
        <defs><marker id="ah" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#8A9BB0"/></marker></defs>
        <rect x="290" y="20" width="250" height="190" rx="10" fill="rgba(242,184,75,.06)" stroke="rgba(242,184,75,.35)"/>
        <text x="530" y="40" fill="#F2B84B" font-size="12" text-anchor="end">先做：价值高、好落地</text>
        <text x="60" y="200" fill="#8A9BB0" font-size="12">价值高、难：稳着做</text>
        <text x="530" y="395" fill="#8A9BB0" font-size="12" text-anchor="end">好落地：顺手做</text>
        <line x1="50" y1="410" x2="545" y2="410" stroke="#8A9BB0" marker-end="url(#ah)"/>
        <line x1="50" y1="410" x2="50" y2="15" stroke="#8A9BB0" marker-end="url(#ah)"/>
        <text x="300" y="432" fill="#8A9BB0" font-size="12" text-anchor="middle">落地容易程度 →</text>
        <text x="20" y="215" fill="#8A9BB0" font-size="12" text-anchor="middle" transform="rotate(-90 20 215)">业务价值 →</text>
        <line x1="290" y1="20" x2="290" y2="405" stroke="#1C2B40" stroke-dasharray="4 4"/>
        <line x1="55" y1="210" x2="540" y2="210" stroke="#1C2B40" stroke-dasharray="4 4"/>
        <g id="dots" font-size="12"></g>
      </svg>
    </div>
    <ol class="rank">${S6.rank.map(([b, d, c, t, f]) => `<li${f ? ' class="first"' : ''}><div><b>${b}</b><span class="d">${d}</span></div><span class="chip ${c}">${t}</span></li>`).join('')}</ol>
  </div>
</section>

<section id="road">
  <p class="eyebrow">07 · 路线图</p>
  <h2>${S7.h2}</h2>
  <p class="lead">${S7.lead}</p>
  <div class="stages">${S7.stages.map(([ph, t, g, p], i) => `<div class="stage${i === S7.stages.length - 1 ? ' s4' : ''}"><span class="ph">${ph}</span><h3>${t}</h3><div class="goal">${g}</div><div class="pass">${p}</div></div>`).join('')}</div>
  <div class="road-wrap" style="padding-top:26px"><div class="road" id="road-grid"></div></div>
  <p class="small" style="margin-top:10px">${S7.note}</p>
</section>

<section id="ipo">
  <p class="eyebrow">${S8.eyebrow}</p>
  <h2>${S8.h2}</h2>
  <p class="lead">${S8.lead}</p>
  <div style="overflow-x:auto;margin-top:20px"><table class="ipo"><thead><tr>${S8.th.map(t => `<th>${t}</th>`).join('')}</tr></thead>
    <tbody>${S8.rows.map(([a, b, c]) => `<tr><td>${a}</td><td>${b}</td><td class="ev">${c}</td></tr>`).join('')}</tbody></table></div>
  <div class="dont">${S8.dont.map(([b, t]) => `<div><b>${b}</b>${t}</div>`).join('')}</div>
</section>

<section id="first">
  <p class="eyebrow">09 · 第一步</p>
  <h2>${S9.h2}</h2>
  <div class="first-grid">
    <div class="card"><h3>四周怎么走</h3><div class="weeks">${S9.weeks.map(([a, b]) => `<div class="wk"><b>${a}</b><br>${b}</div>`).join('')}</div></div>
    <div class="card"><h3>${S9.prepTitle}</h3><ul class="clean">${S9.prep.map(x => `<li>${x}</li>`).join('')}</ul></div>
    <div class="card"><h3>${S9.deliverTitle}</h3><ul class="clean">${S9.deliver.map(x => `<li>${x}</li>`).join('')}</ul></div>
  </div>
  <div class="ask"><h3>${S9.askTitle}</h3><ol>${S9.asks.map(x => `<li>${x}</li>`).join('')}</ol></div>
</section>`;

  // ---------------- 01 大屏动效 ----------------
  let simSec = 14 * 3600;
  setInterval(() => { simSec += 7; const h = String(Math.floor(simSec / 3600) % 24).padStart(2, '0'), m = String(Math.floor(simSec / 60) % 60).padStart(2, '0'), s = String(simSec % 60).padStart(2, '0'); $('#clock').textContent = `${h}:${m}:${s}`; }, 1000);
  const cv = $('#net'), ctx = cv.getContext('2d');
  let W = 0, H = 0, dpr = 1;
  function size() { dpr = Math.min(2, devicePixelRatio || 1); const r = cv.getBoundingClientRect(); W = r.width; H = r.height; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  size(); addEventListener('resize', size);
  const nodes = S1.nodes.map(n => ({ ...n, state: 'ok' }));
  const hub = { x: .5, y: .5 };
  let pulses = [];
  function spawn() {
    pulses.push({ n: nodes[Math.floor(Math.random() * nodes.length)], dir: 1, p: 0, c: '#36C5F0' });
    if (Math.random() < .35) pulses.push({ n: nodes[Math.floor(Math.random() * nodes.length)], dir: -1, p: 0, c: '#F2B84B' });
  }
  function draw(t) {
    ctx.clearRect(0, 0, W, H);
    const hx = hub.x * W, hy = hub.y * H;
    nodes.forEach(n => { ctx.strokeStyle = 'rgba(54,197,240,.18)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.moveTo(n.x * W, n.y * H); ctx.lineTo(hx, hy); ctx.stroke(); });
    pulses.forEach(p => { p.p += 0.012; const x0 = p.n.x * W, y0 = p.n.y * H; const k = p.dir > 0 ? p.p : 1 - p.p; ctx.fillStyle = p.c; ctx.shadowColor = p.c; ctx.shadowBlur = 10; ctx.beginPath(); ctx.arc(x0 + (hx - x0) * k, y0 + (hy - y0) * k, 2.6, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0; });
    pulses = pulses.filter(p => p.p < 1);
    const r = Math.min(W, H) * .15, pr = r * (1.15 + .08 * Math.sin(t / 500));
    ctx.strokeStyle = 'rgba(242,184,75,.35)'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(hx, hy, pr, 0, Math.PI * 2); ctx.stroke();
    const g = ctx.createRadialGradient(hx, hy, 2, hx, hy, r); g.addColorStop(0, 'rgba(242,184,75,.55)'); g.addColorStop(1, 'rgba(242,184,75,.06)');
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(hx, hy, r, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#F2B84B'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(hx, hy, r, 0, Math.PI * 2); ctx.stroke();
    ctx.fillStyle = '#E6EDF5'; ctx.font = '700 ' + Math.max(12, r * .32) + 'px "Noto Sans SC",sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(CFG.brainName, hx, hy - r * .14); ctx.font = Math.max(10, r * .15) + 'px "Noto Sans SC",sans-serif'; ctx.fillStyle = '#F7D697'; ctx.fillText('数据 · 模型 · 智能体', hx, hy + r * .26);
    nodes.forEach(n => {
      const x = n.x * W, y = n.y * H, s = n.big ? 11 : 8;
      const col = n.state === 'bad' ? '#F2994A' : n.state === 'fix' ? '#3DD68C' : '#36C5F0';
      if (n.state === 'bad') { ctx.strokeStyle = 'rgba(242,153,74,.6)'; ctx.beginPath(); ctx.arc(x, y, s + 6 + 4 * Math.sin(t / 180), 0, Math.PI * 2); ctx.stroke(); }
      ctx.fillStyle = '#0C1522'; ctx.strokeStyle = col; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.rect(x - s, y - s, s * 2, s * 2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = col; for (let i = -1; i <= 1; i++) ctx.fillRect(x - s + 3, y + i * (s * .55) - 1, s * 2 - 6, 2);
      ctx.fillStyle = '#C9D5E3'; ctx.font = '12px "Noto Sans SC",sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'top'; ctx.fillText(n.name, x, y + s + 5);
    });
    requestAnimationFrame(draw);
  }
  if (!reduce) setInterval(spawn, 260);
  requestAnimationFrame(draw);

  function now() { return String(Math.floor(simSec / 3600) % 24).padStart(2, '0') + ':' + String(Math.floor(simSec / 60) % 60).padStart(2, '0'); }
  function push(list, item, cls, max) { const li = document.createElement('li'); li.className = cls; li.innerHTML = `<span class="t">${now()}</span><b>${item[0]}</b>　${item[1]}`; list.prepend(li); while (list.children.length > max) list.lastChild.remove(); }
  const feed = $('#feed'), td = $('#todo');
  S1.auto.slice(0, 5).forEach((a, i) => push(feed, a, i % 2 ? 'ai' : '', 6));
  S1.todo.slice(0, 3).forEach(a => push(td, a, 'bad', 4));
  let ai = 5, ti = 3;
  const BS = S1.barsScale; // [最小, 最大, 小数位, 抖动]
  function barW(v) { return Math.max(4, Math.min(100, (v - BS[0]) / (BS[1] - BS[0]) * 100)); }
  S1.bars.forEach(([, v], i) => { document.querySelector(`.fill[data-i="${i}"]`).style.width = barW(+v).toFixed(0) + '%'; });
  if (!reduce) {
    setInterval(() => {
      push(feed, S1.auto[ai++ % S1.auto.length], Math.random() < .5 ? 'ai' : '', 6);
      const el = $('#ag' + Math.floor(Math.random() * S1.agents.length)); el.textContent = +el.textContent + 1;
      S1.kpis.forEach((k, i) => { if (k.live === 'inc') { const e = $('#kb' + i); e.textContent = (+e.textContent.replace(/,/g, '') + Math.floor(Math.random() * 40 + 10)).toLocaleString('en-US'); } });
    }, 2600);
    setInterval(() => {
      const n = nodes[Math.floor(Math.random() * nodes.length)];
      if (n.state === 'ok') { n.state = 'bad'; push(td, S1.todo[ti++ % S1.todo.length], 'bad', 4); setTimeout(() => { n.state = 'fix'; setTimeout(() => n.state = 'ok', 2200); }, 4200); }
    }, 5200);
    setInterval(() => {
      const vals = S1.bars.map(([, v]) => +v + (Math.random() - 0.5) * BS[3]);
      vals.forEach((x, i) => { $('#bv' + i).textContent = x.toFixed(BS[2]); document.querySelector(`.fill[data-i="${i}"]`).style.width = barW(x).toFixed(0) + '%'; });
      S1.kpis.forEach((k, i) => { if (k.live === 'avg') $('#kb' + i).textContent = (vals.reduce((a, b) => a + b) / vals.length).toFixed(BS[2]); });
    }, 3000);
  }

  // ---------------- 02 业务地图 ----------------
  const chain = $('#chain'), support = $('#support');
  function show(o, btn) {
    document.querySelectorAll('.link').forEach(b => b.classList.remove('on')); btn.classList.add('on');
    $('#d-pain').textContent = o.pain; $('#d-how').textContent = o.how;
    $('#d-agent').innerHTML = o.ag.map(a => `<span class="chip ${a[1]}">${a[0]}</span>`).join('');
  }
  S2.biz.forEach((o, i) => { const b = document.createElement('button'); b.type = 'button'; b.className = 'link'; b.innerHTML = `<span class="no">${String(i + 1).padStart(2, '0')} · ${o.s}</span><b>${o.k}</b><small>${o.ag.length} 个AI抓手</small>`; b.onclick = () => show(o, b); chain.appendChild(b); });
  S2.sup.forEach(o => { const b = document.createElement('button'); b.type = 'button'; b.className = 'link'; b.innerHTML = `<b>${o.k}</b>`; b.onclick = () => show(o, b); support.appendChild(b); });
  const di = S2.defaultIdx ?? 0; show(S2.biz[di], chain.children[di]);
  const tb = $('#matrix tbody');
  [...S2.biz, ...S2.sup].forEach(o => { const tr = document.createElement('tr'); if (o.hl) tr.className = 'hl'; tr.innerHTML = `<td>${o.k}</td><td class="pain">${o.pain}</td><td>${o.how}</td><td>${o.ag.map(a => `<span class="chip ${a[1]}">${a[0]}</span>`).join('')}</td>`; tb.appendChild(tr); });

  // ---------------- 05 运行图 ----------------
  const steps = S5.steps, lanes = $('#lanes');
  steps.forEach((s, i) => { const row = [`<div class="c time" data-i="${i}">${s.t}</div>`]; for (let col = 1; col <= 5; col++) row.push(`<div class="c" data-i="${i}">${s.c[0] === col ? `<span class="${s.c[1]}">${s.c[2]}</span>` : ''}</div>`); lanes.insertAdjacentHTML('beforeend', row.join('')); });
  let timer = null;
  function runStep(i) { lanes.classList.add('playing'); lanes.querySelectorAll('.c').forEach(c => c.classList.toggle('on', +c.dataset.i <= i)); $('#runcap').textContent = `${steps[i].t}　${steps[i].cap}`; }
  $('#play').onclick = () => { clearInterval(timer); let i = 0; runStep(0); timer = setInterval(() => { i++; if (i >= steps.length) { clearInterval(timer); $('#runcap').textContent = S5.endCap; return; } runStep(i); }, reduce ? 600 : 2200); };
  $('#reset').onclick = () => { clearInterval(timer); lanes.classList.remove('playing'); lanes.querySelectorAll('.c').forEach(c => c.classList.remove('on')); $('#runcap').textContent = ''; };

  // ---------------- 06 矩阵 ----------------
  const colr = { p1: '#F2B84B', p2: '#36C5F0', p3: '#8A9BB0', m: '#A99BFF' }, gd = $('#dots');
  S6.pts.forEach(p => { const x = 55 + p[1] * 480, y = 405 - p[2] * 380, right = p[1] > .8; gd.insertAdjacentHTML('beforeend', `<circle cx="${x}" cy="${y}" r="7" fill="${colr[p[3]]}" fill-opacity=".9" stroke="#070D16" stroke-width="2"/><text x="${x + (right ? -10 : 10)}" y="${y + 4}" fill="#E6EDF5" text-anchor="${right ? 'end' : 'start'}">${p[0]}</text>`); });

  // ---------------- 07 路线图 ----------------
  const rg = $('#road-grid'), months = S7.months;
  rg.insertAdjacentHTML('beforeend', '<div class="mh"></div>' + months.map(m => `<div class="mh">${m}</div>`).join('') + `<div class="mh y">${S7.idealHead || '第2–3年 理想态'}</div>`);
  S7.rows.forEach((r, ri) => {
    const line = ri + 2;
    rg.insertAdjacentHTML('beforeend', `<div class="lane" style="grid-row:${line};grid-column:1">${r[0]}</div>`);
    r[1].forEach(b => rg.insertAdjacentHTML('beforeend', `<div class="bar ${b[2]}" style="grid-row:${line};grid-column:${b[0] + 1}/${b[1] + 2}" title="${b[3]}">${b[3]}</div>`));
    rg.insertAdjacentHTML('beforeend', `<div class="bar b4" style="grid-row:${line};grid-column:14">${r[2]}</div>`);
  });
  function gates() {
    rg.querySelectorAll('.gateline').forEach(e => e.remove());
    const heads = rg.querySelectorAll('.mh');
    S7.gates.forEach(([mi, lab]) => { const h = heads[mi]; const d = document.createElement('div'); d.className = 'gateline'; d.style.left = (h.offsetLeft + h.offsetWidth) + 'px'; d.innerHTML = `<span class="gatelab">${lab}</span>`; rg.appendChild(d); });
  }
  gates(); addEventListener('resize', gates);
  window.__bpReady = true;
}
