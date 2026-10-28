---
name: "tao-spatial-video"
description: "把真人口播原片+文稿做成「真实背景里玻璃卡从人物身后浮出」的科技感4K60成片。用户给出原视频位置和口播稿、说做成片/包装口播/按上次效果出片时使用。"
---

# tao-spatial-video｜口播原片 → 空间感玻璃卡 4K60 成片（工具包 v1.4.5）

风格基准（第一条成品）：`自媒体/30-口播稿/加更-WorkBuddy还是豆包工作/成片_WorkBuddy还是豆包工作_4K60.mp4`
工具包：`自媒体/bin/spatial_video/`。**先读 `README.md` 和 `STORYBOARD.md`**，所有步骤都走 `make_video.py`，从一份分镜表 `storyboard.json` 出发；不要再手写 seq.py / sprites.py（那是 v1.0 的做法，备份在 `_v1.0/`）。

## 用户要的效果（已确认，别改）

- **人物始终是主体**，背景是**真实房间**，不虚化、不调色、不加滤镜。原片像素只在卡片区域被改动。
- **玻璃拟态卡片从人物两侧、从身后浮出来**，带轻微 3D 透视，内侧边缘被头和肩挡住，墙上有淡淡投影——人和 UI 在同一个空间里，不是「视频上盖 PPT」。
- 发光大字、结论条、划掉动画压在胸前；顶部挂章节标（01/02/03…）。每个元素卡着口播关键词弹出，配剪映音效（规则固定在工具包里）。
- **输出 = 原片同规格**：2160×3840、60fps、H.264 High、CRF 15、bt709、AAC 320k。帧数必须 = 原片帧数 `n_src`。
- **保留平台安全区**（2026-10-02 定）：默认 `safe_x: 90`。**信息不能因为安全区打折**——侧边照样放完整的列表卡、循环图、宫格、流程图、自绘图解（`svg_panel`），不能因为卡片变小就把列表挪到胸前小标签。
- **片尾不加静帧**：`hold` 为 0，原片结束成片就结束。交付前用 `freezedetect` 查片尾 3 秒，必须是 0 处。
- **侧卡让位只量头和肩，手势不算**（v1.4.2，2026-10-04 用户原话「这条不要改，要保持住，写进规则」）：抬到脸旁的手不能把侧卡压小、不能让卡片跟着手势忽大忽小。实现在 `sv/comp4k.py` 的 `update_head_core`，`safe_x>0` 时自动启用；**任何时候都不要改回旧算法**。
- 画面上**不出现**「评论区 / 私信 / 扣 xx」这类引导字样；字幕里口播说到「评论区」的，把这三个字删掉。

## 交付规则

**Jesse（本账号用户）固定这样交付，不用再问**（2026-10-04 定）：
- 成片命名 `Final` + 原文件名（不含扩展名，**空格照用户写法保留**），例：`AI 原生组织.mp4` → `FinalAI 原生组织.mp4`
- 放进 `桌面/自媒体/成品/<完成日期MMDD> <原文件名>/`，**每条一个文件夹**，成片只放这一处，例：`成品/1004 AI 原生组织/FinalAI 原生组织.mp4`（日期按北京时间）
- 规则已写在 `bin/spatial_video/delivery.json`，分镜表写 `"deliver_name": "<用户叫这条视频的名字>"`，做完执行 `make_video.py deliver storyboard.json --src <拼好的成片>`，然后删掉 `~/work/jobN/final.mp4`。
- 用户说的文件名和实际文件名不一致（比如说「中国没有几个 FDE」，文件是 `中国没有几个真正FDE.mp4`）时，按实际文件名交付，并在消息里说一句。
- 用户之前明确同意把成片放进 `成品/` 的新子文件夹；`成品/` 里已有的东西不动。

**新用户第一次用（没有 `delivery.json`）**：`deliver` 会停下来。先问用户「成片放哪个文件夹、文件夹和文件怎么命名」，按 README「交付规则」写进 `delivery.json`（`root` / `folder` / `file` / `tz`，可用 `{name}` `{MMDD}` `{YYYY}` `{MM}` `{DD}` `{title}` `{ext}`），再交付。

## 工具包维护：每次更新都推送到 GitHub

