# OCR backfill tracker — re-OCR at 300dpi

Created 2026-07-06 per Michiko's request: all pages below were OCR'd at the old
150dpi default and need to be redone at 300dpi (see PIPELINE.md "OCR quality
backfill" section for the procedure). Mark a slug `[x]` once all its pages have
been re-OCR'd and the file overwritten in `ocr_text/`. Order below is the
priority order (Colored American first, then Pennsylvania Freeman, then
Pencil Pusher) — work top to bottom across runs.

## Colored American (26 issues, ~100 pages)
- [x] CA_1837-01-07
- [x] CA_1837-01-14
- [x] CA_1837-01-21
- [x] CA_1837-01-28
- [x] CA_1837-02-04
- [ ] CA_1837-02-11
- [ ] CA_1837-02-18
- [ ] CA_1837-02-22
- [ ] CA_1837-02-25
- [ ] CA_1837-03-04
- [ ] CA_1837-03-11
- [ ] CA_1837-03-18
- [ ] CA_1837-03-25
- [ ] CA_1837-04-01
- [ ] CA_1837-04-08
- [ ] CA_1837-04-15
- [ ] CA_1837-04-22
- [ ] CA_1837-04-29
- [ ] CA_1837-05-06
- [ ] CA_1837-05-13
- [ ] CA_1838-01-13
- [ ] CA_1838-01-20
- [ ] CA_1838-01-27
- [ ] CA_1838-02-03
- [ ] CA_1838-03-15
- [ ] CA_1838-04-12

## Pennsylvania Freeman (4 issues, ~16 pages)
- [ ] PF_1838-01-18
- [ ] PF_1838-01-25
- [ ] PF_1838-02-08
- [ ] PF_1838-02-15

## Pencil Pusher (86 issues, ~86 pages — mostly single-page clippings)
- [ ] PP_000 .. PP_085 (all pending; see ocr_text/ for the full slug list, e.g. `ls ocr_text | grep '^PP_' | sed -E 's/_p[0-9]+\.txt$//' | sort -u`)

## Progress log
- 2026-07-06: List seeded (116 issues / ~204 pages total pending). Backfilled CA_1837-01-07, 01-14, 01-21, 01-28 (16 pages) at 300dpi this session -- overwrote ocr_text/ in place, rebuilt (match_names -> load_extractions -> apply_merges -> find_merge_candidates -> build_viewer), pushed. ~188 pages remain (22 CA issues, 4 PF issues, 86 PP issues).
- 2026-07-06 (7th scheduled run): Backfilled CA_1837-02-04 (4 pages) at 300dpi -- page 4 timed out at 300dpi even at 43s, dropped to 200dpi per the documented fallback and it completed in 32s. Overwrote ocr_text/CA_1837-02-04_p*.txt in place. ~184 pages remain (21 CA issues, 4 PF issues, 86 PP issues, plus new CA_1837-05-20/05-27/06-03/06-10/06-17 issues processed this run at native 300dpi so they never need backfill).
- Note on OCR tool flakiness: the first `tesseract` call on a just-rendered 300dpi page consistently produces an empty file or errors ("Error during processing" / timeout) — an immediate retry on the same .pgm file succeeds reliably. Budget 2 tesseract attempts per page when estimating run time.
