---
name: tao-spatial-video
description: 把真人口播原片+文稿做成「真实背景里玻璃卡从人物身后浮出」的科技感4K60成片。用户给出原视频位置和口播稿、说做成片/包装口播/按上次效果出片时使用。
---

# tao-spatial-video｜口播原片 → 空间感玻璃卡 4K60 成片（v1.1）

**风格基准**：第一条成片《WorkBuddy 还是豆包工作》。它的完整分镜表在 `toolkit/golden/workbuddy/storyboard.json`，用本工具包能逐帧复现——新片子照它的写法做。

**工具包**：本目录下的 `toolkit/`，唯一入口 `make_video.py`。下文命令都在工具包目录里运行，写作 `python3 make_video.py <命令>`，分镜表用绝对路径。
分镜表格式看 `toolkit/STORYBOARD.md`；环境、分机器、一致性说明看 `toolkit/README.md`。
「自媒体」工作台里如果有本地副本 `自媒体/bin/spatial_video/`（带音效），优先用它。

> 你（Agent）只写两样东西：**校对字幕 `lines.txt`** 和 **分镜表 `storyboard.json`**。
> 坐标、动画、玻璃卡样式、音效、渲染参数都由工具包固定生成。不要自己写合成代码，不要改 `sv/` 里的文件——这是不同 Agent 出片一致的前提。

## 用户要的效果（已确认，别改）

- **人物始终居中是主体**，背景就是**真实房间**，不虚化、不调色、不加滤镜。原片像素不动，只改卡片所在区域。
- **玻璃拟态卡片从人物两侧、从身后浮出来**，带轻微 3D 透视，**内侧边缘被人的头和肩挡住**，墙上有淡淡投影。人和 UI 在同一个空间里，不是「视频上盖几张 PPT」。
- 发光大字、结论条压在胸前（前景）；顶部挂章节标（01/02/03…）。
- **每个元素卡着口播关键词弹出**，一层一层出现，配剪映音效。
- **输出 = 原片同规格**：2160×3840、60fps、H.264 High、CRF 15、bt709。
- **画面上不出现「评论区扣 xx」这类引导评论/私信的字样**（平台不允许）；字幕里口播说到「评论区」的，删掉这三个字（如「有需要的可以告诉我」）。

## 输入

原视频位置（一般在桌面 `自媒体/` 下，iPhone 竖拍 4K HDR .MOV）+ 口播稿（贴在对话里或 md 文件）。缺哪样问哪样，其余直接做；**不用先出样片**，但渲染前必须做静帧自检。

## 流程

### 0. 准备
1. 能访问 `~/Desktop/自媒体` 时：读 `CLAUDE.md` 和 `00-定位/账号宪法.md`，按会话协议跑 `python3 bin/status.py`、`python3 bin/log.py --show`。
2. 这台机器第一次用：`python3 make_video.py setup`（下载并校验字体、模型）→ `doctor` → `selftest --pixels`，全部 ✓ 再开始。音效按 `toolkit/sfx/README.md` 放好。
3. `python3 make_video.py probe <原片>`：把输出的 `source` 字段抄进分镜表。不是 2160×3840 的素材先跟用户说。
4. 项目文件夹 `30-口播稿/<选题ID或加更-短标题>/`：分镜表、字幕放它下面的 `_工作文件/`；分镜表里写 `"output": "../成片_<短标题>_4K60.mp4"`，成片就落在项目文件夹。

### 1. 听写与对齐
1. `python3 make_video.py asr <原片> <_工作文件>/asr.json`
2. 对照识别结果和口播稿写 `lines.txt`：**以录音为准**，一行一句 ≤16 字，产品名写对（识别常把 WorkBuddy 听成「五合八」「克巴里」），删掉「评论区」。
3. `python3 make_video.py align asr.json lines.txt lines.json`（同时生成 `lines_chars.json`，关键词卡点靠它）。
4. 另存一份 `字幕.srt` 和实录版 `口播稿.md` 到项目文件夹。

### 2. 写分镜表（最花心思的一步）
复制 `golden/workbuddy/storyboard.json` 改。套路：
- 按口播结构分章：开场钩子 → 第一/二/三点 → 收尾。每章开头一个 `badge`（slot `TOP`），整章常驻、章末 out；章节切换处加 `streaks`（y=330）。
- 讲 A → 左卡（slot `L`，color A）；讲 B → 右卡（slot `R`，color B）。**颜色和左右全片固定**。
- 列举 → `list_panel` + `set.wipe` 逐行亮起，`ticks` 对准口播里说到每一项的时刻（用关键词）。
- 小结论 → 胸前 `verdict` / `judge`；金句 → `glow_text`（「不是 X」用 `dim_text` + `strike` 划掉）；重音加 `boosts` + 一个 `ding3`。
- `at` 用关键词 `{"kw": "…"}` 卡在说到那个词的瞬间；一段话讲完就 `out`。同屏**最多**：左卡 + 右卡 + 胸前 1–3 行 + 章节标。
- 片尾：`laptop`（示意界面，标「示意」）+ `rating_panel`（空星，不写假分数），`hold` 1.5 秒。
- 格式细节、组件清单、默认音效见 `STORYBOARD.md`。

