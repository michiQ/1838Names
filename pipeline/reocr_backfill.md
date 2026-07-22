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
- [x] CA_1837-02-22 (1-page issue; redone at 300dpi 2026-07-15, 34th scheduled run)
- [x] CA_1837-02-25 (4 pages redone at 300dpi 2026-07-15, 34th scheduled run)
- [x] CA_1837-03-04 (5 pages redone at 300dpi 2026-07-15, 34th scheduled run)
- [x] CA_1837-03-11 (4 pages redone at 300dpi 2026-07-15, 35th scheduled run)
- [x] CA_1837-03-18 (4 pages redone at 300dpi 2026-07-15, 35th scheduled run)
- [x] CA_1837-03-25 (4 pages redone at 300dpi 2026-07-15, 35th scheduled run)
- [x] CA_1837-04-01 (4 pages redone at 300dpi 2026-07-15, 35th scheduled run)
- [x] CA_1837-04-08 (4 pages redone at 300dpi 2026-07-16, 36th scheduled run)
- [x] CA_1837-04-15 (300dpi; re-OCR'd 2026-07-16 run #36 — output byte-identical to repo, which already held a 300dpi version from a prior push; Drive copy synced)
- [x] CA_1837-04-22 (300dpi; same as 04-15 — repo already 300dpi, Drive synced 2026-07-16 run #36)
- [x] CA_1837-04-29 (300dpi; same as 04-15 — repo already 300dpi, Drive synced 2026-07-16 run #36)
- [x] CA_1837-05-06 (300dpi; same as 04-15 — repo already 300dpi, Drive synced 2026-07-16 run #36)
- [x] CA_1837-05-13 (300dpi; same as 04-15 — repo already 300dpi, Drive synced 2026-07-16 run #36)
- [x] CA_1838-01-13 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1838-01-20 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1838-01-27 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1838-02-03 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1838-03-15 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1838-04-12 (4 pages redone at 300dpi 2026-07-16, 37th scheduled run)
- [x] CA_1837-08-19 (all 4 pages redone at full 300dpi 2026-07-16, 37th scheduled run — sandbox load ~0.02, held cleanly)
- [x] CA_1837-08-26 (300dpi; re-OCR'd 2026-07-16 run #37 — output byte-identical to repo, which already held a 300dpi version; Drive copy synced)
- [x] CA_1837-09-02 (300dpi; same as 08-26 — repo already 300dpi, Drive synced 2026-07-16 run #37)
- [x] CA_1837-10-21 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run — overwritten in place; 18-20K bytes/page vs old 200dpi)
- [x] CA_1837-10-28 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run)
- [x] CA_1837-11-04 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run)
- [x] CA_1837-11-11 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run)

## Pennsylvania Freeman (4 issues, ~16 pages)
- [ ] PF_1838-01-18
- [ ] PF_1838-01-25
- [ ] PF_1838-02-08
- [ ] PF_1838-02-15

## Freedoms Journal (1 issue at 300dpi backfilled; 4 new issues added at 150dpi)
- [x] FJ_1827-04-06 (p2 only -- DONE 2026-07-10 (17th scheduled run): re-OCR'd at full 300dpi by splitting the render (pdftoppm) and OCR (tesseract) into separate bash calls to dodge the 45s wall; 21,731 bytes, overwritten in place and picked up by that run's full rebuild. Previously: 300dpi timed out on the 2026-07-09 6th-batch run, was at 200dpi.)
- [x] FJ_1828-01-25 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run — confirmed genuine 4-page issue, p5 empty)
- [x] FJ_1828-02-01 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run — genuine 4-page issue)
- [x] FJ_1828-02-08 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run — genuine 4-page issue)
- [x] FJ_1828-02-15 (all 4 pages redone at full 300dpi 2026-07-17, 40th scheduled run — genuine 4-page issue)

## Pencil Pusher (86 issues, ~86 pages — mostly single-page clippings)
- [ ] PP_000 .. PP_085 (all pending; see ocr_text/ for the full slug list, e.g. `ls ocr_text | grep '^PP_' | sed -E 's/_p[0-9]+\.txt$//' | sort -u`)

