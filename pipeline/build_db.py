#!/usr/bin/env python3
"""Build the 1838 Black Metropolis names database.
Schema + Winch reference parser."""
import sqlite3, re, sys, unicodedata

DB = "/tmp/black_metropolis.db"
WINCH = "/tmp/winch.txt"

SCHEMA = """
CREATE TABLE IF NOT EXISTS newspapers(
  id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS issues(
  id INTEGER PRIMARY KEY, newspaper_id INT REFERENCES newspapers(id),
  issue_date TEXT, filename TEXT UNIQUE, ocr_status TEXT DEFAULT 'pending');
CREATE TABLE IF NOT EXISTS articles(
  id INTEGER PRIMARY KEY, issue_id INT REFERENCES issues(id),
  headline TEXT, author TEXT, article_type TEXT, -- news|editorial|letter|notice|minutes|ad|poem
  summary TEXT, page INT);
CREATE TABLE IF NOT EXISTS people(
  id INTEGER PRIMARY KEY, canonical_name TEXT, norm_name TEXT,
  life_dates TEXT, winch_entry TEXT, source TEXT DEFAULT 'winch');
CREATE INDEX IF NOT EXISTS idx_people_norm ON people(norm_name);
CREATE TABLE IF NOT EXISTS winch_references(
  id INTEGER PRIMARY KEY, person_id INT REFERENCES people(id),
  note TEXT, citation TEXT);
CREATE TABLE IF NOT EXISTS events(
  id INTEGER PRIMARY KEY, name TEXT, event_date TEXT, location TEXT,
  description TEXT, article_id INT REFERENCES articles(id));
CREATE TABLE IF NOT EXISTS appearances(
  id INTEGER PRIMARY KEY, person_id INT REFERENCES people(id),
  article_id INT REFERENCES articles(id), event_id INT REFERENCES events(id),
  role TEXT, -- author|mentioned|attendee|officer|chair|secretary|speaker|signer|agent
  context TEXT);
CREATE INDEX IF NOT EXISTS idx_app_person ON appearances(person_id);
"""

BOILER = re.compile(
    r"^(The 1838 Black Metropolis Julie Winch Database|CC BY-SA|Page \d+|"
    r"The Julie Winch 1838 Black Metropolis Names Reference|Sources/Abbreviations)")
# Name header: Surname, First ...  optionally with (dates). Short line, no trailing period-sentence.
NAME_RE = re.compile(
    r"^([A-Z][A-Za-z'\-]+(?: [A-Z][A-Za-z'\-]+)?, (?:or [A-Z][A-Za-z'\-]+ )?"
    r"[A-Z][A-Za-z.'\-]*(?:[ -][A-Za-z.'()’\-]+){0,4})"
    r"\s*(\(.*?\))?\s*$")
CITE_RE = re.compile(r"\(([^()]{3,120}?)\)\s*$")
STOP_FIRST = {
 "vice-president","vice-pres.","co-founder","ex-officio","member","members","marshal","officer","officers","deacon","rev","committee","secretary",
 "treasurer","trustee","trustees","president","vice","elder","vestryman","manager","managers",
 "delegate","delegates","steward","grand","director","directors","teacher","preacher","minister",
 "pastor","agent","subscriber","contributor","attends","attended","born","died","dead","signs",
 "signer","sons","daughters","census","directories","directory","buried","baptized","married",
 "marries","joins","founder","chairman","chair","counsellor","captain","sergeant","private",
 "corporal","lieutenant","colonel","exhorter","licensed","local","class","leader","one","also",
 "listed","appointed","elected","moves","dies","widow","wife","husband","daughter","son","brother",
 "sister","mother","father","see","possibly","probably","later","free","slave","enslaved","works",
 "speaker","supporter","organizer","assistant","superintendent","collector","auditor","librarian",
 "porter","waiter","labourer","laborer","mariner","barber","oysterman","carpenter","shoemaker"}

def norm(name):
    n = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z ]", "", n.lower()).strip()

def parse_winch(path):
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    entries = []  # (name, dates, [note lines])
    cur = None
    started = False
    for raw in lines:
        ln = raw.replace("​", "").rstrip()
        if not ln.strip() or BOILER.search(ln.strip()):
            continue
        if not started:
            # skip preamble until first single-letter section marker like "A"
            if re.fullmatch(r'"?[A-Z]"?', ln.strip()):
                started = True
            continue
        if re.fullmatch(r'"?[A-Z]"?', ln.strip()):
            continue  # section letter
        m = NAME_RE.match(ln.strip())
        # Heuristic: name lines are short and contain a comma early
        first = ln.strip().split(",")[0].strip().lower()
        if m and len(ln.strip()) < 60 and "," in ln[:30] and first not in STOP_FIRST:
            if cur: entries.append(cur)
            cur = {"name": m.group(1).strip(), "dates": (m.group(2) or "").strip("() "), "notes": []}
        elif cur:
            cur["notes"].append(ln.strip())
    if cur: entries.append(cur)
    return entries

def group_notes(notes):
    """Group note lines into (note, citation) pairs. A citation line like (Lib., ...) attaches to preceding note."""
    refs, buf = [], []
    for ln in notes:
        cm = CITE_RE.match(ln.strip()) if ln.strip().startswith("(") else None
        if cm:
            refs.append((" ".join(buf).strip(), cm.group(1)))
            buf = []
        else:
            m = CITE_RE.search(ln)
            if m and len(m.group(1)) > 5 and any(c.isdigit() for c in m.group(1)):
                pre = ln[:m.start()].strip()
                buf.append(pre)
                refs.append((" ".join(buf).strip(), m.group(1)))
                buf = []
            else:
                buf.append(ln.strip())
    if buf:
        refs.append((" ".join(buf).strip(), None))
    return [(n, c) for n, c in refs if n or c]

def main():
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    for p in ["Colored American", "Freedom's Journal", "Pennsylvania Freeman",
              "Pencil Pusher (Philadelphia Tribune)", "The Liberator",
              "The North Star", "Moral Reformer"]:
        con.execute("INSERT OR IGNORE INTO newspapers(name) VALUES(?)", (p,))
    entries = parse_winch(WINCH)
    print(f"parsed {len(entries)} entries")
    for e in entries:
        full = "\n".join(e["notes"])
        cur = con.execute(
            "INSERT INTO people(canonical_name, norm_name, life_dates, winch_entry) VALUES(?,?,?,?)",
            (e["name"], norm(e["name"]), e["dates"] or None, full))
        pid = cur.lastrowid
        for note, cite in group_notes(e["notes"]):
            con.execute("INSERT INTO winch_references(person_id, note, citation) VALUES(?,?,?)",
                        (pid, note or None, cite))
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM people").fetchone()[0]
    r = con.execute("SELECT COUNT(*) FROM winch_references").fetchone()[0]
    print(f"people={n} refs={r}")

if __name__ == "__main__":
    main()
