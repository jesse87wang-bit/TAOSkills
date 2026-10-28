# 网页 Demo 规范（01_网页演示版_双击启动）

每个案例都做。用来让学员看到“做成产品是什么样”，不要求学员照做。标准来自尚航 03 HR 招聘 Agent 演示版、05 运维节能 Agent v4；骨架直接用商务差旅：`~/Desktop/AI产品库/商务差旅助手Agent/01_网页演示版_双击启动/`（本技能 assets/网页Demo骨架/ 也有一份 app/、web/、tests/ 和三个脚本）。

## 一、技术约束

- Mac 本地运行，只依赖系统自带 Python 3.9+ 标准库；前端纯 HTML/CSS/JS，不走 CDN（要图表就把库放本地一份）
- `启动.command` 双击启动：`cd "$(dirname "$0")"`；检查 python3，缺失提示 `xcode-select --install` 并等按键；`export PYTHONDONTWRITEBYTECODE=1`；`python3 app/server.py`
- 服务只听 127.0.0.1；端口固定起点，被占用往后找 20 个；`NO_BROWSER=1` 不开浏览器（测试用）；`<APP>_DEMO_PORT` 改起点。已用：8765 运维节能、8766/8767 HR 招聘、8768 商务差旅，新案例从 8769 起
- 计算全部 `subprocess.run([sys.executable, 工具/xx.py, ...], cwd=ROOT)`，和 WorkBuddy 版同一套程序；每个批次的输入先复制到 `data/runs/<批次>/输入/` 再算（拍板会改输入的情况，例如“改订标准席别”，只改副本）
- 状态 `data/state.json` 原子写（先写 .tmp 再 os.replace），一把全局 RLock 包住所有 POST

## 二、服务端要点（app/server.py、app/store.py）

store.py：
```python
TRIPS/BATCHES = {"sh": {"id","dir","label","dates", 扩展样例文件名或 None, 早报日期…}, "cd": {...}}
ROLES = {"assistant": {"label":"差旅助理","desc":"查、算、起草；不能替人拍板、下单、审批"},
         "traveler": {...}, "manager": {...}, "finance": {...}}
_blank_batch() -> {"stage":"需求","plan_ready":False,"decisions":{},"mode_confirmed":None,"chosen":None,
                   "package_ready":False, 各扩展_ready:False, ...}
log(s, role, batch, action, detail)   # 插到 audit 最前，保留 300 条
reset()                                # 删 data/runs 和 state.json，写一条“重置演示状态”日志
```

server.py：
```python
class Denied(Exception): ...   # → 403 {"error": ..., "denied": True}
class ToolError(Exception): ...# → 500 “程序运行出错：…”
# ValueError → 400（输入不对、口径不一致等）

def need(role, allowed, what, why):
    if role not in allowed:
        raise Denied("当前身份是“%s”。%s要由%s来做：%s。请在右上角切换身份。" % (...))
```

- GET：`/api/meta`（数据标签、身份、批次、各批次状态、模型公开配置）、`/api/audit`、`/api/settings`、`/api/doc?name=`（白名单：规则卡、制度、标准、偏好、格式说明、README）、`/api/<批次>/info|plan|package|change|expense|briefs|file?kind=&name=&inline=1`
- POST：`/api/<批次>/plan`、`decide`（key/value；不同 key 不同身份；有的决定触发重算）、`choose`（选定方案；和已定口径不一致返回 400）、`todo`（按事项判断谁来确认；两步审批；订类写“演示：未连接<平台>…”）、扩展动作、`/api/reset`（指定身份）、`/api/settings`（指定身份）、`/api/settings/test`、`/api/agent`
- 文件下载：`os.path.normpath` 后必须以 data/runs/<批次>/<kind> 开头，否则 404；静态文件同样防越界
- `.md/.txt/.csv` 加 `charset=utf-8`，`.ics` 用 `text/calendar`；`Content-Disposition` 用 `filename*=UTF-8''…`
- 身份用请求头 `X-Role`，值用 ASCII 代码（中文放不进 header）
- 选定方案后清空下游结果（早报、变动、报销），避免新方案配旧结果