## Progress log
- 2026-07-22 (RUN #57, retry on a HEALTHY container): No backfill done — could NOT fetch source PDF bytes this session (Drive download_file_content = "session expired" on every try; device_stage_files = cloud placeholders not hydrated; device_bash = device workspace unavailable), so no re-OCR possible. Backfill queue UNCHANGED: 4 Pennsylvania Freeman (PF_1838-01-18/01-25/02-08/02-15) + 86 Pencil Pusher clippings still pending a 300dpi pass. Separately DID complete the approved michiQ->1838BlackMetropolis PROMOTE (production advanced run #55 -> run #56). Unblock next run: re-auth the Google Drive connector OR make the PF/PP source folders available offline on michikos-imac.
- 2026-07-21 (RUN #56): No backfill items done — focused on new PF dds-* bundle (dds-41234 -> PF_1838-03-15/03-22, the first Whittier Pennsylvania Freeman + the Appeal-of-Forty-Thousand disfranchisement meeting). Backfill queue unchanged: 4 Pennsylvania Freeman (PF_1838-01-18/01-25/02-08/02-15) + 86 Pencil Pusher clippings still pending a 300dpi pass. (These new dds bundles are OCR'd at 150dpi + half-page split by necessity — dense ~17x23.5in broadsheets time out at 300dpi; they are new content, not backfill.)
- 2026-07-18 (44th scheduled run): NO WORK COMPLETED — same bash sandbox outage as runs #38/#39/#41/#42/#43 (session sleepy-vibrant-shannon; container root FS full, "useradd failed ... No space left on device", 4 paced retries all failed). No re-OCR, no rebuild, no push. Backfill queue unchanged: 4 Pennsylvania Freeman (PF_1838-01-18/01-25/02-08/02-15) + 86 Pencil Pusher clippings still pending a 300dpi pass. Retry bash next run.
- 2026-07-18/19 (43rd scheduled run — SUCCESS, session pensive-gallant-mendel, run interactively after several blocked auto-runs): bash recovered on a healthy container (4.1G free). NO backfill items done this run (focused on new issues) — PF and PP backfill still pending. Processed 5 NEW Freedom's Journal issues at 300dpi (FJ_1828-05-30/06-06/06-13/06-27/07-04, 40 pages, all genuine single 8-page issues). NOTE for future runs: FJ_1828-05-30/06-06/06-13 already had extractions in extractions40.json from run #40, but their OCR text was never synced to Drive/repo — this run OCR'd them for real; extractions41.json was trimmed to only NET-NEW 06-27/07-04 content to avoid duplicating extractions40. Backfill queue unchanged: 4 Pennsylvania Freeman (PF_1838-01-18/01-25/02-08/02-15) + 86 Pencil Pusher clippings still pending a 300dpi pass.
- 2026-07-17 (40th scheduled run): Bash sandbox healthy on a clean container (the run #38/#39 'No space left on device' outage is cleared; 30G free). Source PDFs are cloud-only Drive placeholders that the device bridge won't hydrate and device_bash is unavailable this session, so PDFs were pulled via the Google Drive connector (download_file_content -> base64 saved to a result file -> decoded to PDF in-container) rather than staged. Backfilled 4 Colored American issues 200dpi->300dpi (CA_1837-10-21/10-28/11-04/11-11, 16 pages) and 4 Freedom's Journal issues 150dpi->300dpi (FJ_1828-01-25/02-01/02-08/02-15, 16 pages), all overwritten in place. Resolved the open p5-8 question for the Jan-Feb 1828 FJ issues: their source PDFs are genuinely 4 pages (p5 empty), so no missing pages there — the 8-page-single pattern only applies to the later 1828 issues (May onward). Also processed 3 NEW FJ issues (05-30/06-06/06-13, all single 8-page, Whole No. 62/63/64). Remaining backfill: 4 Pennsylvania Freeman issues (PF_1838-01-18/01-25/02-08/02-15) + 86 Pencil Pusher clippings.
- 2026-07-16 (37th scheduled run): Sandbox idle (load 0.02), 300dpi held cleanly all run. Backfilled 9 Colored American issues to full 300dpi (36 pages): the Jan–Apr 1838 CA block Michiko is actively reviewing (CA_1838-01-13/01-20/01-27/02-03/03-15/04-12) plus CA_1837-08-19 (genuine sub-300dpi→300dpi upgrade); CA_1837-08-26 and 09-02 re-OCR'd but came back byte-identical to the repo's already-300dpi copies (tracker was stale — same situation as the April–May 1837 block in run #36), Drive now synced. Also processed 2 NEW Freedom's Journal issues (FJ_1828-05-16, FJ_1828-05-23). IMPORTANT FINDING for Michiko: both May PDFs are single 8-page issues, NOT two bundled 4-page weeklies — masthead-verified (05-16: p1 AND p5 both read "Vol. 2 No. 8 / Whole No. 60 / May 16"; 05-23: p1 AND p5 both "No. 9 / Whole No. 61 / May 23"), and p5-8 content is distinct from p1-4. So all 8 pages were kept per issue. This differs from the run #35/#36 "take only pages 1-4" convention, which means the earlier FJ issues (all stored at 4 pages in ocr_text) may be UNDER-processed and missing their pages 5-8 — worth revisiting. Reliable OCR pattern this run: pdftoppm renders all pages in ~1s; each tesseract call must be its own bash call (2 in one call blows the 45s wall); using `tesseract pgm outfile` (file output) instead of stdout redirect eliminated the empty-first-attempt flake entirely. Remaining backfill: ~17 CA/PF issues (the 08-19-neighbor sub-300dpi CA set minus 08-19/08-26/09-02 now done: 10-21/10-28/11-04/11-11 + 4 PF) + 4 FJ (150dpi, run #33) + 86 PP.
- 2026-07-16 (36th scheduled run): Sandbox idle at start (load 0.00), so 300dpi held. Backfilled the CA_1837 April–May block: CA_1837-04-08 (genuine 150→300dpi upgrade, 4 pages) plus 04-15/04-22/04-29/05-06/05-13 (re-OCR'd at 300dpi — output came back byte-identical to the GitHub repo, which already held 300dpi versions of these five from a prior push even though this tracker still listed them pending and the Drive ocr_text copies were stale; Drive is now synced to match). Net: the entire CA April–May 1837 run is confirmed 300dpi across Drive + repo. Also processed 3 NEW Freedom's Journal issues at native 300dpi (FJ_1828-04-25/05-02/05-09 — 8-page bundles, took pages 1-4 = the dated issue only, per convention). Discovered 2 FJ source PDFs are 31-byte "File missing: docs/suspend.htm" Drive tombstones (FJ_1827-11-30, FJ_1828-02-22) — genuinely missing from Drive, cannot be processed until re-uploaded. Remaining backfill: 19 CA/PF issues (04-08's neighbors done; the 08-19→11-11 sub-300dpi CA set + Jan-Apr 1838 CA + 4 PF) + 4 FJ (150dpi, run #33) + 86 PP.
- 2026-07-15 (35th scheduled run): Sandbox load low at start (~0.14), briefly spiked to ~3.5 mid-run (one CA page timed out at 300dpi and was recovered via the split render/OCR two-call trick). Backfilled CA_1837-03-11, 03-18, 03-25, 04-01 (16 pages) at full 300dpi, overwritten in place. Also processed 2 NEW Freedom's Journal issues at native 300dpi (FJ_1828-04-11, FJ_1828-04-18 — pages 1-4 only; these source PDFs bundle two weekly issues at 8 pages each, so only the dated issue's 4 pages were taken to avoid cross-contamination — no backfill entry needed). Did NOT re-touch the FJ 150dpi backfill entries from run #33 (still pending). Remaining: 25 CA/PF issues + 4 FJ (150dpi) issues + 86 PP issues pending a 300dpi pass.
- 2026-07-15 (34th scheduled run): Sandbox load was very low (~0.03), so 300dpi held cleanly. Backfilled CA_1837-02-22 (1pg), CA_1837-02-25 (4pg), CA_1837-03-04 (5pg) at full 300dpi, overwritten in place. Did NOT re-touch the FJ 150dpi backfill entries from run #33 (still pending). Remaining: 29 CA/PF issues + 4 FJ (150dpi) issues + 86 PP issues pending a 300dpi pass. Note: CA pages are dense scans — ~40s/page tesseract at 300dpi, so one page per bash call for CA; FJ pages OCR faster (~15s each), 2 per call is safe.
- 2026-07-14 (33rd scheduled run): processed 4 new Freedoms Journal issues (FJ_1828-01-25/02-01/02-08/02-15, 16 pages) but sandbox was under heavy load (load avg 4-5+); 300dpi and 200dpi tesseract both blew the 45s wall repeatedly, so all 16 pages landed at 150dpi and were added to the FJ backfill section above rather than skipped. Did not touch the pre-existing backfill queue. Now 32 CA/PF issues + 4 FJ issues + 86 PP issues pending a clean 300dpi pass.
- 2026-07-10 (18th scheduled run): Backfilled CA_1837-02-11 (2 pages — it is a 2-page issue, matching its 2 existing ocr_text files) and CA_1837-02-18 (4 pages) at full 300dpi, all first-attempt, overwritten in place and picked up by this run's full rebuild. Remaining: 30 CA/PF issues + 86 PP issues.
- 2026-07-10 (17th scheduled run): Backfilled FJ_1827-04-06_p2 at 300dpi (the only FJ pending item — FJ section now clear). All 20 pages of this run's 5 new FJ issues hit native 300dpi (one page needed the split render/OCR two-call trick), so no new entries. Remaining: 32 CA/PF issues + 86 PP issues.
- 2026-07-06: List seeded (116 issues / ~204 pages total pending). Backfilled CA_1837-01-07, 01-14, 01-21, 01-28 (16 pages) at 300dpi this session -- overwrote ocr_text/ in place, rebuilt (match_names -> load_extractions -> apply_merges -> find_merge_candidates -> build_viewer), pushed. ~188 pages remain (22 CA issues, 4 PF issues, 86 PP issues).
- 2026-07-06 (7th scheduled run): Backfilled CA_1837-02-04 (4 pages) at 300dpi -- page 4 timed out at 300dpi even at 43s, dropped to 200dpi per the documented fallback and it completed in 32s. Overwrote ocr_text/CA_1837-02-04_p*.txt in place. ~184 pages remain (21 CA issues, 4 PF issues, 86 PP issues, plus new CA_1837-05-20/05-27/06-03/06-10/06-17 issues processed this run at native 300dpi so they never need backfill).
- Note on OCR tool flakiness: the first `tesseract` call on a just-rendered 300dpi page consistently produces an empty file or errors ("Error during processing" / timeout) — an immediate retry on the same .pgm file succeeds reliably. Budget 2 tesseract attempts per page when estimating run time.
- 2026-07-07 (10th scheduled run): sandbox was unusually slow all session (load average climbed from ~4 to ~7 on a 4-core box over the course of the run); even repeated retries at 300/200/150dpi kept hitting the 45s wall on most pages, so the 3 new issues processed this run (CA_1837-08-19/08-26/09-02) were OCR'd mostly at 100dpi rather than the 300dpi default -- added to this backfill list above rather than skipped, since the intent of the backfill tracker is "every page ends up at 300dpi eventually," not just pre-2026-07-06 pages. Did not touch the pre-existing backfill queue this run (25 items were already pending; still 25 pending, now +3 more added at the bottom of the CA section). Total remaining: ~184 pre-existing pages (21 CA + 4 PF + 86 PP, unchanged) + 3 new issues (11 sub-300dpi pages) = effectively 28 CA/PF issues + 86 PP issues still need a 300dpi pass.
- 2026-07-08 (12th scheduled run): sandbox hit 45s tesseract timeouts at 300dpi again (first issue, retry included); dropped to 200dpi per the fallback ladder for all 4 new issues processed this run (CA_1837-10-21/10-28/11-04/11-11, 16 pages) -- added to the list above rather than skipped. Did not touch the pre-existing backfill queue (28 CA/PF issues + 86 PP issues carried over unchanged); now 32 CA/PF issues + 86 PP issues total pending a clean 300dpi pass.
