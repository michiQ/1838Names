#!/usr/bin/env python3
"""Merge Run #97 reader output (ext_A Jul, ext_B Aug, ext_C Sep 1866, plus the re-read files
ext_B2 = Aug 18/25 p4 at full slicing, ext_D = page-3 ad columns Aug/Sep) into
pipeline/extractions92.json.

Conservative, matching Runs #95-#96: fold only unambiguous cross-reader duplicates
(standing ads and notices reprinted week to week). Editorial judgment calls (multiple
printings of one meeting: call / notice / report) are LEFT SEPARATE for Michiko and
listed in [MERGE] notes."""
import json, os

SCRATCH = "/home/claude/run97_scratch"
OUT = "/home/claude/1838names/pipeline/extractions92.json"

A = []; E = []; N = []; F = []
for l in ["A", "B", "C", "B2", "D"]:
    p = f"{SCRATCH}/ext_{l}.json"
    if not os.path.exists(p):
        print(f"(no ext_{l}.json)"); continue
    d = json.load(open(p))
    A += d.get("articles", []); E += d.get("events", [])
    N += [f"[Reader {l}] {x}" for x in d.get("notes", [])]
    F += [f"[Reader {l}] {x}" for x in d.get("flags", [])]


def find(lst, issue, kw, field):
    r = [x for x in lst if x["issue"] == issue and kw.lower() in x[field].lower()]
    assert len(r) == 1, (issue, kw, [x[field] for x in r])
    return r[0]

def art(issue, kw): return find(A, issue, kw, "headline")
def ev(issue, kw): return find(E, issue, kw, "name")

def addp(dst, src, key):
    names = {p[0] for p in dst.get(key, [])}
    for p in src.get(key, []):
        if p[0] not in names:
            dst.setdefault(key, []).append(p); names.add(p[0])

def fold(keep, drops, key, note, lst):
    for d in drops:
        addp(keep, d, key)
        lst.remove(d)
    keep["summary" if key == "people" else "description"] += " " + note
    keep.setdefault("_repeats", []).extend(d["issue"][3:] for d in drops)


# ---------------- standing ads: keep the first printing, drop later repeats ----------------
# 1) The "Mrs. J." ice cream saloon. Three readers, nine printings read at DPI=1600.
sal = art("CR_1866-07-07", "Ice Cream")
sal_drops = [art("CR_1866-08-04", "Ice Cream"), art("CR_1866-09-08", "Ice Cream")]
for d in sal_drops: A.remove(d)
sal["_repeats"] = ["1866-07-14", "1866-07-21", "1866-07-28", "1866-08-04", "1866-08-11",
                   "1866-08-18", "1866-09-08", "1866-09-15", "1866-09-22"]
sal["summary"] += (" (Standing ad, p3, Jul 7 through Sep 22, 1866. Three readers read every printing at "
                   "DPI=1600 independently: the surname prints C?lq?houn, with C, l, q, h, o, u, n certain and "
                   "the vowel after C and the letter after q uncertain; best reading Colquhoun. No. 913 Lombard "
                   "Street is clear on Jul 7-28 and Aug 4. Not 'Culyahouse'. This is the 'Mrs. J.' ice cream "
                   "saloon left off the ads page in Run #96.)")

# 2) William Still, coal yard, Washington Ave. (changed from the captured 107 N. Fifth St. coal/stoves ad).
still = art("CR_1866-07-07", "Coal Yard")
fold(still, [art("CR_1866-08-04", "Coal Yard"), art("CR_1866-09-01", "Coal Yard")], "people",
     "(Standing ad; replaces the captured 107 N. Fifth St. coal/stoves ad. Ran through Sep 1866, p3 then p4.)", A)

# 3) Houston & Boling, South St. House number does not settle across printings.
hb = art("CR_1866-07-07", "Houston")
fold(hb, [art("CR_1866-08-04", "Houston")], "people",
     "(Standing ad, p3, Jul-Sep 1866. House number: the July printings read 625 South Street (also seen on "
     "the Jul 7 page image in the merge session); the September printings read 825 (clearest Sep 29, checked "
     "at DPI=1600), matching the Jul 28 p2 editorial puff's 825. Either the ad changed or one is a misprint "
     "[VERIFY]. Ownership not established: owner to decide whether it belongs.)", A)