## 三、页面（web/）

- `index.html`：左侧导航（品牌、总览、按业务顺序的 ①②③… 步骤页、规则与管理）、顶栏（批次选择、当前身份选择、“样例数据 · 演示模式”标签、模型标签、窄屏菜单按钮）、main、右下角“问助理”按钮和抽屉、toast、确认弹框
- `app.js`：hash 路由；`api(path, body)` 统一带 X-Role，非 2xx 抛错（带 denied、status）；`act(fn, okText)` 统一 toast；`refresh()` 动作后重新拉 meta、保持滚动位置再渲染；`confirmBox(html, okText)`；轻量 md 渲染（标题、表格、列表、引用块带“复制”按钮）
- 身份和批次存 localStorage（读写包 try/catch）
- 方案页只显示和已定口径一致的方案卡；“必须先拍板的事”卡片上每项写“由谁拍板”，按钮按身份点
- 待办表：🔒 事项点“确认”弹框，写清订什么、多少钱、要提供哪些信息、“演示系统没有连接订票平台：确认后只记录‘本人已同意’，不会产生订单，也不会付款”
- 设置页：身份说明表；大模型（服务商下拉自动填模型名和地址、Key 密码框“不改就留空”、保存、测试连接）；重置演示状态
- `style.css`：蓝白企业风；`:root` 变量；卡片、tile、pill、表格（th 不换行、`td button{white-space:nowrap}`）；900px 以下侧栏抽屉化、网格降列；520px 以下单列；手机 390 宽不横向滚动

## 四、问助理（app/agent.py）

- PROVIDERS：offline、deepseek、qwen、kimi、hunyuan（OpenAI 兼容 /chat/completions）、claude（/v1/messages，`anthropic-version: 2023-06-01`）、ollama（本机，不外发）
- config.json：key、base_url、model、api_key；chmod 600；环境变量优先；`public_cfg()` 不回传 Key，只回 has_key
- SYSTEM：只用程序结果里的数字；不能下单/付款/发消息/提交/审批，也不能说已经办了；该谁拍板的只摆选项和代价；说明样例数据；先结论后依据（注明编号或文件名）
- `context_text(ctx)`：已做的决定、方案要点、问题清单、待办（编号、事项、截止、状态）、费用、扩展结果摘要；截断到 14k 字
- `check_answer(text, ctx_text)`：回答里的数字（去逗号，长度≥2）不在上下文里 → 提醒；出现 ACTION_WORDS（已下单、已支付、已付款、已发送、已提交、已改签、已预订、订好了、已审批、已批准……）→ 提醒
- 缓存：key = sha1(批次 | 规范化问题 | sha1(上下文))；在线成功写缓存；在线失败先回放缓存（标“离线回放（模型，时间）”+ 本次失败原因），再退到程序摘要
- `BOOK_RE = r"(帮我|给我|替我|直接).{0,6}订|订.{0,3}(票|酒店|机票|高铁)|下单|付款|支付|买票|订了"`（按场景改动词）：命中就由程序回答，从不在线、从不缓存
- 离线意图：为什么不推荐最便宜、两种口径差多少、单住/分住差多少、冲突怎么办、超标、截止、早报几点、变动怎么办、报销还差什么、推荐方案、帮助

## 五、测试（tests/test_demo.py）

```python
setUpClass: tempfile.mkdtemp → copytree(HERE, ignore=data,交付记录,__pycache__,tests) → 建空 data/
            Popen([sys.executable, "-u", app/server.py], env NO_BROWSER=1, PORT=空闲端口, 去掉 API Key 环境变量)
            读第一行 stdout 拿地址
tearDownClass: terminate → wait(5) → kill；rmtree
call(method, path, body, role, raw) / ok(...) 断言 200 / denied(...) 断言 403 且 denied=True
```

