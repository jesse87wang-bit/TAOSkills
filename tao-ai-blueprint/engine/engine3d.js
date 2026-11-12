import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/examples/jsm/postprocessing/OutputPass.js';

export function run(CFG) {
const BRAIN = CFG.brainName, BOSS = CFG.bossName;
const $ = s => document.querySelector(s);

// ---------------- 把配置写进页面文字 ----------------
(function fillPage() {
  const P = CFG.page, set = (sel, html) => { const e = document.querySelector(sel); if (e != null && html != null) e.innerHTML = html; };
  document.title = CFG.shortName + ' AI 运转全景';
  set('#logo', `<b>${CFG.shortName}</b> / AI 运转全景`);
  set('#logo-sub', (CFG.enName ? CFG.enName.toUpperCase() + ' · ' : '') + 'AI OPERATIONS DIGITAL TWIN');
  if (CFG.org.perm) { set('#perm-2', CFG.org.perm.draft); set('#perm-note', CFG.org.perm.note); }
  set('#p-money-t', P.money.title); set('#p-money-src', P.money.src);
  set('#p-money-rows', P.money.rows.map((r, i) => `<div class="row"><span>${r[0]}</span><div class="track"><i style="width:${Math.max(1.5, r[1])}%;background:${['var(--lime)', 'var(--cyan)', '#6b7280', '#A99BFF'][i] || '#6b7280'}"></i></div><b>${r[1]}%</b></div>`).join('') + `<div class="modesrc">${P.money.note}</div>`);
  set('#p-shift-t', P.shift.title);
  set('#p-shift', `<div class="shift"><div><b>${P.shift.from[0]}</b>${P.shift.from[1]}</div><span class="arr">→</span><div class="to"><b>${P.shift.to[0]}</b>${P.shift.to[1]}</div></div><div class="modesrc">${P.shift.note}</div>`);
  set('#leg-token', CFG.campus.tokenName || '客户订单');
  set('#foot', CFG.footnote);
  const K = CFG.cockpit;
  set('#ck-title', K.title); set('#ck-sub', K.sub);
  set('#ck-kpis', K.kpis.map(k => `<div class="p${k.hot ? ' hot' : ''}"><span>${k.label}</span><b ${k.pending ? 'id="ck-k-dec"' : `data-to="${k.value}" data-dec="${k.dec || 0}"`}>${k.pending ? K.decisions.length : Number(k.value).toLocaleString('en-US', { minimumFractionDigits: k.dec || 0 })}${k.unit ? `<small>${k.unit}</small>` : ''}</b></div>`).join(''));
  const CH = K.charts;
  set('#cvt-rev', CH.trend.title); set('#cvt-pue', CH.live.title); set('#cvt-rack', CH.target.title); set('#cvt-mix', CH.mix.title);
  set('#ck-foot', K.foot);
})();
const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
const isMobile = () => innerWidth < 1000;
const V = (x, y, z) => new THREE.Vector3(x, y, z);

// ---------------- 颜色 ----------------
const C = {
  lime: 0xC6F432, cyan: 0x36C5F0, amber: 0xF2B84B, red: 0xFF6B4A, violet: 0xA99BFF,
  body: 0x59606B, roof: 0x4A515C, ground: 0x1F232A, road: 0x2A2F37, grey: 0x6B7280,
};

// ---------------- 场景 ----------------
const stage = $('#stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 1.75));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.25;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
stage.prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x101318);
scene.fog = new THREE.Fog(0x101318, 170, 320);

const camera = new THREE.PerspectiveCamera(30, 1, 1, 600);
camera.position.set(98, 108, 132);
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0, 2);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI * 0.44;
controls.minDistance = 30; controls.maxDistance = 220;

scene.add(new THREE.HemisphereLight(0xc9d4e4, 0x22252b, 1.25));
const sun = new THREE.DirectionalLight(0xfff4e6, 1.9);
sun.position.set(-50, 90, 40); sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -80, right: 80, top: 80, bottom: -80, near: 10, far: 250 });
scene.add(sun);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(512, 512), 0.75, 0.55, 0.82);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------------- 构件 ----------------
const groups = {};           // 每个区域一组，便于高亮和透视
const xrayMats = [];          // 透视时变化的材质
const edgeMats = [];
function grp(name) { const g = new THREE.Group(); g.name = name; scene.add(g); groups[name] = g; return g; }

function box(g, w, h, d, x, y, z, color = C.body, opt = {}) {
  const geo = new THREE.BoxGeometry(w, h, d);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: opt.r ?? 0.78, metalness: opt.m ?? 0.15, emissive: opt.e ?? 0x000000, emissiveIntensity: opt.ei ?? 1, transparent: true, opacity: 1 });
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y + h / 2, z);
  m.castShadow = !opt.noShadow; m.receiveShadow = true; g.add(m);
  if (!opt.noXray) xrayMats.push({ mat, base: { color: mat.color.clone(), opacity: 1, e: mat.emissive.clone() } });
  if (!opt.noEdge) {
    const em = new THREE.LineBasicMaterial({ color: C.lime, transparent: true, opacity: 0.12 });
    const l = new THREE.LineSegments(new THREE.EdgesGeometry(geo), em); l.position.copy(m.position); g.add(l); edgeMats.push(em);
  }
  return m;
}
function cyl(g, r, h, x, y, z, color = C.body, opt = {}) {
  const geo = new THREE.CylinderGeometry(opt.rt ?? r, r, h, opt.seg ?? 20);
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.6, metalness: 0.3, emissive: opt.e ?? 0, transparent: true });
  const m = new THREE.Mesh(geo, mat); m.position.set(x, y + h / 2, z); m.castShadow = true; m.receiveShadow = true;
  if (opt.rotZ) m.rotation.z = opt.rotZ;
  g.add(m); xrayMats.push({ mat, base: { color: mat.color.clone(), opacity: 1, e: mat.emissive.clone() } });
  return m;
}
const paneGeo = new THREE.PlaneGeometry(1, 1);
function windows(g, w, d, x, z, floors, y0, fh, color = 0xFFD58A, density = 0.7) {
  const on = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.62 });
  const off = new THREE.MeshBasicMaterial({ color: 0x1b2430, transparent: true, opacity: 0.9 });
  const pw = 0.9, ph = fh * 0.42;
  for (let f = 0; f < floors; f++) {
    const y = y0 + f * fh + fh * 0.5;
    const nx = Math.max(1, Math.floor(w / 1.4)), nz = Math.max(1, Math.floor(d / 1.4));
    for (let i = 0; i < nx; i++) {
      const m = new THREE.Mesh(paneGeo, Math.random() < density ? on : off);
      m.scale.set(pw, ph, 1); m.position.set(x - w / 2 + (i + 0.5) * w / nx, y, z + d / 2 + 0.03); g.add(m);
    }
    for (let i = 0; i < nz; i++) {
      const m = new THREE.Mesh(paneGeo, Math.random() < density ? on : off);
      m.scale.set(pw, ph, 1); m.rotation.y = Math.PI / 2; m.position.set(x + w / 2 + 0.03, y, z - d / 2 + (i + 0.5) * d / nz); g.add(m);
    }
  }
}
function tree(g, x, z, s = 1) {
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.12 * s, 0.15 * s, 0.9 * s, 6), new THREE.MeshStandardMaterial({ color: 0x3a2f25 }));
  trunk.position.set(x, 0.45 * s, z); g.add(trunk);
  const crown = new THREE.Mesh(new THREE.IcosahedronGeometry(0.85 * s, 0), new THREE.MeshStandardMaterial({ color: 0x2f4a33, roughness: 0.9, flatShading: true }));
  crown.position.set(x, 1.55 * s, z); crown.castShadow = true; g.add(crown);
}

function roofKit(g, w, d, x, y, z) {
  box(g, w + 0.3, 0.5, 0.3, x, y, z - d / 2, C.roof, { noEdge: true, noXray: true });
  box(g, w + 0.3, 0.5, 0.3, x, y, z + d / 2, C.roof, { noEdge: true, noXray: true });
  box(g, 0.3, 0.5, d, x - w / 2, y, z, C.roof, { noEdge: true, noXray: true });
  box(g, 0.3, 0.5, d, x + w / 2, y, z, C.roof, { noEdge: true, noXray: true });
  const n = Math.max(1, Math.floor(w / 4));
  for (let i = 0; i < n; i++) box(g, 1.3, 0.8, 1.1, x - w / 2 + 1.5 + i * (w - 3) / Math.max(1, n - 1 || 1), y, z - d / 4, 0x50565f, { noEdge: true, noXray: true });
}
// 地面与道路
const base = grp('base');
const ground = new THREE.Mesh(new THREE.PlaneGeometry(1200, 1200), new THREE.MeshStandardMaterial({ color: C.ground, roughness: 1 }));
ground.rotation.x = -Math.PI / 2; ground.receiveShadow = true; base.add(ground);
const grid = new THREE.GridHelper(200, 100, 0x2A303A, 0x232830); grid.position.y = 0.01; base.add(grid);
function road(x1, z1, x2, z2, w = 3.2) {
  const len = Math.hypot(x2 - x1, z2 - z1);
  const r = new THREE.Mesh(new THREE.BoxGeometry(len, 0.06, w), new THREE.MeshStandardMaterial({ color: C.road, roughness: 0.95 }));
  r.position.set((x1 + x2) / 2, 0.03, (z1 + z2) / 2); r.rotation.y = -Math.atan2(z2 - z1, x2 - x1); r.receiveShadow = true; base.add(r);
  const line = new THREE.Mesh(new THREE.BoxGeometry(len, 0.07, 0.12), new THREE.MeshBasicMaterial({ color: C.lime, transparent: true, opacity: 0.45 }));
  line.position.copy(r.position); line.position.y = 0.05; line.rotation.y = r.rotation.y; base.add(line);
}
CFG.campus.roads.forEach(r => road(...r));
for (let i = 0; i < 70; i++) {
  const x = (Math.random() - 0.5) * 140, z = (Math.random() - 0.5) * 110;
  if (Math.abs(x) < 50 && Math.abs(z) < 42) { if (Math.random() < 0.82) continue; }
  if (CFG.campus.roads.some(([x1, z1, x2, z2]) => (z1 === z2 && Math.abs(z - z1) < 3 && x >= Math.min(x1, x2) - 2 && x <= Math.max(x1, x2) + 2) || (x1 === x2 && Math.abs(x - x1) < 3 && z >= Math.min(z1, z2) - 2 && z <= Math.max(z1, z2) + 2))) continue;
  if ((CFG.campus.items || []).some(o => Math.abs(x - o.x) < (o.w || 8) / 2 + 2 && Math.abs(z - o.z) < (o.d || 8) / 2 + 2)) continue;
  tree(base, x, z, 0.8 + Math.random() * 0.6);
}

