# Run #102 addendum: Christian Recorder, October - December 1867 (Vol. VII, Nos. 40-52)

Read `/home/claude/1838names/pipeline/cr_reader_brief.md` FIRST for the full method, the owner's
extraction rules, name format, output format and the topics to watch. That file is authoritative.
This addendum gives ONLY what differs for this quarter.

## Differences from that brief
- Quarter: October 5 to December 28, 1867. 13 weekly (Saturday) issues, Vol. VII Nos. 40-52,
  printed pages 157-208.
- SINGLE PAGES (not two-up spreads). In `crop.py` the `<frame>` argument IS the PDF page number.
  Frame-to-date-and-page map: `/home/claude/1838names/pipeline/run102_wip/jobs.txt` (`frame:slug:page`).
  CLEAN quarter: 52 pages, no missing sheets, no duplicates.
- Scratch dir S = `/home/claude/1838names/pipeline/run102_wip`.
  - OCR text (finding aid): `/home/claude/1838names/ocr_text/CR_<date>_p<N>.txt` (7 columns, `[column N]`
    markers; microfilm OCR, names often garbled).
  - Page overview images: `/home/claude/1838names/pages/CR_<date>_p<N>.jpg` (2000px).
  - HIGH-RES reading crops: `python3 S/crop.py <frame> <x0> <y0> <x1> <y1> <out.png>` then Read the png.
    DPI 1000 default; `DPI=1600 S/crop.py ...` for a recheck. One column is ~1/7 width; crop ~1/7 wide
    x ~1/5 tall per slice, about five slices per column, ONE column per crop. Run ONE crop at a time.
- Editor all quarter: Rev. Elisha Weaver, Editor and Publisher, 631 Pine St. Note any change.
- ALREADY CAPTURED: everything through the September 28, 1867 issue is already in the database
  (Runs #74-#101). A repeated standing ad/notice is entered ONCE and is already in; enter it again ONLY
  if its proprietor, address or wording has CHANGED. Say in your notes which repeats you saw.
- STILL WATCHING (not found Jul-Sep, so keep looking): any Caroline R. Le Count item, any Robert Smalls
  street-car item, O. V. Catto, the Equal Rights League, and ANY report of the street-car law (signed
  March 1867) in use, refused, enforced, prosecuted or celebrated. This quarter also likely holds: the
  October 1867 Pennsylvania state election and Black-suffrage agitation, Thanksgiving observances, year-end
  society and church annual reports, Freedmen's work, and A.M.E. conference/appointment news.

## TWO HARD RULES (a Run #101 QA review caught both being bent)
1. READ PAGES 1 AND 4 OF EVERY ISSUE IN FULL FROM IMAGE CROPS, column by column, ~5 slices each. Do NOT
   triage page 1 or page 4 from the OCR. Confirm every column from the image, even if you then skip it as
   poetry, a reprinted selection, an out-of-town letter or a standing ad.
2. BE EXHAUSTIVE ON LONG NAME LISTS. On donor/subscription lists and officer rosters, transcribe EVERY name
   from the image, in order, with amounts/offices. (Last quarter a reader captured 30 of ~39 contributors
   on one list.) When a list is long, crop it in enough slices to read all of it; do not sample.

## Output
Write JSON to `S/ext_<LABEL>.json` in the EXACT format of the main brief:
`{"articles":[...],"events":[...],"notes":[...],"flags":[...]}`. SAVE AFTER EACH ISSUE. Touch nothing else
(no git, no database, no file but your own `ext_<LABEL>.json`). In your FINAL report, list issue by issue
exactly which pages and columns you read in full from crops, every street-car / Le Count / Smalls item,
every uncertainty, and counts of articles and events.
