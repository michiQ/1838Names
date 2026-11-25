#!/usr/bin/env python3
"""Merge Run #102 reader output (ext_A Oct, ext_B Nov, ext_C Dec 7-21, ext_Cfin Dec 28) into
pipeline/extractions97.json. Conservative, like Runs #95-#101: fold only unambiguous repeat printings
of one ad; multiple reports of one event LEFT SEPARATE for Michiko with [MERGE] notes. Names a reader
could not settle ([VERIFY] in the name) are pulled OUT of the linked people into the text."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/1838names/pipeline/extractions97.json"
A = []; E = []; N = []; F = []
for l in ["A", "B", "C", "Cfin"]:
    d = json.load(open(f"{HERE}/ext_{l}.json"))
    for a in d.get("articles", []): a["_r"] = l; A.append(a)
    for e in d.get("events", []):   e["_r"] = l; E.append(e)
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

# --- Fold the Beaufort, S.C. 'Freedman's Cheap Store' (Smalls & Gleaves) ad: non-Philadelphia, ran
# every week. Keep one record (earliest, Reader A Oct), drop the rest, proprietors in description only. ---
def is_smalls(x):
    b = json.dumps(x, ensure_ascii=False).lower()
    return "smalls" in b and "beaufort" in b
sm = [x for x in A + E if is_smalls(x)]
keep = [x for x in sm if x["_r"] == "A"] or sm[:1]
for x in sm:
    if x not in keep[:1]:
        (A if x in A else E).remove(x)
if keep:
    k = keep[0]; fld = "summary" if k in A else "description"
    k[fld] = k.get(fld, "").rstrip() + (" (Standing ad; ran every week of the quarter, October-December 1867. "
        "Proprietors Capt. Robert Smalls and R. H. Gleaves are in Beaufort, S.C., so not linked here.)")
    if "attendees" in k: k["attendees"] = []
    if "people" in k:    k["people"] = []

# --- Pull [VERIFY] names out of linked people/attendees into the text ---
for x in A + E:
    key, fld = ("people", "summary") if x in A else ("attendees", "description")
    kept = []
    for p in x.get(key, []):
        if "VERIFY" in p[0]:
            nm = p[0].replace(" [VERIFY]", "").strip()
            if nm.split()[-1] not in x.get(fld, ""):
                x[fld] = x.get(fld, "") + f" (Also named: {nm} [VERIFY], {p[1] if len(p) > 1 else ''}.)"
        else:
            kept.append(p)
    if key in x: x[key] = kept
for x in A + E: x.pop("_r", None)

# --- Summary notes for Michiko ---
N += [
 "[FIND] Street-car thread, Oct-Dec 1867: still NO Caroline R. Le Count item and NO Robert Smalls "
 "street-car item. Two street-car items did surface: (1) 'More Outrages' (Oct 12 p2), post-election "
 "Democrats ill-treating colored ladies and gentlemen trying to ride the street cars, one woman nearly "
 "injured until the conductor and passengers intervened (no names); (2) the Pennsylvania Supreme Court "
 "'Miles' railroad-car exclusion decision (Nov 16 p2), plaintiff ejected from the cars, which the editor "
 "stresses applies only to the period BEFORE the March 1867 anti-exclusion law (plaintiff printed only "
 "'Mrs. Miles', not linked). The only Smalls trace remains the Beaufort, S.C. store ad.",
 "[FIND] This quarter is heavy on the October 1867 Pennsylvania election and Black suffrage: 'Defeated' "
 "(Oct 12) and the 'To Our Colored Fellow-Citizens' editorial series (Oct 19, Nov 2). Also F. E. W. "
 "Harper lecturing at Liberty Hall (Oct 19, introduced by Josiah Wears), and a likely young Archibald H. "
 "Grimke in a Lincoln University memorial (Nov 2).",
 "[EDITOR] Masthead all quarter: Rev. Elisha Weaver, Editor and Publisher, 631 Pine St.",
 "[CHECK] Sarah Irons shrouding ad: Readers A and B (and your earlier ruling) read No. 320 Union Street; "
 "Reader C-fin read the Dec 28 printing as No. 820 Union Street. Kept as 320 per your ruling; the figure "
 "may print ambiguously (3 vs 8 in the type). Worth a look if you want it settled.",
 "[CHECK] Bethel (Philadelphia) pastor is printed 'D. Dorrell' / 'Deaton Dorrell' throughout Oct-Dec, "
 "against the database's 'James Hollen'. Reader A flagged for reconciliation.",
 "[CHECK] Address readings that differ between the Dec readers (left as printed, [VERIFY]): James W. "
 "Brown dyeing 1003 Shippen vs 606; Griffin 604 Barclay vs 904; Morning Post 735 Sansom vs 735 Chestnut.",
 "[MERGE] The Good Samaritans / Daughters of Samaria lodges recur (Sheba Lodge No. 1 Fifth Anniversary, "
 "Oct 19; Shiloh Union Lodge No. 12 organized at Springfield PA, Nov 2). Left separate; owner to reconcile "
 "with the Run #101 lodge records.",
 "[IA] Source item for this quarter is christianrecorder_1867_v7_no40_to_52 (Michiko's file name); not "
 "confirmed as an Archive URL, so no link added.",
 "[BACKFILL] Clean quarter: 13 weekly issues, Nos. 40-52, printed pages 157-208, no missing sheets, no "
 "duplicates. December complete (Dec 7-21 by reader C, Dec 28 by the finish reader; Dec 21 p1/p4 verified "
 "fully read).",
 "[QA] Main session spot-checked a roster (Sheba Lodge Fifth Anniversary, Oct 19) against the image: the "
 "reader's transcription matched. Name lists are short this quarter (8 max), so the completeness problem "
 "from Run #101 did not recur.",
]
json.dump({"articles": A, "events": E, "notes": N, "flags": F}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
