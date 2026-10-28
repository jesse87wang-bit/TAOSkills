# 生成 storyboard.json：《AI 时代护城河》—— v1.4 样式（留安全区 90、片尾不定格）
# 取景偏近：左侧约 0.71 倍、右侧约 0.56 倍（人偏右）→ 列表/宫格/图解放左，右侧放大字卡和「五类资产」进度表。
# 左 = A 青蓝（细节 / 怎么做），右 = B 紫靛（结论），全片固定。
exec(open('helpers.py').read())
exec(open('sbhelp.py').read())

def detour_svg():
    """技术：对手未必复制你的技术，也可能借助 AI 换一条路满足同一个需求"""
    return (f'<defs>{MK("ma", "{A2}")}{MK("mb", "{B2}")}</defs>'
            '<circle cx="338" cy="170" r="54" fill="{B1}" fill-opacity="0.16" stroke="{B2}" stroke-width="3"/>'
            '<circle cx="338" cy="170" r="30" fill="{B2}" fill-opacity="0.9"/>'
            '<text x="338" y="179" font-size="24" text-anchor="middle" fill="#fff">需求</text>'
            '<text x="338" y="256" font-size="22" text-anchor="middle" class="thin">客户需求</text>'
            '<rect x="0" y="34" width="168" height="60" rx="18" fill="{A2}"/>'
            '<text x="84" y="73" font-size="26" text-anchor="middle" fill="#fff">你的技术</text>'
            '<path d="M174 64 C240 64 270 90 292 128" stroke="{A2}" stroke-width="5" fill="none" stroke-linecap="round" marker-end="url(#ma)"/>'
            '<text x="84" y="124" font-size="21" text-anchor="middle" class="thin">专利仍有保护</text>'
            '<rect x="0" y="236" width="168" height="60" rx="18" fill="#fff" fill-opacity="0.9" stroke="{B2}" stroke-width="2.5"/>'
            '<text x="84" y="275" font-size="26" text-anchor="middle" fill="{B3}">对手 + AI</text>'
            '<path d="M174 266 C240 266 270 246 292 212" stroke="{B2}" stroke-width="5" stroke-dasharray="10 9" fill="none" stroke-linecap="round" marker-end="url(#mb)"/>'
            '<text x="0" y="326" font-size="21" class="thin">不复制，换一种办法</text>')

def scale_svg():
    """规模：用 AI 的小团队 ≈ 不用 AI 的大组织"""
    s = ['<rect x="0" y="20" width="176" height="176" rx="22" fill="#fff" fill-opacity="0.7" stroke="{A2}" stroke-width="2.5"/>']
    for k, x in enumerate([44, 88, 132]):
        s.append(f'<circle cx="{x}" cy="78" r="18" fill="{{A2}}"/>')
    s.append('<rect x="48" y="118" width="80" height="48" rx="14" fill="{B2}"/>'
             '<text x="88" y="151" font-size="26" text-anchor="middle" fill="#fff" class="en">AI</text>'
             '<text x="202" y="124" font-size="52" text-anchor="middle" fill="{B3}">≈</text>'
             '<rect x="228" y="20" width="176" height="176" rx="22" fill="#fff" fill-opacity="0.7" stroke="{SUB}" stroke-width="2"/>')
    for r in range(3):
        for c in range(4):
            s.append(f'<circle cx="{256 + c*40}" cy="{58 + r*50}" r="13" fill="{{SUB}}" fill-opacity="0.55"/>')
    s.append('<text x="88" y="232" font-size="23" text-anchor="middle">用 AI 的小团队</text>'
             '<text x="316" y="232" font-size="23" text-anchor="middle">不用 AI 的大组织</text>'
             '<rect x="52" y="270" width="300" height="56" rx="28" fill="{A2}"/>'
             '<text x="202" y="307" font-size="26" text-anchor="middle" fill="#fff">效能可能拉平</text>')
    return ''.join(s)