**用户 2026-10-28 定：工具包有任何改动，都自动推送到 GitHub，不用再问。**
- 真源是电脑上的 `自媒体/bin/spatial_video/`；GitHub 镜像是 `jesse87wang-bit/TAOSkills` 的 `tao-spatial-video/`（main 分支）。
- 改动后先更新版本号和记录：`README.md` 首行、本文件标题、`manifest.json`、`CHANGELOG.md`（写清改了什么、为什么）。
- 推送（在云端做）：`add_repo`（push 权限）→ 克隆仓库 → `bash publish_github.sh <工具包目录> <仓库目录> "<提交说明>"`。脚本只拷代码和文档，自动排除 `sfx/*.wav`（剪映音效需自有授权，不能公开）、字体、`build/`、`_v1.*`、`_patch_v1.4`、`_离线模型/`、`__pycache__`、`fonts/.fontconfig/`，并在推送前核对没有音效和字体进入提交。
- 只推工具包本身；成片、原片、口播稿、项目文件不进仓库。推完在回复里说一句推送了哪个版本。
- 新会话克隆工具包也优先从 GitHub 拉（几秒）；音效 `sfx/*.wav` 仍从电脑取。

## 输入

用户给：原视频位置（一般在 `桌面/自媒体/待包装视频/`，iPhone 竖拍 4K HDR）+ 口播稿（贴在对话里）。缺哪样问哪样，其余直接做，不用先出样片，但渲染前必须做静帧预览自检。用户常说「视频稍后移进文件夹」——先做不需要原片的部分，移进来后按队列继续。原稿存到项目文件夹 `原稿.md`。

## 环境分工

| 在哪 | 做什么 |
|---|---|
| 用户电脑（device_bash，每次 ≤180 秒） | 原片在这：probe / framing / asr / align / grab 静帧 / mix / 分段 render / 拼接 / deliver |
| 云端容器（Playwright + Chromium） | 写分镜表、sprites 玻璃卡、subs 字幕贴图、preview 静帧预览（RVM 模型放 `/root/work/sv/rvm.onnx`） |

### 环境准备（v1.4.5，每次开工先做，装好的会自动跳过）

**路径**：「自媒体」文件夹单独连接时电脑上是 `~/mnt/自媒体/`，连接整个桌面时是 `~/mnt/Desktop/自媒体/`。下文的 `自媒体/…` 按实际挂载位置换算；`_next_chunk.sh`、`_finish.sh` 两种都认。

**云端容器**（每个新会话都是全新的）：
1. 从电脑取工具包：`device_stage_files` 拿 `自媒体/bin/spatial_video/` 下的代码、`sfx/`、`golden/`、`fonts/Poppins-*.ttf`（不用拿 4 个中文字体，太大），放到 `/root/work/toolkit/`。
2. `cd /root/work/toolkit && python3 make_video.py setup`：字体主地址被屏蔽时会自动改从 Noto 官方发布包（github.com releases）取，模型从 GitHub releases 下载，全部按 sha256 校验。
3. `python3 make_video.py doctor`：云端只要求 opencv / onnxruntime / pillow / playwright、字体、`rvm.onnx`、音效全 ✓；sherpa-onnx / soundfile 缺失不影响（语音识别在电脑上做）。不要重装 Playwright，用容器预装的版本。
4. 可选 `selftest --pixels`：Chromium 版本和基准不同时，部分玻璃卡有几级灰度的抗锯齿差异，字幕应 69/69 一致；这是 README 说明过的正常情况。

**用户电脑**（Claude 桌面版的 Linux 工作区，换账号或重装后要重新装一次）：
`cd ~/mnt/<桌面或自媒体>/…/bin/spatial_video` 后依次 `bash setup_device.sh deps` → `bash setup_device.sh models`（没下完就再跑）→ `bash setup_device.sh check`。doctor 里除 playwright/Chromium（电脑端不需要）外全 ✓ 才开始做片。
device_bash 报「Workspace still downloading / failed to start」时，Linux 工作区还没起来：请用户退出并重新打开 Claude 桌面版，等几分钟再试；渲染步骤都离不开它，不要把原片传到云端绕过。

原片不往云端传。容器 → 电脑：`tar czf b.tgz sp3 sub4k` → `split -b 18m` → `device_commit_files` 到项目 `_工作文件/` → 电脑上 `cat` 合并、核对 md5、解压到 `~/work/jobN/`（`SV_BUILD=~/work/jobN`，分段视频很大，不写进同步盘）。电脑 → 容器：静帧打 tar 后 `device_stage_files`。

## 流程