// 路上的车
const cars = [];
const lanes = CFG.campus.roads;
for (let i = 0; i < 16; i++) {
  const L = lanes[i % lanes.length];
  const car = new THREE.Group();
  const bd = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.6, 0.9), new THREE.MeshStandardMaterial({ color: [0xd9dde3, 0x2b3038, 0x8a96a6, 0xc6f432][i % 4], roughness: 0.4, metalness: 0.5 }));
  bd.position.y = 0.4; bd.castShadow = true; car.add(bd);
  const cab = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.45, 0.8), new THREE.MeshStandardMaterial({ color: 0x1a2230 })); cab.position.set(-0.1, 0.9, 0); car.add(cab);
  const hl = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.15, 0.7), new THREE.MeshBasicMaterial({ color: 0xfff1c4 })); hl.position.set(0.92, 0.45, 0); car.add(hl);
  base.add(car); cars.push({ car, L, t: Math.random(), sp: 0.03 + Math.random() * 0.03, dir: i % 2 ? 1 : -1, off: i % 2 ? 0.8 : -0.8 });
}
// ---------- AI 中枢 ----------
const hub = grp('hub');
box(hub, 18, 0.5, 18, 0, 0, 2, 0x2c3139, { noEdge: false });
const glass = cyl(hub, 4.2, 13, 0, 0.8, 2, 0x36C5F0, { seg: 40 });
glass.material.opacity = 0.16; glass.material.userData.op = 0.16; glass.material.metalness = 0.6; glass.material.roughness = 0.1;
const core = new THREE.Mesh(new THREE.IcosahedronGeometry(2.1, 1), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 1.3, flatShading: true }));
core.position.set(0, 8, 2); hub.add(core);
const rings = [];
for (let i = 0; i < 3; i++) {
  const t = new THREE.Mesh(new THREE.TorusGeometry(5.6 + i * 1.2, 0.07, 8, 96), new THREE.MeshBasicMaterial({ color: i === 1 ? C.amber : C.lime, transparent: true, opacity: 0.8 }));
  t.position.set(0, 4 + i * 3.2, 2); t.rotation.x = Math.PI / 2; hub.add(t); rings.push(t);
}
const beam = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 1.2, 40, 24, 1, true), new THREE.MeshBasicMaterial({ color: C.amber, transparent: true, opacity: 0.045, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false }));
beam.position.set(0, 20, 2); beam.visible = false;

// ---------- 园区积木：每家公司按真实业务摆放 ----------
const KIT = {
  // 大厅/机房/厂房：屋顶一排风机（数据中心机房、冷库、厂房都能用）
  hall(g, o) {
    const w = o.w ?? 24, h = o.h ?? 7, d = o.d ?? 7, fl = o.floors ?? 2;
    box(g, w, h, d, o.x, 0, o.z, o.color ?? C.body);
    windows(g, w, d, o.x, o.z, fl, 0, h / fl, o.win ?? 0x9BE7FF, o.density ?? 0.55);
    const n = o.fans ?? Math.floor(w / 4);
    for (let i = 0; i < n; i++) {
      const fx = o.x - w / 2 + 2 + i * (w - 4) / Math.max(1, n - 1);
      box(g, 2.6, 1.4, 2.6, fx, h, o.z, 0x3B424D, { noEdge: true });
      const fan = cyl(g, 0.95, 0.25, fx, h + 1.4, o.z, 0x1a1d22); fan.userData.fan = true;
    }
  },
  // 办公楼/普通楼宇：女儿墙、屋顶设备、窗格
  office(g, o) {
    const w = o.w ?? 10, h = o.h ?? 8, d = o.d ?? 8, fl = o.floors ?? Math.max(1, Math.floor(h / 3));
    box(g, w, h, d, o.x, 0, o.z, o.color ?? 0x6A6F78); roofKit(g, w, d, o.x, h, o.z);
    windows(g, w, d, o.x, o.z, fl, 0, o.fh ?? h / fl, o.win ?? 0xFFD58A, o.density ?? 0.6);
    for (let i = 0; i < (o.units ?? 0); i++) box(g, 1.6, 1.2, 1.6, o.x - w / 2 + 2 + i * 3, h, o.z, 0x4a505a, { noEdge: true });
  },
  // 卧式冷机一排（制冷站、空压站）
  chillers(g, o) {
    const n = o.n ?? 4;
    for (let i = 0; i < n; i++) cyl(g, 0.9, 4.6, o.x + i * 2.5, 1.0, o.z, o.color ?? 0x4C7FA6, { rotZ: Math.PI / 2 });
    box(g, n * 2.5 + 1, 0.5, 4, o.x + (n - 1) * 1.25, 0, o.z, 0x2a2f36, { noEdge: true });
  },
  // 变压器/配电
  substation(g, o) { for (let i = 0; i < (o.n ?? 3); i++) box(g, 2.2, 2.6, 2.2, o.x - i * 3.2, 0, o.z, 0x5a5f68); },
  // 光伏阵列
  solar(g, o) {
    for (let r = 0; r < (o.rows ?? 4); r++) for (let c = 0; c < (o.cols ?? 6); c++) {
      const p = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.12, 1.8), new THREE.MeshStandardMaterial({ color: 0x1D2E4A, metalness: 0.6, roughness: 0.3, emissive: 0x0a1630 }));
      p.position.set(o.x + c * 3.9, 1, o.z + r * 2.8); p.rotation.x = -0.35; p.castShadow = true; g.add(p);
    }
  },
  // 通信塔
  mast(g, o) {
    cyl(g, 0.35, o.h ?? 16, o.x, 0, o.z, 0x8a929e, { rt: 0.15, seg: 8 });
    for (let i = 0; i < 3; i++) { const d = new THREE.Mesh(new THREE.TorusGeometry(0.9, 0.08, 6, 24), new THREE.MeshBasicMaterial({ color: C.cyan })); d.position.set(o.x, (o.h ?? 16) * 0.56 + i * 2.4, o.z); g.add(d); }
  },
  // 算力舱/集装箱/设备舱
  pods(g, o) {
    for (let i = 0; i < (o.n ?? 3); i++) {
      box(g, 3.2, 3, o.d ?? 7, o.x + i * 4, 0, o.z, 0x40454f);
      const s = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.4, (o.d ?? 7) - 0.6), new THREE.MeshBasicMaterial({ color: o.glow ?? C.violet }));
      s.position.set(o.x + 1.65 + i * 4, 2.2, o.z); g.add(s);
    }
  },
  // 仓库/物流中心：锯齿屋顶 + 装卸口
  warehouse(g, o) {
    const w = o.w ?? 22, h = o.h ?? 6, d = o.d ?? 12, n = Math.max(2, Math.floor(w / 5));
    box(g, w, h, d, o.x, 0, o.z, o.color ?? 0x5d646f);
    for (let i = 0; i < n; i++) {
      const sh = new THREE.Shape(); sh.moveTo(0, 0); sh.lineTo(w / n, 0); sh.lineTo(w / n, 1.8); sh.lineTo(0, 0);
      const geo = new THREE.ExtrudeGeometry(sh, { depth: d, bevelEnabled: false });
      const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x4a515c, roughness: 0.7, transparent: true }));
      m.position.set(o.x - w / 2 + i * w / n, h, o.z - d / 2); m.castShadow = true; g.add(m);
      xrayMats.push({ mat: m.material, base: { color: m.material.color.clone(), opacity: 1, e: m.material.emissive.clone() } });
    }
    for (let i = 0; i < (o.docks ?? 5); i++) box(g, 2, 2.6, 0.2, o.x - w / 2 + 2.5 + i * 3.4, 0, o.z + d / 2 + 0.05, 0x2a2f36, { noEdge: true, noXray: true });
    windows(g, w, d, o.x, o.z, 1, 0, h, o.win ?? 0x9BE7FF, 0.35);
  },
  // 筒仓/储罐（粮库、化工、能源）
  silo(g, o) {
    for (let i = 0; i < (o.n ?? 4); i++) {
      const x = o.x + i * ((o.r ?? 2.2) * 2 + 0.8);
      cyl(g, o.r ?? 2.2, o.h ?? 10, x, 0, o.z, o.color ?? 0x9aa3ad, { seg: 28 });
      const cap = new THREE.Mesh(new THREE.ConeGeometry((o.r ?? 2.2) * 1.02, 1.6, 28), new THREE.MeshStandardMaterial({ color: 0x7c858f, metalness: 0.4, roughness: 0.4 }));
      cap.position.set(x, (o.h ?? 10) + 0.8, o.z); cap.castShadow = true; g.add(cap);
    }
  },
  // 门店：一排小店铺，带彩色雨棚和灯箱
  store(g, o) {
    for (let i = 0; i < (o.n ?? 3); i++) {
      const x = o.x + i * ((o.w ?? 5) + 1.5);
      box(g, o.w ?? 5, o.h ?? 3.4, o.d ?? 4.5, x, 0, o.z, 0x6a707a);
      const aw = new THREE.Mesh(new THREE.BoxGeometry((o.w ?? 5) + 0.4, 0.3, 1.4), new THREE.MeshStandardMaterial({ color: o.color ?? 0xE4572E, emissive: o.color ?? 0xE4572E, emissiveIntensity: 0.25 }));
      aw.position.set(x, (o.h ?? 3.4) * 0.72, o.z + (o.d ?? 4.5) / 2 + 0.6); aw.rotation.x = 0.25; g.add(aw);
      const sign = new THREE.Mesh(new THREE.BoxGeometry((o.w ?? 5) * 0.8, 0.6, 0.12), new THREE.MeshBasicMaterial({ color: 0xFFE6A8 }));
      sign.position.set(x, (o.h ?? 3.4) - 0.5, o.z + (o.d ?? 4.5) / 2 + 0.08); g.add(sign);
      const glass = new THREE.Mesh(new THREE.PlaneGeometry((o.w ?? 5) * 0.8, 1.6), new THREE.MeshBasicMaterial({ color: 0xFFD58A, transparent: true, opacity: 0.6 }));
      glass.position.set(x, 1.1, o.z + (o.d ?? 4.5) / 2 + 0.04); g.add(glass);
    }
  },
  // 工厂：锯齿屋顶车间 + 烟囱
  factory(g, o) {
    KIT.warehouse(g, { ...o, docks: 0, color: o.color ?? 0x666d77 });
    cyl(g, 0.9, (o.h ?? 6) + 9, o.x + (o.w ?? 22) / 2 - 2, 0, o.z - (o.d ?? 12) / 2 + 2, 0x8b939c, { rt: 0.7 });
  },
  // 平台/广场底座
  pad(g, o) { box(g, o.w ?? 10, 0.4, o.d ?? 10, o.x, 0, o.z, o.color ?? 0x2c3139, { noEdge: true }); },
};
(CFG.campus.items || []).forEach(o => { const g = groups[o.g] || grp(o.g); (KIT[o.type] || KIT.office)(g, o); });

