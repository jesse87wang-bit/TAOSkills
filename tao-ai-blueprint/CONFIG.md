# 配置字段说明

一份 `configs/<公司>.js`：`export default { ... }`。完整写法看 `configs/example-qinghe.js`，下面说明每个字段的意思和硬性数量。数量是按“效果不能比第一家差”定的，`tools/lint.mjs` 会检查。

## 顶层

| 字段 | 说明 |
|---|---|
| `shortName` | 简称，2–4 字。用在标题、文件名、“××大脑”。 |
| `enName` | 拼音或英文名，显示在左上角小字。 |
| `fullName` | 全称。 |
| `brainName` | 中枢名，一般 `<简称>大脑`。 |
| `bossName` | 老板称呼（如“李总”）。不知道就问用户，别编。 |
| `footnote` | 左下角脚注：哪些是真实数据（写出处），哪些是示意。 |
| `page.money` | 左上“怎么赚钱”：`rows:[[名称, 百分比]]`，`src` 写出处或“示意”，`note` 一句话说利润在哪。 |
| `page.shift` | 左上第二张卡“模式在转”：`from/to` 各 `[标题, 一句]`，`note`。 |

## campus（园区全景）

- `tokenName`：沿路径跑的那个光点叫什么（客户订单 / 一单补货 / 一批粮…）。
- `roads`：`[x1,z1,x2,z2]` 道路线段。
- `items`：建筑。`{g:组名, type:积木, x, z, ...尺寸}`。同一组可以有多个建筑。**≥8 个，≥5 种积木。**
- `nodes`：`{组名:[x,y,z]}`，数据流和路径的端点，一般放在组的屋顶上方。
- `tags`：建筑上的标签 `{p:[x,y,z], n:名, s:副标题, g:组名, big?:1}`。
- `shots`：镜头 `{名:{p:[x,y,z], t:[x,y,z]}}`，**必须有 `all`**；一般还有 `biz` 和每步一个。
- `depts`：**正好 8 个**部门小楼 `{k, n, x, z?, agent:'数字员工名'}`。默认 z=24（前排），x 间距 10；放不下的两个用 `z:40`。高亮时写 `d-<k>`。
- `steps`：**8 步**，讲“一单业务走完全公司”。每步：
  - `t` 标题；`shot` 镜头名；`hl` 要高亮的组（组名或 `d-<k>`）；
  - `path` 光点路径，节点用 `nodes` 的组名、部门 `k` 或 `hub`（大脑），`null` 表示不跑；
  - `before` 今天怎么做；`after` AI 之后怎么做；`agents` 数字员工名；`ev` 留下的证据。
- 第 1 步讲“靠什么赚钱/全景”，最后 1 步讲财务经营或职能，中间按业务主链走。

## hud

- `aiDone` 今日完成任务起始数；`metric` 第三个 KPI（`label` 用本行业最关心的指标：PUE、缺货率、损耗率…，`base/jitter/dec`，`beforeDelta` 今天模式比 AI 之后差多少）。
- `deptLoad` 每个部门今日任务数，key 对齐 `campus.depts[].k`。
- `events` **≥8 条** `[数字员工, 一句发生了什么]`，要具体到门店/机房/产线/金额。

## org（组织·过渡态）

- `depts` **8 个** `{k, n, ag:[两个业务Agent], sys:'对接系统'}`；不必和园区部门完全一致（可加总经办）。
- `kbSub/modelSub` 知识库、专用模型平台的小字。
- `perm` `{draft, note}`：权限三级里“起草建议”的本行业例子，以及“什么永远停在第 2 级”（安全/食安/医疗处置…）。
- `steps` **8 步**，`paths` 是若干条节点链，节点名：`boss` `brain` `screen` `mKb` `mData` `mModel` `mRule`，部门的 `h-<k>`(负责人) `a-<k>`(部门助理) `g-<k>-0/1`(业务Agent) `s-<k>`(系统)。`hl` 可用 `L-boss L-brain L-dept L-agent L-sys`、`boss`、`brain`、`d-<k>`。镜头名：`org orgTop orgMid orgLow orgL`。`hA/hB` 是两栏标题。
- 8 步的固定节奏：五层结构 → 老板一句话拆目标 → 一次异常处置 → 一单跨部门交接 → 周会数据自动汇 → 人改一次 Agent 学一次 → 人的角色怎么变 → 权限与节奏。

