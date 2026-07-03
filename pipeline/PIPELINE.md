# Batch processing pipeline — 1838 Black Metropolis names database

Instructions for any Claude session continuing this project. Priority order: **Pencil Pusher** first, then **Freedoms Journal**, then remaining Colored American / Pennsylvania Freeman issues.

## Setup (each run)
1. The working folder is `<Newspapers>/1838 Names Database/` (this folder). Scripts are in `pipeline/`.
2. Copy `black_metropolis.db` from this folder to `/tmp/black_metropolis.db` (SQLite can't journal on the cloud mount).
3. Paths inside scripts reference a session mount like `/sessions/<name>/mnt/...` — adjust to the current session's mount paths (see the Shell access section of the system prompt).

## Per-issue processing (repeat for as many issues as the run allows, ~10-15 issues)
1. Pick the next unprocessed PDF (not present as `ocr_text/<slug>_p1.txt`). Slug format: `PP_<n>` for Pencil Pusher files (use the number in the filename, e.g. `PENCIL_PUSHER_POINTS (23).pdf` → `PP_023`; the plain one → `PP_000`), `FJ_<yyyy-mm-dd>` for Freedoms Journal.
2. Hydrate the cloud-only PDF: run the Grep tool on the HOST path of the PDF (pattern `%PDF`, output_mode count). Bash reads fail with "Resource deadlock avoided" until this is done.
3. OCR one page per bash call (45s limit): `pdftoppm -f N -l N -r 150 -gray <pdf> /tmp/w/pg` then `tesseract /tmp/w/pg-N.pgm - --psm 3 > ocr_text/<slug>_pN.txt`. Drop to `-r 100` if a page times out. Pencil Pusher files are single clippings — often 1 page.
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

## State
- Done so far: 10 pilot issues (CA_1838-*, PF_1838-*) — see ocr_text/.
- The Winch reference is fully loaded (2,909 people / 4,565 refs). Do NOT re-run build_db.py — it wipes and rebuilds people from the Winch PDF (only do this if the DB is lost; the Winch PDF is in this folder as backup: Julie Winch Names Reference).
