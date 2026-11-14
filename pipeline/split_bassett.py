#!/usr/bin/env python3
"""Split Shadrack Bassett out of the mis-parsed Winch "Bassett, Ebenezer D." record.

The Winch parse ran the entry "Bassitt or Bassett, Shadrack" into the entry above it, so
Ebenezer D. Bassett (id 172) carried Shadrack's notes: AME deacon (1834), Board of Managers of
the American Society of Free Persons of Color (1830), Board of Education of the Association for
Mental and Moral Improvement (Procs. 1837), and the 1847 census line at 412 Fourth. Only
"Member, PA Equal Rights League (1865)" is Ebenezer's. This moves Shadrack's notes to a Winch
person "Bassett, Shadrack", which merges.json then joins with his two census records, his
Christian Recorder obituary record and his blog record. Michiko approved 2026-11-13.

Idempotent: keyed on the text "Bassitt or Bassett, Shadrack" still being in Ebenezer's note.
Runs each rebuild after split_swilliams and BEFORE apply_merges.
"""
import sqlite3, re, unicodedata, os

DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
MARK = "Bassitt or Bassett, Shadrack"
EBEN = "Member, PA Equal Rights League (1865)"

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)
eb = con.execute("SELECT id, winch_entry FROM people WHERE canonical_name='Bassett, Ebenezer D.' AND source='winch'").fetchone()
if not eb:
    print("split_bassett: no Winch 'Bassett, Ebenezer D.' -- no-op"); con.close(); raise SystemExit
eid, entry = eb
r = con.execute("SELECT id FROM people WHERE canonical_name='Bassett, Shadrack' AND source='winch'").fetchone()
if r: sid = r[0]
else:
    sid = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES('Bassett, Shadrack', ?, 'winch')",
                      (norm("Bassett, Shadrack"),)).lastrowid
moved = 0
for rid, note, cite in con.execute("SELECT id, note, citation FROM winch_references WHERE person_id=?", (eid,)).fetchall():
    note = note or ""
    if MARK in note:
        before, after = note.split(MARK, 1)
        con.execute("UPDATE winch_references SET note=?, citation=NULL WHERE id=?", (before.strip(), rid))
        con.execute("INSERT INTO winch_references(person_id, note, citation) VALUES(?,?,?)",
                    (sid, "Entered by Winch as 'Bassitt or Bassett, Shadrack'. " + after.strip(), cite))
        moved += 1
    elif note.startswith("1847 census") and "412 Fourth" in note:
        con.execute("UPDATE winch_references SET person_id=? WHERE id=?", (sid, rid)); moved += 1
if entry and MARK in entry:
    before, after = entry.split(MARK, 1)
    con.execute("UPDATE people SET winch_entry=? WHERE id=?", (before.strip(), eid))
    con.execute("UPDATE people SET winch_entry=? WHERE id=?", (MARK + after, sid))
con.commit()
print(f"split_bassett: moved {moved} note(s) from 'Bassett, Ebenezer D.' (id{eid}) to 'Bassett, Shadrack' (id{sid})")
con.close()
