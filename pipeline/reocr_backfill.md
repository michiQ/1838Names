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
- [x] CA_1837-02-11 (2-page issue; both pages redone at 300dpi 2026-07-10, 18th scheduled run)
- [x] CA_1837-02-18 (all 4 pages redone at 300dpi 2026-07-10, 18th scheduled run)
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
- [ ] CA_1837-08-19 (only p1 is at 300dpi; p2 at 200dpi, p3/p4 at 100dpi -- sandbox was under heavy CPU load during the 2026-07-07 10th scheduled run and 300dpi tesseract calls kept timing out even after retries)
- [ ] CA_1837-08-26 (all 4 pages at 100dpi, same load-driven fallback as above)
- [ ] CA_1837-09-02 (all 4 pages at 100dpi, same load-driven fallback as above)
- [ ] CA_1837-10-21 (all 4 pages at 200dpi -- sandbox under load during the 2026-07-08 12th scheduled run, 300dpi tesseract calls timed out even after a retry)
- [ ] CA_1837-10-28 (all 4 pages at 200dpi, same load-driven fallback as above)
- [ ] CA_1837-11-04 (all 4 pages at 200dpi, same load-driven fallback as above)
- [ ] CA_1837-11-11 (all 4 pages at 200dpi, same load-driven fallback as above)

## Pennsylvania Freeman (4 issues, ~16 pages)
- [ ] PF_1838-01-18
- [ ] PF_1838-01-25
- [ ] PF_1838-02-08
- [ ] PF_1838-02-15

## Freedoms Journal (1 issue, 1 page)
- [x] FJ_1827-04-06 (p2 only -- DONE 2026-07-10 (17th scheduled run): re-OCR'd at full 300dpi by splitting the render (pdftoppm) and OCR (tesseract) into separate bash calls to dodge the 45s wall; 21,731 bytes, overwritten in place and picked up by that run's full rebuild. Previously: 300dpi timed out on the 2026-07-09 6th-batch run, was at 200dpi.)

## Pencil Pusher (86 issues, ~86 pages — mostly single-page clippings)
- [ ] PP_000 .. PP_085 (all pending; see ocr_text/ for the full slug list, e.g. `ls ocr_text | grep '^PP_' | sed -E 's/_p[0-9]+\.txt$//' | sort -u`)

## Progress log
- 2026-07-10 (18th scheduled run): Backfilled CA_1837-02-11 (2 pages — it is a 2-page issue, matching its 2 existing ocr_text files) and CA_1837-02-18 (4 pages) at full 300dpi, all first-attempt, overwritten in place and picked up by this run's full rebuild. Remaining: 30 CA/PF issues + 86 PP issues.
- 2026-07-10 (17th scheduled run): Backfilled FJ_1827-04-06_p2 at 300dpi (the only FJ pending item — FJ section now clear). All 20 pages of this run's 5 new FJ issues hit native 300dpi (one page needed the split render/OCR two-call trick), so no new entries. Remaining: 32 CA/PF issues + 86 PP issues.
- 2026-07-06: List seeded (116 issues / ~204 pages total pending). Backfilled CA_1837-01-07, 01-14, 01-21, 01-28 (16 pages) at 300dpi this session -- overwrote ocr_text/ in place, rebuilt (match_names -> load_extractions -> apply_merges -> find_merge_candidates -> build_viewer), pushed. ~188 pages remain (22 CA issues, 4 PF issues, 86 PP issues).
- 2026-07-06 (7th scheduled run): Backfilled CA_1837-02-04 (4 pages) at 300dpi -- page 4 timed out at 300dpi even at 43s, dropped to 200dpi per the documented fallback and it completed in 32s. Overwrote ocr_text/CA_1837-02-04_p*.txt in place. ~184 pages remain (21 CA issues, 4 PF issues, 86 PP issues, plus new CA_1837-05-20/05-27/06-03/06-10/06-17 issues processed this run at native 300dpi so they never need backfill).
- Note on OCR tool flakiness: the first `tesseract` call on a just-rendered 300dpi page consistently produces an empty file or errors ("Error during processing" / timeout) — an immediate retry on the same .pgm file succeeds reliably. Budget 2 tesseract attempts per page when estimating run time.
- 2026-07-07 (10th scheduled run): sandbox was unusually slow all session (load average climbed from ~4 to ~7 on a 4-core box over the course of the run); even repeated retries at 300/200/150dpi kept hitting the 45s wall on most pages, so the 3 new issues processed this run (CA_1837-08-19/08-26/09-02) were OCR'd mostly at 100dpi rather than the 300dpi default -- added to this backfill list above rather than skipped, since the intent of the backfill tracker is "every page ends up at 300dpi eventually," not just pre-2026-07-06 pages. Did not touch the pre-existing backfill queue this run (25 items were already pending; still 25 pending, now +3 more added at the bottom of the CA section). Total remaining: ~184 pre-existing pages (21 CA + 4 PF + 86 PP, unchanged) + 3 new issues (11 sub-300dpi pages) = effectively 28 CA/PF issues + 86 PP issues still need a 300dpi pass.
- 2026-07-08 (12th scheduled run): sandbox hit 45s tesseract timeouts at 300dpi again (first issue, retry included); dropped to 200dpi per the fallback ladder for all 4 new issues processed this run (CA_1837-10-21/10-28/11-04/11-11, 16 pages) -- added to the list above rather than skipped. Did not touch the pre-existing backfill queue (28 CA/PF issues + 86 PP issues carried over unchanged); now 32 CA/PF issues + 86 PP issues total pending a clean 300dpi pass.
