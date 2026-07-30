# Batch processing pipeline — 1838 Black Metropolis names database

Instructions for any Claude session continuing this project. Priority order: **Pencil Pusher** first, then **Freedoms Journal**, then remaining Colored American / Pennsylvania Freeman issues.

## ⚠️ PROD PUSH FAILSAFE (Michiko, 2026-07-29)
Before ANY push to production (`1838BlackMetropolis/NamesDB`), you MUST ask Michiko for the prod-push password in the chat and only proceed if she gives the correct one. This gate applies to every "promote" — no exceptions, even if she just said "promote". Staging (`michiQ/1838Names`) pushes do NOT require the password. The password value and the production PAT are stored OUTSIDE this repo and outside Google Drive (in `~/.ssh/`, mode 600) so they never get committed or synced — never write either to git or Drive, and never echo them in output.

## Setup (each run)
1. The working folder is `<Newspapers>/1838 Names Database/` (this folder). Scripts are in `pipeline/`.
2. Copy `black_metropolis.db` from this folder to `/tmp/black_metropolis.db` (SQLite can't journal on the cloud mount).
3. Paths inside scripts reference a session mount like `/sessions/<name>/mnt/...` — adjust to the current session's mount paths (see the Shell access section of the system prompt).

## Per-issue processing (repeat for as many issues as the run allows, ~10-15 issues)
1. Pick the next unprocessed PDF (not present as `ocr_text/<slug>_p1.txt`). Slug format: `PP_<n>` for Pencil Pusher files (use the number in the filename, e.g. `PENCIL_PUSHER_POINTS (23).pdf` → `PP_023`; the plain one → `PP_000`), `FJ_<yyyy-mm-dd>` for Freedoms Journal.
2. Hydrate the cloud-only PDF: run the Grep tool on the HOST path of the PDF (pattern `%PDF`, output_mode count). Bash reads fail with "Resource deadlock avoided" until this is done.
3. OCR one page per bash call (45s limit). Default resolution is now **300dpi** (changed from 150dpi on 2026-07-06 at Michiko's request — meaningfully fewer character-level misreads on body text, worth the extra time): `pdftoppm -f N -l N -r 300 -gray <pdf> /tmp/w/pg` then `tesseract /tmp/w/pg-N.pgm - --psm 3 > ocr_text/<slug>_pN.txt`. This takes ~30s/page, still within the 45s limit but with less margin. If a page times out, drop resolution in this order: 300 → 200 → 150 → 100. Pencil Pusher files are single clippings — often 1 page.
   - Note: the ornate masthead title font and recurring "Terms of the Paper"/agent-list boilerplate on Colored American pages will OCR poorly regardless of resolution (stylized/tiny font) — this is expected and low-value text anyway; don't burn extra effort trying to clean it up. Column-cropping was tested (2026-07-06) and didn't add meaningful quality over the resolution bump alone, so it's not part of the pipeline.
4. NOTE: Pencil Pusher is W.C. Bolivar's "Pencil Pusher Points" column from the Philadelphia Tribune (early 1900s) — it is retrospective history naming many 1830s-40s figures. Treat each clipping as one `article` (headline "Pencil Pusher Points", author "William Carl Bolivar") and write a 2-3 sentence summary after reading the OCR text.
5. Register the issue in `issues` (newspaper_id: look up by name; add 'Philadelphia Tribune (Pencil Pusher)' if needed), then run `match_names.py` logic to cross-match Winch names (script rebuilds ALL appearances from ocr_text/, so just run it after adding new pages — it re-registers issues too; it needs slug prefix→paper mapping updated for PP_ and FJ_).
6. For high-value pages (meetings, event rosters, articles with authors), read the OCR text and append structured extractions to a new `extractions<N>.json` following the schema in existing extractions*.json, then run `load_extractions.py`.

## Finish (each run)
1. For every newly processed issue: (a) render page JPEGs into `pages/` named `<slug>_pN.jpg` (`pdftoppm -jpeg -jpegopt quality=68 -r 110` — use `-r 90` for oversized scans; rename `_p-N` to `_pN`); (b) look up the PDF's Google Drive viewUrl via the Drive connector `search_files` and add it to `pipeline/issue_urls.json`. The viewer's "view page" / "full issue" links depend on both.
2. Run `build_viewer.py` (regenerates the viewer; update its PAPERS slug-prefix map for new papers).
3. Copy `/tmp/black_metropolis.db` back over `black_metropolis.db` in this folder, and the regenerated viewer HTML to BOTH `1838_black_metropolis_viewer.html` and `index.html` (the GitHub Pages copy).
3. Update `progress.txt` in this folder: which files are done, any problem PDFs.
4. GitHub auto-push: if `pipeline/github_token.txt` exists, clone https://github.com/michiQ/1838Names.git, sync index.html / black_metropolis.db / pages/ / ocr_text/ / pipeline/ (EXCLUDING github_token.txt — never commit it), commit and push with `git push "https://x-access-token:<token>@github.com/michiQ/1838Names.git" main`. Skip gracefully if the token file is absent or expired.
5. Message summary: issues processed, new people matched, notable finds, whether GitHub was updated.

## Census datasets (loaded)
The DB contains `census_1838` (PAS census, 3,296 households), `census_1847` (SOFAAC, 4,284), `census_matches` (445 confirmed 1838↔1847 matches), and `census_links` (person↔household). ALL heads of household exist as `people` rows (source='census') unless they matched a Winch person unambiguously. Source files live in `../census/`. ORDER MATTERS each run: `import_census.py` (recreates census people) must run BEFORE `match_names.py` and `load_extractions.py`, else appearances reference deleted people ids. Full rebuild order: import_census.py → import_1820_directory.py → match_names.py → load_extractions.py → apply_merges.py → load_nolibs.py → find_merge_candidates.py → build_viewer.py. (See "1820 Philadelphia directory" section below for the new import_1820_directory.py step, added 2026-07-10.)

## 1820 Philadelphia directory (loaded 2026-07-10)
`pipeline/import_1820_directory.py` imports `pipeline/1820_directory_source.csv` (1,654 rows —
Michiko's cross-marked "†" extraction of Black residents from the 1820 Philadelphia city
directory; columns First Name/Second Name/Occupation/Address/PDF Page/Confidence/Needs
Review/Original OCR Entry). CSV name order is directory-style surname-first: "First Name" holds
the SURNAME, "Second Name" holds the GIVEN name (verified against the Original OCR Entry text,
which is itself surname-then-given). Loads the raw rows into table `directory_1820` and links each
row to a person via table `directory_links(person_id, directory='1820', row_id)` — same shape as
`census_links`. Matching mirrors `import_census.py`: build an index of Winch people (source='winch')
by normalized "given surname", using BOTH `canonical_name` and any confirmed `aliases` (so a name
merged via merges.json in an earlier run, e.g. "John Bowers" as an alias of "Bowers, John C.", is
matchable too); a directory row links to a Winch person only if the name match is unambiguous
(exactly one candidate), otherwise it becomes a brand-new person record tagged source=
'1820directory'. NEVER auto-merges — ambiguous or unmatched rows always get their own new person.
One deliberate departure from `import_census.py`: it does NOT cache/dedupe same-name rows within
the source into one person (census does, via its `cidx`). A check of this CSV found 120 rows
(~60 name-pairs, e.g. two different "Adams, John" entries with different occupations/addresses)
that share a name but are evidently different individuals — deduping by name would have silently
merged them, so every unmatched row gets its own record instead.
Run it alongside `import_census.py`, before `match_names.py` (it only touches `people` and its own
`directory_1820`/`directory_links` tables, same as census, so ordering relative to appearances
doesn't matter — but PIPELINE.md's rebuild order groups all source imports first for consistency).
Full rebuild order is now: import_census.py → import_1820_directory.py → match_names.py →
load_extractions.py → apply_merges.py → load_nolibs.py → find_merge_candidates.py → build_viewer.py.
`build_viewer.py` attaches directory rows to each person (like census) as a `directory` list
(occupation/address/PDF page/confidence/needs-review/OCR text) — no graph edges synthesized from
it, same as census. `find_merge_candidates.py` and `apply_merges.py` were both updated to count/
reassign `directory_links` alongside `census_links` etc. The viewer template gained a "1820
directory" filter chip, a `b-d` source badge, and a detail-panel card section for directory
records. Known data-quality artifact: one source row ("Blackston, Catharine") has an OCR
column-shift where non-numeric text landed in the PDF Page/Confidence columns — loaded as TEXT so
it doesn't crash the import; flagged in that row's own Needs Review text for Michiko to fix
upstream in the CSV if desired.

## Viewer changes — MANDATORY smoke test
Before pushing ANY change to viewer_template.html, run `node pipeline/smoke_test.js <built index.html>`. It executes both script blocks with a stubbed DOM and fails on runtime errors (a TDZ ordering bug shipped on 2026-07-06 and blanked the site; syntax checks alone do not catch this class of error).

## "All connections" map layout — baked precompute (added 2026-07-28)
The full-network map used to run community detection + a 260-tick force settle over ~1131
nodes synchronously every time it opened, which froze the tab (~0.5-5s on real devices).
Three viewer-only changes fixed this (no data/DB change; every other view untouched):
- **Baked layout (instant first open):** `pipeline/precompute_fullmap.js` (headless Chromium)
  opens the built viewer, lets the map settle, and dumps the settled positions/communities to
  `pipeline/fullmap_layout.json` (~56KB). `build_viewer.py` injects that file into the
  `/*__FULLMAP__*/null` placeholder as `BAKED_FULLMAP`; the viewer restores it on first open and
  skips the settle (measured 2308ms -> 27ms). It is an OPTIONAL, MANUAL step (needs Playwright) —
  NOT part of the core rebuild. Refresh after a data change with `node pipeline/precompute_fullmap.js`
  then rebuild. If the file is missing or the node set changed, the viewer detects the mismatch
  (`nodes.every(... cache.has ...)` in buildFullGraph) and settles live — so a stale/absent file is safe.
- **Non-blocking settle (fallback):** when it does settle live, it now runs a few ticks per frame
  via `window._bigSettle` in draw() instead of one blocking loop, so the tab never freezes.
- **In-session cache:** after any live settle, positions are cached in `window._fullLayoutCache`
  so reopening the map is instant even without the baked file.
build_viewer.py stays runnable with NO Playwright (it just reads the JSON if present); only the
optional refresh script needs it.

## Person merges
`pipeline/merges.json` is the curated list of duplicate-person merges (e.g. "J. J. G. Bias" = "Bias, James J. G."). `apply_merges.py` applies it (idempotent): reassigns appearances/references/census links to the kept person, records the other spellings in `people.aliases`, dedupes appearances. It MUST run after the other imports (they recreate alias people) and before build_viewer. When Michiko identifies new duplicates, append a group to merges.json — never edit the DB by hand.

`find_merge_candidates.py` runs every rebuild and regenerates `pipeline/merge_candidates.md` — a ranked review list of likely duplicates (initial-expansions, cross-source name matches, OCR variants). It NEVER merges automatically. In each run summary, mention the 3-5 strongest NEW candidates so Michiko can confirm them in chat.

## State
- Done so far: 10 pilot issues (CA_1838-*, PF_1838-*) — see ocr_text/.
- The Winch reference is fully loaded (2,909 people / 4,565 refs). Do NOT re-run build_db.py — it wipes and rebuilds people from the Winch PDF (only do this if the DB is lost; the Winch PDF is in this folder as backup: Julie Winch Names Reference).

## OCR quality backfill (added 2026-07-06, per Michiko)
All pages OCR'd before 2026-07-06 were done at 150dpi. Michiko asked to re-OCR all of them at the new 300dpi default. This is a large job (~204 pages across CA/PF/PP as of 2026-07-06) that will span many runs. **Until `pipeline/reocr_backfill.md` shows everything done, spend part of every run's budget on backfill before (or interleaved with) new-issue processing** — Michiko's priority is fixing the existing Colored American data first since that's what she's actively reviewing.
1. Read `pipeline/reocr_backfill.md` for the current pending list.
2. For each pending slug: hydrate its PDF (Grep %PDF trick), re-run OCR at 300dpi per the per-issue steps above, overwriting the existing `ocr_text/<slug>_pN.txt` files in place.
3. After re-OCRing a batch, re-run the full rebuild (import_census.py → match_names.py → load_extractions.py → apply_merges.py → load_nolibs.py → find_merge_candidates.py → build_viewer.py) — match_names.py rebuilds ALL appearances from ocr_text/ every time, so this picks up the cleaner text automatically. No changes needed to extractions*.json (those are hand-curated summaries, independent of raw OCR quality).
4. Mark completed slugs done in `pipeline/reocr_backfill.md` and update the count in progress.txt.
5. Once the backfill list is fully done, remove this section and go back to strictly new-issue processing order.

## Northern Liberties tour profiles (added 2026-07-26)
`pipeline/load_nolibs.py` loads `pipeline/nolibs_profiles.json` — curated biographies for the
people in the "Northern Liberties Tour Sources" PDF (a 1838 Black Metropolis document) — onto the
matching people, plus a page-anchored citation linking to `Northern_Liberties_Tour_Sources.pdf`
(kept in the repo root / Drive folder, served alongside index.html). Runs AFTER apply_merges (so
renames/unifications are final) and BEFORE find_merge_candidates/build_viewer. Idempotent:
rebuilds the `nolibs_profiles` table from scratch each run, re-resolving every person by
census-row / canonical-name each time (census people are recreated with new ids every rebuild, so
the profiles MUST be re-resolved — that's why this step exists rather than hand-editing rows). It
also creates the two people the tour documents who are absent from the source data (Rebecca
McCormick, James Julius Jr.) and trims Hetty Burr's sketch out of the 'Burr, David T.' record.
build_viewer.py attaches these as a person's `nolibs` list; viewer_template.html renders a
"Northern Liberties tour" detail card with the clickable page link.
Full rebuild order is now: import_census.py -> import_1820_directory.py -> match_names.py ->
load_extractions.py -> apply_merges.py -> load_nolibs.py -> find_merge_candidates.py -> build_viewer.py.

## William Still's Underground Railroad appearances (added 2026-07-27)
`pipeline/load_ugrr.py` loads `pipeline/ugrr_appearances.json` — appearances of people in
William Still's *The Underground Rail Road* (Philadelphia, 1872; Internet Archive item
`undergroundrailr00lcstil`, OCR source in Drive `Newspapers/Underground Railroad/`). Each entry
ties a person to the CHAPTER they appear in and a page-anchored Internet Archive link. Runs
AFTER load_nolibs and BEFORE find_merge_candidates/build_viewer. Idempotent: rebuilds the
`ugrr_appearances` table each run and re-resolves people by canonical name + source; book-only
people are created source='ugrr' (aliases stored when known).

Build method (working scripts in `pipeline/ugrr_build/`): the table of contents was parsed into
210 chapters with body-anchored page numbers (running-header page map cross-checked vs the TOC);
the named freedom-seekers + helpers in each chapter title/subtitle were extracted; each was
matched to an existing curated person or created new. Matching rules, tuned for precision: only
role='helper' abolitionists LINK to existing DB people (freedom-seekers are always created new,
since a post-1850 escapee rarely IS a same-named 1838 free Philadelphian — find_merge_candidates
surfaces any true overlap); initial-only given names link only on rare/unique surnames; bare-
surname DB rows never link. Sarah Ash ("Woman Escaping in a Box") is a curated mid-narrative link.

The Internet Archive link uses the CHAPTER page + 2 (two front-matter leaves in the scan, so
printed p.608 is leaf 610) and ?q=<surname> to highlight the name, e.g.
https://archive.org/details/undergroundrailr00lcstil/page/610/mode/1up?q=ash . build_viewer.py
attaches these as a person's `ugrr` list; viewer_template.html renders an "Underground Railroad
(William Still)" detail card, a "UGRR" badge (b-u), and an "Underground Railroad" filter chip.
KNOWN GAP: the mid-book "ARRIVAL FROM <place>, <year>" chapters (pp. ~136-600) name their
freedom-seekers only in body prose, not the TOC, so those are not yet captured (future body pass).
The full book OCR text is now committed at `pipeline/ugrr_build/undergroundrailr00lcstil_hocr_searchtext.txt`
(2.66MB, the Internet Archive hOCR search text) — grep it to find those body-prose names for the
future pass, and to check any given name/page before hand-adding an entry. (2026-07-27: added
Mrs. Myers — "Woman Escaping in a Box", p.608, linked to the census person MYERS, RACHEL per
Michiko's identification (not a standalone person) — and John Myers — body sub-heading under
"Arrival from Harford County", p.434, a new ugrr person — this way, as curated mid-narrative links
exactly like Sarah Ash.)
Full rebuild order is now: import_census.py -> import_1820_directory.py -> match_names.py ->
load_extractions.py -> load_coppin.py -> load_storymaps.py -> split_nichols.py -> apply_merges.py ->
load_nolibs.py -> load_ugrr.py -> load_blogs.py -> apply_merges.py (2nd pass) -> find_merge_candidates.py -> build_viewer.py.
apply_merges runs TWICE: pass 1 folds the winch/census/newspaper/coppin/storymap groups so load_nolibs/
load_ugrr resolve against canonical names; pass 2 (after load_blogs) folds the blog-source groups, since
blog people don't exist until load_blogs runs. apply_merges is idempotent so pass 2 re-checks pass-1 groups
as no-ops. IMPORTANT: merges that fold a record into a MERGED-AWAY id break on rebuild (the id is gone and
the loader recreates the record with a new id) -- key such groups on a stable id (winch/census never
reassigned) or on {name, source} which matches the recreated record. A working driver for the last several
steps lives at /tmp/rebuild.sh in-session; loaders read env BM_DB and, per-loader,
COPPIN_SRC/STORYMAPS_SRC/UGRR_SRC/BLOGS_SRC.

## 1838 Black Metropolis blog archive (added 2026-07-30)
`pipeline/load_blogs.py` loads `pipeline/blogs.json` (74 posts, each {slug,title,blog_url,pdf,people[]}).
Each post is its own source ("newspaper"): a row in `blogs` (slug,title,url,pdf) and, per person named,
a `blog_appearances` row (person_id, slug, snippet). Names were extracted per-post (every person named,
excluding modern authors/cited scholars). load_blogs resolves each name to an EXISTING person where the
full name is a confident unique match (exact identity-token set, Jr/Sr kept; else unique surname+first-given);
ambiguous or unmatched names are created as source='blog' people so no connection is dropped, and are
surfaced in `pipeline/blog_matches.md` for Michiko to merge/prune via merges.json (same review flow as ICY/
StoryMaps -- nothing is force-merged). The person card shows each post's title + snippet + View Blog (live
URL) and View PDF (hosted `blogs/<pdf>`); the 74 PDFs are committed under `blogs/`. Runs AFTER the other
loaders (links to final canonical nodes), BEFORE find_merge_candidates/build_viewer. Idempotent.
To refresh a post's people, re-extract into blogs.json and rerun; blog people with no other data stay out
of the "All connections" map (they have no person-person edges) but remain searchable/filterable ("Blog Archive").

## Samuel Nichols split (added 2026-07-30)
`pipeline/split_nichols.py` moves the 7 mis-parsed Samuel Nichols winch notes off the Winch "Newton, Mary"
record onto a dedicated "Nichols, Samuel" winch person, so only the Female Vigilant Committee note follows
the merge of "Newton, Mary" -> "Mary Lewton" (merges.json). Idempotent; runs BEFORE apply_merges; no-op once
"Newton, Mary" has been merged away.
