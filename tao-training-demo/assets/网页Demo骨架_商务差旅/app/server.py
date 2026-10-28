#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商务差旅助手（网页演示版）本地服务。

双击 启动.command 运行；只监听本机 127.0.0.1，默认端口 8768（被占用就往后找）。
只用 Python 标准库，Python 3.9 及以上。

计算全部交给 工具/ 里的五个程序（和 WorkBuddy 版用的是同一套），本服务只负责：
保存每趟出差的进度和决定、按身份检查权限、把程序结果交给网页、Agent 问答、操作日志。
"""
import csv
import json
import mimetypes
import os
import shutil
import subprocess
import sys
import threading
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "app"))
sys.path.insert(0, os.path.join(ROOT, "工具"))
import agent  # noqa: E402
import store  # noqa: E402
import travel_common as tc  # noqa: E402

WEB = os.path.join(ROOT, "web")
PORT = int(os.environ.get("TRAVEL_DEMO_PORT", "8768"))
DATA_LABEL = "样例数据 · 演示模式（公司、人物、航班、酒店、价格全部虚构）"
DOC_WHITELIST = {
    "规则卡": "规则/01_差旅规则卡.md",
    "提醒规则": "规则/02_提醒规则.md",
    "报销规则": "规则/03_报销检查规则.md",
    "差旅标准": "规则/差旅标准.json",
    "差旅管理办法": "输入/公司资料/差旅管理办法_示例.md",
    "偏好档案": "输入/公司资料/偏好档案.json",
    "输入格式": "工具/需求格式说明.md",
    "演示说明": "README_演示说明.md",
}


class Denied(Exception):
    pass


class ToolError(Exception):
    pass


# ---------------------------------------------------------------- 路径与运行程序
def rdir(trip, *parts):
    return os.path.join(store.RUNS, trip, *parts)


def rel(p):
    return os.path.relpath(p, ROOT)


def ensure_input(trip):
    """每趟出差在 data/runs/<trip>/输入/ 下用一份输入副本，原始输入不动。"""
    t = store.TRIPS[trip]
    dst = rdir(trip, "输入", t["dir"])
    if not os.path.isdir(dst):
        os.makedirs(rdir(trip, "输入"), exist_ok=True)
        shutil.copytree(os.path.join(ROOT, "输入", t["dir"]), dst)
        shutil.copytree(os.path.join(ROOT, "输入", "公司资料"), rdir(trip, "输入", "公司资料"))
    return dst


def run_tool(script, args):
    cmd = [sys.executable, os.path.join(ROOT, "工具", script)] + args
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    if r.returncode != 0:
        raise ToolError((r.stderr or r.stdout).strip()[-1200:])
    return r.stdout


def fresh(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    return path


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def plan_path(trip):
    return rdir(trip, "方案", "方案结果.json")


def pkg_dir(trip):
    return rdir(trip, "行程包")


# ---------------------------------------------------------------- 权限
ROLE_LABEL = dict((k, v["label"]) for k, v in store.ROLES.items())


def need(role, allowed, what, why):
    if role not in allowed:
        raise Denied("当前身份是“%s”。%s要由%s来做：%s。请在右上角切换身份。" % (
            ROLE_LABEL.get(role, role), what, "或".join("“%s”" % ROLE_LABEL[a] for a in allowed), why))


def todo_owner(t):
    s = t["事项"]
    if s.startswith("超标处理") or s.startswith("在出差申请里写明分住"):
        return "manager"
    if s.startswith("向财务确认"):
        return "finance"
    return "traveler"


# ---------------------------------------------------------------- 业务动作
def do_plan(trip, st, role):
    inp = ensure_input(trip)
    out = fresh(rdir(trip, "方案"))
    args = ["--trip", rel(inp), "--output", rel(out)]
    if st["mode_confirmed"]:
        args += ["--mode", st["mode_confirmed"]]
    log = run_tool("方案计算.py", args)
    st["plan_ready"] = True
    if st["stage"] == "需求":
        st["stage"] = "已出方案"
    return log


def apply_seat_fix(trip):
    """出行人选择“改订标准席别”：把需求里超出本人标准的指定席别去掉，重新计算。"""
    inp = ensure_input(trip)
    req_p = os.path.join(inp, "需求.json")
    req = load_json(req_p)
    std = load_json(os.path.join(ROOT, "规则", "差旅标准.json"))
    people = load_json(rdir(trip, "输入", "公司资料", "偏好档案.json"))["people"]
    changed = []
    for leg in req["legs"]:
        rs = leg.get("requested_seat") or {}
        for who, seat in list(rs.items()):
            allowed = std["policy"]["transport"][people[who]["level"]]["rail"]
            if seat not in allowed:
                rs.pop(who)
                changed.append("%s %s 改为%s" % (people[who]["name"], leg["id"], allowed[0]))
        if "requested_seat" in leg and not rs:
            leg.pop("requested_seat")
    tc.save_text(tc.compact_json(req), req_p)
    return changed


def trip_ctx(trip):
    s = store.load()
    st = s["trips"][trip]
    ctx = {"trip": trip, "label": store.TRIPS[trip]["label"], "state": st, "res": None, "pkg": None, "todos": []}
    if st["plan_ready"] and os.path.exists(plan_path(trip)):
        ctx["res"] = load_json(plan_path(trip))
    if st["package_ready"] and os.path.exists(os.path.join(pkg_dir(trip), "行程.json")):
        ctx["pkg"] = load_json(os.path.join(pkg_dir(trip), "行程.json"))
        ctx["todos"] = load_json(os.path.join(pkg_dir(trip), "待办清单.json"))["待办"]
    if st["change_ready"]:
        f = [x for x in os.listdir(rdir(trip, "航班变动")) if x.endswith(".md")]
        if f:
            ctx["change_md"] = read(rdir(trip, "航班变动", f[0]))
    if st["expense_ready"]:
        ctx["expense"] = expense_view(trip)
    return ctx


def expense_view(trip):
    d = rdir(trip, "报销检查")
    md = read(os.path.join(d, "报销检查.md"))
    rows = []
    with open(os.path.join(d, "报销清单.csv"), encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    summary = [l for l in md.split("\n") if l.startswith("**票据")]
    return {"md": md, "rows": rows, "summary": summary[0].strip("*") if summary else ""}


def trip_info(trip):
    t = store.TRIPS[trip]
    base = os.path.join(ROOT, "输入", t["dir"])
    st = store.load()["trips"][trip]
    inp = rdir(trip, "输入", t["dir"]) if os.path.isdir(rdir(trip, "输入", t["dir"])) else base
    req = load_json(os.path.join(inp, "需求.json"))
    cand = load_json(os.path.join(inp, "候选资源.json"))
    cal = load_json(os.path.join(inp, "日程.json")) if os.path.exists(os.path.join(inp, "日程.json")) else {"items": []}
    people = load_json(os.path.join(ROOT, "输入", "公司资料", "偏好档案.json"))["people"]
    return {"trip": t, "原话": read(os.path.join(base, "需求原话.txt")), "需求": req,
            "候选": dict((k, v) for k, v in cand.items() if k != "source"), "来源": cand.get("source", ""),
            "日程": cal.get("items", []), "出行人": dict((k, people[k]) for k in req["travelers"]), "state": st}


# ---------------------------------------------------------------- HTTP
class H(BaseHTTPRequestHandler):
    server_version = "TravelDemo/1.0"

    def log_message(self, fmt, *args):
        pass

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _bin(self, path, inline=False):
        name = os.path.basename(path)
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        if name.endswith(".md") or name.endswith(".txt") or name.endswith(".csv"):
            ctype += "; charset=utf-8"
        if name.endswith(".ics"):
            ctype = "text/calendar; charset=utf-8"
        with open(path, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Disposition", "%s; filename*=UTF-8''%s" % ("inline" if inline else "attachment", quote(name)))
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if not n:
            return {}
        return json.loads(self.rfile.read(n).decode("utf-8"))

    def _role(self):
        r = self.headers.get("X-Role", "assistant")
        return r if r in store.ROLES else "assistant"

    def do_GET(self):
        u = urlparse(self.path)
        p = unquote(u.path)
        q = dict((k, v[0]) for k, v in parse_qs(u.query).items())
        try:
            if p.startswith("/api/"):
                return self._get(p[5:], q)
            if p == "/":
                p = "/index.html"
            f = os.path.normpath(os.path.join(WEB, p.lstrip("/")))
            if not f.startswith(WEB) or not os.path.isfile(f):
                return self._json({"error": "没有这个页面"}, 404)
            return self._bin(f, inline=True)
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": str(e)}, 500)

    def do_POST(self):
        p = unquote(urlparse(self.path).path)
        try:
            body = self._body()
            with store.LOCK:
                return self._post(p[5:], body, self._role())
        except Denied as e:
            return self._json({"error": str(e), "denied": True}, 403)
        except ToolError as e:
            return self._json({"error": "程序运行出错：%s" % e}, 500)
        except ValueError as e:
            return self._json({"error": str(e)}, 400)
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            return self._json({"error": str(e)}, 500)

    # ---------------- GET
    def _get(self, api, q):
        if api == "meta":
            s = store.load()
            return self._json({"label": DATA_LABEL, "roles": store.ROLES, "trips": store.TRIPS,
                               "states": s["trips"], "model": agent.public_cfg()})
        if api == "audit":
            return self._json(store.load()["audit"])
        if api == "settings":
            return self._json(agent.public_cfg())
        if api == "doc":
            name = q.get("name", "")
            if name not in DOC_WHITELIST:
                return self._json({"error": "不能读取这个文件"}, 404)
            return self._json({"name": name, "path": DOC_WHITELIST[name], "text": read(os.path.join(ROOT, DOC_WHITELIST[name]))})
        parts = api.split("/")
        if parts[0] == "trip" and len(parts) >= 3 and parts[1] in store.TRIPS:
            trip, what = parts[1], parts[2]
            if what == "info":
                return self._json(trip_info(trip))
            ctx = trip_ctx(trip)
            if what == "plan":
                if not ctx["res"]:
                    return self._json({"error": "还没有出方案"}, 404)
                return self._json({"res": ctx["res"], "state": ctx["state"]})
            if what == "package":
                if not ctx["pkg"]:
                    return self._json({"error": "还没有选定方案"}, 404)
                d = pkg_dir(trip)
                todos = ctx["todos"]
                for t in todos:
                    t["谁来确认"] = ROLE_LABEL[todo_owner(t)]
                    t["谁来确认_key"] = todo_owner(t)
                    if t["事项"].startswith("提交 OA 出差申请") and t["状态"] == "已提交·待审批":
                        t["谁来确认"], t["谁来确认_key"] = ROLE_LABEL["manager"], "manager"
                return self._json({"pkg": ctx["pkg"], "todos": todos, "state": ctx["state"],
                                   "texts": dict((n, read(os.path.join(d, n))) for n in ("行程单.md", "待办与确认清单.md", "报备与通知草稿.md", "提醒计划.md"))})
            if what == "change":
                if not ctx.get("change_md"):
                    return self._json({"error": "还没有算航班变动"}, 404)
                return self._json({"md": ctx["change_md"], "state": ctx["state"], "notice": self._notice(trip)})
            if what == "expense":
                if not ctx.get("expense"):
                    return self._json({"error": "还没有检查发票"}, 404)
                return self._json(ctx["expense"])
            if what == "briefs":
                d = rdir(trip, "早报")
                out = []
                if os.path.isdir(d):
                    for day in sorted(os.listdir(d)):
                        fs = sorted(x for x in os.listdir(os.path.join(d, day)) if x.endswith(".md"))
                        if fs:
                            md = read(os.path.join(d, day, fs[0]))
                            sms = os.path.join(d, day, fs[0][:-3] + "_短信版.txt")
                            out.append({"date": day, "md": md, "sms": read(sms) if os.path.exists(sms) else ""})
                return self._json(out)
            if what == "notice":
                return self._json(self._notice(trip))
            if what == "file":
                kind, name = q.get("kind", ""), q.get("name", "")
                base = os.path.normpath(rdir(trip, kind))
                f = os.path.normpath(os.path.join(base, name))
                if not f.startswith(store.RUNS) or not f.startswith(base) or not os.path.isfile(f):
                    return self._json({"error": "没有这个文件"}, 404)
                return self._bin(f, inline=q.get("inline") == "1")
        return self._json({"error": "未知接口"}, 404)

    def _notice(self, trip):
        t = store.TRIPS[trip]
        if not t["change"]:
            return None
        return load_json(os.path.join(ROOT, "输入", t["dir"], t["change"]))

    # ---------------- POST
    def _post(self, api, body, role):
        s = store.load()
        if api == "reset":
            need(role, ["assistant"], "重置演示状态", "重置会清空所有人的操作，由助理统一做")
            store.reset()
            return self._json({"ok": True})
        if api == "settings":
            need(role, ["assistant"], "修改模型设置", "模型设置影响所有人")
            cfg = agent.save_cfg(body)
            store.log(s, role, "", "修改模型设置", cfg["label"])
            store.save(s)
            return self._json(cfg)
        if api == "settings/test":
            return self._json(agent.test_connection())
        if api == "agent":
            trip = body.get("trip", "sh")
            ctx = trip_ctx(trip)
            return self._json(agent.answer(body.get("question", ""), ctx))
        parts = api.split("/")
        if parts[0] != "trip" or len(parts) < 3 or parts[1] not in store.TRIPS:
            return self._json({"error": "未知接口"}, 404)
        trip, what = parts[1], parts[2]
        st = s["trips"][trip]
        t = store.TRIPS[trip]

        if what == "plan":
            out = do_plan(trip, st, role)
            store.log(s, role, trip, "出方案", "运行 工具/方案计算.py")
            store.save(s)
            return self._json({"ok": True, "log": out, "res": load_json(plan_path(trip)), "state": st})

        if what == "decide":
            key, val = body.get("key"), body.get("value")
            if key == "口径确认":
                need(role, ["finance"], "确认第七条口径", "制度怎么解释由财务定，出行人只能选“先按哪种准备”")
                if val not in ("A", "B"):
                    raise ValueError("口径只能是 A 或 B")
                st["mode_confirmed"] = val
                st["decisions"]["口径"] = val
                do_plan(trip, st, role)
                store.log(s, role, trip, "确认第七条口径", "按口径%s执行，方案已重算" % val)
            elif key in ("冲突", "口径", "住法", "超标"):
                need(role, ["traveler"], "这项决定", "口径怎么准备、合住还是分住、冲突怎么处理、超标怎么办，都由出行人本人拍板")
                st["decisions"][key] = val
                detail = "%s：%s" % (key, val)
                if key == "超标" and val == "改订标准席别" and not st["seat_fix"]:
                    changed = apply_seat_fix(trip)
                    st["seat_fix"] = True
                    do_plan(trip, st, role)
                    detail += "（%s，方案已重算）" % "；".join(changed)
                store.log(s, role, trip, "拍板", detail)
            else:
                raise ValueError("不认识的决定：%s" % key)
            store.save(s)
            return self._json({"ok": True, "state": st, "res": load_json(plan_path(trip))})

        if what == "choose":
            need(role, ["traveler"], "选定方案", "选哪个方案由出行人本人拍板，助理只把选项和代价摆清楚")
            if not st["plan_ready"]:
                raise ValueError("请先出方案")
            pick = body.get("pick", "推荐")
            decided = st["mode_confirmed"] or st["decisions"].get("口径")
            if decided and body.get("mode") and body["mode"] != decided:
                raise ValueError("这个方案是按口径%s算的，但现在定的是按口径%s准备。要选它，先把口径改成%s。" % (body["mode"], decided, body["mode"]))
            mode = decided or body.get("mode")
            if not mode:
                raise Denied("第七条口径还没定：请出行人在“必须先拍板的事”里先选按口径A还是口径B准备。")
            args = ["--result", rel(plan_path(trip)), "--choose", pick, "--mode", mode, "--output", rel(fresh(pkg_dir(trip)))]
            rooms = body.get("rooms") or st["decisions"].get("住法")
            res = load_json(plan_path(trip))
            if rooms and rooms != "单住" and len(res["行程"]["出行人"]) > 1:
                args += ["--rooms", rooms]
            outp = run_tool("生成行程包.py", args)
            st["package_ready"], st["chosen"], st["stage"] = True, {"pick": pick, "mode": mode, "rooms": rooms}, "已选定"
            for k in ("change_ready", "expense_ready"):
                st[k] = False
            st["briefs"] = []
            for sub in ("早报", "航班变动", "报销检查"):
                fresh(rdir(trip, sub))
            store.log(s, role, trip, "选定方案", "%s（口径%s%s），生成行程包" % (pick, mode, "，%s" % rooms if rooms else ""))
            store.save(s)
            return self._json({"ok": True, "log": outp, "state": st})

        if what == "todo":
            if not st["package_ready"]:
                raise ValueError("还没有行程包")
            tid = body.get("id")
            tf = os.path.join(pkg_dir(trip), "待办清单.json")
            doc = load_json(tf)
            item = [x for x in doc["待办"] if x["编号"] == tid]
            if not item:
                raise ValueError("没有这个待办")
            x = item[0]
            if x["状态"] == "完成":
                return self._json({"ok": True, "todo": x})
            owner = todo_owner(x)
            if x["事项"].startswith("提交 OA 出差申请"):
                if x["状态"] == "待办":
                    need(role, ["traveler"], "提交出差申请", "申请由出行人本人提交")
                    x["状态"] = "已提交·待审批"
                    msg = "提交出差申请（演示：没有真的提交到 OA）"
                else:
                    need(role, ["manager"], "审批出差申请", "部门负责人审批")
                    x["状态"] = "完成"
                    msg = "审批通过出差申请（演示）"
            else:
                why = {"manager": "超标和分住要部门负责人事前同意", "finance": "制度口径由财务确认",
                       "traveler": "下单、发消息、改日历、建提醒都要出行人本人确认，付款也由本人完成"}[owner]
                need(role, [owner], "“%s”" % x["事项"], why)
                x["状态"] = "完成"
                msg = x["事项"]
                if x["事项"].startswith("订"):
                    msg += "（演示：未连接订票平台，没有产生订单，也没有付款）"
                elif x["事项"].startswith("给") or x["事项"].startswith("把行程单发给"):
                    msg += "（演示：没有真的发送）"
            x["确认时间"] = time.strftime("%Y-%m-%d %H:%M")
            x["确认人"] = ROLE_LABEL[role]
            tc.save_json(doc, tf)
            store.log(s, role, trip, "确认待办 %s" % tid, msg)
            store.save(s)
            return self._json({"ok": True, "todo": x})

        if what == "brief":
            if not st["package_ready"]:
                raise ValueError("先选定方案、生成行程包，才能出早报")
            day = body.get("date") or t["brief_dates"][0]
            out = fresh(rdir(trip, "早报", day))
            log = run_tool("出行早报.py", ["--package", rel(pkg_dir(trip)), "--date", day, "--output", rel(out)])
            if day not in st["briefs"]:
                st["briefs"].append(day)
            store.log(s, role, trip, "生成早报", day)
            store.save(s)
            return self._json({"ok": True, "log": log})

        if what == "change":
            if not t["change"]:
                raise ValueError("这趟出差没有航班变动样例")
            if not st["package_ready"]:
                raise ValueError("先选定方案、生成行程包，才能处理航班变动")
            if body.get("choice"):
                need(role, ["traveler"], "选择改签或保持", "改不改签、改哪班由出行人本人决定；改签、退票、付款都由本人在平台完成")
                st["change_choice"] = body["choice"]
                store.log(s, role, trip, "航班变动：选择办法", "%s（演示：没有真的改签）" % body["choice"])
                store.save(s)
                return self._json({"ok": True, "state": st})
            inp = ensure_input(trip)
            out = fresh(rdir(trip, "航班变动"))
            log = run_tool("航班变动处理.py", ["--package", rel(pkg_dir(trip)), "--change", rel(os.path.join(inp, t["change"])), "--output", rel(out)])
            st["change_ready"] = True
            store.log(s, role, trip, "航班变动：算影响", "运行 工具/航班变动处理.py")
            store.save(s)
            return self._json({"ok": True, "log": log})

        if what == "expense":
            if not t["invoices"]:
                raise ValueError("这趟出差没有发票样例")
            if not st["package_ready"]:
                raise ValueError("先选定方案、生成行程包，才能检查报销")
            inp = ensure_input(trip)
            out = fresh(rdir(trip, "报销检查"))
            log = run_tool("报销检查.py", ["--package", rel(pkg_dir(trip)), "--invoices", rel(os.path.join(inp, t["invoices"])), "--output", rel(out)])
            st["expense_ready"], st["stage"] = True, "已报销检查"
            store.log(s, role, trip, "报销检查", "运行 工具/报销检查.py")
            store.save(s)
            return self._json({"ok": True, "log": log})

        return self._json({"error": "未知接口"}, 404)


def main():
    os.makedirs(store.DATA, exist_ok=True)
    srv, port = None, PORT
    for port in range(PORT, PORT + 20):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", port), H)
            break
        except OSError:
            continue
    if not srv:
        print("端口 %d—%d 都被占用了，关掉别的程序再试" % (PORT, PORT + 19))
        sys.exit(1)
    url = "http://127.0.0.1:%d" % port
    print("商务差旅助手（网页演示版）已启动：%s" % url)
    print("数据：%s" % DATA_LABEL)
    print("关掉这个窗口，服务就停止。")
    if not os.environ.get("NO_BROWSER"):
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
