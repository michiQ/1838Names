#!/usr/bin/env python3
"""Merge Run #101 reader output (ext_A Jul-early Aug, ext_B/B2 Aug, ext_C/C2 Sep 1867) into
pipeline/extractions96.json. Conservative, like Runs #95-#100: fold only unambiguous repeat
printings of one ad; multiple reports of one event are LEFT SEPARATE for Michiko with [MERGE]
notes. Names a reader could not settle ([VERIFY] in the name) are pulled OUT of the linked people
and kept in the text. Includes a QA correction to the First Colored Church donor list (main
session read the image: Reader A had missed several contributors)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = "/home/claude/1838names/pipeline/extractions96.json"
A = []; E = []; N = []; F = []
for l in ["A", "B", "B2", "C", "C2"]:
    d = json.load(open(f"{HERE}/ext_{l}.json"))
    for a in d.get("articles", []): a["_r"] = l; A.append(a)
    for e in d.get("events", []):   e["_r"] = l; E.append(e)
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

# --- QA correction: First Colored Church acknowledgment (CR 1867-07-20 p2, Reader A) ---
# Main session read column 3 of the image directly; Reader A had captured 30 of ~39 contributors.
ack = [e for e in E if e["_r"] == "A" and "First Colored Church" in e.get("name", "")]
assert len(ack) == 1, ("ack event", len(ack))
ack = ack[0]
have = {p[0] for p in ack["attendees"]}
add = [
    ["Mary Brown", "contributor $1 (Mrs.)"],
    ["C. Gilbert", "contributor $1 (Mrs.)"],
    ["J. C. White", "contributor $1 (Mrs.)"],
    ["C. Jackson", "contributor $1 (Mrs.)"],
    ["Mrs. Button", "contributor $1"],
    ["John T. Brown", "contributor $1"],
]
for p in add:
    if p[0] not in have: ack["attendees"].append(p)
ack["description"] = ack.get("description", "").rstrip() + (
    " [QA, main session, read from the image:] Reader A had missed several contributors; added "
    "Mrs. Mary Brown, Mrs. C. Gilbert, Mrs. J. C. White, Mrs. C. Jackson, Mrs. Button and John T. "
    "Brown ($1 each). Three more were read with low confidence and are left unlinked: Mr. Morse "
    "($5), M. B. Cors ($1) and Mrs. H. Ferman ($1). George Gray raised $21 of the total; the whole "
    "amount received and paid over was $58; signed A. M. Cropper, July 20, 1867.")

# --- Fold the Beaufort, S.C. 'Freedman's Cheap Store' (Smalls & Gleaves) ad: non-Philadelphia, ran
# the whole quarter. Keep one record (Reader B, first appearance Aug 10), drop Reader C's duplicate,
# and keep the proprietors in description only (not linked; out of scope). ---
smalls = [x for x in A + E if "smalls" in json.dumps(x, ensure_ascii=False).lower()
          and "beaufort" in json.dumps(x, ensure_ascii=False).lower()]
keep = [x for x in smalls if x["_r"] == "B"]
drop = [x for x in smalls if x["_r"] != "B"]
for x in drop:
    (A if x in A else E).remove(x)
if keep:
    k = keep[0]
    fld = "summary" if k in A else "description"
    k[fld] = k.get(fld, "").rstrip() + (" (Standing ad; ran across the quarter, July-September 1867. "
        "Proprietors Capt. Robert Smalls and R. H. Gleaves are in Beaufort, S.C., so not linked here.)")
    if "attendees" in k: k["attendees"] = []
    if "people" in k:    k["people"] = []

# --- Pull [VERIFY] names out of linked people/attendees into the text (brief rule) ---
for x in A + E:
    key, fld = ("people", "summary") if x in A else ("attendees", "description")
    keep2 = []
    for p in x.get(key, []):
        if "VERIFY" in p[0]:
            nm = p[0].replace(" [VERIFY]", "").strip()
            if nm.split()[-1] not in x.get(fld, ""):
                x[fld] = x.get(fld, "") + f" (Also named: {nm} [VERIFY], {p[1] if len(p)>1 else ''}.)"
        else:
            keep2.append(p)
    if key in x: x[key] = keep2
for x in A + E: x.pop("_r", None)

# --- Summary notes for Michiko ---
N += [
 "[FIND] No Caroline R. Le Count item, no Robert Smalls street-car item, and NO report of the "
 "Pennsylvania street-car law (signed March 1867) in use, refused, enforced or celebrated, in any "
 "of the 13 issues July 6 - September 28, 1867. All three readers plus the page-1/page-4 top-up "
 "re-reads (B2 Aug, C2 Sep) confirm this. The only Smalls trace is the Beaufort, S.C. store ad. "
 "The only transportation-exclusion items are Bishop J. P. Campbell put off the steamer Commercial "
 "in Arkansas (Sep 21 p1) and a Maryland railroad conductor incident in J. M. Brown's letter "
 "(Sep 14 p1); neither is a Philadelphia street car.",
 "[EDITOR] Masthead all quarter: Rev. Elisha Weaver, Editor and Publisher, 631 Pine St. "
 "Rev. James Lynch had left the editor's chair by the June 29 issue; no further change July-September.",
 "[MERGE] Good Samaritans / Daughters of Samaria lodges appear more than once and are LEFT SEPARATE: "
 "Reader A has D.G. Lodge No. 2 officers elected June 4 (CR 07-20 p3); Readers B2/C have the standing "
 "directory ad naming Sheba Lodge (A. Cropper, S. Young) and Sumner & Wilson Lodge No. 8 "
 "(Masonic Hall, South Eleventh St.). Owner to reconcile.",
 "[QA] Main session spot-checked the highest-risk capture (the First Colored Church donor list) "
 "against the image and found Reader A had missed about a quarter of the names; corrected above. "
 "Readers' lists are thorough but not guaranteed exhaustive; a scan of the longer name lists is wise.",
 "[IA] Internet Archive / source item for this quarter is christianrecorder_1867_v7_no27_to_39 "
 "(Michiko's file name); not confirmed as an Archive URL, so no link added.",
 "[BACKFILL] Clean quarter: 13 weekly issues, Nos. 27-39, printed pages 105-156, no missing sheets. "
 "PDF page 53 is a duplicate scan of page 52 (Sep 28 p4).",
]
json.dump({"articles": A, "events": E, "notes": N, "flags": F}, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
print("First Colored Church attendees now:", len(ack["attendees"]))
