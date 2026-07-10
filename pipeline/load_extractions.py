#!/usr/bin/env python3
"""Load hand-extracted articles/events/attendees into the DB, linking to Winch people."""
import sqlite3, json, glob, re, unicodedata

DB = "/tmp/fj4/black_metropolis.db"
EXT = "/sessions/practical-happy-tesla/mnt/Newspapers/1838 Names Database/pipeline/extractions*.json"

def norm(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii","ignore").decode()
    return re.sub(r"[^a-z ]", "", n.lower()).strip()

def main():
    con = sqlite3.connect(DB)
    for col in ("issue_id INT", "page INT"):
        try: con.execute(f"ALTER TABLE events ADD COLUMN {col}")
        except sqlite3.OperationalError: pass
    con.execute("DELETE FROM articles"); con.execute("DELETE FROM events")
    con.execute("DELETE FROM appearances WHERE role != 'mentioned' AND role != 'mentioned?'")
    # index winch people by normalized "first last"
    pidx = {}
    for pid, name in con.execute("SELECT id, canonical_name FROM people"):
        if "," in name:
            sur, given = [x.strip() for x in name.split(",", 1)]
            given = re.sub(r"\(.*?\)", "", given).strip()
            key = norm(f"{given} {sur}")
            pidx.setdefault(key, []).append(pid)
            # also surname + first token of given
            g1 = given.split()[0] if given.split() else ""
            if g1: pidx.setdefault(norm(f"{g1} {sur}"), []).append(pid)

    def person_id(display_name, source_tag):
        """Find Winch person or create a newspaper-sourced person."""
        key = norm(re.sub(r"\(.*?\)", "", display_name))
        cands = pidx.get(key, [])
        if len(set(cands)) == 1:
            return cands[0], True
        cur = con.execute("SELECT id FROM people WHERE norm_name=? AND source='newspaper'", (key,)).fetchone()
        if cur: return cur[0], False
        c = con.execute("INSERT INTO people(canonical_name, norm_name, source) VALUES(?,?,'newspaper')",
                        (display_name, key))
        pidx.setdefault(key, [])  # don't link future to this automatically
        return c.lastrowid, False

    def issue_id(slug):
        r = con.execute("SELECT id FROM issues WHERE filename=?", (slug,)).fetchone()
        return r[0] if r else None

    linked = created = 0
    for path in sorted(glob.glob(EXT)):
        data = json.load(open(path))
        for a in data.get("articles", []):
            iid = issue_id(a["issue"])
            cur = con.execute("INSERT INTO articles(issue_id, headline, author, article_type, summary, page) VALUES(?,?,?,?,?,?)",
                (iid, a["headline"], a.get("author"), a["type"], a["summary"], a["page"]))
            aid = cur.lastrowid
            # author appearance if resolvable
            auth = a.get("author") or ""
            m = re.match(r"^([A-Z][A-Za-z.'\- ]+?)(?:,| \(|$)", auth)
            if m and len(m.group(1).split()) >= 2:
                pid, was_winch = person_id(m.group(1).strip(), a["issue"])
                con.execute("INSERT INTO appearances(person_id, article_id, role, context, issue_id, page, strength) VALUES(?,?,?,?,?,?,?)",
                            (pid, aid, "author", a["headline"], iid, a["page"], 2))
        for e in data.get("events", []):
            iid = issue_id(e["issue"])
            cur = con.execute("INSERT INTO events(name, event_date, location, description, issue_id, page) VALUES(?,?,?,?,?,?)",
                (e["name"], e.get("date"), e.get("location"), e.get("description"), iid, e["page"]))
            eid = cur.lastrowid
            for nm, role in e.get("attendees", []):
                pid, was_winch = person_id(nm, e["issue"])
                if was_winch: linked += 1
                else: created += 1
                con.execute("INSERT INTO appearances(person_id, event_id, role, context, issue_id, page, strength) VALUES(?,?,?,?,?,?,?)",
                            (pid, eid, role, e["name"], iid, e["page"], 2))
        for g in data.get("agents", []):
            iid = issue_id(g["issue"])
            for nm, role in g.get("names", []):
                pid, was_winch = person_id(nm, g["issue"])
                if was_winch: linked += 1
                else: created += 1
                con.execute("INSERT INTO appearances(person_id, role, context, issue_id, page, strength) VALUES(?,?,?,?,?,?)",
                            (pid, role, g.get("note",""), iid, g["page"], 2))
    con.commit()
    print("articles:", con.execute("SELECT COUNT(*) FROM articles").fetchone()[0],
          "events:", con.execute("SELECT COUNT(*) FROM events").fetchone()[0],
          "linked-to-winch:", linked, "new-people:", created)
    for r in con.execute("""SELECT p.canonical_name, p.source, a.role FROM appearances a JOIN people p ON p.id=a.person_id
                            WHERE a.event_id IS NOT NULL LIMIT 8"""): print(r)

if __name__ == "__main__":
    main()
