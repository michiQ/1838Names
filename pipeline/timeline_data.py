"""Organization Timelines tab data (added 2026-11-01 at Michiko's request).

build(people, events, orgs, here) -> list of lanes for DATA.timeline.
Each lane: {name, cat, founded, pas, pasName, pasNote, note, undated, att}
att rows: [year, yearTo, personId, role, source, isOfficer]

Years come only from the record itself: an event date, a newspaper issue date, a year written in a
curated role or citation, or the year Julie Winch wrote right after the society's name. Founding
years and 1837 figures come from the 1838 PAS report table (pas1838_beneficial.json).
"""
import json, os, re

OFF = re.compile(r"president|vice|secretar|treasurer|founder|founding|director|manager|chair|librarian|"
                 r"marshal|steward|trustee|officer|warden|agent|committee|board", re.I)


def _years(t):
    out = []
    for m in re.finditer(r"\b(1[78]\d\d)(?:\s*[-–]\s*(\d{2,4}))?", t or ""):
        a = int(m.group(1)); b = m.group(2)
        if b:
            b = int(b) if len(b) == 4 else int(str(a)[:2] + b)
            if b < a or b - a > 40: b = a
        else:
            b = a
        out.append((a, b))
    return out


def _winch_hits(person, kw):
    """Years Winch wrote right after the society's name in this person's notes."""
    hits = []
    for r in person.get("refs") or []:
        t = r.get("n") or ""
        for m in re.finditer(kw, t):
            tail = t[m.end():m.end() + 45]
            mm = re.match(r"[^()\d]{0,30}?[(,]?\s*(?:ca\.\s*)?(1[78]\d\d(?:\s*[-–]\s*\d{2,4})?)", tail)
            if not mm: continue
            a, b = _years(mm.group(1))[0]
            st = max(0, t.rfind(" ", 0, max(0, m.start() - 40)))
            clause = t[st:m.end() + mm.end() + 1].strip()
            clause = re.sub(r"^.*?\b(Member|President|Vice|Secretary|Treasurer|Founding|On the|Delegate|Chosen|"
                            r"Elected|Manager|Director|Librarian|Committee)", r"\1", clause)
            clause = re.sub(r"\s+", " ", clause).strip(" .")
            hits.append((a, b, clause, "Winch" + (", " + r["c"] if r.get("c") else "")))
    return hits


def build(people, events, orgs, here):
    cfg = json.load(open(os.path.join(here, "timeline_lanes.json"), encoding="utf-8"))
    pas = json.load(open(os.path.join(here, "pas1838_beneficial.json"), encoding="utf-8"))
    rows = {r[0]: r for r in pas["rows"]}
    org_by = {o["name"]: o for o in orgs}
    used_pas = set()
    lanes = []
    for L in cfg["lanes"]:
        att, seen, undated = [], set(), 0
        kw = L.get("kw")
        label_year = re.search(r"\((1[78]\d\d)\)", L["label"])
        cands = {}
        note = ""
        for on in L.get("orgs", []):
            o = org_by.get(on)
            if not o: continue
            note = note or o.get("note", "")
            for pid in o["members"]:
                cands.setdefault(pid, o["src"].get(pid) or o["src"].get(str(pid)) or {})
        if kw:
            rx = re.compile(kw)
            for pid, p in people.items():
                if pid not in cands and any(rx.search(r.get("n") or "") for r in p.get("refs") or []):
                    cands[pid] = {}
        for pid, src in cands.items():
            p = people.get(pid)
            if not p: continue
            got = []
            role, cite = src.get("r", ""), src.get("c", "")
            if "e" in src and src["e"] in events:
                e = events[src["e"]]
                r2 = next((a[1] for a in e["att"] if a[0] == pid), "")
                d = e.get("date") or ""
                if re.match(r"\d{4}", d):
                    y = int(d[:4]); got.append((y, y, role or r2 or "", e["name"] + ", " + d))
            if not got and "i" in src:
                m = re.search(r"_(\d{4})-\d\d-\d\d", src["i"])
                if m:
                    y = int(m.group(1)); got.append((y, y, role, src["i"].split("_")[0] + " " + src["i"].split("_")[1]))
            if not got and (role or cite):
                for a, b in _years(role + " " + cite)[:1]:
                    got.append((a, b, re.sub(r"\s*\(1[78]\d\d\)", "", role), cite or "Winch"))
            if not got and kw:
                got = _winch_hits(p, kw)
            if not got and label_year and ("i" in src or "w" in src):
                y = int(label_year.group(1))
                got.append((y, y, role, cite or ("W. C. Bolivar, Philadelphia Tribune, 1913" if "PP_" in src.get("i", "") else "Winch")))
            if not got:
                undated += 1; continue
            for a, b, rl, sc in got:
                if a > 1880: continue
                k = (pid, a)
                if k in seen: continue
                seen.add(k)
                rl = re.sub(r"\s+", " ", rl or "").strip(" .")
                att.append([a, b, pid, rl, sc, 1 if OFF.search(rl) and not rl.lower().startswith("shareholder") else 0])
        att.sort(key=lambda x: (x[0], -x[5]))
        lane = {"name": L["label"], "cat": L["cat"], "note": note, "undated": undated, "att": att}
        if L.get("marks"): lane["marks"] = L["marks"]
        if L.get("pas"):
            r = rows[L["pas"]]; used_pas.add(r[0])
            lane.update({"founded": r[2], "pas": r[3:], "pasName": r[1], "pasRow": r[0]})
            if L.get("pasNote"): lane["pasNote"] = L["pasNote"]
        lanes.append(lane)
    # every other society in the 1838 table becomes its own lane (founding year + 1837 figures only)
    for no, r in rows.items():
        if no in used_pas: continue
        lanes.append({"name": r[1], "cat": "aid", "note": "", "undated": 0, "att": [],
                      "founded": r[2], "pas": r[3:], "pasName": r[1], "pasRow": r[0], "pasOnly": 1})
    return {"lanes": lanes, "pasSource": pas["source"], "pasUrl": pas["url"], "pasFoot": pas["footnotes"]}
