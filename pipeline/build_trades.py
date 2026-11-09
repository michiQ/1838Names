#!/usr/bin/env python3
"""1838 Register of Trades page (added 2026-11-08 at Michiko's request).

Writes trades.html at the repo root: every line of the Register, grouped by trade in printed order,
each name linked to its record (index.html#p<id>). build_viewer.py calls main() at the end.
"""
import json, os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")


def main():
    con = sqlite3.connect(DB)
    if not con.execute("SELECT 1 FROM sqlite_master WHERE name='register_1838'").fetchone():
        print("trades page: no register_1838 table, skipped"); return
    link = {rid: pid for pid, rid in con.execute("SELECT person_id, row_id FROM directory_links WHERE directory='1838rot'")}
    rows = []
    for rid, sur, given, suf, trade, also, addr, biz in con.execute(
            "SELECT rowid_, surname, given, suffix, trade, also, address, carries_on_business FROM register_1838 ORDER BY rowid_"):
        name = " ".join(x for x in [given, sur, suf.capitalize() if suf else ""] if x)
        rows.append({"name": name, "trade": trade, "also": also, "addr": addr, "biz": 1 if biz else 0, "pid": link.get(rid)})
    tpl = open(os.path.join(HERE, "trades_template.html"), encoding="utf-8").read()
    open(os.path.join(ROOT, "trades.html"), "w", encoding="utf-8").write(
        tpl.replace("/*__ROWS__*/[]", json.dumps(rows, ensure_ascii=False, separators=(",", ":"))))
    print("trades page:", len(rows), "listings |", sum(1 for r in rows if r["pid"]), "linked")


if __name__ == "__main__":
    main()
