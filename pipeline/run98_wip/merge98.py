#!/usr/bin/env python3
"""Merge Run #98 reader output (ext_A Oct, ext_B Nov, ext_C Dec 1866) into pipeline/extractions93.json.
Conservative, as Runs #95-#97: fold only unambiguous cross-reader duplicates; multiple printings of one
event are LEFT SEPARATE for Michiko and listed in [MERGE] notes."""
import json, os
SCRATCH = "/home/claude/run98_scratch"
OUT = "/home/claude/1838names/pipeline/extractions93.json"
A = []; E = []; N = []; F = []
for l in ["A", "B", "C"]:
    d = json.load(open(f"{SCRATCH}/ext_{l}.json"))
    A += d.get("articles", []); E += d.get("events", [])
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

def find(lst, issue, kw, field):
    r = [x for x in lst if x["issue"] == issue and kw.lower() in x[field].lower()]
    assert len(r) == 1, (issue, kw, [x[field] for x in r]); return r[0]
art = lambda i, k: find(A, i, k, "headline")
ev = lambda i, k: find(E, i, k, "name")
def fold(keep, drops, key, note, lst):
    names = {p[0] for p in keep.get(key, [])}
    for d in drops:
        for p in d.get(key, []):
            if p[0] not in names: keep.setdefault(key, []).append(p); names.add(p[0])
        lst.remove(d)
    keep["summary" if key == "people" else "description"] += " " + note

fold(art("CR_1866-11-17", "Irons"), [art("CR_1866-12-01", "Irons")], "people",
     "(Changed ad: Run #96 captured Mrs. Sarah Irons at 619 Pine. Also ran Dec 1866.)", A)
fold(art("CR_1866-11-03", "A. Upham, advertisement"), [art("CR_1866-12-01", "Upham")], "people",
     "(Also ran Dec 1866. Upham's is the white-owned confectionery named in the June 30, 1866 letter 'Ill-Treatment of "
     "Patrons'; kept off the Black business ads page.)", A)
fold(ev("CR_1866-12-01", "Wilmington"), [ev("CR_1866-12-08", "Wilmington")], "attendees",
     "(Notice reprinted Dec 8, 1866.)", E)

N += [
 "[MERGE] Book Concern (Great Union) Fair at Liberty Hall, printed as: the call (Oct 6 p3), postponement (Nov 3 p2), opening fixed for Nov 15 (Nov 10 p2), opening (Nov 24 p2), in progress with officers (Dec 1 p2), closing Nov 29 (Dec 8 p2), prizes (Dec 15 p2). Left separate for Michiko.",
 "[MERGE] Institute for Colored Youth commencement/examination: Nov 3 p2 and Nov 10 p2. Left separate.",
 "[MERGE] Colored Soldiers' and Sailors' National Convention (Philadelphia, Jan 8, 1867): call Nov 3 p1 and announcement Dec 22 p2. Left separate.",
 "[MERGE] National Equal Rights League meeting at Washington (Jan 10, 1867): call Nov 24 p2 and Dec 15 p2. Left separate.",
 "[MERGE] Union A.M.E. quarterly meeting (Oct 21): notice Oct 20 p3 and Oct 27 p2. Left separate.",
 "[CHECK] J. H. Moore's china store: the Sep 22, 1866 printing reads No. 706 Lombard (checked at 1600 dpi in the merge session); Oct-Dec printings read 716. Entered Dec 1 as printed; the ads page keeps the Sep 22 printing.",
 "[CHECK] Lodgings: Sep 22 printing reads 410 Gaskill (1600 dpi, merge session); the Oct 6 printing reads 416. Entered Oct 6 as printed. Wanted apprentices: Sep 29 reads 401 South Seventh (1600 dpi); Oct printing reads 410 (not entered).",
 "[EDITOR] Masthead lines unchanged all quarter (Weaver Publisher, Lynch Editor), but Lynch left Oct 23 for 6-8 weeks in the South and Weaver edited from Oct 27; from Nov 10 the office is given as 631 Pine (the Depository ad still says 619).",
 "[BACKFILL] Oct 6, 1866 (No. 40): pages 1-2 missing on the film; pages 3-4 present.",
]
json.dump({"articles": A, "events": E, "notes": N, "flags": F}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
