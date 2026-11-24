#!/usr/bin/env python3
"""Merge Run #100 reader output (ext_A Apr, ext_B/B2 May, ext_C/C2/C3 Jun 1867) into pipeline/extractions95.json.
Conservative, as Runs #95-#99: fold only unambiguous repeat printings of one ad or notice; multiple reports of one
event are LEFT SEPARATE for Michiko and listed in [MERGE] notes. Names the readers could not settle ([VERIFY] in the
name) are taken OUT of the linked people (the brief's rule) and kept in the text."""
import json
HERE = "/home/claude/1838names/pipeline/run100_wip"
OUT = "/home/claude/1838names/pipeline/extractions95.json"
A = []; E = []; N = []; F = []
for l in ["A", "B", "B2", "C", "C2", "C3"]:
    d = json.load(open(f"{HERE}/ext_{l}.json"))
    for a in d.get("articles", []): a["_r"] = l; A.append(a)
    for e in d.get("events", []): e["_r"] = l; E.append(e)
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

def find(lst, issue, kw, field, r=None):
    x = [x for x in lst if x["issue"] == issue and kw.lower() in x[field].lower() and (r is None or x["_r"] == r)]
    assert len(x) == 1, (issue, kw, [y[field] for y in x]); return x[0]
art = lambda i, k, r=None: find(A, i, k, "headline", r)
def fold(keep, drops, key, note, lst):
    names = {p[0] for p in keep.get(key, [])}
    for d in drops:
        for p in d.get(key, []):
            if p[0] not in names: keep.setdefault(key, []).append(p); names.add(p[0])
        lst.remove(d)
    fld = "summary" if key == "people" else "description"
    keep[fld] = keep.get(fld, "") + " " + note

fold(art("CR_1867-05-25", "First-Class Dentist"), [art("CR_1867-06-01", "First-Class Dentist")], "people",
     "(Also ran June 1867.)", A)
fold(art("CR_1867-05-25", "Amelia Anderson"), [art("CR_1867-06-01", "Country Boarding")], "people",
     "(Also ran June 1867.)", A)
fold(art("CR_1867-06-15", "Masonry and Christianity"), [art("CR_1867-06-29", "Masonry and Christianity")], "people",
     "(Also ran June 29, 1867.)", A)
# Irons: a standing ad (Run #98); its number is disputed, so the June 1 'number now clear' entry is a note, not a new ad.
A.remove(art("CR_1867-06-01", "Sarah Irons"))

for x in A + E:
    key, fld = ("people", "summary") if x in A else ("attendees", "description")
    keep = []
    for p in x.get(key, []):
        if "VERIFY" in p[0]:
            nm = p[0].replace(" [VERIFY]", "").strip()
            if nm.split()[-1] not in x.get(fld, ""):
                x[fld] = x.get(fld, "") + f" (Also named: {nm} [VERIFY], {p[1]}.)"
        else: keep.append(p)
    if key in x: x[key] = keep
for x in A + E: x.pop("_r", None)

N += [
 "[MERGE] Philadelphia Annual Conference 1867 (51st session, Bethel, from May 18): announced Apr 6 and Apr 27; opening and committees May 25; proceedings and appointments Jun 1; fifth to ninth days Jun 8. Left separate.",
 "[MERGE] Parent, Home and Foreign Missionary Society annual meeting (May 23): Apr 27 and May 18 notices. Left separate.",
 "[MERGE] Hurst Street Wesley fourth quarterly meeting (May 12): Apr 27, May 4, May 11 notices. Left separate.",
 "[MERGE] Union League grand re-union: Reader A has it announced for Apr 26 at National Hall; Reader B dates the festival Apr 20 (May 4 report). Left separate; dates differ.",
 "[MERGE] Union Grand Lodge of New Jersey, St. John's Day (Jun 24): Jun 15 notice and Jun 29 item. Left separate.",
 "[CHECK] Mrs. Sarah Irons, Union Street: readers split between 320 and 820; a high-resolution check of the Apr 27 - May 25 printings reads 820 (first figure closed on the left), June 1 and 22 were read 320. Owner to rule; the ads page keeps the card without a number.",
 "[EDITOR] Weaver Publisher / Lynch Editor through June 8. The Conference appointed Lynch to Bethel (Jun 1); Lynch's 'Our Appointment' and 'Valedictory' (Jun 8); Book Concern trustees accept his resignation and name Weaver to the editorial chair (Jun 13, printed Jun 15); editor line gone from page 2 (Jun 22); masthead 'Rev. Elisha Weaver, Editor' (Jun 29). Bethel then under 'Rev. H. Dorrell' [VERIFY].",
 "[BACKFILL] Apr 13 (No. 15) and May 11 (No. 19): first sheet (pages 1-2) missing on the film. May 18 page 1 filmed twice (frames 23, 24). Jun 29 pages 3-4 filmed in reverse order.",
 "[IA] Internet Archive item for Apr-Jun 1867 probably christianrecorder_1867_v7_no14_26 (Michiko's file name); not confirmed, so no Archive link added.",
]
json.dump({"articles": A, "events": E, "notes": N, "flags": F}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
