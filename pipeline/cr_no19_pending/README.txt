Christian Recorder Vol I No. 19 -- pages 3 and 4 ONLY (printed pp. 75-76).
The reel (frames 10R/11L) is missing this issue's pages 1-2, so there is NO masthead
and NO printed issue date on the surviving pages.

*** MICHIKO'S RULING (2026-08-19): the YEAR is 1854. *** Register with slug
CR_1854-08-31 -- an ESTIMATED day, not a source-printed one. Rationale: No.19 falls
between No.18 (masthead Aug 17 1854) and No.20 (masthead Sep 16 1854); the surviving
pp.75-76 carry letters dated Aug 1854 (Westchester Aug 25, Saratoga Aug 12, St
Catharine's C.W. Aug 4/6); a ~biweekly cadence from Aug 17 lands on Aug 31. Only the
YEAR is firm; the day is an estimate and may be renamed if a better date surfaces.

TO REGISTER (next session, on a clean disk):
1. Move NO19_p3.txt/.jpg -> ocr_text/CR_1854-08-31_p3.txt + pages/CR_1854-08-31_p3.jpg;
   NO19_p4.txt/.jpg -> ocr_text/CR_1854-08-31_p4.txt + pages/CR_1854-08-31_p4.jpg.
   (Pages 1-2 do not exist; the viewer will simply have no p1/p2 links for this issue.)
2. Add CR_1854-08-31 -> the Vol I reel Drive viewUrl
   (https://drive.google.com/file/d/1SV9-6PtyN9dk89D7fexeAu26JjgE61du/view) to
   pipeline/issue_urls.json.
3. git rm this cr_no19_pending/ folder.
4. Run the full rebuild chain, smoke_test, re-bake, push to staging, sync Drive; note in
   progress.txt that the day is an estimate.
(2026-08-19; superseding the earlier "held pending date" note.)