def cycle_svg():
    """五类资产连成持续改进的循环：知识→方法→流程→标准→数据→知识"""
    import math
    cx, cy, r = 202, 158, 118
    nodes = [("知识", "理解问题"), ("方法", "处理问题"), ("流程", "反复执行"), ("标准", "检验结果"), ("数据", "复盘改进")]
    pts = [(cx + r*math.cos(math.radians(-90 + 72*k)), cy + r*math.sin(math.radians(-90 + 72*k))) for k in range(5)]
    s = [f'<defs>{MK("mc", "{A2}")}</defs>']
    for k in range(5):
        a0 = math.radians(-90 + 72*k + 20); a1 = math.radians(-90 + 72*(k+1) - 20)
        x0, y0 = cx + r*math.cos(a0), cy + r*math.sin(a0); x1, y1 = cx + r*math.cos(a1), cy + r*math.sin(a1)
        s.append(f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{{A2}}" stroke-width="5" fill="none" stroke-linecap="round" marker-end="url(#mc)"/>')
    s.append(f'<circle cx="{cx}" cy="{cy}" r="44" fill="{{B2}}"/>'
             f'<text x="{cx}" y="{cy - 4}" font-size="22" text-anchor="middle" fill="#fff">持续</text>'
             f'<text x="{cx}" y="{cy + 22}" font-size="22" text-anchor="middle" fill="#fff">改进</text>')
    for k, ((x, y), (n, v)) in enumerate(zip(pts, nodes)):
        s.append(f'<rect x="{x - 44:.1f}" y="{y - 22:.1f}" width="88" height="44" rx="22" fill="#fff" stroke="{{A2}}" stroke-width="2.5"/>'
                 f'<text x="{x:.1f}" y="{y + 9:.1f}" font-size="25" text-anchor="middle" fill="{{A3}}">{n}</text>')
        ty = y + 44 if k in (2, 3) else (y - 30 if k == 0 else y + 46)
        tx = x if k in (0, 2, 3) else (x - 6 if k == 1 else x + 6)
        if k == 0: tx, ty = x + 104, y + 8
        s.append(f'<text x="{tx:.1f}" y="{ty:.1f}" font-size="20" text-anchor="middle" class="thin">{v}</text>')
    return ''.join(s)

# ---------------- 开场 ----------------
GLOW("T_HOOK", 0.21, 2.90, "AI 时代，企业真正的护城河是什么？", 60, sfx={"name": "ding3", "gain": 0.8})
GRID("L_OLD", "L", 3.40, 18.40, "A", "过去的壁垒", "我们常说的",
     [["award", "品牌", "BRAND"], ["cpu", "技术", "TECH"], ["users", "规模", "SCALE"], ["lock", "难换掉", "LOCK-IN"]],
     [4.11, 4.65, 5.19, 6.60], glyph="shield")
BIG("R_WALL", "R", 8.70, 13.30, "B", "过去常说的", "竞争壁垒", "品牌、技术、规模")
GLOW("T_CATCH", 13.43, 15.81, "当 AI 让对手更容易追上来", 62)
BIG("R_HOLD", "R", 15.83, 19.90, "B", "你原来的优势", "还能守多久", "得重新问一句", bsize=72)

# ---------------- 01 品牌 ----------------
BADGE("B01", 20.37, 51.20, "01", "品牌")
BIG("R_NAME", "R", 21.39, 28.10, "B", "品牌的一部分优势", "熟悉的名字", "客户没精力反复比较", bsize=76)
LIST("L_CMP", "L", 28.22, 43.40, "A", "spark", "AI 帮客户比较", "按具体需求筛选",
     [["card", "比较产品"], ["coin", "比较价格"], ["chat", "比较评价"], ["funnel", "按需求筛选"]], [30.62, 31.10, 31.52, 33.70], tsize=44)
GLOW("T_MEAN", 34.36, 35.80, "这意味着什么？", 88)
BIG("R_FIRST", "R", 36.12, 43.40, "B", "广告多、名字响", "未必首选", "客户越来越依赖 AI 决策")
BIG("L_TRUST", "L", 43.51, 51.20, "A", "品牌信任", "仍然重要", "靠真实产品和体验支撑")
STRIKE("FAME", "只靠知名度", 45.55, 46.40, 47.09, size=88, s=0.8)
GLOW("T_REAL", 47.11, 51.20, "不靠真实产品和体验支撑，更难守住", 54)

# ---------------- 02 技术 ----------------
BADGE("B02", 51.32, 82.60, "02", "技术")
BIG("R_LEAD", "R", 53.17, 59.00, "B", "过去别人做不出来", "保持领先", "做不出、开发不起", bsize=82)
LIST("L_ENG", "L", 59.00, 68.20, "A", "cpu", "AI 进入开发", "工程开发、技术门槛降低",
     [["doc", "帮助生成代码"], ["flow", "减少重复工作"], ["chart", "获取门槛降低"]], [61.82, 63.26, 66.14])
BIG("R_DOWN", "R", 64.88, 68.20, "B", "部分技术能力", "门槛降低", "获取门槛正在降低")
SVG("L_DETOUR", "L", 68.28, 82.60, "A", "换一条路", "对手未必复制你的技术", detour_svg(), glyph="switch",
    rv=[(130, 68.46), (330, 74.74)], ticks=[68.46, 74.74, 76.72])
BIG("R_PATENT", "R", 70.14, 78.40, "B", "要警惕的是", "另一种办法", "借助 AI 更快探索", bsize=76)
GLOW("T_NEED", 79.99, 82.60, "守住技术 ≠ 守住客户需求", 64, sfx={"name": "ding3", "gain": 0.6})

# ---------------- 03 规模 ----------------
BADGE("B03", 82.78, 109.90, "03", "规模")
BIG("R_BIG", "R", 84.12, 89.10, "B", "过去团队大", "分工齐全", "能做小公司做不了的事")
SVG("L_SMALL", "L", 89.21, 103.80, "A", "效能拉平", "AI 时代的小团队", scale_svg(), glyph="users",
    rv=[(240, 90.89), (330, 93.23)], ticks=[90.89, 92.63, 93.23])
BIG("R_STILL", "R", 94.07, 97.50, "B", "工厂、供应链", "规模优势", "并没有消失", bsize=82)
BIG("R_GAIN", "R", 97.59, 103.80, "B", "靠人多形成的能力", "小团队也能有", "部分能力", bsize=64)
STRIKE("HEADS", "只看有多少人", 103.90, 105.04, 105.68, size=84, s=0.8)
BIG("L_COST", "L", 105.70, 109.90, "A", "同样的业务结果", "谁成本更低", "你和对手比一比", bsize=78)

# ---------------- 04 客户黏性 ----------------
BADGE("B04", 110.07, 136.60, "04", "客户黏性")
BIG("R_STAY", "R", 112.21, 116.20, "B", "客户不换你", "不只因为好", "不只是最好、关系最硬", bsize=76)
for eid, t, g, txt in [("C_SYS", 116.64, "db", "系统难迁"), ("C_DATA", 117.42, "doc", "数据难搬"), ("C_HARD", 118.38, "warn", "换家麻烦")]:
    add(id=eid, type="chip", slot="F", row="three", at=t, out=119.80, props={"glyph": g, "text": txt, "color": "A"})
LIST("L_MIG", "L", 119.84, 127.90, "A", "spark", "AI 辅助迁移", "降低更换系统的成本",
     [["book", "理解旧系统"], ["doc", "转换代码"], ["flow", "规划迁移"]], [121.67, 122.33, 123.19])
BIG("R_SWITCH", "R", 125.27, 127.90, "B", "更换系统的成本", "可能降低", "一部分")
LIST("L_WHY", "L", 127.96, 136.60, "A", "target", "为什么留下", "客户留下，要分清楚",
     [["award", "你越来越有价值"], ["lock", "暂时换不掉你"]], [130.90, 132.40])
BIG("R_WEAK", "R", 133.50, 136.60, "B", "暂时换不掉", "会被削弱", "后面那种壁垒")

# ---------------- 05 同一个问题 ----------------
BADGE("B05", 136.78, 162.80, "05", "同一个问题")
GLOW("T_SAME", 137.32, 140.20, "几种冲击背后，是同一个问题", 60, sfx={"name": "ding3", "gain": 0.6})
BIG("L_CATCH", "L", 140.34, 148.30, "A", "对手追赶你的", "成本下降了", "这几种冲击背后", bsize=82)
BIG("R_GAP", "R", 142.62, 146.70, "B", "你靠什么", "拉开距离", "继续领先")
STRIKE("TOOLS", "买更多的 AI 工具", 144.85, 146.76, 147.56, size=80, s=0.8)
BIG("R_BUY", "R", 146.76, 148.30, "B", "AI 工具", "对手也能买", "拉不开距离", bsize=72)
JUDGE("J_MINE", 148.36, 151.80, "B", "我的判断", "把独有积累变成能力")
FLOW("L_TURN", "L", 149.02, 162.80, "A", "steps", "变成能力", "企业必须做的事",
     [["db", "独有积累", "你真正独有的"], ["spark", "AI 参与使用", "让 AI 用得上"], ["users", "组织持续改进", "整个组织一起"]],
     [150.64, 152.70, 154.38])
BIG("R_COMP", "R", 156.38, 162.80, "B", "独有的积累", "互补资产", "数据、经验、组织能力", bsize=82)

# ---------------- 06 五类资产 ----------------
BADGE("B06", 162.94, 222.20, "06", "五类资产")
add(id="R_FIVE", type="list_panel", slot="R", at=162.94, out=222.20, ticks=[164.02, 175.56, 188.33, 200.24, 210.25],   # 「有五类」时整张目录一起出
    props={"color": "B", "glyph": "grid", "title": "五类资产", "sub": "新的护城河",
           "rows": [["book", "知识 Knowledge"], ["steps", "方法 Skill"], ["flow", "流程 Workflow"], ["check", "标准 Eval"], ["db", "数据 Data"]]})
LIST("L_KNOW", "L", 163.60, 174.70, "A", "book", "知识", "Knowledge · 业务认知",
     [["cpu", "工艺约束"], ["users", "客户需求"], ["warn", "故障经验"], ["doc", "失败教训"]], [165.75, 166.57, 167.35, 168.19])
STRIKE("PILE", "资料的堆砌", 169.59, 170.73, 171.31, size=88, s=0.8)
GLOW("T_KNOW", 171.33, 174.70, "真实经营中积累的业务认知", 62)
LIST("L_SKILL", "L", 174.84, 187.60, "A", "steps", "方法", "Skill · 可重复使用",
     [["chart", "怎么调参数"], ["users", "怎么选供应商"], ["target", "怎么判断需求"], ["warn", "怎么处理异常"]], [176.82, 178.02, 179.21, 180.17])
GLOW("T_SKILL", 181.33, 184.60, "经过验证的方法，沉淀下来", 62)
STRIKE("REDO", "每次都从头摸索", 185.08, 186.40, 186.82, size=80, s=0.8)
LIST("L_FLOW", "L", 187.79, 199.40, "A", "flow", "流程", "Workflow · 进入业务",
     [["coin", "采购"], ["cpu", "生产"], ["chart", "销售"], ["check", "交付"]], [190.85, 191.63, 192.05, 192.53])
for eid, t, g, txt in [("C_AI", 194.23, "spark", "AI 做"), ("C_HUMAN", 195.85, "users", "人判断")]:
    add(id=eid, type="chip", slot="F", row="three", at=t, out=196.60, props={"glyph": g, "text": txt, "color": "A"})
GLOW("T_FLOW", 196.63, 199.40, "能力不只停留在某个高手身上", 58)
LIST("L_EVAL", "L", 199.58, 209.40, "A", "check", "标准", "Eval · 做得对不对",
     [["check", "什么叫合格"], ["warn", "什么必须返工"], ["shield", "什么交给人审核"]], [201.86, 202.85, 204.86])
GLOW("T_EVAL", 205.91, 209.40, "不只要快，还要对", 84, sfx={"name": "ding3", "gain": 0.5})
LIST("L_DATA", "L", 209.53, 222.20, "A", "db", "数据", "Data · 留下真实结果",
     [["chart", "哪次调参提高良率"], ["coin", "哪种产品带来复购"], ["warn", "哪次交付出了问题"]], [212.68, 214.18, 215.54])
GLOW("T_DATA", 217.33, 222.20, "检验和更新前面的知识、方法与流程", 52)

# ---------------- 07 改进循环 ----------------
BADGE("B07", 222.36, 246.80, "07", "改进循环")
GLOW("T_WHY", 222.36, 226.10, "为什么能形成新的护城河？", 62)
SVG("L_CYCLE", "L", 226.26, 246.80, "A", "改进循环", "五类资产连起来", cycle_svg(), glyph="flow",
    ticks=[229.93, 232.57, 234.63, 236.37, 238.75])
BIG("R_LOOP", "R", 228.54, 239.80, "B", "连成一个", "持续改进", "的循环")
BIG("R_DEAL", "R", 239.90, 246.80, "B", "做完一笔生意", "不只赚钱", "还留下做得更好的能力")

# ---------------- 08 回头再看 ----------------
BADGE("B08", 246.98, 274.20, "08", "回头再看")
LIST("L_BACK", "L", 248.24, 265.40, "A", "switch", "四种优势", "再回头看背后",
     [["award", "品牌：产品和体验"], ["cpu", "技术：研发能力"], ["users", "规模：运营效率"], ["lock", "黏性：理解和服务"]],
     [249.72, 253.30, 257.36, 261.95])
BIG("R_BACK", "R", 249.72, 265.40, "B", "背后都是", "持续积累", "越来越稳、越来越深")
STRIKE("DROP", "扔掉原来的护城河", 265.50, 266.76, 268.17, size=76, s=0.8)
BIG("L_RENEW", "L", 268.63, 274.20, "A", "用五类资产", "不断更新", "让原来的优势一直更新")
BIG("R_RENEW", "R", 268.63, 274.20, "B", "别坐等", "被追平", "原来的优势")
GLOW("T_RENEW", 270.01, 272.20, "让原来的优势不断更新", 66, sfx={"name": "ding3", "gain": 0.6})

# ---------------- 09 持续领先 ----------------
BADGE("B09", 274.30, None, "09", "持续领先")
BIG("R_SAME", "R", 274.30, 281.20, "B", "别人可以买到", "一样的 AI", "工具拉不开距离", bsize=82)
BIG("L_COPY", "L", 276.34, None, "A", "未必能复制", "经营能力", "真实验证、不断改进")
GLOW("T_MOAT", 281.31, 284.30, "真正值得建设的护城河", 70)
STRIKE("LEAD", "我今天领先你多少", 284.37, 285.93, 286.33, size=76, s=0.8)
BIG("R_MECH", "R", 286.35, None, "B", "真正的护城河", "一套机制", "让自己持续领先")
GLOW("T_END", 286.35, None, "有没有一套机制，让自己持续领先", 56, sfx={"name": "ding3", "gain": 0.9})

N_SRC = 17380
SB = {
    "schema": "tao-spatial-video/storyboard@1.1",
    "title": "AI 时代护城河",
    "deliver_name": "AI 时代护城河",
    "source": {"path": "../../待包装视频/AI 时代护城河.mp4", "hdr": True, "n_src": N_SRC},
    "safe_x": 90,
    "lines": "lines.json",
    "palette": {"A": ["#06B6D4", "#3B82F6", "#0369A1"], "B": ["#A855F7", "#6366F1", "#5B21B6"]},
    "names": {"A": "细节 / 怎么做", "B": "结论"},
    "rows": {"three": {"y": 1195, "s": 0.9, "gap": 14}, "four": {"y": 1195, "s": 0.84, "gap": 12}},
    "elements": E,
    "boosts": [[0.23, 0.9], [9.84, 0.8], [13.45, 0.9], [17.21, 0.8], [26.74, 0.8], [34.40, 0.9], [42.30, 0.8], [46.40, 0.9],
               [58.18, 0.8], [66.92, 0.8], [76.24, 0.8], [80.01, 1.0], [93.23, 0.9], [96.59, 0.8], [105.04, 0.9], [108.88, 0.8],
               [119.22, 0.8], [125.57, 0.8], [135.06, 0.9], [138.76, 0.9], [143.70, 0.8], [146.76, 0.9], [148.54, 0.9],
               [161.85, 0.8], [163.06, 1.0], [170.73, 0.9], [183.85, 0.8], [186.40, 0.9], [198.37, 0.8], [205.93, 1.0],
               [219.55, 0.8], [224.94, 0.9], [228.54, 0.9], [245.57, 0.8], [266.76, 0.9], [271.70, 0.9], [273.32, 0.8],
               [278.08, 0.8], [283.33, 0.9], [285.93, 0.9], [287.31, 1.1]],
    "sfx": [[0.19, "ding3", 0, 0.5], [80.0, "ding3", 0, 0.5], [137.30, "ding3", 0, 0.6], [162.92, "ding3", 0, 0.6],
            [222.34, "ding3", 0, 0.5], [286.33, "ding3", 0, 0.7]],
    "streaks": [[0.19, 1195, 0.45], [20.35, 330, 0.45], [51.30, 330, 0.45], [82.76, 330, 0.45], [110.05, 330, 0.45],
                [136.76, 330, 0.45], [162.92, 330, 0.45], [222.34, 330, 0.45], [246.96, 330, 0.45], [274.28, 330, 0.45],
                [286.33, 1195, 0.45]],
    "render": {"chunks": list(range(0, N_SRC, 220)) + [N_SRC]},
}
json.dump(SB, open('storyboard.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(E), 'elements')