# 4) Georgina Gleaves removed to 1028 Lombard (changed ad).
gg = art("CR_1866-07-07", "Gleaves")
fold(gg, [art("CR_1866-08-11", "Gleaves")], "people",
     "(Changed ad: Georgina Gleaves's earlier captured address was 633 Pine. Ran through Aug 1866.)", A)

# 5) Miss E. E. Hunter, dress and cloak maker, at Mrs. S. S. Hawkins's store.
hu = art("CR_1866-07-14", "Hunter")
fold(hu, [art("CR_1866-08-11", "Hunter")], "people", "(Standing ad; also ran Aug 11, 1866.)", A)

# 6) Jones's auction dry goods, No. 718 Lombard (the New Hall). Name printed three ways.
jn = art("CR_1866-07-28", "Jones' Auction")
jn["people"] = [["A. T. Jones", "proprietor, auction dry goods and trimmings, No. 718 Lombard Street (as printed Jul 28; also printed A. P., A. I. and A. J., one man per Michiko 2026-11-20)"]]
for d in [art("CR_1866-08-11", "Jones' Auction"), art("CR_1866-09-01", "Jones' Auction")]:
    A.remove(d)
jn["_repeats"] = ["1866-08-04", "1866-08-11", "1866-08-18", "1866-08-25", "1866-09-01"]
jn["summary"] += (" (Standing ad, Jul 28 - Sep 1866. The proprietor's initials print three ways: 'A. T. Jones' "
                  "on Jul 28 p3 (clear at DPI=1600), 'A. I. Jones' in the August printings, 'A. J. Jones' on Sep 1 p4. "
                  "The Sep 1 p2 editorial calls him Mr. A. J. Jones and says the ad misprints the name as 'A. I. "
                  "Jones'; the Jul 14 p2 editorial prints 'A. P. Jones'. Recorded as printed; identity is the owner's call.)")

# 7) James W. Brown, the New Store, No. 14 South Sixth St. (changed ad).
jb = art("CR_1866-08-11", "James W. Brown")
fold(jb, [art("CR_1866-09-08", "James W. Brown")], "people",
     "(Changed ad; also ran Sep 1866. 'Late of No. 1?8 / 13? South Fifth Street' is not clear in either "
     "printing; the captured steam-dyeing ad gave 120 S. Fifth.)", A)

# ---------------- notices reprinted week to week: keep the first printing ----------------
ev_ev = ev("CR_1866-07-21", "Evesham")
fold(ev_ev, [ev("CR_1866-08-04", "Evesham")], "attendees",
     "(Notice reprinted Aug 4, 1866, which adds the committee of arrangements: William Muse, Jefferson Johnson, "
     "Charles Green, William Roberts, Stephen Johnson, Robert Davis.)", E)
# Link review: very common names on this New Jersey committee stay in the text only (brief rule), because
# they otherwise auto-link to same-named Philadelphia census heads (Charles Green, Robert Davis did).
COMMON = {"Charles Green", "William Roberts", "Stephen Johnson", "Robert Davis"}
ev_ev["attendees"] = [p for p in ev_ev["attendees"] if p[0] not in COMMON]
N.append("[LINKS] Evesham (N.J.) camp-meeting committee: Charles Green, William Roberts, Stephen Johnson and Robert "
         "Davis kept in the description only (very common names; two had auto-linked to Philadelphia census heads).")

mac = ev("CR_1866-07-28", "Macedonia")
fold(mac, [ev("CR_1866-08-04", "Macedonia")], "attendees", "(Notice reprinted Aug 4, 1866.)", E)

oc = ev("CR_1866-08-25", "Olive Cemetery")
fold(oc, [ev("CR_1866-09-01", "Olive Cemetery")], "attendees",
     "(Notice reprinted Sep 1, 1866, which names U. B. Vidal as secretary.)", E)

