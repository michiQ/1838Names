# Run #101 addendum: Christian Recorder, July - September 1867 (Vol. VII, Nos. 27-39)

Read `/home/claude/1838names/pipeline/cr_reader_brief.md` FIRST for the full method,
the owner's extraction rules, name format, output format and the topics to watch. That
file is authoritative. This addendum gives ONLY what differs for this quarter.

## Differences from that brief
- Quarter: July 6 to September 28, 1867. 13 weekly (Saturday) issues, Vol. VII Nos. 27-39,
  printed pages 105-156.
- SINGLE PAGES this time (not two-up spreads). In `crop.py` the `<frame>` argument IS the
  PDF page number. The frame-to-date-and-page map is `/home/claude/1838names/pipeline/run101_wip/jobs.txt`
  (`frame:slug:page`). CLEAN quarter: no missing sheets. PDF page 53 is a duplicate scan of
  page 52 (Sep 28 p4); ignore it except to recheck a blurred word.
- Scratch dir S = `/home/claude/1838names/pipeline/run101_wip`.
  - OCR text (finding aid): `/home/claude/1838names/ocr_text/CR_<date>_p<N>.txt` (7 columns,
    `[column N]` markers; microfilm OCR, names often garbled).
  - Page overview images: `/home/claude/1838names/pages/CR_<date>_p<N>.jpg` (2000px, whole page).
  - HIGH-RES reading crops: `python3 S/crop.py <frame> <x0> <y0> <x1> <y1> <out.png>` (fractions
    0-1 of the paper area), then Read the png. DPI 1000 default; `DPI=1600 python3 S/crop.py ...`
    for a VERIFY recheck. A column is ~1/7 width; crop ~1/7 width x ~1/5 height per slice, about
    five slices per column, ONE column per crop. Run ONE crop at a time (three readers share a
    small 2-core machine); the first crop of a page is slow (render+cache), later crops are fast.
- Editorship: by the June 29 issue Rev. Elisha Weaver is EDITOR and Publisher and Rev. James
  Lynch has left the editor's chair. Record the masthead/editor exactly as printed each issue and
  note any further change.
- ALREADY CAPTURED: everything through the June 29, 1867 issue is already in the database
  (Runs #74-#100). A repeated standing ad or notice is entered ONCE and is already in; enter it
  again ONLY if its proprietor, address or wording has CHANGED. Say in your notes which repeats
  you saw.
- HOPED-FOR FIND: the owner is watching for Caroline R. Le Count and the Robert Smalls streetcar
  episodes, and for ANY report of the new street-car law (signed March 1867) being used, refused,
  enforced, prosecuted or celebrated. Capture every such item in full and flag anything uncertain.

## Output
Write JSON to `S/ext_<LABEL>.json` in the EXACT format of the main brief:
`{"articles":[...],"events":[...],"notes":[...],"flags":[...]}`.
SAVE AFTER EACH ISSUE (rewrite the whole file each time) so nothing is lost if interrupted.
Touch nothing else: do not edit the database, git, or any file outside your own `ext_<LABEL>.json`.

In your FINAL report back, list issue by issue exactly which pages and columns you read in full
from image crops and which you could not read, call out every street-car / Le Count / Smalls item
and every uncertainty, and give counts of articles and events you captured.
