# -*- coding: utf-8 -*-
"""
商务差旅助手（网页演示版）回归测试。双击 运行测试.command，或：
    python3 -m unittest discover -s tests -v

做法：把整个演示文件夹复制到临时目录，在空闲端口上启动一份独立服务，
按课堂演示的顺序把整条链走一遍，核对关键数字、身份权限和“不替人下单”的底线。
不碰你正在用的 data/ 目录，也不联网（Agent 用离线模式）。
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request
from urllib.parse import quote

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class DemoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="travel_demo_test_")
        cls.root = os.path.join(cls.tmp, "demo")
        shutil.copytree(HERE, cls.root, ignore=shutil.ignore_patterns("data", "交付记录", "__pycache__", "tests"))
        os.makedirs(os.path.join(cls.root, "data"))
        port = free_port()
        env = dict(os.environ, NO_BROWSER="1", TRAVEL_DEMO_PORT=str(port), PYTHONDONTWRITEBYTECODE="1")
        env.pop("TRAVEL_API_KEY", None)
        cls.proc = subprocess.Popen([sys.executable, "-u", os.path.join(cls.root, "app", "server.py")], cwd=cls.root,
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        line = cls.proc.stdout.readline()
        if "http://" not in line:
            cls.proc.kill()
            raise RuntimeError("服务没有启动：%s" % line)
        cls.base = line[line.index("http://"):].split()[0]
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        try:
            cls.proc.wait(5)
        except Exception:
            cls.proc.kill()
        cls.proc.stdout.close()
        shutil.rmtree(cls.tmp, ignore_errors=True)

    # ------------------------------------------------------------ 小工具
    def call(self, method, path, body=None, role="assistant", raw=False):
        data = json.dumps(body or {}).encode("utf-8") if method == "POST" else None
        req = urllib.request.Request(self.base + path, data=data, method=method,
                                     headers={"Content-Type": "application/json", "X-Role": role})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                payload = r.read()
                return r.status, (payload if raw else json.loads(payload.decode("utf-8")))
        except urllib.error.HTTPError as e:
            payload = e.read()
            try:
                return e.code, json.loads(payload.decode("utf-8"))
            except Exception:
                return e.code, payload

    def ok(self, method, path, body=None, role="assistant"):
        code, j = self.call(method, path, body, role)
        self.assertEqual(code, 200, "%s %s 应该成功，实际 %s：%s" % (method, path, code, j))
        return j

    def denied(self, method, path, body=None, role="assistant"):
        code, j = self.call(method, path, body, role)
        self.assertEqual(code, 403, "%s %s（身份 %s）应该被拦下，实际 %s：%s" % (method, path, role, code, j))
        self.assertTrue(j.get("denied"))
        return j

    def todo(self, trip, tid):
        pkg = self.ok("GET", "/api/trip/%s/package" % trip)
        return [t for t in pkg["todos"] if t["编号"] == tid][0]

    def reset(self):
        self.ok("POST", "/api/reset")

    # ------------------------------------------------------------ 测试
    def test_01_page_and_meta(self):
        code, html = self.call("GET", "/", raw=True)
        self.assertEqual(code, 200)
        self.assertIn("商务差旅助手".encode("utf-8"), html)
        meta = self.ok("GET", "/api/meta")
        self.assertEqual(set(meta["trips"]), {"sh", "cd"})
        self.assertEqual(set(meta["roles"]), {"assistant", "traveler", "manager", "finance"})
        self.assertIn("样例数据", meta["label"])
        self.assertEqual(meta["model"]["key"], "offline")

    def test_02_full_chain_shanghai(self):
        """课堂主线：出方案 → 出行人拍板 → 选定 → 待办逐件确认 → 早报 → 航班延误 → 报销检查。"""
        self.reset()
        j = self.ok("POST", "/api/trip/sh/plan")
        res = j["res"]
        self.assertEqual(res["组合统计"]["可选"], 72)
        self.assertEqual(len(res["问题清单"]), 19)
        self.assertEqual(len(res["必须先拍板"]), 5)
        self.assertEqual(res["方案"]["推荐A"]["id"], "O2+T1+R5+H2·合住")
        self.assertEqual(res["方案"]["推荐A"]["费用"]["合计"], 3748)
        self.assertEqual(res["方案"]["推荐B"]["id"], "O2+T1+R1+H2·合住")
        self.assertEqual(res["方案"]["推荐B"]["费用"]["合计"], 3951)
        self.assertEqual(res["方案"]["最省钱"]["费用"]["合计"], 3428)

        # 助理不能替人拍板、不能选方案
        self.denied("POST", "/api/trip/sh/decide", {"key": "口径", "value": "B"})
        self.denied("POST", "/api/trip/sh/choose", {"pick": "推荐"})
        # 口径没定之前，出行人也不能直接选
        self.denied("POST", "/api/trip/sh/choose", {"pick": "推荐"}, role="traveler")

        for k, v in (("口径", "B"), ("冲突", "线上参加"), ("住法", "合住")):
            self.ok("POST", "/api/trip/sh/decide", {"key": k, "value": v}, role="traveler")
        # 定了口径B，就不能拿口径A的方案来选
        code, j = self.call("POST", "/api/trip/sh/choose", {"pick": "推荐", "mode": "A"}, role="traveler")
        self.assertEqual(code, 400, j)
        j = self.ok("POST", "/api/trip/sh/choose", {"pick": "推荐", "mode": "B"}, role="traveler")
        self.assertEqual(j["state"]["chosen"]["mode"], "B")

        pkg = self.ok("GET", "/api/trip/sh/package")
        self.assertEqual(pkg["pkg"]["方案"]["id"], "O2+T1+R1+H2·合住")
        self.assertEqual(pkg["pkg"]["费用预估"], {"交通": 3531, "住宿": 420, "伙食补助": 440, "合计": 4391})
        self.assertEqual(len(pkg["todos"]), 14)
        self.assertEqual(len(pkg["pkg"]["提醒计划"]), 10)
        self.assertEqual(pkg["pkg"]["报销截止"], "2026-12-04")
        self.assertTrue(all(t["状态"] == "待办" for t in pkg["todos"]))
        owners = dict((t["编号"], t["谁来确认_key"]) for t in pkg["todos"])
        self.assertEqual(owners["T02"], "finance")
        self.assertEqual(owners["T04"], "manager")
        self.assertEqual(owners["T05"], "traveler")

        # 订票：助理点确认被拦；出行人确认后只记录“本人已同意”，不产生订单
        self.denied("POST", "/api/trip/sh/todo", {"id": "T05"})
        j = self.ok("POST", "/api/trip/sh/todo", {"id": "T05"}, role="traveler")
        self.assertEqual(j["todo"]["状态"], "完成")
        log = self.ok("GET", "/api/audit")
        self.assertIn("未连接订票平台", log[0]["说明"])

        # 出差申请：出行人提交 → 部门负责人审批
        self.ok("POST", "/api/trip/sh/todo", {"id": "T03"}, role="traveler")
        self.assertEqual(self.todo("sh", "T03")["状态"], "已提交·待审批")
        self.denied("POST", "/api/trip/sh/todo", {"id": "T03"}, role="traveler")
        self.ok("POST", "/api/trip/sh/todo", {"id": "T03"}, role="manager")
        self.assertEqual(self.todo("sh", "T03")["状态"], "完成")
        # 口径确认只能财务点；超标只能部门负责人点
        self.denied("POST", "/api/trip/sh/todo", {"id": "T02"}, role="traveler")
        self.ok("POST", "/api/trip/sh/todo", {"id": "T02"}, role="finance")
        self.denied("POST", "/api/trip/sh/todo", {"id": "T04"}, role="traveler")
        self.ok("POST", "/api/trip/sh/todo", {"id": "T04"}, role="manager")

        # 日历文件带提醒
        code, ics = self.call("GET", "/api/trip/sh/file?kind=%s&name=%s" % (quote("行程包"), quote("行程.ics")), raw=True)
        self.assertEqual(code, 200)
        ics = ics.decode("utf-8")
        self.assertIn("BEGIN:VCALENDAR", ics)
        self.assertIn("BEGIN:VALARM", ics)

        # 早报
        self.ok("POST", "/api/trip/sh/brief", {"date": "2026-11-19"})
        briefs = self.ok("GET", "/api/trip/sh/briefs")
        self.assertEqual([b["date"] for b in briefs], ["2026-11-19"])
        self.assertIn("QH-1503", briefs[0]["md"])
        self.assertTrue(briefs[0]["sms"])

        # 航班延误：12:20 到达，到场只剩 10 分钟
        self.ok("POST", "/api/trip/sh/change")
        ch = self.ok("GET", "/api/trip/sh/change")
        self.assertIn("12:20", ch["md"])
        self.assertIn("只剩 10 分钟", ch["md"])
        self.assertIn("3 个可行", ch["md"])
        self.denied("POST", "/api/trip/sh/change", {"choice": "保持原航班"})
        self.ok("POST", "/api/trip/sh/change", {"choice": "保持原航班"}, role="traveler")

        # 报销检查：T04 超标已由部门负责人批过 → 张工一等座 64 元全额可报
        # 11 张票，5,279 = 4,093 + 506 + 680
        self.ok("POST", "/api/trip/sh/expense")
        ex = self.ok("GET", "/api/trip/sh/expense")
        self.assertEqual(len(ex["rows"]), 11)
        for s in ("5,279", "4,093", "506", "680", "12月4日"):
            self.assertIn(s, ex["summary"])
        self.assertEqual(sum(int(r["金额"]) for r in ex["rows"]), 5279)
        i04 = [r for r in ex["rows"] if r["编号"] == "I04"][0]
        self.assertEqual(i04["结论"], "可报")

    def test_02b_expense_without_overstandard_approval(self):
        """超标没批：张工一等座超出的 25 元个人承担 → 5,279 = 4,068 + 506 + 705（课堂演示默认路径）。"""
        self.reset()
        self.ok("POST", "/api/trip/sh/plan")
        for k, v in (("口径", "B"), ("冲突", "线上参加"), ("住法", "合住")):
            self.ok("POST", "/api/trip/sh/decide", {"key": k, "value": v}, role="traveler")
        self.ok("POST", "/api/trip/sh/choose", {"pick": "推荐"}, role="traveler")
        self.ok("POST", "/api/trip/sh/expense")
        ex = self.ok("GET", "/api/trip/sh/expense")
        for s in ("5,279", "4,068", "506", "705"):
            self.assertIn(s, ex["summary"])
        i04 = [r for r in ex["rows"] if r["编号"] == "I04"][0]
        self.assertEqual(i04["结论"], "部分可报")
        self.assertEqual(i04["个人承担或不能报"], "25")

    def test_03_finance_confirm_reruns_plan(self):
        """财务确认口径A：方案按A重算，之后出行人只能按A选。"""
        self.reset()
        self.ok("POST", "/api/trip/sh/plan")
        self.denied("POST", "/api/trip/sh/decide", {"key": "口径确认", "value": "A"}, role="traveler")
        j = self.ok("POST", "/api/trip/sh/decide", {"key": "口径确认", "value": "A"}, role="finance")
        self.assertEqual(j["state"]["mode_confirmed"], "A")
        self.assertTrue(j["res"]["第七条口径"]["已确认"])
        code, _ = self.call("POST", "/api/trip/sh/choose", {"pick": "推荐", "mode": "B"}, role="traveler")
        self.assertEqual(code, 400)
        self.ok("POST", "/api/trip/sh/choose", {"pick": "推荐"}, role="traveler")
        pkg = self.ok("GET", "/api/trip/sh/package")
        self.assertEqual(pkg["pkg"]["口径"], "A")
        self.assertTrue(pkg["pkg"]["口径已确认"])
        self.assertFalse(any(t["事项"].startswith("向财务确认") for t in pkg["todos"]))

    def test_04_seat_fix_reruns(self):
        """出行人选“改订标准席别”：去掉超标的一等座，重算后推荐方案不再有超标问题。"""
        self.reset()
        self.ok("POST", "/api/trip/sh/plan")
        before = self.ok("GET", "/api/trip/sh/plan")["res"]
        self.assertTrue(any("超出标准" in p["问题"] for p in before["问题清单"]))
        j = self.ok("POST", "/api/trip/sh/decide", {"key": "超标", "value": "改订标准席别"}, role="traveler")
        self.assertTrue(j["state"]["seat_fix"])
        after = j["res"]
        self.assertFalse(any("超出标准" in p["问题"] for p in after["问题清单"]))
        self.assertLess(after["方案"]["推荐B"]["费用"]["合计"], before["方案"]["推荐B"]["费用"]["合计"])
        # 原始输入没被改
        with open(os.path.join(self.root, "输入", "第一批_上海苏州", "需求.json"), encoding="utf-8") as f:
            self.assertIn("requested_seat", f.read())

    def test_05_agent_never_books(self):
        self.reset()
        self.ok("POST", "/api/trip/sh/plan")
        for q in ("帮我把机票订了", "直接下单吧", "替我付款"):
            a = self.ok("POST", "/api/agent", {"trip": "sh", "question": q})
            self.assertIn("不能直接下单", a["text"], q)
            self.assertTrue(a["mode"].startswith("离线"))
        a = self.ok("POST", "/api/agent", {"trip": "sh", "question": "为什么不推荐最便宜的？"})
        self.assertIn("3,428", a["text"])
        a = self.ok("POST", "/api/agent", {"trip": "sh", "question": "两种口径差多少？"})
        self.assertIn("203", a["text"])  # 3,951 - 3,748

    def test_06_chengdu_and_guards(self):
        self.reset()
        j = self.ok("POST", "/api/trip/cd/plan")
        self.assertTrue(j["res"]["方案"])
        code, _ = self.call("POST", "/api/trip/cd/change")
        self.assertEqual(code, 400)
        code, _ = self.call("POST", "/api/trip/cd/brief")
        self.assertEqual(code, 400)
        # 读文件不能越界
        code, _ = self.call("GET", "/api/doc?name=" + quote("../app/agent.py"))
        self.assertEqual(code, 404)
        code, _ = self.call("GET", "/api/trip/sh/file?kind=%s&name=%s" % (quote("行程包"), quote("../../state.json")))
        self.assertEqual(code, 404)
        code, _ = self.call("GET", "/" + quote("../app/agent.py"))
        self.assertEqual(code, 404)
        # 只有助理能重置、改模型设置
        self.denied("POST", "/api/reset", role="manager")
        self.denied("POST", "/api/settings", {"key": "deepseek"}, role="traveler")

    def test_07_reset(self):
        self.ok("POST", "/api/trip/sh/plan")
        self.reset()
        meta = self.ok("GET", "/api/meta")
        self.assertFalse(meta["states"]["sh"]["plan_ready"])
        self.assertEqual(meta["states"]["sh"]["decisions"], {})
        code, _ = self.call("GET", "/api/trip/sh/plan")
        self.assertEqual(code, 404)
        self.assertFalse(os.path.isdir(os.path.join(self.root, "data", "runs")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
