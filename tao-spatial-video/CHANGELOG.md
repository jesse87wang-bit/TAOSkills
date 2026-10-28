# Changelog

## v1.4.5 · 2026-10-28

从 v1.0 到 v1.4.4 的更新此前只保存在本地，这次一并推送。

- 架构：一份分镜表 `storyboard.json` + 命令行 `make_video.py`（probe / framing / asr / align / validate / sprites / subs / preview / render / mix / assemble / verify / deliver / selftest），不再手写 seq.py / sprites.py
- 组件 24 种：列表、宫格、流程、循环、自绘 svg 图解、大字、结论、划掉、判断、章节标等；固定翻译规则保证不同 Agent 出片一致
- 默认保留平台安全区（safe_x 90），侧卡只按头肩主体让位，手势不影响卡片大小；片尾不加静帧
- `framing` 取景检查；`deliver` 按 delivery.json 命名交付；`mkdocs.py` 生成字幕和实录口播稿
- `selftest` 基准回归：合成器源码指纹、时间轴逐项、素材/字幕逐像素
- 字体主地址被屏蔽时自动改从 Noto 官方发布包下载（sha256 校验）
- `setup_device.sh`：Claude 桌面版 Linux 工作区分步安装（deps / models / check），支持离线安装包与离线模型
- 渲染脚本兼容「自媒体」单独连接和整个桌面连接两种路径
- 维护规则：工具包每次更新都推送到 GitHub 镜像；新增 `publish_github.sh`（自动排除音效、字体和运行产物，推送前核对）

## v1.0.0 · 2026-09-29

首个版本，来自第一条成片《WorkBuddy 还是豆包工作？》的完整制作流程。

- 真实背景 + 人物 RVM 抠像 + 3D 透视玻璃卡（卡片可在人物身后被遮挡）
- 合成器按人头位置自动缩小/外移侧边卡片，保证文字不被遮挡
- iPhone HLG / 杜比视界原片的 HDR→SDR 色调映射（zscale + hable）
- 4K60 分段渲染（单段 ≤450 帧，适配单次命令 180 秒限制），逐段核对帧数
- 语音识别 + 校对字幕逐字对齐，关键词卡点
- 玻璃卡组件库：列表卡、大字卡、章节标、结论条、判断行、标签、盖章、电脑屏幕、评分面板
- 6 类剪映音效的使用规则与混音（-16 LUFS）
