#!/usr/bin/env python3
"""Merge Run #96 reader output (ext_A Apr, ext_B May, ext_C Jun 1866) into
pipeline/extractions91.json. Conservative, matching Run #95: fold only the
unambiguous cross-reader duplicates (three standing ads that ran across months).
Genuine editorial judgment calls (the Philadelphia Annual Conference printed as
three printings Apr 21 / May 5 / Jun 2, and the many Semi-Centenary printings)
are LEFT SEPARATE for Michiko's review."""
import json, os

SCRATCH = "/home/claude/run96_scratch"
OUT = "/home/claude/1838names/pipeline/extractions91.json"

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

def addp(dst, src, key):
    seen = {tuple(p) for p in dst.get(key, [])}
    names = {p[0] for p in dst.get(key, [])}
    for p in src.get(key, []):
        if p[0] not in names:
            dst.setdefault(key, []).append(p); names.add(p[0])

# --- Fold standing ads: keep first printing, carry any new proprietor into it, drop later repeats ---
# 1) African Civilization Society: identical all quarter, no linked people.
acs_keep = find_art("CR_1866-04-07", "African Civ")
for di, dk in [("CR_1866-05-05", "African Civ"), ("CR_1866-06-02", "African Civ")]:
    A.remove(find_art(di, dk))
acs_keep["summary"] += " (Standing ad; ran again May 5 and June 2, 1866, unchanged.)"
acs_keep.setdefault("_repeats", []).extend(["1866-05-05", "1866-06-02"])

# 2) Security Life Insurance (Jos. C. Bustill, solicitor): keep Apr 14; carry Durham from May 5.
sec_keep = find_art("CR_1866-04-14", "Security")
sec_drop = find_art("CR_1866-05-05", "Security")
addp(sec_keep, sec_drop, "people")   # brings in Nathaniel L. Durham, 911 1/2 Christian St.
A.remove(sec_drop)
sec_keep["summary"] += " (Standing ad; also ran May 5, 1866, when N. L. Durham appeared as an adjoining 'also Solicitor for Security Life' at 911 1/2 Christian St.)"
sec_keep.setdefault("_repeats", []).append("1866-05-05")

# 3) Great Union Intelligence Office: keep first printing Apr 28; drop May 19 repeat.
gui_keep = find_art("CR_1866-04-28", "Union Intelligence")
gui_drop = find_art("CR_1866-05-19", "Union Intelligence")
A.remove(gui_drop)
gui_keep["summary"] += " (Standing ad; also ran May 19, 1866, where the proprietor is printed 'E. Demund & Co.')"
gui_keep.setdefault("_repeats", []).append("1866-05-19")

# --- Cross-reference note for the judgment calls left separate (NOT merged) ---
N.append("[MERGE] Philadelphia Annual Conference (A.M.E.), spring 1866 session at Princeton, N.J. "
         "(May 23-28), is printed THREE times and left as three separate entries for Michiko: "
         "Apr 21 p3 (Wayman's advance call + the candidate examination classes), May 5 p2 (brief "
         "editorial notice, bishops expected), Jun 2 p1 (full proceedings with the ~32-charge "
         "appointment roster). Candidate-class men (Apr) reappear as appointed charges (Jun). "
         "Merge or keep separate is Michiko's call.")
N.append("[MERGE] The A.M.E. Church Semi-Centenary generates many entries across April-May "
         "(Bethel laymen's meeting, Bethel anniversary, Union, Little Wesley/Hurst St, the Bethel "
         "Sabbath School, Burlington N.J., Washington D.C., the May 5 'Day We Celebrate' letter). "
         "Some are advance notices and reports of the same Bethel observance. Left separate per the "
         "Run #95 precedent; Michiko to decide any merges (an open item from Run #95 too).")

out = {"articles": A, "events": E, "notes": N, "flags": F}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"WROTE {OUT}")
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
print(f"linked people-slots in articles: {sum(len(a.get('people',[])) for a in A)}")
print(f"linked attendee-slots in events: {sum(len(e.get('attendees',[])) for e in E)}")
