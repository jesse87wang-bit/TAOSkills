# -*- coding: utf-8 -*-
"""差旅助手 Agent：离线按程序结果回答；接了大模型时由模型组织语言，程序核对数字和说法；在线回答自动缓存，断网可回放。

大模型只负责解释和起草：不算数、不下单、不审批。所有数字以程序结果为准。
"""
import hashlib
import json
import os
import re
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_FILE = os.path.join(ROOT, "config.json")
CACHE_FILE = os.path.join(ROOT, "data", "agent_cache.json")

PROVIDERS = {
    "offline": dict(provider="offline", base_url="", model="", label="离线（程序摘要 / 回放）"),
    "deepseek": dict(provider="openai", base_url="https://api.deepseek.com", model="deepseek-chat", label="DeepSeek"),
    "qwen": dict(provider="openai", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1", model="qwen-plus", label="通义千问"),
    "kimi": dict(provider="openai", base_url="https://api.moonshot.cn/v1", model="moonshot-v1-32k", label="Kimi"),
    "hunyuan": dict(provider="openai", base_url="https://api.hunyuan.cloud.tencent.com/v1", model="hunyuan-turbos-latest", label="腾讯混元"),
    "claude": dict(provider="anthropic", base_url="https://api.anthropic.com", model="claude-sonnet-5-5", label="Claude"),
    "ollama": dict(provider="openai", base_url="http://127.0.0.1:11434/v1", model="qwen2.5:7b", label="本机 Ollama（不外发）"),
}

SYSTEM = """你是企业的差旅助理，在一个培训演示系统里回答问题。规则：
1. 所有金额、时间、条数只能用“程序结果”里出现过的数字，不能自己计算或估计；程序结果里没有的写“程序结果里没有”。
2. 你不能下单、付款、发消息、提交申请、审批或改日历，也不能说这些事“已经办了”。需要办的，告诉用户在系统哪个页面、由哪个身份确认。
3. 第七条航班时段口径、合住还是分住、日程冲突怎么处理，由本人或财务决定；你只把选项和代价说清楚。
4. 数据是样例数据（虚构），回答里提到时说明。
5. 用中文，简短，先给结论，再给依据（注明问题编号或文件名）。"""


# ---------------------------------------------------------------- 配置
def load_cfg():
    cfg = {"key": "offline"}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    base = dict(PROVIDERS.get(cfg.get("key"), PROVIDERS["offline"]))
    for k in ("base_url", "model"):
        if cfg.get(k):
            base[k] = cfg[k]
    base["key"] = cfg.get("key", "offline")
    base["api_key"] = os.environ.get("TRAVEL_API_KEY") or cfg.get("api_key", "")
    return base


def save_cfg(body):
    cur = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, encoding="utf-8") as f:
                cur = json.load(f)
        except Exception:
            cur = {}
    key = body.get("key", "offline")
    if key not in PROVIDERS:
        raise ValueError("不认识的服务商：%s" % key)
    cur["key"] = key
    for k in ("base_url", "model"):
        cur[k] = (body.get(k) or "").strip()
    if body.get("api_key"):
        cur["api_key"] = body["api_key"].strip()
    if body.get("clear_key"):
        cur.pop("api_key", None)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cur, f, ensure_ascii=False, indent=1)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass
    return public_cfg()


def public_cfg():
    c = load_cfg()
    return {"key": c["key"], "label": c["label"], "model": c["model"], "base_url": c["base_url"],
            "has_key": bool(c["api_key"]), "online": c["provider"] != "offline" and (bool(c["api_key"]) or c["key"] == "ollama"),
            "providers": [{"key": k, "label": v["label"], "model": v["model"], "base_url": v["base_url"]} for k, v in PROVIDERS.items()]}