# ---------------- cross-reference notes for judgment calls left separate ----------------
N.append("[MERGE] Pennsylvania State Equal Rights League annual meeting, Pittsburgh, Aug 8-10, 1866: printed as "
         "the call (Jul 14 p3; Jul 28 p2, issued from 717 Lombard St.), the meeting report (Aug 18 p2) and its "
         "continuation (Sep 1 p1). Left as separate entries for Michiko.")
N.append("[MERGE] Bristol Circuit Semi-Centenary camp meeting: Jul 21 p3 (for Aug 3), Aug 18 p3 (for Aug 23, "
         "Vandergrift's woods), and possibly reported Sep 1 p3 ('near Eddington Station', Aug 26). Dates differ; "
         "left separate. Joins the open Semi-Centenary merge question from Runs #95-#96.")
N.append("[MERGE] Harvest Home at Princeton, N.J., Aug 22, 1866: notice Aug 11 p3 and report Sep 15 p1. Left separate.")
N.append("[MERGE] Centenary of Methodism, Philadelphia Conference committee: two rosters, Sep 15 p3 and Sep 29 p2. "
         "Left separate. Keep apart from the A.M.E. Semi-Centenary.")
N.append("[MERGE] National Equal Rights League: the Nashville call (Aug 18 p1), the Executive Board protest "
         "(Sep 1 p1) and the revocation/Washington call (Sep 15 p2) are distinct items, kept separate.")
N.append("[IDENTITY] J. H. Moore's china store, No. 706 Lombard St., under Liberty Hall (Sep 22 p3) and the "
         "china-store keeper in the New Hall item read 'Jeremiah Moore [VERIFY]' (Jul 14 p2): possibly one man. "
         "Not linked; owner's call.")
N.append("[IDENTITY] Jones of 718 Lombard printed A. P. (Jul 14 p2), A. T. (Jul 28 p3 ad), A. I. (Aug ads), "
         "A. J. (Jul 28 p2, Sep 1 p2 and p4). The Sep 1 editorial gives A. J. Jones. Recorded as printed.")
N.append("[CHECK] Organs for Sale (Joseph H. Carter): the Jul 28 p3 printing reads 'Inquire at No. 1340, South "
         "St.' at DPI=1600 (checked in the merge session); another reading of Aug 25 p4 suggested '1019'. [VERIFY]")
N.append("[LINKS] Split off by split_appearances.json (Run #97 link review): Rev. Wm. Moore of Trenton (Jul 28, "
         "Sep 22) -> newspaper W. Moore; J. Lee of Salem N.J.; Henry Collins (Information Wanted, Md.); George W. "
         "Jones (grove, Chester Co.); John Atkins (West Chester bush meeting).")
N.append("[LINKS] FLAG FOR MICHIKO: plausible Philadelphia links on common names, left in place: DAVIS, SARAH "
         "(census; Book Concern Fair vice president, Sep 29); Davis, William H (census; Harper lecture committee, "
         "Jul 14); Johnson, Daniel (census; Grand Lodge recording secretary, Sep 22); Brooks, Henry (census; husband "
         "of Amelia Brooks, Sep 1); Harris, Elizabeth (census; Bethel Daughters of Conference, d. 1866); and the 1866 "
         "bride and groom Thompson, Harriet and Ross, Richard (census heads of 1838/1847). Review whether each is the "
         "census person.")
N.append("[BACKFILL] Aug 11, 1866 (No. 32): pages 1-2 missing on the film (frame 21 is a dark target card); pages 3-4 present.")

out = {"articles": A, "events": E, "notes": N, "flags": F}
json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False)
print(f"WROTE {OUT}")
print(f"articles: {len(A)}  events: {len(E)}  notes: {len(N)}  flags: {len(F)}")
print(f"linked people-slots in articles: {sum(len(a.get('people',[])) for a in A)}")
print(f"linked attendee-slots in events: {sum(len(e.get('attendees',[])) for e in E)}")
