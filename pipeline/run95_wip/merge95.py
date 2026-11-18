#!/usr/bin/env python3
"""Merge Run #95 reader output (ext_A Jan, ext_B Feb, ext_C Mar 1866) into
pipeline/extractions90.json. Conservative: fold only the unambiguous cross-reader
duplicates (four standing ads each entered once per month, and the Feb 20 Equal
Rights League special meeting printed in both Jan 27 and Feb 3). Genuine
editorial judgment calls (Semi-Centenary spread, SCSA meetings, the two Old
Folks' concerts) are LEFT SEPARATE for Michiko's review.

Paths are for this session's checkout (/home/claude/1838names)."""
import json, os

SCRATCH = "/home/claude/run95_scratch"
OUT = "/home/claude/1838names/pipeline/extractions90.json"

A=[]; E=[]; N=[]; F=[]
for l in "ABC":
    d = json.load(open(f"{SCRATCH}/ext_{l}.json"))
    A += d["articles"]; E += d["events"]
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]

def find_art(issue, kw):
    r = [a for a in A if a["issue"] == issue and kw.lower() in a["headline"].lower()]
    assert len(r) == 1, (issue, kw, [a["headline"] for a in r])
    return r[0]

def find_ev(issue, kw):
    r = [e for e in E if e["issue"] == issue and kw.lower() in e["name"].lower()]
    assert len(r) == 1, (issue, kw, [e["name"] for e in r])
    return r[0]

def addp(dst, src, key):
    seen = {p[0] for p in dst.get(key, [])}
    for p in src.get(key, []):
        if p[0] not in seen:
            dst.setdefault(key, []).append(p); seen.add(p[0])

# --- fold standing ads: keep first printing, carry proprietor names, drop later repeats ---
AD_FOLDS = [
    # (keep issue, keep kw), [(drop issue, drop kw), ...]
    (("CR_1866-01-06", "Mayhew"), [("CR_1866-02-03", "Mayhew"), ("CR_1866-03-03", "Mayhew")]),
    (("CR_1866-01-20", "Jonathan Davis"), [("CR_1866-02-03", "Jonathan Davis"), ("CR_1866-03-03", "Jonathan Davis")]),
    (("CR_1866-01-20", "G. A. Brown"), [("CR_1866-02-03", "G. A. Brown"), ("CR_1866-03-03", "G. A. Brown")]),
    (("CR_1866-02-03", "Maria Butler"), [("CR_1866-03-03", "Maria Butler")]),
]
for (ki, kk), drops in AD_FOLDS:
    keep = find_art(ki, kk)
    for di, dk in drops:
        d = find_art(di, dk)
        addp(keep, d, "people")
        A.remove(d)
    keep.setdefault("_repeats", []).extend([di for di, dk in drops])
    keep["summary"] = keep.get("summary", "") + " (Standing ad; also ran " + ", ".join(di[3:] for di, dk in drops) + ".)"

# --- fold the one duplicate event: Equal Rights League special meeting of Feb 20 ---
keep = find_ev("CR_1866-01-27", "special meeting")
dropev = find_ev("CR_1866-02-03", "special meeting")
addp(keep, dropev, "attendees")
keep["description"] = keep.get("description", "") + " || Also printed in the Christian Recorder of Feb. 3, 1866, page " + str(dropev["page"]) + "."
E.remove(dropev)

A.sort(key=lambda a: (a["issue"], a["page"]))
E.sort(key=lambda e: (e["issue"], e["page"]))

out = {
 "_note": ("Christian Recorder, Jan-Mar 1866 (Run #95, 2026-11-18). Vol. VI, Nos. 1-13; "
   "continuous pagination 1-52. Readers A (January), B (February), C (March), one pass each, "
   "pages 1 and 4 read column by column from image crops. Two issues are missing their front "
   "leaf in our copy and were read as pages 3-4 only: Jan 13 (No. 2) and Mar 24 (No. 12); the "
   "missing pages 1-2 are a separate backfill. Four standing ads (Mrs. Edith Mayhew shrouding; "
   "Dr. Jonathan Davis; Mrs. G. A. Brown, Indian Doctress; Mrs. Maria Butler's House of "
   "Application) were entered once at first printing and their later monthly repeats folded in. "
   "The Equal Rights League special meeting of Feb 20 (printed Jan 27 and Feb 3) is one event. "
   "LEFT SEPARATE for Michiko's review (possible same-occasion collapses): the A.M.E. "
   "Semi-Centenary planning across Feb 3 and Mar 3; the SCSA organizing/election and lecture "
   "course; and the two 'Old Folks' Concerts' (Zion A.M.E. Mission, announced Jan 27 / reported "
   "Feb 24, vs the Book Concern benefit of Mar 13). Names recorded as printed. OPEN questions "
   "flagged for Michiko: 'R. P. Gibbs' is printed clearly as pastor of Union A.M.E. (Feb 17, "
   "Mar 24) -- reconcile with the Run #94 'J. P. Gibbs is NOT R. P. Gibbs' note; H. J. Rhodes "
   "(Zion A.M.E. Mission) kept separate from H. G. Rhodes (Book Concern trustee); Malcolm's "
   "branch address reads 609 Walnut in Jan 6, Mar 10 and Mar 17 (the handoff VERIFY resolves to 609)."),
 "articles": A, "events": E, "notes": N, "flags": F,
}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print("articles:", len(A), "events:", len(E), "notes:", len(N), "flags:", len(F))
print("linked person-rows:", sum(len(a.get("people", [])) for a in A) + sum(len(e.get("attendees", [])) for e in E))
print("wrote", OUT)