// ---------- 部门 ----------
const DEPTS = CFG.campus.depts.map(d => ({ ...d }));
const agents = [];
DEPTS.forEach(d => {
  const g = grp('d-' + d.k); d.g = g; d.z = d.z ?? 24;
  box(g, 7, 3.6, 6, d.x, 0, d.z, 0x555C67);
  box(g, 7.4, 0.4, 6.4, d.x, 3.6, d.z, 0x3B424D, { noEdge: true });
  windows(g, 7, 6, d.x, d.z, 1, 0, 3.6, 0xFFD58A, 0.85);
  const a = new THREE.Mesh(new THREE.OctahedronGeometry(0.9), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 2.4, flatShading: true }));
  a.position.set(d.x, 6.4, d.z); g.add(a); agents.push(a); d.agentMesh = a;
  const ring = new THREE.Mesh(new THREE.RingGeometry(1.2, 1.35, 40), new THREE.MeshBasicMaterial({ color: C.amber, transparent: true, opacity: 0.6, side: THREE.DoubleSide }));
  ring.rotation.x = -Math.PI / 2; ring.position.set(d.x, 4.1, d.z); g.add(ring); d.ring = ring;
});

// ================= AI 原生组织（第二个视图，建在园区东侧远处） =================
const OX = 300;
const org = grp('org');
const orgNodes = {};
const orgAgentObjs = [];   // “今天”模式下隐藏
const orgSpin = [];
const orgTagDefs = [];
const orgAiLines = [];     // 经过 Agent 的连线
const orgOldLines = [];    // 今天：层层传话的连线
const LY = { boss: 44, brain: 33, dept: 22, agent: 11, sys: 0 };
const ODEPT = CFG.org.depts.map(d => ({ ...d }));
function platform(w, d, y, color, label) {
  const geo = new THREE.BoxGeometry(w, 0.35, d);
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color, transparent: true, opacity: 0.42, roughness: 0.35, metalness: 0.25, emissive: color, emissiveIntensity: 0.25, depthWrite: false }));
  m.position.set(OX, y - 0.2, 0); m.receiveShadow = true; org.add(m);
  const e = new THREE.LineSegments(new THREE.EdgesGeometry(geo), new THREE.LineBasicMaterial({ color: C.lime, transparent: true, opacity: 0.6 }));
  e.position.copy(m.position); org.add(e);
  orgTagDefs.push({ p: V(OX - w / 2, y + 0.4, d / 2), n: label[0], s: label[1], g: 'L-' + label[2], layer: 1 });
}
platform(30, 16, LY.boss, 0x2b4560, ['① 老板 · 管理层', '定目标 · 拍板 · 看结果', 'boss']);
platform(52, 22, LY.brain, 0x5a4214, ['② ' + BRAIN, '总控Agent + 共享能力', 'brain']);
platform(80, 14, LY.dept, 0x1f4258, ['③ 部门', '负责人 + 部门助理Agent', 'dept']);
platform(80, 14, LY.agent, 0x4a4a12, ['④ 业务Agent', '每个岗位的数字员工', 'agent']);
platform(80, 14, LY.sys, 0x2a2f37, ['⑤ 系统与设施', '只读接入 · 受控执行', 'sys']);

const humanMat = new THREE.MeshStandardMaterial({ color: 0xA9E4F7, emissive: 0x1d5d74, emissiveIntensity: 0.7, roughness: 0.45 });
function human(x, y, z, s = 1) {
  const g = new THREE.Group();
  const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.42 * s, 0.85 * s, 4, 12), humanMat); b.position.y = 0.9 * s; b.castShadow = true; g.add(b);
  const h = new THREE.Mesh(new THREE.SphereGeometry(0.36 * s, 16, 16), humanMat); h.position.y = 1.95 * s; g.add(h);
  g.position.set(x, y, z); org.add(g); return g;
}
function agentNode(x, y, z, r = 0.75, inten = 1.6) {
  const m = new THREE.Mesh(new THREE.OctahedronGeometry(r), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: inten, flatShading: true }));
  m.position.set(x, y, z); org.add(m); orgAgentObjs.push(m); orgSpin.push({ m, y }); return m;
}
function link(a, b, color = C.lime, op = 0.35, list = orgAiLines) {
  const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: op });
  const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]), mat); org.add(l); list.push({ l, mat, op }); return l;
}

// ① 老板层
human(OX - 4, LY.boss, 0, 1.35); orgNodes.boss = V(OX - 4, LY.boss + 3, 0);
human(OX - 9, LY.boss, -3, 0.95); human(OX - 9, LY.boss, 3, 0.95);
const scr = new THREE.Mesh(new THREE.BoxGeometry(7, 3.8, 0.25), new THREE.MeshStandardMaterial({ color: 0x0b1a26, emissive: C.cyan, emissiveIntensity: 0.55 }));
scr.position.set(OX + 6, LY.boss + 2.6, -2); scr.rotation.y = -0.35; org.add(scr);
for (let i = 0; i < 5; i++) { const bar = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.6 + i * 0.45, 0.05), new THREE.MeshBasicMaterial({ color: i === 4 ? C.lime : C.cyan })); bar.position.set(-2.4 + i * 1.1, -1.4 + (0.6 + i * 0.45) / 2, 0.15); scr.add(bar); }
orgNodes.screen = V(OX + 6, LY.boss + 2.6, -2);
orgTagDefs.push({ p: V(OX - 4, LY.boss + 4.6, 0), n: BOSS + ' · 领导小组', s: '定目标 · 拍板', g: 'boss', human: 1 });
orgTagDefs.push({ p: V(OX + 6, LY.boss + 5.2, -2), n: '经营驾驶舱', s: '问一句，答案带出处', g: 'boss' });

// ② 大脑
const ocore = new THREE.Mesh(new THREE.IcosahedronGeometry(2.4, 1), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 1.4, flatShading: true }));
ocore.position.set(OX, LY.brain + 3, 0); org.add(ocore); orgAgentObjs.push(ocore);
const oring = new THREE.Mesh(new THREE.TorusGeometry(4, 0.08, 8, 80), new THREE.MeshBasicMaterial({ color: C.lime, transparent: true, opacity: 0.8 }));
oring.position.copy(ocore.position); oring.rotation.x = Math.PI / 2; org.add(oring); orgAgentObjs.push(oring);
orgNodes.brain = ocore.position.clone();
orgTagDefs.push({ p: V(OX, LY.brain + 6.8, 0), n: '总控Agent', s: '拆目标 · 派任务 · 汇总 · 管权限', g: 'brain', hub: 1 });
const MODS = [
  ['mData', '数据底座', '统一口径', -17, -5, 0x36C5F0], ['mKb', '知识库', CFG.org.kbSub || '规程 · 案例 · 手册', -17, 5, 0x36C5F0],
  ['mModel', '专用模型', CFG.org.modelSub || '预测 · 寻优', 17, -5, 0xA99BFF], ['mRule', '规则 · 红线 · 审计', '权限与回退', 17, 5, 0x3DD68C],
];
MODS.forEach(([k, n, s, dx, dz, col]) => {
  const geo = new THREE.BoxGeometry(6.5, 1.8, 3.2);
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: 0x1a2028, emissive: col, emissiveIntensity: 0.35 }));
  m.position.set(OX + dx, LY.brain + 0.9, dz); org.add(m); orgAgentObjs.push(m);
  orgNodes[k] = V(OX + dx, LY.brain + 2, dz);
  link(orgNodes[k], orgNodes.brain, col, 0.5);
  orgTagDefs.push({ p: V(OX + dx, LY.brain + 3, dz), n: n, s: s, g: 'brain' });
});
link(orgNodes.boss, orgNodes.brain, C.amber, 0.6);
link(orgNodes.screen, orgNodes.brain, C.cyan, 0.45);

// ③④⑤ 部门、业务Agent、系统
ODEPT.forEach((d, i) => {
  const x = OX - 35 + i * 10; d.x = x;
  human(x - 1.6, LY.dept, 0.5);
  agentNode(x + 1.6, LY.dept + 1.5, 0.5, 0.85);
  orgNodes['h-' + d.k] = V(x - 1.6, LY.dept + 2, 0.5);
  orgNodes['a-' + d.k] = V(x + 1.6, LY.dept + 1.5, 0.5);
  link(orgNodes['h-' + d.k], orgNodes['a-' + d.k], C.cyan, 0.5);
  link(orgNodes['a-' + d.k], orgNodes.brain, C.amber, 0.22);
  link(orgNodes.boss, orgNodes['h-' + d.k], 0x8a96a6, 0.0, orgOldLines);   // 今天：老板直接找部门要
  orgTagDefs.push({ p: V(x, LY.dept + 4.4, 0.5), n: d.n, s: '负责人 + 部门助理', g: 'd-' + d.k });
  d.ag.forEach((an, j) => {
    const ax = x + (j ? 2.3 : -2.3);
    agentNode(ax, LY.agent + 1.2, 0, 0.6, 1.3);
    orgNodes[`g-${d.k}-${j}`] = V(ax, LY.agent + 1.2, 0);
    link(orgNodes[`g-${d.k}-${j}`], orgNodes['a-' + d.k], C.amber, 0.3);
    orgTagDefs.push({ p: V(ax, LY.agent + 2.6, 0), n: an, s: '', g: 'd-' + d.k, mini: 1 });
  });
  // 今天：部门里的人直接操作系统
  human(x - 0.6, LY.agent, 3.5, 0.8).userData.oldOnly = true;
  human(x + 0.9, LY.agent, 3.5, 0.8).userData.oldOnly = true;
  const sb = new THREE.Mesh(new THREE.BoxGeometry(7, 2, 4), new THREE.MeshStandardMaterial({ color: 0x3a414c, roughness: 0.7 }));
  sb.position.set(x, LY.sys + 1, -0.5); sb.castShadow = true; org.add(sb);
  const strip = new THREE.Mesh(new THREE.BoxGeometry(6, 0.18, 0.05), new THREE.MeshBasicMaterial({ color: C.cyan })); strip.position.set(x, LY.sys + 1.5, 1.53); org.add(strip);
  orgNodes['s-' + d.k] = V(x, LY.sys + 2.2, -0.5);
  d.ag.forEach((_, j) => link(orgNodes[`g-${d.k}-${j}`], orgNodes['s-' + d.k], C.cyan, 0.2));
  link(orgNodes['h-' + d.k], orgNodes['s-' + d.k], 0x8a96a6, 0.0, orgOldLines);
  orgTagDefs.push({ p: V(x, LY.sys + 3, -0.5), n: d.sys, s: '', g: 'd-' + d.k, mini: 1, sys: 1 });
});
const oldOnly = []; org.traverse(o => { if (o.userData.oldOnly) oldOnly.push(o); });

