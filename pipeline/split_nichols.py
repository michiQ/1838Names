#!/usr/bin/env python3
"""Split Samuel Nichols out of the mis-parsed Winch "Newton, Mary" record.

The Winch parse jammed seven of Samuel Nichols's biographical notes (a male
second-hand-clothes dealer at Shippen St, Second Presbyterian, convention
delegate) into the entry for "Newton, Mary" (id2014). Only the FIRST note --
"Member of the Female Vigilant Committee" (Pa. Freeman, July 5, 1838) -- is
actually Mary. This moves the other notes onto a dedicated "Nichols, Samuel"
Winch person so Mary can be merged cleanly into the "Mary Lewton" newspaper
record (see merges.json). Michiko approved 2026-07-30.

Idempotent + reproducible: keys on the Winch person still literally named
"Newton, Mary" and moves every winch_reference of hers EXCEPT the Female
Vigilant Committee note. Once merges.json folds "Newton, Mary" into
"Mary Lewton" (so the name no longer exists as a standalone Winch record), this
is a no-op. winch_references are static (build_db is frozen), so this runs each
rebuild without accumulating. Must run BEFORE apply_merges.
"""
import sqlite3, re, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("BM_DB", os.path.join(HERE, "..", "black_metropolis.db"))

# the one note that really is Mary (stays with her, follows the merge to Mary Lewton)
MARY_NOTE_PREFIX = "Member of the Female Vigilant Committee"

def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", s.lower()).strip()

con = sqlite3.connect(DB)
row = con.execute("SELECT id FROM people WHERE canonical_name='Newton, Mary' AND source='winch'").fetchone()
if not row:
    print("split_nichols: no standalone Winch 'Newton, Mary' (already split/merged) -- no-op")
    con.close(); raise SystemExit

mary_id = row[0]
nichols_refs = [(rid, note) for rid, note in
                con.execute("SELECT id, note FROM winch_references WHERE person_id=?", (mary_id,))
                if not (note or "").startswith(MARY_NOTE_PREFIX)]
if not nichols_refs:
    print("split_nichols: 'Newton, Mary' carries only Mary's note -- no-op")
    con.close(); raise SystemExit

# find or create the dedicated Samuel Nichols Winch person
r = con.execute("SELECT id FROM people WHERE canonical_name='Nichols, Samuel' AND source='winch'").fetchone()
if r:
    nichols_id = r[0]
else:
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES('Nichols, Samuel', ?, 'winch')",
                      (norm("Nichols, Samuel"),))
    nichols_id = cur.lastrowid

for rid, _ in nichols_refs:
    con.execute("UPDATE winch_references SET person_id=? WHERE id=?", (nichols_id, rid))
con.commit()
print(f"split_nichols: moved {len(nichols_refs)} Samuel Nichols notes from 'Newton, Mary' (id{mary_id}) "
      f"-> 'Nichols, Samuel' (id{nichols_id}); 'Newton, Mary' left with only the Female Vigilant note")
con.close()
