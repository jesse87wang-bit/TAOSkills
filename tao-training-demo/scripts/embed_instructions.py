# -*- coding: utf-8 -*-
"""
把模板里单独一行的 <<相对路径>> 换成该文件全文（```text 代码块），保证手册里的指令和 txt 一字不差。

用法：python3 embed_instructions.py <基准文件夹> <模板1.md> <输出1.md> [<模板2.md> <输出2.md> ...]
例：  python3 embed_instructions.py 02_WorkBuddy版_构建与演示 tpl_手册.md 02_WorkBuddy版_构建与演示/用WorkBuddy构建X_构建与演示手册.md
"""
import os
import re
import sys

base = sys.argv[1]
for tpl, out in zip(sys.argv[2::2], sys.argv[3::2]):
    s = open(tpl, encoding="utf-8").read()

    def sub(m):
        path = os.path.join(base, m.group(1))
        txt = open(path, encoding="utf-8").read().rstrip("\n")
        assert "```" not in txt, path
        return "```text\n" + txt + "\n```"

    s2, n = re.subn(r"^<<(.+?)>>$", sub, s, flags=re.M)
    assert not re.search(r"^<<.+>>$", s2, flags=re.M)
    open(out, "w", encoding="utf-8").write(s2)
    print(out, "嵌入", n, "处")