// ================= 理想态：任务驱动的 AI 原生组织（建在园区西侧远处） =================
const IX = -320;
const ideal = grp('ideal');
const iTagDefs = [];
const iFlash = [];          // 被派到任务时闪一下的执行者
const W = (x, y, z) => V(IX + x, y, z);

// 底盘
const disc = new THREE.Mesh(new THREE.CylinderGeometry(34, 34, 0.4, 72), new THREE.MeshStandardMaterial({ color: 0x182230, transparent: true, opacity: 0.85, roughness: 0.5 }));
disc.position.copy(W(0, 0.2, 0)); disc.receiveShadow = true; ideal.add(disc);
const discEdge = new THREE.Mesh(new THREE.TorusGeometry(34, 0.12, 6, 120), new THREE.MeshBasicMaterial({ color: C.lime, transparent: true, opacity: 0.6 }));
discEdge.position.copy(W(0, 0.4, 0)); discEdge.rotation.x = Math.PI / 2; ideal.add(discEdge);

// 大脑：总控调度
const icore = new THREE.Mesh(new THREE.IcosahedronGeometry(3, 1), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 1.4, flatShading: true }));
icore.position.copy(W(0, 9, 0)); ideal.add(icore);
iTagDefs.push({ p: W(0, 13.5, 0), n: BRAIN + ' · 总控调度', s: '按能力和风险派单', g: 'i-core', hub: 1 });

// 任务池环
const pool = new THREE.Mesh(new THREE.TorusGeometry(13, 0.3, 10, 120), new THREE.MeshStandardMaterial({ color: 0x0b2a38, emissive: C.cyan, emissiveIntensity: 0.6, transparent: true, opacity: 0.85 }));
pool.position.copy(W(0, 3, 0)); pool.rotation.x = Math.PI / 2; ideal.add(pool);
iTagDefs.push({ p: W(-9, 4.2, 10), n: '任务池', s: '所有工作都变成任务', g: 'i-pool', layer: 1 });
const ringPt = a => W(Math.cos(a) * 13, 3, Math.sin(a) * 13);

// 共享底座四根柱
const PILLARS = [['数据', 0x36C5F0, Math.PI * 0.25], ['知识', 0x36C5F0, Math.PI * 0.75], ['模型', 0xA99BFF, Math.PI * 1.25], ['规则 · 审计', 0x3DD68C, Math.PI * 1.75]];
const pillarTop = {};
PILLARS.forEach(([n, col, a]) => {
  const x = Math.cos(a) * 6.5, z = Math.sin(a) * 6.5;
  const m = new THREE.Mesh(new THREE.CylinderGeometry(1.1, 1.3, 5.5, 20), new THREE.MeshStandardMaterial({ color: 0x1a2028, emissive: col, emissiveIntensity: 0.55 }));
  m.position.copy(W(x, 2.75, z)); m.castShadow = true; ideal.add(m);
  pillarTop[n] = W(x, 5.8, z);
  iTagDefs.push({ p: W(x, 6.6, z), n, s: '', g: 'i-base', mini: 1, sys: 1 });
});

// 共享 Agent 能力池（绕大脑转）
const poolAgents = [];
for (let i = 0; i < 10; i++) {
  const m = new THREE.Mesh(new THREE.OctahedronGeometry(0.55), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 1.5, flatShading: true }));
  m.userData.a = i / 10 * Math.PI * 2; ideal.add(m); poolAgents.push(m); iFlash.push(m);
}
iTagDefs.push({ p: W(9.5, 8.6, 0), n: 'Agent 能力池', s: '共享，谁需要就调谁', g: 'i-core' });

// 人
const ihumanMat = new THREE.MeshStandardMaterial({ color: 0xA9E4F7, emissive: 0x1d5d74, emissiveIntensity: 0.7, roughness: 0.45 });
function ihuman(x, y, z, s = 1) {
  const g = new THREE.Group();
  const b = new THREE.Mesh(new THREE.CapsuleGeometry(0.42 * s, 0.85 * s, 4, 12), ihumanMat); b.position.y = 0.9 * s; b.castShadow = true; g.add(b);
  const h = new THREE.Mesh(new THREE.SphereGeometry(0.36 * s, 16, 16), ihumanMat); h.position.y = 1.95 * s; g.add(h);
  g.position.copy(W(x, y, z)); ideal.add(g); iFlash.push(g); return g;
}
function iagent(x, y, z, r = 0.65) {
  const m = new THREE.Mesh(new THREE.OctahedronGeometry(r), new THREE.MeshStandardMaterial({ color: 0x111111, emissive: C.amber, emissiveIntensity: 1.5, flatShading: true }));
  m.position.copy(W(x, y, z)); ideal.add(m); iFlash.push(m); m.userData.y = y; return m;
}
function iline(a, b, color, op = 0.35) {
  const l = new THREE.Line(new THREE.BufferGeometry().setFromPoints([a, b]), new THREE.LineBasicMaterial({ color, transparent: true, opacity: op })); ideal.add(l); return l;
}

// 四条价值流小队
const PODS = CFG.ideal.pods.map((p, i, A) => ({ ...p, a: p.a ?? (Math.PI * (0.75 - 0.5 * i)) }));
PODS.forEach(p => {
  const cx = Math.cos(p.a) * 23, cz = Math.sin(p.a) * 23; p.cx = cx; p.cz = cz;
  const hex = new THREE.Mesh(new THREE.CylinderGeometry(7.5, 7.5, 0.6, 6), new THREE.MeshStandardMaterial({ color: p.col, emissive: p.col, emissiveIntensity: 0.4, transparent: true, opacity: 0.9 }));
  hex.position.copy(W(cx, 0.7, cz)); hex.receiveShadow = true; ideal.add(hex);
  const he = new THREE.LineSegments(new THREE.EdgesGeometry(hex.geometry), new THREE.LineBasicMaterial({ color: C.lime, transparent: true, opacity: 0.7 }));
  he.position.copy(hex.position); ideal.add(he);
  p.humans = [ihuman(cx - 1.2, 1, cz, 1.3), ihuman(cx + 1.4, 1, cz + 1.2, 0.95)];
  p.agents = p.ag.map((n, i) => {
    const aa = i / p.ag.length * Math.PI * 2 + 0.4;
    const ax = cx + Math.cos(aa) * 4.6, az = cz + Math.sin(aa) * 4.6;
    const m = iagent(ax, 2.4, az);
    iTagDefs.push({ p: W(ax, 3.6, az), n, s: '', g: 'i-pod-' + p.k, mini: 1 });
    return m;
  });
  iline(W(cx, 1.2, cz), ringPt(p.a), C.cyan, 0.4);
  iTagDefs.push({ p: W(cx, 6.2, cz), n: p.n, s: p.s, g: 'i-pod-' + p.k, layer: 1 });
});

// 职责节点：没有部门，只有挂在人身上的职责
const DUTY = CFG.ideal.duties.map((d, i) => [d[0], d[1], i]);
const dutyNodes = [];
DUTY.forEach(([n, sub, i]) => {
  const a = i / 6 * Math.PI * 2, x = Math.cos(a) * 30, z = Math.sin(a) * 30;
  const pad = new THREE.Mesh(new THREE.CylinderGeometry(2, 2, 0.4, 6), new THREE.MeshStandardMaterial({ color: 0x14301f, emissive: 0x3DD68C, emissiveIntensity: 0.35 }));
  pad.position.copy(W(x, 0.6, z)); ideal.add(pad);
  const badge = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.1, 6, 40), new THREE.MeshBasicMaterial({ color: 0x3DD68C }));
  badge.position.copy(W(x, 4.2, z)); badge.rotation.x = Math.PI / 2; ideal.add(badge);
  const h = ihuman(x, 0.8, z, 1.1); dutyNodes.push(h);
  iline(W(x, 3, z), pillarTop['规则 · 审计'], 0x3DD68C, 0.3);
  iTagDefs.push({ p: W(x, 5.4, z), n, s: sub, g: 'i-duty', dom: 1 });
});

// 老板：目标与边界
const bossDisc = new THREE.Mesh(new THREE.CylinderGeometry(5, 5, 0.4, 40), new THREE.MeshStandardMaterial({ color: 0x2b4560, emissive: 0x2b4560, emissiveIntensity: 0.4, transparent: true, opacity: 0.9 }));
bossDisc.position.copy(W(0, 18, -24)); ideal.add(bossDisc);
const bossH = ihuman(-1.5, 18.2, -24, 1.35);
const bscr = new THREE.Mesh(new THREE.BoxGeometry(5, 3, 0.2), new THREE.MeshStandardMaterial({ color: 0x0b1a26, emissive: C.cyan, emissiveIntensity: 0.55 }));
bscr.position.copy(W(2.5, 20.3, -25)); ideal.add(bscr);
iline(W(0, 18, -24), icore.position, C.amber, 0.6);
iTagDefs.push({ p: W(0, 23.5, -24), n: BOSS + ' · 目标与边界', s: '定目标 · 给资源 · 拍大事', g: 'i-boss', human: 1 });

// 任务入口
const GATES = CFG.ideal.gates.map(g => ({ n: g.n, p: W(g.x, 0, g.z), pod: g.pod }));
GATES.forEach(g => {
  const gg = new THREE.Group(); gg.position.copy(g.p);
  const pm = new THREE.MeshStandardMaterial({ color: 0x0b2a38, emissive: C.cyan, emissiveIntensity: 0.9 });
  const p1 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 5, 0.5), pm); p1.position.set(-2, 2.5, 0); gg.add(p1);
  const p2 = p1.clone(); p2.position.x = 2; gg.add(p2);
  const bm = new THREE.Mesh(new THREE.BoxGeometry(4.5, 0.5, 0.5), pm); bm.position.y = 5; gg.add(bm);
  gg.lookAt(icore.position.x, 0, icore.position.z); ideal.add(gg);
  g.p = g.p.clone().setY(1.5);
  iTagDefs.push({ p: g.p.clone().setY(7), n: g.n, s: '自动变成任务', g: 'i-gate', gate: 1 });
});

// 现场
for (let i = 0; i < 4; i++) {
  const r = new THREE.Mesh(new THREE.BoxGeometry(1.2, 3, 2.6), new THREE.MeshStandardMaterial({ color: 0x2a2f37, emissive: 0x0b2a38 }));
  r.position.copy(W(28 + i * 1.5, 1.5, 27)); r.castShadow = true; ideal.add(r);
}
const sitePool = [ihuman(26.5, 0, 31, 1.0), ihuman(29, 0, 32, 1.0), ihuman(31.5, 0, 31, 1.0)];
const siteH = sitePool[0];
const sitePod = PODS.find(p => p.site) || PODS[1];
iline(W(29, 2, 31), W(sitePod.cx, 1.5, sitePod.cz), C.cyan, 0.5);
iTagDefs.push({ p: W(30, 5.6, 28), n: CFG.ideal.site.n, s: CFG.ideal.site.s, g: 'i-site', human: 1 });

