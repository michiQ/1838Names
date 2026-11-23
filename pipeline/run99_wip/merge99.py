#!/usr/bin/env python3
"""Merge Run #99 reader output (ext_A/A2 Jan, ext_B/B2 Feb, ext_C/C2 Mar 1867) into pipeline/extractions94.json.
Conservative, as Runs #95-#98: fold only unambiguous repeat printings of one ad or notice; multiple reports of one
event are LEFT SEPARATE for Michiko and listed in [MERGE] notes. Names the readers could not settle ([VERIFY] in the
name) are taken OUT of the linked people (the brief's rule) and kept in the text."""
import json, re
SCRATCH = "/home/claude/run99_scratch"
OUT = "/home/claude/1838names/pipeline/extractions94.json"
A = []; E = []; N = []; F = []
for l in ["A", "A2", "B", "B2", "C", "C2"]:
    d = json.load(open(f"{SCRATCH}/ext_{l}.json"))
    for a in d.get("articles", []): a["_r"] = l; A.append(a)
    for e in d.get("events", []): e["_r"] = l; E.append(e)
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

def find(lst, issue, kw, field, r=None):
    x = [x for x in lst if x["issue"] == issue and kw.lower() in x[field].lower() and (r is None or x["_r"] == r)]
    assert len(x) == 1, (issue, kw, [y[field] for y in x]); return x[0]
art = lambda i, k, r=None: find(A, i, k, "headline", r)
ev = lambda i, k, r=None: find(E, i, k, "name", r)
def fold(keep, drops, key, note, lst):
    names = {p[0] for p in keep.get(key, [])}
    for d in drops:
        for p in d.get(key, []):
            if p[0] not in names: keep.setdefault(key, []).append(p); names.add(p[0])
        lst.remove(d)
    fld = "summary" if key == "people" else "description"
    keep[fld] = keep.get(fld, "") + " " + note

# Repeat printings of one ad or notice
fold(art("CR_1867-02-09", "Kennard"), [art("CR_1867-03-02", "Kennard")], "people",
     "(New ad. Also ran Mar 1867; the number prints 832 on three printings and 632 on one.)", A)
fold(art("CR_1867-02-16", "China Store"), [art("CR_1867-03-02", "China Store")], "people",
     "(Also ran Mar 1867. J. H. Moore's store is No. 716 Lombard in the Jan-Mar 1867 printings.)", A)
fold(art("CR_1867-02-23", "Sheba Lodge"), [art("CR_1867-03-09", "Sheba Lodge")], "people",
     "(Standing notice; also ran Mar 1867.)", A)
fold(art("CR_1867-01-26", "Hinton"), [art("CR_1867-02-02", "Hinton"), art("CR_1867-02-09", "Hinton")], "people",
     "(Also printed Feb 2 and Feb 9, 1867, signed by Eliza (Elisa) Riley, the mother.)", A)

# Reader A2's corrected Boling obituary replaces A's. Port Republic, N.J.: out of town, text only (brief's rule).
old = art("CR_1867-01-05", "Boling", "A"); A.remove(old)
b = art("CR_1867-01-05", "Boling", "A2"); b["headline"] = "Obituary (Mary E. Boling, Port Republic, N.J.)"; b["people"] = []
# A2's NERL officers supplement folds into A's NERL event (same item, Jan 19 p2)
fold(ev("CR_1867-01-19", "Equal Rights League", "A"), [ev("CR_1867-01-19", "SUPPLEMENT", "A2")], "attendees",
     "(Officers and closing business from the foot of column 6 and column 7, read in a second pass: E. Weaver of Pennsylvania on the Executive Committee.)", E)

# Michiko 2026-11-23: the Eddys are one man. Bethel Feb 9 p3 prints Deacons Joshua Eddy and Josiah Eddy; link once.
bc = ev("CR_1867-02-09", "Bethel Church: Bishop Campbell")
bc["attendees"].append(["Josiah Eddy", "deacon (Rev.), assisting at the Lord's Supper; printed 'Joshua Eddy, Josiah Eddy' as two names, one man by Michiko's ruling"])

