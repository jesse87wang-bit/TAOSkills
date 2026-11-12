# tao-company-atlas 工具包 v1.0.3

给一家公司生成两张可离线打开的网页：

| 产物 | 内容 |
|---|---|
| `<简称>AI运转全景.html` | three.js 3D 园区。四个视图：**园区全景**（一单业务走完全公司，8 步）、**组织·过渡态**（五层：老板/大脑/部门/业务 Agent/系统，8 步）、**组织·理想态**（没有部门：任务池 + 目标小队 + 职责节点，8 步）、**老板驾驶舱**（全公司状态、AI 发现的问题、待决策、批准即派发、派发路径随 AI 阶段升级、4 张动态图表、问一句）。今天/AI 之后/AI 透视三种模式，自动讲解，全屏。 |
| `<简称>AI全貌蓝图.html` | 9 个板块：01 理想态中枢大屏、02 全业务 AI 地图（可点）、03 架构、04 样板流程、05 运行图（可播放）、06 先后顺序矩阵、07 路线图（甘特 + 关口）、08 行业专属视角（上市/扩张/合规…）、09 第一个月。 |

两张页都由**一份配置**生成：`configs/<公司>.js`。引擎不随公司改；新公司只写配置。

## 用法

```bash
npm install                                   # three 0.169 + esbuild 0.24
node tools/lint.mjs configs/<公司>.js           # 配置体检，必须项全过才构建
node tools/build.mjs configs/<公司>.js out      # 生成两张单文件 HTML
python3 tools/qa.py out/<简称>AI运转全景.html qa  # 3D 页功能验收（3 种宽度、拦截谷歌字体）
python3 tools/qa_bp.py out/<简称>AI全貌蓝图.html qa
python3 tools/snap.py out/<简称>AI运转全景.html snap   # 逐步截图，看镜头和标签
```

QA 需要 Playwright + Chromium（云端容器已预装）。swiftshader 软件渲染很慢，`qa.py` 要 2–4 分钟，放后台跑。

## 目录

```
engine/engine3d.js          3D 引擎：export function run(CFG)
engine/template3d.html      3D 页模板（样式、面板骨架）
engine/blueprint.js         蓝图渲染：export function render(CFG)
engine/template-blueprint.html
configs/example-tingtao.js   虚构示例（连锁便利店）——写新公司时照它的字段写
tools/build.mjs lint.mjs qa.py qa_bp.py snap.py publish_github.sh
CONFIG.md                   配置字段说明（写配置前必读）
NARRATION.md                两份讲解稿的写法和骨架
```

## 镜头怎么调（最花时间的一步）

园区坐标约定：x 向右、z 向前（朝镜头），地面 y=0，可用范围约 x∈[-75,65]、z∈[-50,45]。

- 后排（z≈-30）放生产/基础设施（机房、仓、厂、筒仓），右侧（x≈20~40）放总部和合作方，左侧（x≈-60）放客户，前排（z≈24 默认）是 8 个部门小楼，中心（0,·,0）是“大脑”。
- 每个 `shots.<名>`：`t` = 要看的那组建筑的中心，`p` = t + 约 (+40~60, +45~60, +50~70)。全景 `all` 约 `p:[98,108,132] t:[-4,0,0]`。
- 跑 `snap.py`，逐张看：要讲的那组建筑在画面中上部、不被底部步骤卡挡住；标签不叠成一团；左右面板没盖住主角。不对就改 `p/t` 重跑。
- 经验：画面里看得清的范围大约是以 t 为中心、半径 25 的一圈；离 t 远的建筑会跑到左右面板底下。一步要同时讲两处（客户和部门），把 t 放在两者之间偏主角一侧，再把 p 拉高拉远。第一版镜头几乎都要改 1–3 轮。
- 手机宽度（<1000）镜头会自动拉近 18%，不用单独配。

## 积木库（campus.items 的 type）

`hall` 机房/厂房（屋顶风机）· `office` 楼宇 · `chillers` 冷机 · `substation` 变配电 · `solar` 光伏 · `mast` 通信塔 · `pods` 算力舱/集装箱 · `warehouse` 仓库/物流中心 · `silo` 筒仓/储罐 · `store` 门店一排 · `factory` 工厂（锯齿顶+烟囱）· `pad` 广场底座。

行业需要新造型（医院、港口吊机、风机、高炉…）就在 `engine3d.js` 的 `KIT` 里加一个函数，只用 `box/cyl/windows/roofKit` 这些现成工具，新增参数都要有默认值，旧配置不受影响。加完跑示例和至少一份旧配置的 QA，确认没退化。

## 已踩过的坑（别再踩）

- 按钮选择器一律写 `button[data-view]`，`[data-view]` 会选中 `<body data-view>`，点哪步都回到第 1 步。
- 驾驶舱 grid-template-areas 每个区域必须连续；改布局后跑 qa.py 的“1180/390 宽面板不被挤窄”。
- 谷歌字体用 `media="print" onload` 异步加载，国内或离线打开不阻塞渲染。
- 镜头补间按真实时间（不是被截断的 dt）走，慢机器上不会停在半路。
- 页面上真实数据（年报、官网）写出处；其余数字一律标“示意”。员工数、门店数这类事实以最新公开资料为准，查不到就不写具体数。