用例（按课堂脚本）：01 页面和 meta；02 主线全流程（每个关键数字、每种越权 403、口径不一致 400、下单只记录、两步审批、日历带 VALARM、早报、变动、报销）；02b 默认路径的另一组数字（如超标没批）；03 财务确认口径后重算；04 会改输入的拍板只改副本；05 Agent 拒绝下单、离线回答带正确数字；06 第二批次和越界读文件、只有指定身份能重置/改设置；07 重置后清空。

用 `uv python find 3.9` 找 3.9，两个版本各跑一次，输出写进 交付记录/。

## 六、浏览器回归（scripts/browser_regression.js）

Playwright + Chromium（环境里已装，不要再 install）。1440×900 按课堂脚本点一遍，每一步 `screenshot` 到 `交付记录/截图/NN_名称.png`；`expect(页面, 文字)` 断言关键金额、拦截提示、Agent 拒绝下单；切到第二批次再跑一次主程序；390×844 新上下文看 `document.documentElement.scrollWidth <= 390`；收集 console error（预期内的 403 写进说明）。结果写 `交付记录/浏览器回归结果.txt`。

**截图要逐张用眼看**。常见问题：选定的方案和已定口径不一致；动作完成后页面没刷新；表格按钮文字竖排；toast 挡住关键内容；意图没识别（“帮我把机票订了”没走拒绝分支）。修了重跑。

## 七、README_演示说明（八节，照 HR / 运维的写法）

```
# <场景> · 网页演示版 · 使用与演示说明
<日期> · 王涛
一段定位 + 4—5 条要点（数字全部由程序算；AI 只查、算、起草，不替人拍板；下单停在确认；<日历和提醒/证据和留痕>；大模型只负责解释和起草）
一句真假说明

## 一、怎么启动
1. 双击 启动.command（首次“仍要打开”）2. 地址和端口（被占用往后找，以终端显示为准）3. 关窗口即停
python3 缺失怎么办；和其他 Demo 端口不冲突；拿到新版先双击 运行测试.command 看到 OK
**N 种身份**表：身份 / 能做什么 / 不能做什么；被拦下会说明原因，被拦的操作不写日志

## 二、接入大模型（可选，建议提前一天配好）
步骤 1—5（选服务商、Key、测试连接、外发提醒、Key 存哪、程序核对）
**离线时怎么表现**：程序摘要；缓存回放；下单类从不发模型、从不回放

## 三、哪些是真的，哪些是模拟的（表）

## 四、演示数据里的情形
程序不读预埋标记。每批：规模和问题分布；逐条预埋问题（带具体数字和编号）；方案结果；正式产物数字；扩展步骤结果（表）；第二批

## 五、课堂演示脚本（约 40 分钟；标“选”的按时间取舍）
开场一句话
| 顺序 | 页面 | 演示什么 | 时间 |（工作台 → 各步骤 → 拍板被拦 → 选定 → 待办确认和两步审批 → 扩展 → 问助理 → 换批次（选）→ 收尾引出 WorkBuddy 版）
演示结束后重置
**建议在课上问助理的问题**（列表，含“帮我把XX办了”）

## 六、现场可能被问到的问题
能不能真的执行；日历/提醒怎么到手机；价格/数据准不准；为什么不让 AI 定口径；会不会编数；权限可靠吗（说实话）；数据会不会出去；和 WorkBuddy 版什么关系

## 七、演示前检查（清单）

## 八、文件说明（表）
```

HR 招聘那种复杂案例可以加节（问卷对应表、渠道接入、多人模式、复盘沉淀、材料来源、逐份核验结果、口径问题），运维那种可以加“两种模式”（演示/真实）、Agent 评测脚本、升级说明。

## 八、打包.sh

zip 到上一级目录，文件名带日期；排除 config.json、state.json、data/runs、__pycache__、.DS_Store、*.zip；问答缓存可以保留（方便断网回放）。