nerl = ev("CR_1867-01-19", "Equal Rights League convention"); nerl["date"] = "1867-01-10"

# Names the readers could not settle: out of the links, kept in the text
dropped = 0
for x in A + E:
    key, fld = ("people", "summary") if "people" in x or x in A else ("attendees", "description")
    keep = []
    for p in x.get(key, []):
        if "VERIFY" in p[0]:
            dropped += 1
            nm = p[0].replace(" [VERIFY]", "").strip()
            if nm.split()[-1] not in x.get(fld, ""):
                x[fld] = x.get(fld, "") + f" (Also named: {nm} [VERIFY], {p[1]}.)"
        else: keep.append(p)
    if key in x: x[key] = keep
for x in A + E: x.pop("_r", None)

N += [
 "[MERGE] Benevolent Daughters of Wesley Society 45th anniversary: Feb 16 p2 (event and report) and Feb 23 p2 (fuller report). Left separate for Michiko.",
 "[MERGE] Consecration of the A.M.E. Church of Germantown: notices Mar 9 p3, Mar 23 p3 (postponed to Mar 24) and Mar 23 p2 (Rev. Henry J. Rhodes, pastor). Left separate.",
 "[MERGE] Philadelphia Annual Conference 1867 (Bethel, May 18): announced Feb 2 p3 and Mar 30 p3. Left separate.",
 "[MERGE] National Equal Rights League convention, Washington: Weaver's report Jan 19 p2 and 'The Washington Convention' Jan 26 p2. Left separate. Event dated 1867-01-10: the Jan 26 items say it was called for January 10 and sat 10-12 (Weaver's faint report gives no clear date).",
 "[MERGE] Streetcar bill, as the Recorder printed it: Senate passes (Feb 9 p2), text of the bill and 'House has passed' (Feb 16 p2), stalled in the House (Feb 23 p2), Common Council resolution (Mar 2 p3), House passes the Sunday car bill (Mar 9 p3), House adopts first section (Mar 16 p2), passed both houses (Mar 23 p2 and p3), Gov. Geary signs (Mar 30 p3). Each kept as its own item. The Feb 16 'House has passed' line contradicts the Feb 23 editorial: recorded as printed.",
 "[CHECK] Mrs. Sarah Irons, Union Street: 320 on two February printings (one at 1600 dpi) and more likely 320 in March; not certain. The ads page keeps the card without a number.",
 "[CHECK] J. H. Moore's china store is No. 716 Lombard in every Jan-Mar 1867 printing (the Sep 22, 1866 printing read 706).",
 "[RULED] Dr. T. M. Kennard (ad), 'Rev. Thomas W. Kinnard' (Feb 9 p2) and the 1854 dentist Thomas M. Kinnard are one person (Michiko, 2026-11-23): merges.json.",
 "[RULED] 'Joshua Eddy' and 'Josiah Eddy', printed side by side as two deacons (Feb 9, 1867), are one man, J. P. B. Eddy (Michiko, 2026-11-23).",
 "[EDITOR] Masthead lines unchanged all quarter (Weaver Publisher, Lynch Editor). Lynch was away (Cincinnati, ill at Galena) and returned Jan 25 ('Our Western Trip', Feb 2); preached at Hurst Street Wesley Mar 3; left Mar 8 to visit the Baltimore and southern conferences. The terms box gives the office as 631 Pine.",
 "[BACKFILL] Mar 2 (No. 9) and Mar 30 (No. 13): first sheet (pages 1-2) missing on the film. Jan 5 (No. 1) pages 1-2 torn, about half of each lost.",
 "[IA] The Internet Archive item for Jan-Mar 1867 is probably christianrecorder_1867_v7_no1_to_13 (Michiko's file name), but it could not be confirmed from here, so no Archive link was added for 1867.",
]
json.dump({"articles": A, "events": E, "notes": N, "flags": F}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}  unsettled names moved to text: {dropped}")
