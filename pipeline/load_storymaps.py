#!/usr/bin/env python3
"""Load the 1838 Black Metropolis StoryMaps (five Philadelphia anti-Black mob
attacks: 1834, 1835, 1842, 1849, 1871) -- each its own source.

For each attack: create an EVENT node (date/location/description) and link every
named person to it as an attendee with a role, so the attack groups its people and
shows 'also there'. Every named person is brought in as source='storymap' with a
per-person story SNIPPET and a link to that year's StoryMap (stored in the
storymap_people table, rendered on the person card like the UGRR/Coppin sources).

NOTHING is auto-linked to existing records (Michiko's rule, mirroring the ICY
source): genuine same-person matches (Octavius Catto, Robert Purvis, Stephen Smith,
Jacob C. White Sr./Jr., Isaiah Wears, William Still, Dr. J.J.G. Bias, William
McMullen across 1849/1871, ...) are surfaced by find_merge_candidates and confirmed
by Michiko via merges.json. A person may appear in more than one attack.

Runs AFTER load_extractions (which DELETEs events) so these attack events survive;
source='storymap' people are excluded from match_names/load_extractions matching.

Idempotent: storymap_people is rebuilt each run; the attack events are re-inserted;
people are reused via get_or_create(name,'storymap'). Source: pipeline/storymaps.json.
"""
import sqlite3, json, re, unicodedata, os

HERE = os.path.dirname(os.path.abspath(__file__))
DB  = os.environ.get("BM_DB", os.path.join(HERE, "..", "black_metropolis.db"))
SRC = os.environ.get("STORYMAPS_SRC", os.path.join(HERE, "storymaps.json"))

def norm(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]", " ", n.lower())).strip()

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row
# storymap_people: one row per (person, attack) -- carries the snippet + link for the card
con.execute("""CREATE TABLE IF NOT EXISTS storymap_people(
    person_id INT, story_key TEXT, title TEXT, story_date TEXT, url TEXT, role TEXT, snippet TEXT)""")
con.execute("DELETE FROM storymap_people")
# make sure events has the columns load_extractions uses (it created them earlier this run)
for col in ("issue_id INT", "page INT"):
    try: con.execute(f"ALTER TABLE events ADD COLUMN {col}")
    except sqlite3.OperationalError: pass

def get_or_create(name):
    r = con.execute("SELECT id FROM people WHERE canonical_name=? AND source='storymap'", (name,)).fetchone()
    if r: return r["id"]
    cur = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?, 'storymap')",
                      (name, norm(name)))
    return cur.lastrowid

data = json.load(open(SRC, encoding="utf-8"))
n_people = n_app = n_events = 0
for atk in data["attacks"]:
    # the attack event
    cur = con.execute("INSERT INTO events(name, event_date, location, description) VALUES(?,?,?,?)",
                      (atk["title"], atk.get("date"), atk.get("location"), atk.get("description")))
    eid = cur.lastrowid; n_events += 1
    seen = set()
    for entry in atk["people"]:
        name, role, snippet = entry[0], entry[1], entry[2]
        if name in seen:  # dedupe a person listed twice in the same attack
            continue
        seen.add(name)
        pid = get_or_create(name)  # never auto-link; merge review confirms identities
        con.execute("INSERT INTO appearances(person_id, event_id, role, context, strength) VALUES(?,?,?,?,2)",
                    (pid, eid, role, atk["title"]))
        con.execute("INSERT INTO storymap_people(person_id, story_key, title, story_date, url, role, snippet) VALUES(?,?,?,?,?,?,?)",
                    (pid, atk["key"], atk["title"], atk.get("date"), atk["url"], role, snippet))
        n_app += 1
con.commit()
n_people = con.execute("SELECT COUNT(DISTINCT person_id) FROM storymap_people").fetchone()[0]

# review aid: same-name overlaps with existing NON-storymap records (candidate merges).
# StoryMap names are "First Last" but the DB stores census/Winch as "Last, First", so match on an
# order-independent key (sorted name tokens) to catch cross-form matches (Catto, Purvis, Stephen Smith...).
def okey(name):
    return " ".join(sorted(norm(name).split()))
idx = {}
for pid, cname, source in con.execute("SELECT id, canonical_name, source FROM people WHERE source IS NOT 'storymap'"):
    idx.setdefault(okey(cname), []).append((cname, source))
matches = []
for name in sorted({p[0] for a in data["attacks"] for p in a["people"]}):
    cands = idx.get(okey(name), [])
    if cands: matches.append((name, cands))
lines = ["# StoryMaps (mob attacks) -- name matches to confirm", "",
         "Each StoryMap name below shares an exact name with an existing record. NONE are",
         "auto-linked. To confirm a same-person match, add a group to `merges.json` (keep the",
         "existing record; source-qualify the storymap alias), e.g.:",
         '`{\"keep\": \"Catto, Octavius V.\", \"aliases\": [{\"name\": \"Octavius V. Catto\", \"source\": \"storymap\"}]}`',
         "", f"{len(matches)} of {n_people} StoryMap people share a name with an existing record:", ""]
for nm, cands in matches:
    lines.append(f"- **{nm}** (storymap)  ↔  " + ", ".join(f"{cn} ({sr})" for cn, sr in cands))
open(os.path.join(HERE, "storymap_matches.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")

print(f"storymaps: {n_events} attack events, {n_app} person-appearances, {n_people} storymap people "
      f"(no auto-linking); {len(matches)} same-name matches -> storymap_matches.md")