// ---------- 任务流转 ----------
const iTasks = [];
const icount = { agent: 46, human: 9, exc: 7, learn: 5 };   // 起始值给一个合理底数，避免刚打开时显示 0%
const taskGeo = new THREE.BoxGeometry(1, 1, 1);
const TCOL = { agent: 0xF2B84B, pool: 0xF2B84B, human: 0xA9E4F7, exc: 0xFF8A4A };
function spawnTask(tk) {
  const g = GATES[Math.floor(Math.random() * GATES.length)];
  const pod = PODS[g.pod];
  const a0 = Math.atan2(g.p.z, g.p.x - IX), a1 = pod.a;
  let da = a1 - a0; while (da > Math.PI) da -= Math.PI * 2; while (da < -Math.PI) da += Math.PI * 2;
  const pts = [g.p.clone(), ringPt(a0)];
  for (let i = 1; i <= 8; i++) pts.push(ringPt(a0 + da * i / 8));
  const r = Math.random(); let kind, execs;
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  if (r < 0.58) { kind = 'agent'; execs = [pick(pod.agents)]; }
  else if (r < 0.74) { kind = 'pool'; execs = [pick(poolAgents)]; }
  else if (r < 0.88) { kind = 'human'; execs = [pod.site && Math.random() < 0.6 ? pick(sitePool) : pick(pod.humans)]; }
  else { kind = 'exc'; execs = [pick(pod.agents), dutyNodes[pod.duty ?? 0]]; }
  const flashAt = [];
  execs.forEach(e => { const wp = new THREE.Vector3(); e.getWorldPosition(wp); wp.y += 1.4; pts.push(wp); flashAt.push({ i: pts.length - 1, e }); });
  pts.push(icore.position.clone()); pts.push(pillarTop['知识'].clone());
  const path = new THREE.CurvePath();
  for (let i = 0; i < pts.length - 1; i++) path.add(new THREE.LineCurve3(pts[i], pts[i + 1]));
  const cum = path.getCurveLengths(), total = path.getLength();
  tk.path = path; tk.total = total; tk.t = 0; tk.kind = kind;
  tk.flash = flashAt.map(f => ({ at: cum[f.i - 1] / total, e: f.e, done: false }));
  tk.counted = false;
  tk.m.material.color.set(TCOL[kind]);
}
for (let i = 0; i < 16; i++) {
  const m = new THREE.Mesh(taskGeo, new THREE.MeshBasicMaterial({ color: 0xffffff }));
  ideal.add(m); const tk = { m }; spawnTask(tk); tk.t = Math.random() * 0.8; iTasks.push(tk);
}
function idealTick(dt, sp) {
  icore.rotation.y += dt * 0.5 * sp; pool.rotation.z += dt * 0.2 * sp;
  poolAgents.forEach((m, i) => { m.userData.a += dt * 0.25 * sp; m.position.copy(W(Math.cos(m.userData.a) * 9.5, 7 + Math.sin(i) * 0.6, Math.sin(m.userData.a) * 9.5)); m.rotation.y += dt * 1.5 * sp; });
  iTasks.forEach(tk => {
    tk.t += (dt * 11 * (sp || 0.4)) / tk.total;
    tk.flash.forEach(f => { if (!f.done && tk.t >= f.at) { f.done = true; f.e.userData.flash = 1; } });
    if (tk.t >= 1) {
      icount.learn++;
      icount[tk.kind === 'pool' ? 'agent' : tk.kind]++;
      spawnTask(tk); return;
    }
    tk.path.getPoint(tk.t, tmpI); tk.m.position.copy(tmpI); tk.m.rotation.x += dt * 2; tk.m.rotation.y += dt * 2;
  });
  iFlash.forEach(o => {
    const f = o.userData.flash || 0;
    if (f > 0) { o.userData.flash = Math.max(0, f - dt * 1.2); }
    const s = 1 + (o.userData.flash || 0) * 0.7; o.scale.set(s, s, s);
  });
}
const tmpI = new THREE.Vector3();

// ---------------- 数据流 ----------------
const flows = [];
function arc(a, b, h = 8) { const m = a.clone().lerp(b, 0.5); m.y += h; return new THREE.QuadraticBezierCurve3(a, m, b); }
const HUBP = V(0, 6, 2);
const nodes = {};
Object.entries(CFG.campus.nodes).forEach(([k, p]) => nodes[k] = V(...p));
DEPTS.forEach(d => nodes[d.k] = V(d.x, 4, d.z));
function addFlow(from, to, color, n = 9, h = 8) {
  const curve = arc(nodes[from] || from, nodes[to] || to, h);
  const lineMat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.28 });
  const line = new THREE.Line(new THREE.BufferGeometry().setFromPoints(curve.getPoints(48)), lineMat); scene.add(line);
  const dots = [];
  const dm = new THREE.MeshBasicMaterial({ color });
  for (let i = 0; i < n; i++) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.22, 8, 8), dm); scene.add(s); dots.push({ s, t: i / n }); }
  const f = { curve, dots, lineMat, dm, from, to, baseColor: new THREE.Color(color), speed: 0.12 + Math.random() * 0.05 };
  flows.push(f); return f;
}
// 数据进中枢（青）
Object.keys(CFG.campus.nodes).forEach(k => addFlow(k, HUBP, C.cyan, 9, 10));
// 中枢下发到部门（琥珀）
DEPTS.forEach(d => addFlow(HUBP, d.k, C.amber, 6, 6));

// 订单令牌
const tokens = [];
for (let i = 0; i < 4; i++) {
  const tk = new THREE.Mesh(new THREE.SphereGeometry(0.7, 20, 20), new THREE.MeshBasicMaterial({ color: 0xffffff }));
  if (i === 0) tk.add(new THREE.PointLight(C.lime, 30, 18));
  tk.visible = false; scene.add(tk); tokens.push({ m: tk, curve: null, t: 0 });
}

// ---------------- 标签 ----------------
const tagsEl = $('#tags');
const TAGS = [
  ...CFG.campus.tags.map(t => ({ ...t, p: V(...t.p) })),
  { p: V(0, 17, 2), n: BRAIN, s: '数据 · 模型 · 智能体', g: 'hub', hub: 1 },
  ...DEPTS.map(d => ({ p: V(d.x, 8, d.z), n: d.n, s: '数字员工：' + d.agent, g: 'd-' + d.k, dept: d.k })),
].map(t => ({ ...t, view: 'campus' })).concat(orgTagDefs.map(t => ({ ...t, view: 'org' }))).concat(iTagDefs.map(t => ({ ...t, view: 'ideal' })));
TAGS.forEach(t => {
  const el = document.createElement('div'); el.className = 'tag' + (t.big ? ' big' : '') + (t.hub ? ' hubtag' : '') + (t.dept ? ' dept' : '') + (t.layer ? ' layer' : '') + (t.mini ? ' mini' : '') + (t.sys ? ' sys' : '') + (t.human ? ' human' : '') + (t.dom ? ' dom' : '') + (t.gate ? ' gate' : '') + (t.view === 'org' && !t.layer && !t.mini && !t.human && !t.hub && t.g.startsWith('d-') ? ' odept' : '');
  el.innerHTML = `<i></i><b>${t.n}</b><span>${t.s}</span><em class="alert">待人工处理</em>`;
  tagsEl.appendChild(el); t.el = el;
});

// ---------------- 模式 ----------------
let mode = 'after';
function setMode(m) {
  mode = m;
  document.querySelectorAll('button[data-mode]').forEach(b => b.classList.toggle('on', b.dataset.mode === m));
  document.body.dataset.mode = m;
  const xray = m === 'xray', before = m === 'before';
  xrayMats.forEach(({ mat, base }) => {
    if (xray) { mat.color.set(0x0c120a); mat.opacity = 0.18; mat.emissive.set(C.lime); mat.emissiveIntensity = 0.06; mat.depthWrite = false; }
    else { mat.color.copy(base.color); mat.opacity = mat.userData.op ?? 1; mat.emissive.copy(base.e); mat.emissiveIntensity = 1; mat.depthWrite = true; }
  });
  edgeMats.forEach(e => { e.opacity = xray ? 0.9 : 0.12; });
  ground.material.color.set(xray ? 0x0d100c : C.ground);
  flows.forEach(f => {
    const toDept = DEPTS.some(d => d.k === f.to);
    f.lineMat.opacity = before ? 0.08 : xray ? 0.6 : 0.28;
    f.dm.color.copy(before ? new THREE.Color(0x56606c) : f.baseColor);
    f.dots.forEach(d => d.s.visible = !(before && toDept));
  });
  agents.forEach(a => a.visible = !before);
  DEPTS.forEach(d => d.ring.visible = !before);
  
  rings.forEach(r => r.visible = !before); core.visible = !before;
  orgAgentObjs.forEach(o => o.visible = !before);
  orgAiLines.forEach(l => l.mat.opacity = before ? 0 : xray ? Math.min(1, l.op * 2) : l.op);
  orgOldLines.forEach(l => l.mat.opacity = before ? 0.55 : 0);
  oldOnly.forEach(o => o.visible = before);
  bloom.strength = xray ? 0.55 : 0.7; core.material.emissiveIntensity = before ? 0.15 : xray ? 0.9 : 1.3;
  renderHud();
}
document.querySelectorAll('button[data-mode]').forEach(b => b.onclick = () => setMode(b.dataset.mode));

// ---------------- 镜头 ----------------
const SHOTS = {
  ...Object.fromEntries(Object.entries(CFG.campus.shots).map(([k, s]) => [k, { p: V(...s.p), t: V(...s.t) }])),
  org: { p: V(OX + 92, 104, 140), t: V(OX, 30, 0) },
  orgTop: { p: V(OX + 34, 62, 54), t: V(OX, 36, 0) },
  orgMid: { p: V(OX + 46, 46, 70), t: V(OX, 18, 0) },
  orgLow: { p: V(OX + 30, 30, 62), t: V(OX - 8, 10, 0) },
  orgL: { p: V(OX + 10, 40, 70), t: V(OX - 18, 16, 0) },
  ideal: { p: V(IX + 86, 98, 124), t: V(IX, 2, -2) },
  iGate: { p: V(IX + 60, 100, 110), t: V(IX, 0, 0) },
  iTop: { p: V(IX + 30, 58, 50), t: V(IX, 5, 0) },
  iPods: { p: V(IX + 64, 74, 92), t: V(IX, 2, 0) },
  iDom: { p: V(IX + 62, 76, 92), t: V(IX, 2, 0) },
  iSite: { p: V(IX + 62, 38, 72), t: V(IX + 22, 2, 24) },
  iBoss: { p: V(IX + 26, 40, 14), t: V(IX, 16, -22) },
};
let shotFrom = null, shotTo = null, shotT = 1;
function goShot(n) {
  shotTo = SHOTS[n];
  if (stage.clientWidth < 1000 && shotTo) { const k = 0.82; shotTo = { p: shotTo.t.clone().lerp(shotTo.p, k), t: shotTo.t }; } shotFrom = { p: camera.position.clone(), t: controls.target.clone() }; shotT = 0; }