0. **准备**：读 `CLAUDE.md`、`00-定位/账号宪法.md`；项目文件夹 `30-口播稿/加更-<短标题>/`，中间文件放 `_工作文件/`。多条视频时维护 `30-口播稿/_出片队列.md`（顺序、jobN、取景结论、状态、交付路径），中断后从这里恢复。
1. **probe + framing**：`make_video.py probe <原片>` → 分镜表 `source`（`n_src`）；`make_video.py framing <原片>`：✓ ≥0.68 正常做；⚠ 0.55–0.68 照常用图解卡，列表 ≤4 行、每行 ≤8 字，**信息卡放空间大的一侧**；✗ <0.55 先问用户（不留安全区，还是留安全区只放大字卡）。
2. **听写对齐**：`make_video.py asr <原片> asr.json` → 对照口播稿写 `lines.txt`（**按录音实际念的字**，一行 ≤16 字、≤15 个汉字宽；改正识别错字和同音词，去掉「啊」「诶」等语气词）→ `make_video.py align asr.json lines.txt lines.json`（同时出 `lines_chars.json`，用来查关键词时刻）。
3. **写分镜表**：把 `bin/spatial_video/authoring/` 里的 `helpers.py`、`sbhelp.py`、`kw.py` 复制到容器工作目录，照 `authoring/example_make_sb.py`（「AI 时代护城河」完整示例）写 `make_sb.py` 生成 `storyboard.json`（LIST / GRID / FLOW / LOOP / SVG / BIG / GLOW / STRIKE / JUDGE / BADGE / chip；关键词时刻用 `python3 kw.py 词1 词2 @秒` 查）。`make_sb.py` 存一份到项目 `_工作文件/`。`render.chunks` = `list(range(0, n_src, 220)) + [n_src]`。`make_video.py validate` 0 个错误。
4. **素材**：`sprites` → 看 `build/sp3/overflow.json`，有溢出就缩短标题或调 `tsize`/`bsize` 后 `sprites --only <id>` 重渲 → 用 PNG 高度÷3 重写 `heights.json` → 重跑 `make_sb.py`（逐行揭开的时间依赖高度）→ `subs`。拼一张所有侧卡的总览图，逐张看文字有没有换行、贴边。
5. **静帧预览（渲染前必做）**：电脑上 `SV_BUILD=~/work/jobN make_video.py grab storyboard.json 秒…`（每个元素出现后约 1.8 秒取一张，相隔 ≥3 秒，三四十张），打 tar 传到容器，`make_video.py preview storyboard.json 秒…` 每 6 张一张图，全部看完：字被不被头挡、卡片溢不溢出、胸前字和字幕打不打架、逐行揭开是否对上口播。改完把改动的素材和分镜表再传一次（小改动单独打 `upd.tgz`）。
6. **混音**：电脑上 `SV_BUILD=~/work/jobN make_video.py mix storyboard.json`（几秒）。
7. **分段渲染**：`bash 30-口播稿/_next2.sh <项目文件夹> <jobN>`——渲下一个未完成的 220 帧分段，第一段不到 95 秒就接着渲第二段；完成的段写 `~/work/jobN/chunks/.ok_<起始帧>`，断了重跑同一条命令就续上，输出 `ALL DONE` 为止。**同一时间只渲一条片子。**
8. **拼接核对**：`bash 30-口播稿/_finish.sh <项目文件夹> <jobN>`：逐段数帧 → concat + `audio.wav`（AAC 320k、faststart）→ 核对帧数 = `n_src`、规格 → 片尾 freezedetect → `_工作文件/qa_N.jpg`（1 秒一帧总览图）。把总览图拿到容器从头看到尾。
9. **交付**：`make_video.py deliver storyboard.json --src ~/work/jobN/final.mp4` → 删掉 `final.mp4`。
10. **文档和日志**：`python3 bin/spatial_video/mkdocs.py <项目文件夹> meta.json` 生成 `字幕.srt` 和实录版 `口播稿.md`（frontmatter：id、title、column、biz_tier、状态、cta、成片、分镜表；cta 按录音写，实录里没有「关注我」就写「无」）→ `python3 bin/export.py <口播稿.md>` → `python3 bin/log.py 剪辑 <ID> 0 "..."` → 更新出片队列 → 给用户发一条消息（交付路径、时长、帧数、片尾无静帧、做过哪些取舍）。