# ---------------------------------------------------------------- 调模型
def _post(url, headers, body, timeout=60):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=dict({"Content-Type": "application/json"}, **headers), method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def call_llm(cfg, system, user):
    if cfg["provider"] == "anthropic":
        url = cfg["base_url"].rstrip("/") + "/v1/messages"
        out = _post(url, {"x-api-key": cfg["api_key"], "anthropic-version": "2023-06-01"},
                    {"model": cfg["model"], "max_tokens": 1200, "system": system,
                     "messages": [{"role": "user", "content": user}]})
        return "".join(b.get("text", "") for b in out.get("content", []) if b.get("type") == "text")
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    headers = {"Authorization": "Bearer %s" % cfg["api_key"]} if cfg.get("api_key") else {}
    out = _post(url, headers, {"model": cfg["model"], "temperature": 0.2,
                               "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]})
    return out["choices"][0]["message"]["content"]


def test_connection():
    cfg = load_cfg()
    if cfg["provider"] == "offline":
        return {"ok": True, "text": "当前是离线模式：Agent 只用程序结果回答。"}
    if not cfg["api_key"] and cfg["key"] != "ollama":
        return {"ok": False, "text": "还没有填 API Key"}
    t0 = time.time()
    try:
        txt = call_llm(cfg, "你是测试助手。", "只回复四个字：连接成功")
        return {"ok": True, "text": "在线·%s：%s（%d 毫秒）" % (cfg["model"], txt.strip()[:40], (time.time() - t0) * 1000)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "text": "连接失败：%s。检查 Key、模型名和网络；模型名以服务商控制台为准" % str(e)[:200]}


# ---------------------------------------------------------------- 程序核对
ACTION_WORDS = ["已下单", "已经下单", "已支付", "已付款", "已发送", "已经发送", "已提交", "已改签", "已预订", "已经订好", "订好了", "已审批", "已批准"]


def check_answer(text, context_text):
    notes = []
    ctx_nums = set(n.replace(",", "") for n in re.findall(r"\d[\d,]*(?:\.\d+)?", context_text))
    bad = []
    for n in re.findall(r"\d[\d,]*(?:\.\d+)?", text):
        k = n.replace(",", "")
        if k not in ctx_nums and len(k) >= 2 and k not in bad:
            bad.append(k)
    if bad:
        notes.append("以下数字在程序结果里找不到，请以页面为准：%s" % "、".join(bad[:8]))
    hit = [w for w in ACTION_WORDS if w in text]
    if hit:
        notes.append("回答里出现“%s”：本系统不会下单、发送、提交或审批，这类说法不成立" % "、".join(hit))
    return notes


# ---------------------------------------------------------------- 缓存
def _load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_cache(c):
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=1)


def _norm(q):
    return re.sub(r"[\s，。？！?,.!、]", "", q)


# ---------------------------------------------------------------- 离线回答
def yuan(x):
    return "【待补】" if x is None else "{:,.0f} 元".format(x)


def legs_text(p):
    s = "；".join("%s %s %s" % (x["段"], x["方式"], x["班次"]) for x in p["交通"])
    if p["住宿"]:
        s += "；住 %s（%s）" % ("、".join(h["酒店"] for h in p["住宿"]), p["住法"])
    return s


def rec_plans(res, st):
    named = res["方案"]
    mode = st.get("mode_confirmed") or st.get("decisions", {}).get("口径")
    if "推荐" in named:
        return [("推荐", named["推荐"])]
    if mode and ("推荐" + mode) in named:
        return [("推荐（口径%s）" % mode, named["推荐" + mode])]
    return [("推荐（口径%s）" % k[-1], v) for k, v in named.items() if k in ("推荐A", "推荐B")]


def decide_item(res, name):
    for x in res.get("必须先拍板", []):
        if x["事项"] == name:
            return x
    return None


INTENTS = [
    ("book", ["订票", "下单", "帮我订", "订酒店", "订机票", "付款", "支付", "买票"]),
    ("cheap", ["最便宜", "最省钱", "便宜"]),
    ("mode", ["口径", "第七条", "时段"]),
    ("rooms", ["单住", "分住", "合住", "住一间"]),
    ("conflict", ["评审会", "冲突", "线上参", "开会", "预算会"]),
    ("over", ["超标", "一等座", "公务舱"]),
    ("brief", ["早报", "提醒", "几点出门", "几点出发", "明天"]),
    ("delay", ["延误", "改签", "航班变", "晚点"]),
    ("expense", ["报销", "发票", "能不能报"]),
    ("deadline", ["申请", "截止", "加急", "报备"]),
    ("cost", ["多少钱", "费用", "预算", "伙食", "补助"]),
    ("issues", ["问题", "风险", "硬伤"]),
    ("recommend", ["推荐", "怎么安排", "方案", "坐什么", "住哪"]),
]


BOOK_RE = re.compile(r"(帮我|给我|替我|直接).{0,6}订|订.{0,3}(票|酒店|机票|高铁)|下单|付款|支付|买票|订了")


def intent_of(q):
    if BOOK_RE.search(q):
        return "book"
    for name, kws in INTENTS:
        if any(k in q for k in kws):
            return name
    return "help"


def offline_answer(q, ctx):
    res, pkg, st = ctx.get("res"), ctx.get("pkg"), ctx.get("state", {})
    it = intent_of(q)
    src = []
    if it == "book":
        lines = ["我不能直接下单，也不会替您付款。"]
        if pkg:
            todos = [t for t in ctx.get("todos", []) if t["事项"].startswith("订")]
            pend = [t for t in todos if t["状态"] != "完成"]
            lines.append("这次要订的有 %d 件，还没确认的 %d 件：%s。" % (len(todos), len(pend), "；".join(t["事项"] for t in pend) or "无"))
            lines.append("请切换到“出行人”身份，在“行程包 → 待办与确认”里逐件点“确认”。确认时会把要订什么、多少钱、要提供谁的哪些个人信息列出来。演示系统没有连接订票平台，不会真的产生订单；正式使用时付款由本人在订票平台完成。")
            src = ["行程包/待办清单.json"]
        else:
            lines.append("还没有选定方案。先在“方案对比”里由出行人选定方案，生成行程包后，再逐件确认下单。")
        return "\n".join(lines), src
    if not res:
        return ("这趟出差还没出方案。请先到“出差需求”页点“出方案”，程序算完我再回答。"
                "我能回答：为什么不推荐最便宜的、两种口径差多少、单住要多花多少、评审会怎么办、帮我订票、早报几点发、航班延误怎么办、报销还差什么。"), []
    src = ["方案结果.json"]
    if it == "cheap":
        out = []
        for name, p in rec_plans(res, st):
            cheap = res["方案"]["最省钱"]
            out.append("%s：%s，合计 %s。" % (name, legs_text(p), yuan(p["费用"]["合计"])))
            for r in res["推荐理由"].get(name.replace("（口径", "").replace("）", "") if "口径" in name else name, []):
                if r.startswith("比最省钱方案"):
                    out.append(r)
        cheap = res["方案"]["最省钱"]
        out.append("最省钱方案：%s，合计 %s。" % (legs_text(cheap), yuan(cheap["费用"]["合计"])))
        out.append("排序规则：先排除赶不上、日程冲突、缺价格的组合，再比要审批的问题数、提醒数，最后比综合成本。")
        return "\n".join(out), src
    if it == "mode":
        x = decide_item(res, "第七条口径")
        if st.get("mode_confirmed"):
            return "财务已确认按口径%s执行，方案已按这个口径重算。" % st["mode_confirmed"], src
        if x:
            return "%s。%s。%s。" % (x["说明"], x["细节"], x["建议"]), src
        return "第七条口径已确认，方案只按一种口径计算。", src
    if it == "rooms":
        x = decide_item(res, "合住还是分住")
        if x:
            return "%s。%s。%s。" % (x["说明"], x["细节"], x["建议"]), src
        return "这趟只有一位出行人，按单住标准计算，不涉及合住或分住。", src
    if it == "conflict":
        x = decide_item(res, "日程冲突")
        if x:
            ch = st.get("decisions", {}).get("冲突")
            return "%s。%s。%s。%s" % (x["说明"], x["细节"], x["建议"], ("出行人已选择：%s。" % ch) if ch else ""), src
        mids = [i for i in res["问题清单"] if i["规则"] == "R06"]
        if mids:
            return "推荐方案没有线下日程冲突。和线上会议相关的提醒：" + "；".join("%s %s" % (i["编号"], i["问题"]) for i in mids[:4]) + "。", src
        return "没有发现日程冲突。", src
    if it == "over":
        rows = [i for i in res["问题清单"] if i["规则"].startswith("R01") or i["规则"].startswith("R02")]
        if not rows:
            return "所有候选都在差标内。", src
        return "超标的情况：\n" + "\n".join("- %s %s（%s）。建议：%s" % (i["编号"], i["问题"], i["证据"], i["建议"]) for i in rows), src
    if it == "deadline":
        r = res["出差申请"]
        if r["加急"]:
            return "出差申请已过期限：%s 出发，最晚 %s 提交，需求是 %s 才提出的，须部门负责人同意后加急提交（%s）。" % (
                r["出发日"], r["最晚提交"], r["需求日期"], r["依据"]), src
        return "最晚 %s 在 OA 提交出差申请（%s：出发前 3 个工作日）。" % (r["最晚提交"], r["依据"]), src
    if it == "issues":
        c = {"高": 0, "中": 0, "低": 0}
        for i in res["问题清单"]:
            c[i["级别"]] += 1
        hi = [i for i in res["问题清单"] if i["级别"] == "高"]
        return ("一共 %d 条问题：高 %d、中 %d、低 %d。不解决就不能订的（高）：\n" % (len(res["问题清单"]), c["高"], c["中"], c["低"]) +
                "\n".join("- %s %s：%s" % (i["编号"], i["问题"], i["证据"]) for i in hi)), src
    if it == "brief":
        if not pkg:
            return "选定方案、生成行程包之后，系统会排好提醒计划：出发前一天 21:00 发明日提醒，当天早报取 07:30 和出门前 40 分钟里较早的。", src
        rows = pkg.get("提醒计划", [])
        return "提醒计划（%d 条）：\n" % len(rows) + "\n".join("- %s %s：%s" % (r["时间"].replace("T", " "), r["方式"], r["内容"]) for r in rows[:8]), ["行程包/行程.json"]
    if it == "delay":
        if ctx.get("change_md"):
            first = [l for l in ctx["change_md"].split("\n") if l.startswith("**")]
            return "延误处理结果：%s。可选办法见“航班变动”页；改签、退票、发消息都要出行人确认。" % (first[0].strip("*") if first else ""), ["航班变动处理.md"]
        return "到“航班变动”页点“算影响”：程序会算新的到场时间、还剩多少缓冲，列出还来得及的替代班次和消息草稿。", src
    if it == "expense":
        ex = ctx.get("expense")
        if ex:
            return ex["summary"] + "\n有问题的票据：\n" + "\n".join("- %s %s %s：%s" % (r["编号"], r["人"], r["结论"], r["原因"]) for r in ex["rows"] if r["结论"] != "可报"), ["报销清单.csv"]
        return "出差回来后到“报销检查”页点“检查发票”，程序逐张核对行程一致、差标、日期、抬头、招待报备和缺票。", src
    if it == "cost":
        if pkg:
            f = pkg["费用预估"]
            return "费用预估：交通 %s + 住宿 %s + 伙食补助 %s = %s（不含市内交通和招待）。" % (
                yuan(f["交通"]), yuan(f["住宿"]), yuan(f["伙食补助"]), yuan(f["合计"])), ["行程包/行程.json"]
        out = ["%s：交通 %s + 住宿 %s = %s；伙食补助另计 %s。" % (n, yuan(p["费用"]["交通"]), yuan(p["费用"]["住宿"]), yuan(p["费用"]["合计"]),
                                                    yuan(p["伙食补助"]["合计"])) for n, p in rec_plans(res, st)]
        return "\n".join(out), src
    if it == "recommend":
        out = []
        for n, p in rec_plans(res, st):
            out.append("%s：%s，合计 %s，在途 %d 分钟。" % (n, legs_text(p), yuan(p["费用"]["合计"]), p["在途分钟"]))
        out.append("必须先拍板的事：" + "；".join("%s（%s）" % (x["事项"], x["说明"]) for x in res["必须先拍板"]))
        return "\n".join(out), src
    return ("我能回答这些：为什么不推荐最便宜的？两种口径差多少？林总想单住要多花多少？评审会怎么办？哪些超标？"
            "申请什么时候交？帮我订票。早报几点发？航班延误怎么办？报销还差什么？"), []


# ---------------------------------------------------------------- 入口
def context_text(ctx):
    res, pkg = ctx.get("res"), ctx.get("pkg")
    keep = {"行程": ctx.get("label")}
    st = ctx.get("state") or {}
    if st:
        keep["已做的决定"] = {"决定": st.get("decisions", {}), "财务确认的口径": st.get("mode_confirmed"), "选定": st.get("chosen")}
    if res:
        keep["必须先拍板"] = res["必须先拍板"]
        keep["方案"] = dict((k, {"组合": v["id"], "交通": [(x["段"], x["班次"], x["出发"], x["到达"], x["出门"], x["到场"], x["票价合计"]) for x in v["交通"]],
                                 "住宿": [(h["酒店"], h["住法"], h["合计"]) for h in v["住宿"]], "费用": v["费用"], "在途分钟": v["在途分钟"],
                                 "问题": v["问题"]}) for k, v in res["方案"].items())
        keep["问题清单"] = [(i["编号"], i["级别"], i["对象"], i["问题"], i["证据"]) for i in res["问题清单"]]
        keep["出差申请"] = res["出差申请"]
    if pkg:
        keep["费用预估"] = pkg["费用预估"]
        keep["待办"] = [(t["编号"], t["事项"], t["截止"], t["状态"]) for t in ctx.get("todos", [])]
        keep["提醒计划"] = pkg.get("提醒计划")
    if ctx.get("change_md"):
        keep["航班变动处理"] = ctx["change_md"][:2500]
    if ctx.get("expense"):
        keep["报销检查"] = ctx["expense"]["summary"]
    return json.dumps(keep, ensure_ascii=False)[:14000]


def answer(question, ctx):
    q = (question or "").strip()
    if not q:
        return {"text": "请输入问题。", "mode": "离线", "sources": [], "notes": []}
    cfg = load_cfg()
    ctext = context_text(ctx)
    key = hashlib.sha1(("%s|%s|%s" % (ctx.get("trip"), _norm(q), hashlib.sha1(ctext.encode("utf-8")).hexdigest())).encode("utf-8")).hexdigest()
    online = cfg["provider"] != "offline" and (cfg["api_key"] or cfg["key"] == "ollama")
    if online and intent_of(q) != "book":
        try:
            text = call_llm(cfg, SYSTEM, "程序结果（JSON）：\n%s\n\n问题：%s" % (ctext, q))
            notes = check_answer(text, ctext)
            cache = _load_cache()
            cache[key] = {"question": q, "text": text, "notes": notes, "model": cfg["model"], "time": time.strftime("%Y-%m-%d %H:%M")}
            _save_cache(cache)
            return {"text": text, "mode": "在线·%s" % cfg["label"], "sources": ["程序结果"], "notes": notes}
        except Exception as e:  # noqa: BLE001
            cache = _load_cache()
            if key in cache:
                c = cache[key]
                return {"text": c["text"], "mode": "离线回放（%s，%s）" % (c["model"], c["time"]), "sources": ["缓存"], "notes": c.get("notes", []) + ["本次在线调用失败：%s" % str(e)[:80]]}
            text, src = offline_answer(q, ctx)
            return {"text": text, "mode": "离线·程序摘要", "sources": src, "notes": ["在线调用失败，已改用程序摘要：%s" % str(e)[:80]]}
    cache = _load_cache()
    if key in cache and intent_of(q) != "book":
        c = cache[key]
        return {"text": c["text"], "mode": "离线回放（%s，%s）" % (c["model"], c["time"]), "sources": ["缓存"], "notes": c.get("notes", [])}
    text, src = offline_answer(q, ctx)
    return {"text": text, "mode": "离线·程序摘要", "sources": src, "notes": []}