controls.addEventListener('start', () => { shotT = 1; });

// ---------------- 故事：一个订单走完全公司 ----------------
const STEPS_CAMPUS = CFG.campus.steps;
const STEPS_ORG = CFG.org.steps;
const STEPS_IDEAL = CFG.ideal.steps;
let STEPS = STEPS_CAMPUS, view = 'campus';
let step = 0, playing = false, playTimer = null;
const stepsEl = $('#steps');
function buildSteps() {
  stepsEl.innerHTML = '';
  STEPS.forEach((s, i) => { const b = document.createElement('button'); b.type = 'button'; b.textContent = i + 1; b.onclick = () => { stopPlay(); go(i); }; stepsEl.appendChild(b); });
}
buildSteps();
function setView(v) {
  view = v; document.body.dataset.view = v;
  document.querySelectorAll('button[data-view]').forEach(b => b.classList.toggle('on', b.dataset.view === v));
  if (v === 'cockpit') { stopPlay(); goShot('all'); if (document.body.classList.contains('immersive')) setImmersive(false); drawCockpitCharts(); return; }
  STEPS = v === 'org' ? STEPS_ORG : v === 'ideal' ? STEPS_IDEAL : STEPS_CAMPUS;
  if (v === 'ideal' && mode !== 'after') setMode('after');
  stopPlay(); buildSteps(); go(0); renderHud();
}
document.querySelectorAll('button[data-view]').forEach(b => b.onclick = () => setView(b.dataset.view));
function polyCurve(keys) {
  const pts = keys.map(k => orgNodes[k].clone());
  const path = new THREE.CurvePath();
  for (let i = 0; i < pts.length - 1; i++) path.add(new THREE.LineCurve3(pts[i], pts[i + 1]));
  return path;
}
function pathCurve(keys) {
  const pts = keys.map(k => k === 'hub' ? HUBP.clone() : (nodes[k] || V(0, 0, 0)).clone()).map(p => { p.y += 3; return p; });
  const full = [];
  for (let i = 0; i < pts.length - 1; i++) {
    const c = arc(pts[i], pts[i + 1], 7);
    full.push(...c.getPoints(30).slice(i ? 1 : 0));
  }
  return new THREE.CatmullRomCurve3(full);
}
let hlSet = new Set();
function go(i) {
  step = i; const s = STEPS[i];
  stepsEl.querySelectorAll('button').forEach((b, j) => b.classList.toggle('on', j === i));
  $('#s-no').textContent = `第 ${i + 1} 步 / 共 ${STEPS.length} 步`;
  $('#s-title').textContent = s.t;
  $('#s-before').textContent = s.before;
  $('#h-a').textContent = s.hA || '今天'; $('#h-b').textContent = s.hB || 'AI 之后';
  $('#s-after').textContent = s.after;
  $('#s-agents').innerHTML = s.agents.map(a => `<span>${a}</span>`).join('');
  $('#s-ev').textContent = s.ev;
  goShot(s.shot);
  hlSet = new Set(s.hl);
  TAGS.forEach(t => t.el.classList.toggle('hl', hlSet.has(t.g)));
  const ps = s.paths ? s.paths : s.path ? [s.path] : [];
  tokens.forEach((tk, j) => {
    const p = ps[j];
    if (p && view !== 'ideal') { tk.curve = view === 'org' ? polyCurve(p) : pathCurve(p); tk.t = 0; tk.m.visible = true; tk.speed = view === 'org' ? 0.16 : 0.22; }
    else { tk.curve = null; tk.m.visible = false; }
  });
  $('#prev').disabled = i === 0; $('#next').textContent = i === STEPS.length - 1 ? (view !== 'campus' ? '回到第 1 步' : '回到全景') : '下一步';
}
$('#prev').onclick = () => { stopPlay(); if (step > 0) go(step - 1); };
$('#next').onclick = () => { stopPlay(); go(step < STEPS.length - 1 ? step + 1 : 0); };
function stopPlay() { playing = false; clearInterval(playTimer); $('#play').textContent = '▶ 自动讲解'; }
$('#play').onclick = () => {
  if (playing) return stopPlay();
  playing = true; $('#play').textContent = '❚❚ 暂停';
  go(step); playTimer = setInterval(() => { if (step >= STEPS.length - 1) { stopPlay(); return; } go(step + 1); }, 7000);
};

// ---------------- HUD ----------------
const deptLoad = { ...CFG.hud.deptLoad };
let aiDone = CFG.hud.aiDone ?? 1284, pending = 6, pue = CFG.hud.metric.base;
function renderHud() {
  if (view === 'cockpit') return;
  const before = mode === 'before';
  $('#k-ai').textContent = before ? '0' : aiDone.toLocaleString('en-US');
  $('#k-pend').textContent = before ? '—' : pending;
  $('#k-pue').textContent = (before ? pue + (CFG.hud.metric.beforeDelta ?? 0) : pue).toFixed(CFG.hud.metric.dec ?? 2);
  $('#k-sla').textContent = before ? '人工汇总' : '实时';
  const max = 140;
  $('#dept-bars').innerHTML = DEPTS.map(d => {
    const v = before ? 0 : deptLoad[d.k];
    return `<div class="row"><span>${d.n}</span><div class="track"><i style="width:${Math.min(100, v / max * 100)}%"></i></div><b>${before ? '人工' : v}</b></div>`;
  }).join('');
  if (view === 'ideal') {
    ['#kl-1', '#kl-2', '#kl-3', '#kl-4'].forEach((id, i) => $(id).textContent = ['Agent 完成占比', '人完成的任务', '转人工的例外', '回流知识库'][i]);
    const tot = icount.agent + icount.human + icount.exc || 1;
    $('#k-ai').textContent = Math.round(icount.agent / tot * 100) + '%';
    $('#k-pend').textContent = icount.human;
    $('#k-pue').textContent = Math.round(icount.exc / tot * 100) + '%';
    $('#k-sla').textContent = icount.learn;
    $('#modeNote').textContent = '理想态：没有部门。任务池 + 目标小队干活，职责节点守规则、担责任，老板管目标和边界。方块是任务，颜色代表谁在做。';
    return;
  }
  const L = view === 'org' ? ['Agent 完成任务占比', '人工介入率', '异常到人平均用时', '经营数据'] : ['AI 今日完成任务', '待人确认', CFG.hud.metric.label, '经营数据'];
  ['#kl-1', '#kl-2', '#kl-3', '#kl-4'].forEach((id, i) => $(id).textContent = L[i]);
  if (view === 'org') {
    $('#k-ai').textContent = before ? '0%' : '72%';
    $('#k-pend').textContent = before ? '—' : '8%';
    $('#k-pue').textContent = before ? '5 天' : '3 分钟';
    $('#k-sla').textContent = before ? '层层上报' : '自动汇总';
  }
  const lane = $('#modeNote');
  if (view === 'org') { lane.textContent = before ? '今天：老板直接找部门要数据，部门里的人直接操作系统，信息一层层往上报。' : '组织：人定目标、定规则、审例外；总控 Agent 拆解派活，业务 Agent 执行，例外才推给人。'; return; }
  lane.textContent = before ? '今天：数据散在各系统，部门之间靠人传话、靠经验判断。' : mode === 'xray' ? '透视：看清每栋楼里的数据流向“' + BRAIN + '”，再变成各部门的建议。' : 'AI 之后：数据汇入大脑，数字员工在各部门干活，需要拍板的才推给人。';
}
const EVENTS = CFG.hud.events;
let ei = 0;
function tick() {
  if (mode === 'before') { $('#ticker').innerHTML = `<b>人工</b> 各部门周五汇总报表，管理层下周一看到上周数据`; return; }
  const e = EVENTS[ei++ % EVENTS.length];
  $('#ticker').innerHTML = `<b>${e[0]}</b> ${e[1]}`;
  aiDone += 3 + Math.floor(Math.random() * 6); pending = 4 + Math.floor(Math.random() * 5);
  pue = CFG.hud.metric.base + (Math.random() - 0.5) * (CFG.hud.metric.jitter ?? 0.04);
  const k = DEPTS[Math.floor(Math.random() * DEPTS.length)].k; deptLoad[k] += 1;
  renderHud();
}
setInterval(tick, 2600);

// ---------------- 尺寸 ----------------
function resize() {
  const r = stage.getBoundingClientRect();
  renderer.setSize(r.width, r.height); composer.setSize(r.width, r.height);
  camera.aspect = r.width / r.height;
  camera.fov = r.width / r.height < 1 ? 44 : 30;
  if (r.width >= 1000) camera.setViewOffset(r.width, r.height, 0, r.height * 0.13, r.width, r.height); else camera.clearViewOffset();
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize); resize();