## ideal（组织·理想态，上市/成熟期之后，没有部门）

- `pods` **4 个**目标小队 `{k, n, s, a:角度, col:颜色, ag:[4个Agent], duty:挂哪个职责节点下标, site?:true}`。按“价值流”分（客户流/运营流/资源流/经营流），不按部门。
- `duties` **6 个**职责节点 `[名称, 审什么·担什么责]`：责任挂在具体的人身上。不相容职责分给不同的人。
- `gates` **4 个**信息入口 `{n, x, z, pod}`。
- `site` 现场人员池 `{n, s}`：现场的活也是按任务、资质、排班派。
- `steps` **8 步**，镜头名：`ideal iGate iTop iPods iDom iSite iBoss`；`hl` 可用 `i-core i-pool i-boss i-gate i-pod-<k> i-duty i-base i-site`。

## cockpit（老板驾驶舱，每家必有）

- `title/sub/notifier/foot`（foot 必须写示意）。
- `kpis` **6 个**，最后一个 `{label:'待决策', pending:true, hot:true}`。
- `tiles` **≥12 个** `[环节, ok|warn|bad, 状态一句, 补充一句]`，覆盖主链每一环和关键职能。
- `issues` **≥4 条** `[bad|warn, 问题, '负责人：…', 'AI 已经做了什么']`。
- `decisions` **≥4 条** `{id, tile, t, ai, why:[两条依据], imp:'影响（示意）', ex:{dept, human, agent, duty}}`。`ex` 决定派发路径三个阶段里各走到谁。
- `asks` **≥3 条** `[问题, 带出处的回答]`。
- `stages` 可省（用默认的三阶段：到人 / 总控Agent→部门→Agent或人 / 任务池直接派）。
- `charts`：`trend`（12 个月柱状）、`live`（实时小折线，`higherIsBad`）、`target`（达成 vs 目标横条，`lowNote`）、`mix`（结构条）。数值要像真的：有季节性、有一两个低于目标。

## blueprint（AI 全貌蓝图）

字段多，照示例逐段改。要点：

- `cover`：`h1/h1b` 两行大标题（第一行说行业本质，第二行说 AI 带来什么）；`ideals` **4 张**理想态卡；`link3d` 填 3D 页链接（发布后回填再构建一次）。
- `s01` 中枢大屏：`kpis` 3 个（`live:'avg'|'inc'` 会动），`bars` 5 个区域/单元 + `barsScale:[min,max,dec,jitter]` + `barsBest`，`nodes` 地图上的点（x,y ∈0–1），`agents` 8 个 `[名, 今日数, 核心?]`，`auto/todo` 各 4–6 条，`callouts` 4 个角色。
- `s02` 全业务地图：`biz` 主链 **8–10 环** `{k,s,pain,how,ag:[[名, p1|p2|p3|m]],hl?}`，`sup` 支撑部门 ≥3，`modes` 三种经营模式，`defaultIdx` 默认选中哪环（选价值最大的那环）。
- `s03` 架构 7 层（人/入口/智能体/模型/数据底座/现有系统/物理设施），`cls:'new'` 是新增三层；`gov` 6 条治理；`loop` 一句飞轮。
- `s04` 样板流程 **8 步** `[名, 'AI 做'|'人 做', 做什么, 留下什么, 是否人]`，只有一步是人拍板。
- `s05` 运行图 ≥7 拍 `{t:时间, c:[列号1–5, 'm ai|m mdl|m hum|m ok|m bad', 文字], cap}`，`heads` 6 列表头。
- `s06` 矩阵 `pts:[[名, 落地难易0–1, 价值0–1, 批次]]`，`rank` 前十 `[名, 理由, 批次, 时间, 是否第一批]`。
- `s07` 4 阶段卡 + 12 个月 + **7 条线** `[名, [[起月,止月,b1–b6,文字]], 终点]` + 3 道关口 `[月序, 名]` + `note`（节假日、旺季）。
- `s08` 行业专属视角：上市公司写“上市视角”，扩张期写“扩张视角”，强监管写“合规视角”。`th` 三列表头，`rows`，`dont` 4 条“我们不做什么”。
- `s09` 第一个月：4 周、准备清单、一个月后能看到、**5 件**要老板拍板的事。
- `footer` 写清数据出处和示意。