多条排队时：当前这条在电脑上渲染的间隙，在容器里做下一条的分镜表、素材、字幕和预览。
用户要求「额度用完、重置后自动恢复」：队列长时用 send_later 定几次「读出片队列和 .ok_ 标记、从断点继续」的提醒，全部交付后把没触发的提醒删掉。

## 设计规则

- 按口播结构分章：开场钩子 → 各章（顶部章节标整章常驻）→ 收尾。
- **左 = A 色（青蓝，细节 / 怎么做），右 = B 色（紫靛，结论）**，全片固定。人偏一侧时，列表、宫格、图解放空间大的一侧，另一侧放大字卡。
- 列举 → `list_panel`（逐行亮起对准口播说到的词）；3–6 个并列概念 → `grid_panel`；步骤 → `flow_panel`；4 步循环 → `loop_panel`；其他图解（对比、路径、5 节点循环、维恩图等）→ `svg_panel` 自己画；结论 → `big_card`；金句 → `glow_text`；否定 → `dim_text` + `strike`；判断 → `judge`。
- 「有五类 / 有四个标准」这种先报总数、后面逐条展开的，可以放一张整章常驻的目录卡（整张一起出），另一侧逐条放细节卡。
- 同屏最多：左卡 + 右卡 + 胸前 1–2 行 + 顶部章节标；一段话讲完就让卡片退场。最后一章的卡可以留到片尾（`out: null`）。
- 章节标 `num` 只用数字或拉丁字母（中文发虚）；序号别和口播里的「第一关 / 第一类」打架（开场后先有一章时写「02 技术关」，不写「02 第一关 · 技术」）。
- chip 每个 ≤4 个字（长了整排一起缩小）；`list_panel` 标题 52px 时 ≤5 个汉字（长了调 `tsize`）；`big_card` 大字 4 个字最佳（长了调 `bsize`），名字和小字各一行别换行。
- `svg_panel`：颜色只用 `{A1}{A2}{A3}{B1}{B2}{B3}{INK}{SUB}`，字号 ≥20，只能 `url(#id)` 引用；`.en` 英文字体、`.thin` 细灰字；文字离卡片边 8px 以内会被判溢出。
- 字幕里成对的引号「」别拆在两行（拆了就去掉引号）。

## 内容检查（每条都做）

- 账号宪法：屏幕文字**不用「老板 / 高管 / 管理者」称呼观众**。口播里作为第三人称角色出现的（「老板说……」），在分镜表 `role_terms` 里写明理由，校验降为提醒。
- 不虚构数据和案例；举例的数字标「举个例子 / 示意」。事实类说法上屏前查官方来源。
- 不登录、不发布、不回复任何平台账号。
- 不改 `成品/`（已有内容）、`模板/`、`定位与规划/`；改了 md 后用 `bin/export.py` 导出 Office 格式。

## 踩过的坑

- iPhone 原片是 HLG / 杜比视界：必须走工具包里的色调映射（zscale linear npl=100 → hable → bt709），否则画面发灰、人物过曝。
- 电脑上的后台进程活不过一次 device_bash，只能分段；4K HEVC 原片 280 帧一段偶尔超过 150 秒，所以用 220 帧。两个 4K 渲染并行会吃满内存，只能单进程。
- 电脑睡眠 / 断开：已完成的段有 `.ok_` 标记，重跑 `_next2.sh` 续上；「server draining」之类的报错往往命令其实已经跑完，先看标记再决定。
- 连接的文件夹不能直接删文件：临时文件都放 `_工作文件/`，最后提醒用户清理；要删时用 device_request_delete_permission。
- `device_commit_files` 单文件 ≤20MB，超了先 `split -b 18m`；传完核对 md5。
- Python 3.11 的 f-string 花括号里不能有反斜杠（写 SVG 时把 `class="en"` 放进变量）。
- `verdict` 组件会自动加「先看」，不想要就用 `judge`。两个章节标的出入场时间不要重叠。
- 最后一句字幕的结束时间不能超过原片时长（align 后检查，超了截到片尾）。
- 原片是可变帧率，统一 `fps=60`，帧号 = 秒 × 60。

## 收尾回复

一句话说成片放在哪；核对结果（分辨率 / 帧率 / 帧数 = 原片 / 时长 / 片尾无静帧）；预览时做过的取舍；提醒清理 `_工作文件/`（分片包、静帧、总览图）和 `~/work/jobN`；给一个下一步。
