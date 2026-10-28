# -*- coding: utf-8 -*-
"""演示状态：每趟出差走到哪一步、谁做了什么决定、操作日志。保存在 data/state.json，可一键重置。"""
import json
import os
import shutil
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
RUNS = os.path.join(DATA, "runs")
STATE_FILE = os.path.join(DATA, "state.json")
LOCK = threading.RLock()

TRIPS = {
    "sh": {"id": "sh", "dir": "第一批_上海苏州", "label": "林总、张工 · 上海 / 苏州", "dates": "11月19日—20日",
           "traveler": "林总", "change": "航班变动_延误.json", "invoices": "票据识别结果.json",
           "brief_dates": ["2026-11-18", "2026-11-19", "2026-11-20"]},
    "cd": {"id": "cd", "dir": "新批次_成都", "label": "周经理 · 成都", "dates": "11月25日—26日",
           "traveler": "周经理", "change": None, "invoices": None,
           "brief_dates": ["2026-11-24", "2026-11-25", "2026-11-26"]},
}

ROLES = {
    "assistant": {"label": "差旅助理", "desc": "查、算、起草；不能替人拍板、下单、审批"},
    "traveler": {"label": "出行人", "desc": "拍板方案、确认下单和发消息（付款本人完成）"},
    "manager": {"label": "部门负责人", "desc": "审批出差申请、超标、分住"},
    "finance": {"label": "财务", "desc": "确认制度口径（第七条）"},
}


def _blank_trip():
    return {"stage": "需求", "plan_ready": False, "decisions": {}, "mode_confirmed": None, "seat_fix": False,
            "chosen": None, "package_ready": False, "change_ready": False, "change_choice": None,
            "expense_ready": False, "briefs": []}


def _blank():
    return {"version": 1, "trips": dict((k, _blank_trip()) for k in TRIPS), "audit": []}


def load():
    with LOCK:
        if not os.path.exists(STATE_FILE):
            return _blank()
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                s = json.load(f)
        except Exception:
            return _blank()
        for k in TRIPS:
            s["trips"].setdefault(k, _blank_trip())
        return s


def save(s):
    with LOCK:
        os.makedirs(DATA, exist_ok=True)
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(s, f, ensure_ascii=False, indent=1)
        os.replace(tmp, STATE_FILE)


def log(s, role, trip, action, detail=""):
    s["audit"].insert(0, {"时间": time.strftime("%Y-%m-%d %H:%M:%S"), "身份": ROLES.get(role, {}).get("label", role),
                          "行程": TRIPS[trip]["label"] if trip in TRIPS else "", "操作": action, "说明": detail})
    del s["audit"][300:]


def reset():
    with LOCK:
        if os.path.isdir(RUNS):
            shutil.rmtree(RUNS)
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
        s = _blank()
        log(s, "assistant", "", "重置演示状态", "清空方案、行程包、早报、报销结果和所有决定；模型设置和问答缓存保留")
        save(s)
        return s
