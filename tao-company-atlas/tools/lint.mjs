// 配置体检：node tools/lint.mjs configs/<公司>.js
// 构建前先跑。查的是“页面能跑但效果会打折”的问题：数量不够、引用了不存在的节点、忘了标示意。
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
const C = (await import(pathToFileURL(resolve(process.argv[2])).href)).default;
const bad = [], warn = [];
const need = (cond, msg) => { if (!cond) bad.push(msg); };
const want = (cond, msg) => { if (!cond) warn.push(msg); };
const KITS = ['hall', 'office', 'chillers', 'substation', 'solar', 'mast', 'pods', 'warehouse', 'silo', 'store', 'factory', 'pad', 'turbine'];

['shortName', 'enName', 'brainName', 'bossName', 'footnote'].forEach(k => need(C[k], `缺 ${k}`));
need(/示意|模拟/.test(C.footnote || ''), 'footnote 要写明哪些是示意');

// 园区
const cp = C.campus || {};
const groups = new Set((cp.items || []).map(i => i.g));
need((cp.items || []).length >= 8, `园区建筑至少 8 个（现在 ${(cp.items || []).length}）`);
(cp.items || []).forEach(i => want(KITS.includes(i.type), `建筑类型 ${i.type} 不在积木库里，会退化成普通楼；需要就去 engine3d.js 的 KIT 里加`));
want(new Set((cp.items || []).map(i => i.type)).size >= 5, '园区积木种类少于 5 种，画面会单调');
need(cp.shots && cp.shots.all, 'campus.shots 必须有 all（驾驶舱回到全景用）');
need((cp.depts || []).length === 8, `部门要正好 8 个（现在 ${(cp.depts || []).length}）`);
const nodeKeys = new Set([...Object.keys(cp.nodes || {}), ...(cp.depts || []).map(d => d.k), 'hub']);
const hlKeys = new Set([...groups, ...(cp.depts || []).map(d => 'd-' + d.k), 'hub']);
need((cp.steps || []).length === 8, '园区要 8 步');
(cp.steps || []).forEach((s, i) => {
  need(cp.shots[s.shot], `园区第 ${i + 1} 步镜头 ${s.shot} 不存在`);
  (s.path || []).forEach(k => need(nodeKeys.has(k), `园区第 ${i + 1} 步路径节点 ${k} 不存在（可用：${[...nodeKeys].join(' ')}）`));
  (s.hl || []).forEach(k => want(hlKeys.has(k), `园区第 ${i + 1} 步高亮 ${k} 没有对应建筑组`));
  need(s.before && s.after && s.agents && s.ev, `园区第 ${i + 1} 步缺 before/after/agents/ev`);
});
(cp.tags || []).forEach(t => want(groups.has(t.g), `标签 ${t.n} 的组 ${t.g} 没有建筑`));
const H = C.hud || {};
need((H.events || []).length >= 8, '实时动态至少 8 条');
(cp.depts || []).forEach(d => need(H.deptLoad && H.deptLoad[d.k] != null, `hud.deptLoad 缺部门 ${d.k}`));

// 组织
const O = C.org || {};
need((O.depts || []).length === 8, '组织过渡态部门要 8 个');
need(O.perm && O.perm.draft && O.perm.note, 'org.perm 要写本行业的“起草建议”例子和“永远停在第 2 级”的红线');
const okeys = new Set(['boss', 'brain', 'screen', 'mKb', 'mData', 'mModel', 'mRule']);
(O.depts || []).forEach(d => { ['h-', 'a-', 's-'].forEach(p => okeys.add(p + d.k)); (d.ag || []).forEach((_, j) => okeys.add(`g-${d.k}-${j}`)); need((d.ag || []).length === 2, `组织部门 ${d.n} 要 2 个业务 Agent`); });
need((O.steps || []).length === 8, '组织过渡态要 8 步');
(O.steps || []).forEach((s, i) => (s.paths || []).forEach(p => p.forEach(k => need(okeys.has(k), `组织第 ${i + 1} 步路径节点 ${k} 不存在`))));

// 理想态
const I = C.ideal || {};
need((I.pods || []).length === 4, '理想态目标小队要 4 个');
need((I.duties || []).length === 6, '职责节点要 6 个');
need((I.gates || []).length === 4, '入口要 4 个');
need((I.steps || []).length === 8, '理想态要 8 步');

// 驾驶舱
const K = C.cockpit || {};
need((K.kpis || []).length === 6, '驾驶舱 KPI 要 6 个（最后一个是待决策）');
need((K.tiles || []).length >= 12, `状态块至少 12 个（现在 ${(K.tiles || []).length}）`);
need((K.issues || []).length >= 4, 'AI 发现的问题至少 4 条');
need((K.decisions || []).length >= 4, '待决策至少 4 条');
(K.decisions || []).forEach(d => { need(d.ex && d.ex.dept && d.ex.human && d.ex.agent && d.ex.duty, `决策 ${d.t} 的派发对象 ex 不全`); want(/示意/.test(d.imp || ''), `决策 ${d.t} 的影响数字要标（示意）`); });
need((K.asks || []).length >= 3, '问一句至少 3 条');
['trend', 'live', 'target', 'mix'].forEach(k => need(K.charts && K.charts[k], `驾驶舱缺图表 ${k}`));
if (K.charts && K.charts.trend) need(K.charts.trend.labels.length === K.charts.trend.values.length, 'trend 的 labels 和 values 数量不一致');
need(/示意/.test(K.foot || ''), '驾驶舱 foot 要写明示意');

// 蓝图
const B = C.blueprint;
need(B, '缺 blueprint（AI 全貌蓝图）');
if (B) {
  ['cover', 's01', 's02', 's03', 's04', 's05', 's06', 's07', 's08', 's09', 'footer'].forEach(k => need(B[k], `蓝图缺 ${k}`));
  need((B.cover?.ideals || []).length === 4, '封面理想态要 4 张卡');
  need((B.s02?.biz || []).length >= 8, '业务主链至少 8 环');
  need((B.s02?.sup || []).length >= 3, '支撑部门至少 3 个');
  need((B.s04?.steps || []).length === 8, '样板流程要 8 步');
  need(B.s04?.steps?.filter(s => s[4]).length === 1, '样板流程里只有一步是“人做”');
  need((B.s05?.steps || []).length >= 7, '运行图至少 7 拍');
  need((B.s07?.months || []).length === 12, '路线图要 12 个月');
  need((B.s07?.rows || []).length === 7, '路线图要 7 条线');
  need((B.s09?.asks || []).length === 5, '要老板拍板的事写 5 件');
}
console.log(bad.length ? '❌ 必须改：\n  ' + bad.join('\n  ') : '✓ 必须项全过');
if (warn.length) console.log('⚠ 建议看看：\n  ' + warn.join('\n  '));
process.exit(bad.length ? 1 : 0);
