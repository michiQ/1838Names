#!/usr/bin/env python3
"""Business ads page (added 2026-11-01 at Michiko's request).

Builds ads.html at the repo root: every advertisement in the database, shown as a picture cropped
from its newspaper page, with the advertiser linked to their record (index.html#p<id>).
Crop boxes live in pipeline/ad_crops.json, keyed by issue + page + headline (article ids shift
between rebuilds); the addresses printed in the ads live in pipeline/ad_addresses.json, keyed the same way. Crops are written to ads/<issue>_p<page>_<n>.jpg. Run after build_viewer.py
(build_viewer calls it at the end).
"""
import json, os, re, sqlite3, html
from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.environ.get("BM_DB", "/tmp/black_metropolis.db")
PAPERS = {"CR": "Christian Recorder", "FJ": "Freedom's Journal"}
MONTHS = "January February March April May June July August September October November December".split()


def nice_date(slug):
    m = re.search(r"_(\d{4})-(\d\d)-(\d\d)", slug)
    return f"{MONTHS[int(m.group(2)) - 1]} {int(m.group(3))}, {m.group(1)}" if m else ""


def clean_head(h):
    h = re.sub(r"\s*\((?:advertisements?|advertisement,[^)]*)\)\s*$", "", h, flags=re.I)
    h = re.sub(r"^Business notice:\s*", "", h, flags=re.I)
    h = re.sub(r"\s+(?:\u2014|--)\s+", ", ", h)   # no em dashes in titles (Michiko's preference)
    return h.strip()


def display_name(n):
    m = re.match(r"^([^,]+),\s*(.+)$", n or "")
    if m and not re.match(r"^(Jr|Sr)\.?$", m.group(2)):
        g = re.match(r"^(.*?)\s+((?:Jr|Sr)\.?)$", m.group(2))
        n = f"{g.group(1)} {m.group(1)} {g.group(2)}" if g else f"{m.group(2)} {m.group(1)}"
    return n.title() if n.isupper() else n


def main():
    crops = json.load(open(os.path.join(HERE, "ad_crops.json"), encoding="utf-8"))
    key = lambda iss, pg, hl: f"{iss}|{pg}|{hl}"
    boxes = {key(c["issue"], c["page"], c["headline"]): c for c in crops["ads"]}
    # business addresses as printed in the ad (added 2026-11-03); plain text, never linked
    addrs = {key(a["issue"], a["page"], a["headline"]): a["address"]
             for a in json.load(open(os.path.join(HERE, "ad_addresses.json"), encoding="utf-8"))["ads"]}
    con = sqlite3.connect(DB)
    rows = con.execute("""SELECT a.id, i.filename, a.page, a.headline, a.summary FROM articles a
                          JOIN issues i ON i.id = a.issue_id WHERE a.article_type = 'advertisement'
                          ORDER BY i.filename, a.page, a.id""").fetchall()
    os.makedirs(os.path.join(ROOT, "ads"), exist_ok=True)
    out, n_by_page, missing = [], {}, []
    for aid, iss, pg, hl, sm in rows:
        c = boxes.get(key(iss, pg, hl))
        if c and c.get("philadelphia") is False:
            continue   # out-of-town ad: kept in the DB, left off the page (Michiko, 2026-11-03)
        if not c or not c.get("box"):
            missing.append(f"{iss} p{pg} {hl}"); continue
        n_by_page[(iss, pg)] = n_by_page.get((iss, pg), 0) + 1
        fn = f"ads/{iss}_p{pg}_{n_by_page[(iss, pg)]}.jpg"
        im = Image.open(os.path.join(ROOT, "pages", f"{iss}_p{pg}.jpg")).convert("L")
        W, H = im.size
        x0, y0, x1, y1 = c["box"]
        crop = ImageOps.autocontrast(im.crop((int(W * x0), int(H * y0), int(W * x1), int(H * y1))), cutoff=1)
        crop.save(os.path.join(ROOT, fn), "JPEG", quality=85)
        ppl, seen = [], set()
        for pid, nm, role in con.execute("""SELECT p.id, p.canonical_name, ap.role FROM appearances ap
                                            JOIN people p ON p.id = ap.person_id WHERE ap.article_id = ?""", (aid,)):
            if pid in seen: continue
            seen.add(pid); ppl.append([pid, display_name(nm)])
        out.append({"img": fn, "issue": iss, "paper": PAPERS.get(iss[:2], iss[:2]), "date": nice_date(iss),
                    "iso": iss.split("_")[1], "page": pg, "title": clean_head(hl), "people": ppl,
                    "addr": addrs.get(key(iss, pg, hl), []), "where": c.get("where", ""), "note": c.get("note_public", "")})
    tpl = open(os.path.join(HERE, "ads_template.html"), encoding="utf-8").read()
    page = tpl.replace("/*__ADS__*/[]", json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    open(os.path.join(ROOT, "ads.html"), "w", encoding="utf-8").write(page)
    print("ads page:", len(out), "ads |", sum(1 for a in out if a["addr"]), "with an address |", len(missing), "without a crop box")
    for m in missing: print("   no crop:", m)


if __name__ == "__main__":
    main()