// ---------------- 循环 ----------------
const tmp = new THREE.Vector3();
const clock = new THREE.Clock();
function loop() {
  const raw = clock.getDelta(), dt = Math.min(raw, 0.05), t = clock.elapsedTime;
  if (shotT < 1 && shotTo) {
    shotT = Math.min(1, shotT + Math.min(raw, 0.3) / 1.6);  // 镜头按真实时间走，慢机器也不会卡在半路
    const k = shotT < 0.5 ? 2 * shotT * shotT : 1 - Math.pow(-2 * shotT + 2, 2) / 2;
    camera.position.lerpVectors(shotFrom.p, shotTo.p, k); controls.target.lerpVectors(shotFrom.t, shotTo.t, k);
  }
  controls.update();
  const sp = reduce ? 0 : 1;
  core.rotation.y += dt * 0.6 * sp; core.rotation.x += dt * 0.25 * sp;
  rings.forEach((r, i) => r.rotation.z += dt * (0.3 + i * 0.2) * (i % 2 ? -1 : 1) * sp);
  agents.forEach((a, i) => { a.rotation.y += dt * 1.4 * sp; a.position.y = 6.4 + Math.sin(t * 2 + i) * 0.3 * sp; });
  scene.traverse(o => { if (o.userData.fan) o.rotation.y += dt * 6 * sp; });
  cars.forEach(c => {
    c.t = (c.t + dt * c.sp * c.dir * sp + 1) % 1;
    const [x1, z1, x2, z2] = c.L, ang = Math.atan2(z2 - z1, x2 - x1);
    c.car.position.set(x1 + (x2 - x1) * c.t - Math.sin(ang) * c.off, 0, z1 + (z2 - z1) * c.t + Math.cos(ang) * c.off);
    c.car.rotation.y = -ang + (c.dir < 0 ? Math.PI : 0);
  });
  const speedMul = mode === 'before' ? 0.35 : 1;
  flows.forEach(f => f.dots.forEach(d => { d.t = (d.t + dt * f.speed * speedMul * sp) % 1; f.curve.getPoint(d.t, tmp); d.s.position.copy(tmp); }));
  tokens.forEach(tk => { if (!tk.curve) return; tk.t = (tk.t + dt * tk.speed * (sp || 0.5)) % 1; tk.curve.getPoint(tk.t, tmp); tk.m.position.copy(tmp); });
  idealTick(dt, sp);
  ocore.rotation.y += dt * 0.6 * sp; oring.rotation.z += dt * 0.5 * sp;
  orgSpin.forEach((o, i) => { o.m.rotation.y += dt * 1.5 * sp; o.m.position.y = o.y + Math.sin(t * 2 + i) * 0.2 * sp; });
  // 标签投影
  const w = stage.clientWidth, h = stage.clientHeight;
  TAGS.forEach(tg => {
    tmp.copy(tg.p).project(camera);
    const vis = tg.view === view && !(tg.view === 'ideal' && tg.mini && !hlSet.has(tg.g)) && tmp.z < 1 && Math.abs(tmp.x) < 1.1 && Math.abs(tmp.y) < 1.1;
    tg.el.style.display = vis ? '' : 'none';
    if (tg.view === 'ideal') tg.el.classList.toggle('dim', !hlSet.has(tg.g));
    if (vis) tg.el.style.transform = `translate(${(tmp.x * 0.5 + 0.5) * w}px, ${(-tmp.y * 0.5 + 0.5) * h}px)`;
  });
  composer.render();
  requestAnimationFrame(loop);
}
// ================= 老板经营驾驶舱（DOM） =================
const DEFAULT_STAGES = {
  1: { n: '阶段一 · 起步', when: '第 1–6 个月', d: '老板批了，派给部门负责人，人来执行；人用 AI 工具辅助。', gate: '升级门槛：数据底座覆盖首批业务；3 个部门助理 Agent 评测达标；各部门有连续 4 周使用记录。' },
  2: { n: '阶段二 · 过渡', when: '第 7–18 个月', d: '老板批了，总控 Agent 生成任务，部门负责人确认，部门助理 Agent 拆解，再派给业务 Agent 或员工。', gate: '升级门槛：Agent 完成占比超过六成；职责节点清单定稿；规则 · 审计底座上线；人工介入率持续下降。' },
  3: { n: '阶段三 · 理想', when: '第 2–3 年', d: '老板批了，任务直接进任务池，总控按能力和风险派给人或 Agent，例外找对应的职责节点。', gate: '这时组织图上没有部门，只有目标、任务和职责节点。' },
};
const CK = {
  stage: 1,
  stages: CFG.cockpit.stages || DEFAULT_STAGES,
  tiles: CFG.cockpit.tiles.map(t => [...t]),
  issues: CFG.cockpit.issues,
  decisions: CFG.cockpit.decisions.map(d => ({ ...d })),
  asks: CFG.cockpit.asks,
  log: [],
};
function route(d, stage) {
  const e = d.ex;
  if (stage === 1) return [
    [[BOSS + '批准', 'h']], [[CFG.cockpit.notifier || '总经办发通知', 'h']], [[e.dept + '负责人', 'h']], [[e.human + '执行', 'h'], ['用 AI 工具辅助', 'tool']], [['周报回传驾驶舱', 's']],
  ];
  if (stage === 2) return [
    [[BOSS + '批准', 'h']], [['总控 Agent 生成任务', 'c']], [[e.dept + '负责人确认', 'h']], [[e.dept.replace('部', '') + '助理 Agent 拆解', 'a']], [[e.agent + '做方案', 'a'], [e.human + '执行', 'h']], [['自动回传驾驶舱', 's']],
  ];
  return [
    [[BOSS + '批准', 'h']], [['进入任务池', 'c']], [['总控按能力和风险派单', 'c']], [[e.agent, 'a'], [e.human, 'h'], [e.duty + '审例外', 'duty']], [['自动回传驾驶舱', 's']],
  ];
}
const ckEl = s => document.querySelector(s);
let ckTimer = null;
function ckRender() {
  const S = CK.stages[CK.stage];
  document.querySelectorAll('#ck-stage button').forEach(b => b.classList.toggle('on', +b.dataset.st === CK.stage));
  ckEl('#ck-stage-d').innerHTML = `<b>${S.n}</b>（${S.when}）${S.d}<br><span>${S.gate}</span>`;
  ckEl('#ck-tiles').innerHTML = CK.tiles.map(([n, st, m, note]) => `<div class="tile ${st}"><i></i><b>${n}</b><em>${m}</em><span>${note}</span></div>`).join('');
  ckEl('#ck-issues').innerHTML = CK.issues.map(([st, t, o, ai]) => `<li class="${st}"><b>${t}</b><span>${o}</span><em>${ai}</em></li>`).join('');
  const pend = CK.decisions.filter(d => !d.done).length;
  ckEl('#ck-k-dec').textContent = pend;
  ckEl('#ck-decs').innerHTML = CK.decisions.map(d => `
    <div class="dec ${d.done ? 'done' : ''}" data-id="${d.id}">
      <div class="dt">${d.t}</div>
      <div class="dai"><b>AI 建议</b>${d.ai}</div>
      <ul>${d.why.map(w => `<li>${w}</li>`).join('')}</ul>
      <div class="dimp">${d.imp}</div>
      <div class="dbtn">${d.done ? `<span class="ok">已${d.done}</span><button type="button" data-act="show">看派发路径</button>` : `<button type="button" class="go" data-act="ok">批准并派发</button><button type="button" data-act="redo">让 AI 重做</button><button type="button" data-act="no">驳回</button>`}</div>
    </div>`).join('');
  ckEl('#ck-log').innerHTML = CK.log.slice(-5).reverse().map(l => `<li>${l}</li>`).join('') || '<li class="muted">还没有派发记录。批准一项决策试试。</li>';
}
function ckDispatch(d) {
  const r = route(d, CK.stage);
  ckEl('#ck-route-t').textContent = `${d.t} · ${CK.stages[CK.stage].n}`;
  const box = ckEl('#ck-route');
  box.innerHTML = r.map((col, i) => `<div class="rn" data-i="${i}">${col.map(([t, k]) => `<span class="${k}">${t}</span>`).join('')}</div>`).join('<div class="ra">→</div>');
  clearInterval(ckTimer); let i = 0;
  const nodes = box.querySelectorAll('.rn');
  nodes[0].classList.add('on');
  ckTimer = setInterval(() => { i++; if (i >= nodes.length) { clearInterval(ckTimer); return; } nodes[i].classList.add('on'); }, 650);
}
function ckInit() {
  ckEl('#ck-stage').addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; CK.stage = +b.dataset.st; ckRender(); const last = CK.decisions.find(d => d.done === '派发') || CK.decisions[0]; ckDispatch(last); });
  ckEl('#ck-decs').addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    const d = CK.decisions.find(x => x.id === b.closest('.dec').dataset.id);
    const now = new Date(); const hm = String(now.getHours()).padStart(2, '0') + ':' + String(now.getMinutes()).padStart(2, '0');
    if (b.dataset.act === 'ok') {
      d.done = '派发';
      const tile = CK.tiles.find(t => t[0] === d.tile); if (tile) { tile[1] = 'run'; tile[3] = '已派发，执行中'; }
      CK.log.push(`<b>${hm}</b> 批准「${d.t}」，按${CK.stages[CK.stage].n}派发`);
      ckRender(); ckDispatch(d);
    } else if (b.dataset.act === 'redo') {
      CK.log.push(`<b>${hm}</b> 「${d.t}」退回 AI 重做，要求补充方案对比`); ckRender();
    } else if (b.dataset.act === 'no') {
      d.done = '驳回'; CK.log.push(`<b>${hm}</b> 驳回「${d.t}」`); ckRender();
    } else if (b.dataset.act === 'show') ckDispatch(d);
  });
  ckEl('#ck-asks').addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    const a = CK.asks[+b.dataset.i]; ckEl('#ck-ans').innerHTML = `<b>${a[0]}</b>${a[1]}`;
  });
  ckEl('#ck-asks').innerHTML = CK.asks.map((a, i) => `<button type="button" data-i="${i}">${a[0]}</button>`).join('');
  ckRender(); ckDispatch(CK.decisions[0]);
  ckEl('#ck-route-t').textContent += '（预览，尚未批准）';
}
ckInit();
// ================= 驾驶舱图表（SVG，模拟数据，带动效和悬停提示） =================
const NS = 'http://www.w3.org/2000/svg';
const tip = document.createElement('div'); tip.className = 'cktip'; document.body.appendChild(tip);
function showTip(e, html) { tip.innerHTML = html; tip.style.display = 'block'; const x = Math.min(e.clientX + 14, innerWidth - 200); tip.style.left = x + 'px'; tip.style.top = (e.clientY + 14) + 'px'; }
function hideTip() { tip.style.display = 'none'; }
function svg(el, w, h) { el.innerHTML = ''; const s = document.createElementNS(NS, 'svg'); s.setAttribute('viewBox', `0 0 ${w} ${h}`); s.setAttribute('width', '100%'); el.appendChild(s); return s; }
function add(p, tag, attrs, text) { const e = document.createElementNS(NS, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (text != null) e.textContent = text; p.appendChild(e); return e; }
let rnd = 7; const R = () => (rnd = (rnd * 9301 + 49297) % 233280) / 233280;

// 1) 近 12 个月收入（万元）——柱状，单序列
const MONTHS = CFG.cockpit.charts.trend.labels;
const REV = CFG.cockpit.charts.trend.values;
function chartRevenue() {
  const TR = CFG.cockpit.charts.trend;

  const W = 360, H = 170, L = 36, B = 22, T = 10;
  const s = svg(document.querySelector('#cv-rev'), W, H);
  const max = TR.max, min = TR.min, y = v => T + (H - B - T) * (1 - (v - min) / (max - min));
  TR.ticks.forEach(v => { add(s, 'line', { x1: L, x2: W - 4, y1: y(v), y2: y(v), class: 'grid' }); add(s, 'text', { x: L - 6, y: y(v) + 4, class: 'ax', 'text-anchor': 'end' }, v); });
  const bw = (W - L - 8) / REV.length;
  REV.forEach((v, i) => {
    const x = L + i * bw + 3, h = (H - B) - y(v);
    const r = add(s, 'rect', { x, y: H - B, width: bw - 6, height: 0, rx: 3, class: i === REV.length - 1 ? 'bar hl' : 'bar' });
    setTimeout(() => { r.setAttribute('y', y(v)); r.setAttribute('height', h); }, 60 + i * 50);
    const hit = add(s, 'rect', { x: L + i * bw, y: T, width: bw, height: H - B - T, fill: 'transparent' });
    hit.addEventListener('mousemove', e => showTip(e, `<b>${TR.tipLabel ? TR.tipLabel(MONTHS[i]) : MONTHS[i]}</b>${TR.name} ${v.toLocaleString()} ${TR.unit}`)); hit.addEventListener('mouseleave', hideTip);
    if (i % 2 === 1 || i === REV.length - 1) add(s, 'text', { x: x + (bw - 6) / 2, y: H - 6, class: 'ax', 'text-anchor': 'middle' }, MONTHS[i]);
  });
  add(s, 'text', { x: L + (REV.length - 1) * bw + bw / 2, y: y(REV[REV.length - 1]) - 6, class: 'val', 'text-anchor': 'middle' }, REV[REV.length - 1].toLocaleString('en-US'));
}

// 2) Agent 完成任务占比（近 24 周）——折线 + 面积，标出阶段升级
const AG = []; { let v = 6; for (let i = 0; i < 24; i++) { v += 1.4 + R() * 2.4 + (i === 12 ? 6 : 0); AG.push(Math.min(74, Math.round(v))); } }
function chartAgent() {
  const W = 360, H = 170, L = 30, B = 22, T = 12;
  const s = svg(document.querySelector('#cv-agent'), W, H);
  const x = i => L + (W - L - 10) * i / (AG.length - 1), y = v => T + (H - B - T) * (1 - v / 80);
  [0, 20, 40, 60, 80].forEach(v => { add(s, 'line', { x1: L, x2: W - 6, y1: y(v), y2: y(v), class: 'grid' }); add(s, 'text', { x: L - 6, y: y(v) + 4, class: 'ax', 'text-anchor': 'end' }, v + '%'); });
  add(s, 'line', { x1: x(12), x2: x(12), y1: T, y2: H - B, class: 'mark' });
  add(s, 'text', { x: x(12) + 4, y: T + 10, class: 'ax lime' }, '升级到阶段二');
  const d = AG.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join('');
  add(s, 'path', { d: d + `L${x(AG.length - 1)},${H - B}L${x(0)},${H - B}Z`, class: 'area' });
  const line = add(s, 'path', { d, class: 'line' });
  const len = line.getTotalLength ? line.getTotalLength() : 600; line.style.strokeDasharray = len; line.style.strokeDashoffset = len;
  requestAnimationFrame(() => { line.style.transition = 'stroke-dashoffset 1.6s ease'; line.style.strokeDashoffset = 0; });
  const dot = add(s, 'circle', { cx: x(AG.length - 1), cy: y(AG[AG.length - 1]), r: 4.5, class: 'dot pulse' });
  add(s, 'text', { x: x(AG.length - 1) - 4, y: y(AG[AG.length - 1]) - 9, class: 'val', 'text-anchor': 'end' }, AG[AG.length - 1] + '%');
  ['第1周', '第12周', '第24周'].forEach((t, k) => add(s, 'text', { x: x([0, 11, 23][k]), y: H - 6, class: 'ax', 'text-anchor': k === 0 ? 'start' : k === 2 ? 'end' : 'middle' }, t));
  const cross = add(s, 'line', { x1: 0, x2: 0, y1: T, y2: H - B, class: 'cross', style: 'display:none' });
  const hit = add(s, 'rect', { x: L, y: T, width: W - L - 10, height: H - B - T, fill: 'transparent' });
  hit.addEventListener('mousemove', e => {
    const r = s.getBoundingClientRect(); const px = (e.clientX - r.left) / r.width * W;
    const i = Math.max(0, Math.min(AG.length - 1, Math.round((px - L) / (W - L - 10) * (AG.length - 1))));
    cross.setAttribute('x1', x(i)); cross.setAttribute('x2', x(i)); cross.style.display = '';
    showTip(e, `<b>第 ${i + 1} 周</b>Agent 完成 ${AG[i]}% 的任务${i >= 12 ? '<br>阶段二：经总控 Agent 派发' : '<br>阶段一：派给人，人用 AI 工具'}`);
  });
  hit.addEventListener('mouseleave', () => { cross.style.display = 'none'; hideTip(); });
}

// 3) 各区域 PUE 今日——小多图，实时滚动
const ZONES = CFG.cockpit.charts.live.items;
const LV = CFG.cockpit.charts.live, AMP = LV.amp ?? (LV.max - LV.min) * 0.08;
const PUE = ZONES.map(([, b]) => Array.from({ length: 36 }, (_, i) => b + Math.sin(i / 5) * AMP + (R() - 0.5) * AMP * 0.8));
function chartPue() {
  const box = document.querySelector('#cv-pue'); box.innerHTML = '';
  ZONES.forEach(([n], zi) => {
    const row = document.createElement('div'); row.className = 'pr';
    const arr = PUE[zi], cur = arr[arr.length - 1];
    const over = LV.higherIsBad === false ? cur < LV.warn : cur > LV.warn, dec = LV.dec ?? 2;
    row.innerHTML = `<span class="pn">${n}</span><span class="ps"></span><b class="pv">${cur.toFixed(dec)}</b><em class="pf">${over ? (LV.higherIsBad === false ? '▼ 低于 ' : '▲ 高于 ') + LV.warn : ''}</em>`;
    box.appendChild(row);
    const s = svg(row.querySelector('.ps'), 160, 30);
    const x = i => 2 + 156 * i / (arr.length - 1), y = v => 2 + 26 * (1 - (v - LV.min) / (LV.max - LV.min));
    add(s, 'line', { x1: 0, x2: 160, y1: y(LV.warn), y2: y(LV.warn), class: 'mark' });
    add(s, 'path', { d: arr.map((v, i) => `${i ? 'L' : 'M'}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(''), class: 'line thin' });
    add(s, 'circle', { cx: x(arr.length - 1), cy: y(cur), r: 3, class: 'dot' });
    row.addEventListener('mousemove', e => showTip(e, `<b>${n}</b>当前 ${LV.name} ${cur.toFixed(dec)}<br>今日最高 ${Math.max(...arr).toFixed(dec)}，最低 ${Math.min(...arr).toFixed(dec)}<br>虚线：关注线 ${LV.warn}`));
    row.addEventListener('mouseleave', hideTip);
  });
}
setInterval(() => { if (document.body.dataset.view !== 'cockpit') return; PUE.forEach((arr, zi) => { arr.shift(); const b = ZONES[zi][1]; arr.push(b + Math.sin(Date.now() / 4000 + zi) * AMP + (R() - 0.5) * AMP * 0.8); }); chartPue(); }, 2000);

// 4) 各机房上架率 vs 目标——横向条
const RACK = CFG.cockpit.charts.target.items;
function chartRack() {
  const TG = CFG.cockpit.charts.target;
  const box = document.querySelector('#cv-rack'); box.innerHTML = '';
  RACK.forEach(([n, v, t], i) => {
    const low = v < t - 5;
    const r = document.createElement('div'); r.className = 'rr';
    r.innerHTML = `<span class="rn2">${n}</span><span class="rt"><i style="width:0"></i><u style="left:${t}%"></u></span><b>${v}%</b><em>${low ? '⚠ 低于目标' : ''}</em>`;
    box.appendChild(r);
    setTimeout(() => r.querySelector('i').style.width = v + '%', 80 + i * 90);
    r.addEventListener('mousemove', e => showTip(e, `<b>${n}</b>${TG.name} ${v}%，目标 ${t}%${low && TG.lowNote ? '<br>' + TG.lowNote : ''}`)); r.addEventListener('mouseleave', hideTip);
  });
}

// 5) 收入结构（2024 年报，真实数据）——分段条
function chartMix() {
  const box = document.querySelector('#cv-mix');
  const MX = CFG.cockpit.charts.mix, M = MX.items.map((it, i) => [it[0], it[1], 's' + (i + 1)]);
  box.innerHTML = `<div class="mixb">${M.map(([n, v, c]) => `<i class="${c}" style="flex:${v}" data-n="${n}" data-v="${v}"></i>`).join('')}</div>
    <div class="mixl">${M.map(([n, v, c]) => `<span><i class="${c}"></i>${n} <b>${v}%</b></span>`).join('')}</div>`;
  box.querySelectorAll('.mixb i').forEach(seg => { seg.addEventListener('mousemove', e => showTip(e, `<b>${seg.dataset.n}</b>${MX.tip || '占比'} ${seg.dataset.v}%`)); seg.addEventListener('mouseleave', hideTip); });
}

// KPI 数字滚动
function countUp() {
  document.querySelectorAll('.ck-kpis b[data-to]').forEach(b => {
    const to = +b.dataset.to, dec = +(b.dataset.dec || 0), suf = b.querySelector('small') ? b.querySelector('small').outerHTML : '';
    const t0 = performance.now();
    const f = now => { const k = Math.min(1, (now - t0) / 1100), e = 1 - Math.pow(1 - k, 3); b.innerHTML = (to * e).toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + suf; if (k < 1) requestAnimationFrame(f); };
    requestAnimationFrame(f);
  });
}
function drawCockpitCharts() { chartRevenue(); chartAgent(); chartPue(); chartRack(); chartMix(); countUp(); }
window.__drawCockpit = drawCockpitCharts;

// ---------------- 全屏看画面 ----------------
function setImmersive(on) {
  document.body.classList.toggle('immersive', on);
  $('#fs').textContent = on ? '✕ 退出全屏' : '⤢ 全屏看画面';
  if (on) { const el = document.documentElement; try { const p = el.requestFullscreen && el.requestFullscreen(); if (p && p.catch) p.catch(() => {}); } catch (e) {} }
  else if (document.fullscreenElement) { try { document.exitFullscreen(); } catch (e) {} }
  setTimeout(resize, 60); setTimeout(resize, 400);
}
$('#fs').onclick = () => setImmersive(!document.body.classList.contains('immersive'));
document.addEventListener('fullscreenchange', () => { if (!document.fullscreenElement && document.body.classList.contains('immersive')) setImmersive(false); });
addEventListener('keydown', e => { if (e.key === 'Escape' && document.body.classList.contains('immersive')) setImmersive(false); });

document.body.dataset.view = 'campus';
setMode('after'); go(0); loop();
window.__go = go; window.__setMode = setMode; window.__setView = setView;

}
