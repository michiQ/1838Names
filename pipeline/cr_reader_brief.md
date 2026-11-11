# Extraction brief: Christian Recorder, 1864 Q1 and Q2 (January 2 - June 25, 1864)

You are extracting names, articles and events from issues of *The Christian Recorder*
(Philadelphia, organ of the A.M.E. Church; Rev. Elisha Weaver, General Book Steward/editor;
office and AME Book Depository at No. 619 Pine Street) for the **1838 Black Metropolis names
database**, a public-history project recovering the free Black community of antebellum
Philadelphia (c. 1780-1865). The owner is a historian who values source-critical rigor: a wrong
name is worse than a missing one, and every uncertainty must be flagged, not smoothed over.

## Inputs (scratch dir S = /tmp/claude-0/-home-claude/8f46bdc5-7aa7-5a99-9c93-97b7c6b3014b/scratchpad/cr64q1 for January-March 1864, or .../scratchpad/cr64q2 for April-June 1864; your launch message says which)
- OCR text: `S/txt/CR_<date>_p<N>.txt` -- one file per page, 7 columns per page separated by
  `[column N]` markers, top to bottom within each column. Microfilm OCR: names are often garbled.
- Page images: `S/jpg/CR_<date>_p<N>.jpg` (2000px wide, whole page). For READING names you need
  higher resolution: render a crop from the source PDF instead. Frame numbers: ALWAYS look the frame up in S/jobs.txt ('frame:slug:page'). Each S has its own q.pdf, crop.py and jobs.txt, so frame numbers belong to that S only. Vol. IV pages are numbered continuously through the volume (Jan 2 = pp. 1-4, Jan 9 = 5-8 ...); cite the ISSUE page (1-4) as in jobs.txt. The film has library cards saying 'first sheet missing' for four issues, so pages 1 and 2 of these issues DO NOT EXIST in our copy: Feb 6, Mar 5 and Mar 19, 1864 (cr64q1) and Apr 23, 1864 (cr64q2). January-March (cr64q1): Jan 2 (2-5), Jan 9 (6-9), Jan 16 (10-13), Jan 23 (14-17), Jan 30 (18-21), Feb 6 (23-24 = pp3-4), Feb 13 (25-28), Feb 20 (29-32), Feb 27 (33-36), Mar 5 (38-39 = pp3-4), Mar 12 (40, 41, 43, 44), Mar 19 (45-46 = pp3-4), Mar 26 (47-50); frames 1, 22, 37, 42 are library cards. April-June (cr64q2): Apr 2 (1-4), Apr 9 (5-8), Apr 16 (9-12), Apr 23 (14-15 = pp3-4), Apr 30 (16-19), May 7 (20-23), May 14 (24-27), May 21 (28-31), May 28 (32-35), Jun 4 (36-39), Jun 11 (40-43), Jun 18 (44-47), Jun 25 (48-51); frame 13 is a card. Cite by DATE. Crops: render from the PDF with
  ```
  python3 S/crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
  ```
  then Read the png. A single column is ~1/7 of the width; crops of ~1/7 width x ~1/5 height
  read comfortably (crop.py renders at 1000dpi by default, env DPI=1600 for rechecks; this file's scans are 600ppi native). Use the 2000px JPEG (also cropped, e.g. with PIL) to locate things first.
- OCR and image of a page should be used together: OCR to find what is there, the image to read
  names, addresses and numbers exactly.

## Extraction rule (the owner's, for this paper)
Philadelphia-focused deep read:
- CAPTURE: Philadelphia AME and other Black church affairs (Bethel, Union, Wesley/Little Wesley,
  St. Thomas, the Presbyterian and Baptist churches, Frankford, West Philadelphia, Germantown);
  Philadelphia Annual Conference business; meetings, societies, lodges, benevolent and literary
  associations, Sabbath schools, schools (Institute for Colored Youth etc.); notices with named
  officers; signed letters and their signers; marriages and deaths; lists of subscribers/agents/
  donors when Philadelphia or nearby (Bristol, Burlington, Camden, Westchester, Frankford,
  Germantown, Norristown, NJ circuits of the Philadelphia Conference count); ADVERTISEMENTS by
  named proprietors with addresses (these are gold: Black businesses and their addresses).
- NON-Philadelphia names (Baltimore, New York, Ohio, Canada, the West, etc.): mention them in the
  description/summary text only. Do NOT list them as linked `attendees`/`people`, because they
  collide with same-named Philadelphia census people. Exception: AME bishops and Philadelphia
  Conference clergy anywhere (Nazrey, Quinn, Payne, Weaver, Campbell, Brown etc.) may be linked.
- SKIP: devotional essays, reprinted sermons/selections, poetry, general/foreign news and
  white-run commercial ads (insurance, railroads, patent medicines) unless a Black Philadelphian
  or a named Black institution is involved. A note in the issue summary that they exist is enough.
- RECURRING ADS: an ad that repeats every week is captured ONCE, at its clearest impression in
  your issues; later repeats are not re-entered (say so in your notes).

## Output: write JSON to `S/ext_<your-label>.json`
```json
{
  "articles": [
    {"issue": "CR_1861-01-19", "page": 2, "headline": "Our City Carriers (notice)",
     "author": "", "type": "notice",
     "summary": "Opening sentences only, lightly cleaned transcription, enough to identify the piece.",
     "people": [["James Wiggins", "city carrier"], ["W. T. Jones", "city carrier"]]}
  ],
  "events": [
    {"issue": "CR_1861-01-19", "page": 2, "name": "Publication Society of Philadelphia -- meeting called",
     "date": "1861-01-21", "location": "No. 619 Pine street, Philadelphia",
     "description": "Substantive: who, what, the roster with roles and addresses as printed.",
     "attendees": [["Mrs. Lawes", "president (as reported)"]]}
  ],
  "notes": ["per-issue observations, OCR rescues (e.g. 'Wiggivs' = WIGGINS), flags"],
  "flags": ["every uncertain reading, with issue/page and what is uncertain"]
}
```
- `type` is one of: advertisement, notice, letter, editorial, report, obituary, marriage, review,
  sermon, article. Marriages/deaths may be grouped one article per issue-page with all couples/
  deceased as `people` (roles like "groom", "bride", "deceased", "officiating minister").
- Article `summary` = the opening few sentences only (owner's rule). Event `description` =
  substantive, carrying the roster and context.
- `author` = the signer, plain name (e.g. "W. Nazrey"), or "" if unsigned/editorial.
- `people`: everyone named IN an article who is not its author and is in scope (ad proprietors,
  obituary subjects, persons in a notice). Without this field they are invisible in the database.
- NAME FORMAT for `people`/`attendees`: the name as printed, WITHOUT honorifics: "Peter Gardiner"
  not "Rev. Peter Gardiner"; put "Rev."/"Bishop"/"Dr." into the role ("pastor (Rev.)"). Keep
  "Mrs."/"Miss"/"Mr." only when there is no given name ("Mrs. Lawes"). Keep initials as printed
  ("W. T. Jones"). Expand nothing you cannot see; do not normalize spellings.
- Dates ISO (yyyy-mm-dd) when the date of the event is stated or computable; else omit `date`.

## Already captured in Runs #74-#86 (1861, 1862 and ALL of 1863; nothing from 1864 is in the database yet) -- do NOT re-enter unless changed
Recurring: Book Depository of the AME Church (619 Pine; E. Weaver); city carriers James Wiggins & W. T. Jones; Ellis J. Peer's
Fine Cake Bakery (South St.); Mrs. H. S. Duterte, undertaker (634 Lombard); Thomas W. Allmond, furnishing undertaker (1027
Rodman); A. Burris, teacher of vocal music; teachers of the piano; Daughters of Cornish Society standing notice; Nazrey's
"Episcopal Appointments"; "Our Disciplines" appeal; James Downs, clothing; Hope Grand Union (Daughters of Temperance)
notice; Miss Mary Still's school, Clarksborough; hymn-book and carrier notices; the full 1861 Philadelphia Conference
appointments; Wm. Still, coal and stoves (107 N. Fifth); Mrs. E. A. Palmer, trimmings (N. Fifth); the Grand United Order
of Brothers and Sisters of Love and Charity officer list; the Rev. Willis Nazrey Society meeting notice (Aaron Bell, president);
the Daughters of Cornish notice (now with a secretary); Mrs. Jane Johnson and Mrs. Ann Ware, laying out the dead
(641 Lombard); the United Beneficial Sisters of Rev. J. Woodlin Society notice. From Jan-Mar 1862: Joseph H. Cole's Continental Restaurant
(717 Lombard); Mrs. S. Shorter Hawkins (615 Lombard); Mrs. Rebecca O'Donnell, china and glass (South St.); Mrs. E. A. Palmer's
Dry Goods and Trimmings (105 N. Fifth); 'Good News' cutting system (Wm. Bradley; Mrs. Mary C. Weaver); 'Wanted, charge of a
Public School' (J. W. A., 1641 Helmuth St.); Harriet Jacobs's 'Linda' for sale at 107 N. Fifth; the Dorcas Society of Bethel
officers; the Philadelphia Grand Lodge installation roster. From Apr-Jun 1862 (Run #79): Thomas Charnock, General Furnishing Undertaker (427 S. 6th St., second door below Bethel Church), ad and editorial puff; Mrs. S. Shorter Hawkins's 'New Spring Goods' puff (615 Lombard); Miss Mary Still as the Recorder's city and county canvasser ('Our City Canvass', June 28); Rev. Henry Davis boarding notice (Wood St.) and illness notice; A. L. Stanford's twelve lectures at Wesley, Hurst St.; the SCSA Port Royal subscription and donor list; the Bucks County certificate (Emily Johnson); the Nazrey/Quinn 'Recommendation to the Districts'; the 1862 Philadelphia Conference appointments (Campbell to Bethel, Stanford to Wesley, H. Davis to Union, Roberson to Frankford); the Book Concern trustees; John S. Rock's lectures; the death of Rev. William Douglass of St. Thomas'; the J. Woodlin Society anniversary; recurring quarterly-meeting notices for the NJ and West Chester circuits. From Jul-Sep 1862 (Run #81): Miss Jane Johnson, laying out and shrouding the dead (618 South 8th St.) ad and notice; Mrs. Martha Collins's infant school (730 Russell St. above Fitzwater) ad; Banaker House (Cape May) and Union Cottage (Atlantic City) ads (out of town); Miss Mary Still named authorized agent for the city and county; Prof. P. Houston Murray's lectures; Rev. J. P. Campbell's residence notice; the Bethel male members' meeting on colored men as soldiers (Sept 6); the Bethel contraband relief meeting and committee of seven (Sept 27); the Sabbath School Convention of the Philadelphia District called by Bishop Nazrey; Wesley (Hurst St.) pastor's lecture series and appointments; Rev. W. D. W. Schureman's illness; the death of Henry Downing, Bethel Sunday School librarian. Ads that ran all quarter (Book Depository, Duterte, Allmond, Peer, Still's coal, Palmer, Charnock, Jane Johnson, Martha Collins): do NOT re-enter. From Oct-Dec 1862 (Run #82): Mrs. S. Shorter Hawkins's fall and winter goods ad (615 Lombard); Wm. H. Longfellow, surgeon dentist (1126 Rodman) ad and puff; 'Wanted' lodgers (424 South 7th) ad; the Bethel contraband committee roster; the Union A.M.E. freedmen's committee of 21; the SCSA election of Nov 3, Port Royal list, Contraband Fund and clothing lists; Father Richard Roberson's (Robinson's) injury, death and funeral; Garrison James's obituary; the Philadelphia Library Co. 29th anniversary; Rev. Wm. Alston's installation at St. Thomas'; the St. Thomas' Sinking Fund fair; the Friends' evening schools; ICY lecture course (Collins, Bassett); Book Concern executive committee and hymn-book appeal; A. Burris's concerts; Henry Christian seeking his children. From Jan-Mar 1863 (Run #83): the Church Directory of Philadelphia (First Presbyterian, J. C. Gibbs; Central Presbyterian, J. B. Reeve, 907 Lombard; Union A.M.E., Henry Davis; Jacob C. White, superintendent); Mrs. Jane Johnson and Mrs. Ann Wear/Weaver, shrouding (618 S. Eighth); Mrs. Margaret Hazzard's dressmaking 'Wanted' ad (Shippen between 8th and 9th); Edwin A. Hughes, undertaker and sexton (250 S. Tenth); Lewis Fayette, general furnishing undertaker (770 S. Second); George W. Lott, general furnishing undertaker (509 S. Thirteenth); Mrs. S. Shorter Hawkins's spring goods (815 Lombard); Julia Brown's boarders (912 Rodman); Woodlin Society officers; both Grand Lodge rosters; the Banneker Institute election; the SCSA Contraband Fund list; the Union Freedmen's Relief Association of West Philadelphia; the Hutchinson Family benefit concerts; the Annual Conference call (Bethel, May 9) and the elders' examination notice; Weaver's serial life of Richard Robinson. From Jul-Sep 1863 (Run #84): James W. Brown's steam-dyeing works (S. Sixth above Walnut; Shippen St.); Mrs. M. Bennett, herb doctress (S. Seventh below Pine); Mrs. Julia A. Brown, lodging; Mr. and Mrs. H. M. Cropper, boarding (Lombard between 4th and 5th); Dr. P. Gardiner, botanic physician (Princeton); P. Guinn & Son, grocery (South St. above Eleventh); the Soldiers' Relief Association standing notice (Jane L. Johnson, Esther Armstrong, committee of nine); the Wilberforce trustees; the Union, Friendship and Love notice; the 6th USCT flag subscribers; Campbell's hearing and resignation from Bethel (Sept); the Love and Charity expulsions (Longfellow, Eddy). From Oct-Dec 1863 (Run #85): John Oliver's employment office (Clarkson Hall, 615 Cherry); Dr. Wm. Armstrong (240 N. Ninth); Olive Branch Boarding House, Mrs. H. M. Cropper (403 Lombard); William Still's stove store; Georgiana Gleaves, oysters (633 Pine); Bethel under Stephen Smith and W. D. W. Schureman; the 6th USCT departure and the Nov 17 flag presentation; the Love and Charity schism. From Apr-Jun 1863 (Run #86): the 1863 Philadelphia Conference appointments; Wm. S. Walker, barber, 22 Main St., Frankford; the Love and Charity Grand Tabernacle roster (June 1863). Many standing ads (Duterte, Allmond, Peer, Book Depository, Hughes, Fayette, Lott, Hawkins, Jane Johnson shrouding, Hazzard, Julia Brown) will appear in 1864 as repeats: note them, do not re-enter. If any of these ads or notices simply REPEAT in 1864, do not re-enter them (note the repeat). A changed notice (new officers, new dates) is new. Out of scope (white patrons): F. Champion (Brooklyn), Gustine, Reimer, Gregg, D. W. Clark, G. G. Evans, Leary
Getz, Dean, Metz, Elkinton, Rothermel (coal), insurance, railroads, patent medicines. NEW Black-owned ads or changed notices
SHOULD be entered. Quarterly-meeting schedules: one short article per notice, link only named preachers/officers.

## Watch for in these quarters (1864)
- BLACK SOLDIERS: Camp William Penn (Chelten Hills) and the regiments raised there (3rd, 6th, 8th, 22nd, 25th, 32nd USCT etc.):
  departures, flag presentations, chaplains (AME clergy), soldiers' letters from Philadelphians, deaths, the Supervisory Committee,
  bounty and pay questions, the Olustee battle (Feb 20, 1864; the 8th USCT) and its Philadelphia casualties.
- STREETCAR (city passenger railway) exclusion: every ejection, petition, meeting, letter or editorial (1864 saw the Social, Civil
  and Statistical Association petition and the Concert Hall meeting). Capture each as its own article (and event if dated): the
  owner tracks these under a 'Streetcar discrimination' topic.
- The A.M.E. GENERAL CONFERENCE (May 1864, held in Philadelphia) and the PHILADELPHIA ANNUAL CONFERENCE (spring 1864): proceedings,
  committees, elections of bishops, the 1864 appointments (record every Philadelphia-district appointment as printed).
- The GREAT CENTRAL (SANITARY) FAIR, Philadelphia, June 1864: any Black participation, donations, or exclusion.
- Freedpeople relief (Contrabands' Relief, SCSA, church committees), fairs and festivals, Sabbath-school anniversaries,
  the Banneker Institute and ICY (examinations, commencement, lectures), lodge and society elections (officer lists whole),
  Wilberforce University, Bethel and Union church affairs.
- NEW or changed Black-owned ads; marriages and deaths of Philadelphians, with officiating ministers.

## Known identities (record names as printed; mention the identification in `notes`)
- "Robertson" / "Father Robertson" (Bristol, Frankford circuits): the owner has ruled that the
  CR's "Rev. Richard Robertson" IS Rev. Richard Robinson of Frankford. Record a full printed name as printed;
  a bare surname ("Father Robertson") goes in the text only.
- J. C. White in Banneker/ICY contexts of the 1860s is Jacob C. White Jr.: record as "Jacob C. White Jr." with role
  noting the printed form. J. P. Campbell = Bishop Jabez Pitt Campbell (record "J. P. Campbell").
- Do NOT link bare surnames ("Nazrey", "Brother Gaines"): use the full name only when printed or certain from the
  same item (bishops: Willis Nazrey, Daniel A. Payne, William Paul Quinn).
- Subscriber lists from New Jersey / Bucks / Chester County circuits: list them in the event description; link only
  names that are clearly read AND not extremely common (skip linking e.g. "Mary Jones", "John Smith").
- S. Morgan Smith = Rev. Stephen Smith (record as printed). "Mrs. Laws" / "Ann Lawe" = the Publication Society president.
- LAWS FAMILY (owner's rulings, Nov 2026): Mrs. Anna Laws (wife of John Laws; mother of Rev. William J. Laws) is NOT
  Stephen Laws's daughter Anna. The early Stephen Laws (1820 city directory) is a separate man from the later Stephen Laws.
  Record every Laws exactly as printed and put any identification in `notes` only.
  "Mrs. Bunday"/"Mrs. Bundy" = Hope Grand Union. "James F. Needham" is the SON (James Fields Needham); plain "James
  Needham" of the 1830s-40s is the father. O. V. Catto, S. M. Douglass, A. C. Crippen, Prof. Bassett: record as printed.
- Miss Mary Still (Allentown / Clarksborough near Mount Holly N.J.; the Recorder's Philadelphia canvasser from June 1862) is William Still's sister (owner's ruling, Nov 2026); record her as printed.
- Rev. Jonathan C. Gibbs (born 1821; Presbyterian, First African Presbyterian) is the SON. His father, Jonathan C. Gibbs Sr.,
  died in 1831: any 1860s Gibbs is the son.
- 1863 Q3 rulings (owner): the 'Jacob C. White' of the 6th USCT flag list is the elder; 'J. C. White, Jr.' is the son. A. L. Stanford =
  Anthony L. Stanford; U. B. Vidal = Ulysses B. Vidal; T./Theo. Gould = Theodore Gould (record as printed). Rev. Peter Gardiner /
  Gardener and Dr. P. Gardiner are under review: record exactly as printed, no identification.
- 1863 Q2 rulings (owner): 'Libyan Cemetery' (Logan funeral) is Lebanon Cemetery: give 'Lebanon Cemetery (printed ...)' when misprinted.
  Lieutenant Daniel Colley (1863) is NOT Winch's Daniel Colley (b. 1794); record as printed.
- 1863 Q4 rulings (owner): ALL Joshua / Josiah / Joseph / J. P. B. Eddy variations are ONE person (Rev. Joshua P. B. Eddy): record as
  printed, identification in notes. Do NOT merge Wm. / William Cooper, Wm. H. / William H. Longfellow, T. H. / Thomas H. Cooper, or A. M. Green
  with anyone: record as printed. 'Rev. Mr. Shreeves' Lombard St. Church' = J. B. Reeve's Central Presbyterian. William A. Potter and
  Theodore Smith (advertisers) are not known to be Black: enter such ads as notices. 1863 William Still = the William Still (Underground Railroad).
- 1863 Q1 rulings (owner): the Church Directory superintendent 'Jacob C. White' (no Jr./Sr.) is the elder Jacob C. White; the
  undertaker at 509 S. Thirteenth is George W. Lott; Margaret Hassard / Hazzard is one dressmaker, spelled Hazzard. Hawkins's
  Lombard St. number (615 or 815) is not certain: record as printed.
- 1862 rulings (owner): Rev. Richard Roberson / Robertson = Rev. Richard Robinson of Frankford (died Nov. 18, 1862); Mrs. S. Shorter
  Hawkins = Sarah S. Hawkins = Sarah S. Shorter; Wm. Alston / W. A. Alston = Rev. William J. Alston of St. Thomas'; 'E. H. Bassett' =
  E. D. Bassett; Garrison James served both Bethel (chorister) and Union (trustee). Record as printed; identifications in notes.
- Lambsong the confectioner (Culvert above Apple) is Rebecca Lambsong's husband; Robert J. Douglass / Robert Douglass Jr. is the
  painter (owner's rulings, Nov 2026). The 1838 Register of Trades is now in the database: a tradesperson with an address may already
  have a record; record as printed.
- Rev. Walter Proctor died Dec. 10, 1861; Elisha Weaver resumed as editor in Dec. 1861 after A. L. Stanford resigned.
- Isaiah C. Were = Isaiah C. Wears. W. D. W. Schureman (also printed Wm. D. W., Scheroman). Joshua Pernal (also printed
  Purnell). A. L. Stanford (Anthony L. Stanford) was acting editor in the autumn of 1861 while Weaver travelled.
- Bishops of this period: Willis Nazrey ("W. Nazrey", often OCR'd Nazary/Nasrey), Daniel A. Payne,
  William Paul Quinn, Jabez P. Campbell. Elisha Weaver is the General Book Steward/editor.
  John M. Brown (J. M. Brown) edits the Repository of Religion and Literature.

- Henrietta Duterte (undertaker, 634 Lombard; printed 'Mrs. H. S. Duterte') and Francis A. Duterte (her husband, a carpenter
  and builder) are already single merged records: record as printed; do not treat a new printing as a new person. Her husband
  is reported dead before 1862, so a living 1862 'Francis Duterte' needs a flag in `notes`.
- Thomas Butler (the 1838 Butler) is record 'Butler, Thomas'; record any Butler exactly as printed, identification in `notes` only.
- The minister is Woodson (Lewis/Louis Woodson), NOT Woodward. Record as printed and flag if the paper itself prints Woodward.

## Verification (non-negotiable)
- EVERY name, address and number you record must be read on the image crop, not taken from OCR.
- If you cannot read it confidently, either leave it out or record your best reading followed by
  " [VERIFY]" in the name/role/description and add a `flags` entry saying what is uncertain.
- The public site shows no VERIFY flags, so before you finish, RE-READ every [VERIFY] name at DPI=1600 (env DPI=1600 for
  crop.py) and on every other printing of the same item. If it is now certain, remove the flag. If not, keep the flag:
  those names will be kept out of the linked people (the text keeps your best reading). Fewer, certain links beat more.
- Never invent a given name or fill a gap from outside knowledge. You may note a likely
  identification in `notes` (e.g. "probably the Rev. J. P. Campbell of Union Church").

## What to return (your final message)
A short report: issues covered, counts of articles/events/linked names, the 5-10 most notable
finds, and every flag. Keep it under 400 words; the JSON file is the deliverable.