### 3. 素材与校验
1. `validate <分镜表>` → 改到 0 错误。
2. `sprites <分镜表>` → 再 `validate`（第二次带上文字溢出检查；溢出就调小 tsize/bsize/size 或缩短文字，重跑 sprites）。
3. `subs <分镜表>`（字幕太宽会提示拆行）；`plan <分镜表>` 看一遍卡点和音效表。

### 4. 静帧自检（渲染前必做）
`grab <分镜表> 秒 秒 …` 从原片抽 4K 静帧，`preview <分镜表> 秒 秒 …` 出预览（每章 1–2 个时刻，10–15 张）。逐张看：字有没有被头挡、卡片有没有溢出、胸前字和字幕打不打架、左右是否平衡。改分镜表 → 重跑 sprites/preview，满意再渲染。

### 5. 渲染、混音、交付
- 单机、命令没有时长限制：`all <分镜表>`（字幕 → 分段渲染 → 混音 → 拼接 → 核对，可断点续跑）。
- 命令有时长限制（如单次 180 秒）：`render <分镜表> --list` 看分段；每次命令只跑一段 `timeout 176 python3 make_video.py render <分镜表> --range 起 止`，逐段看 `frames=… expected=…`；全部完成后 `mix` → `assemble` → `verify`。
- `verify` 全 ✓ 后，抽 1 秒一帧缩略图（`ffmpeg -i 成片 -vf fps=1,scale=180:320,tile=12x5 总览.jpg`）从头看到尾：卡片不缺、不被挡、字幕对。
- 用 `python3 bin/log.py 剪辑 <ID> 0 "..."` 记日志。

## 内容检查（每条都做）
- 账号宪法：屏幕文字不用「老板/高管/管理者」称呼观众；不虚构数据和案例（validate 会拦红线词，事实要你自己查）。
- 事实类说法（产品支持什么、整合了什么）上屏前查官方来源；会变的加「截至 X 年 X 月 · 以官方为准」，引用写「来源：xx 官方」。示意画面标「示意」。
- 口播里提到的 CTA 物料（如「评测打分表」）在 `40-素材库/物料/` 里不存在时，交付时提醒用户：物料没做出来前不能发，并主动提出帮做。

## 踩过的坑
- iPhone 原片是 HLG/杜比视界：`source.hdr` 必须是 true（probe 会判断），否则画面发灰、人物过曝。
- 两个 4K 渲染并行会把 4GB 内存吃满（BrokenPipe / moov atom not found）：一次只跑一段。
- 分段边界不同，抠像预热不同，会有肉眼看不出的差别；要复现旧片就用分镜表里的 `render.chunks`。
- 连接电脑的文件夹不能直接删文件，临时文件都放 `_工作文件/`，最后提醒用户清理。

## 收尾回复
一句话说成片在哪；列出 verify 结果（分辨率/帧率/帧数/时长/码率）；说明和原片唯一的区别是 SDR（原片 HDR）；提醒 CTA 物料和 `_工作文件` 清理；给一个下一步。

---

## 附：Claude（云端容器 + 用户电脑）怎么分工

原片在用户电脑上（device_bash 可访问；单次命令 ≤180 秒，后台进程活不过一次调用），云端容器有 Chromium。原片（几百 MB）**不要往云端传**。

| 在哪 | 跑什么 |
|---|---|
| 用户电脑（device_bash） | setup --models、probe、asr、align、grab、render --range、mix、assemble、verify |
| 云端容器 | setup --fonts、validate、sprites、subs、plan、preview、selftest --pixels |

- 电脑上用本地副本 `~/mnt/自媒体/bin/spatial_video/`；容器里用 skill 目录的 `toolkit/`（两边版本要相同）。分镜表和字幕是小文本，两边各放一份（电脑上放项目 `_工作文件/`，`source.path` 写 `~/mnt/自媒体/…`）。
- 电脑上设 `SV_BUILD=$HOME/work/build_<短标题>`，分段视频写到虚拟机本地盘，不写进用户的桌面文件夹；成片由 `output` 写回项目文件夹。模型默认在 `~/work/sv`（`setup --models` 下载）。
- 容器里做好的 `build/sp3/`、`build/sub4k/` 打包传到电脑的 `$SV_BUILD/`（device_commit_files 单文件 ≤20MB，超了 `split -b 18m` 分片，传完核对 md5）。
- 静帧：电脑上 `grab` 抽到 `$SV_BUILD/stills/`，传到容器的 `build/stills/`，再在容器里 `preview`。
- 渲染：每次 device_bash 只跑一段 `timeout 176 … render --range`，不要用 `all`；某段超时就把那段拆小（改 `render.chunks`）重跑。
