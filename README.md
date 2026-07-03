# 1838 Black Metropolis — People & Papers Network

An interactive database of names, events, and writings from historic Black newspapers, built for the [1838 Black Metropolis](https://1838blackmetropolis.com) project.

**[→ Open the interactive viewer](./index.html)** (or visit the GitHub Pages site for this repo)

Search any name, click it, and see: everything that person wrote or signed in the papers (headline + summary), events they attended and who else was there, every appearance in the papers with the surrounding quote and a link to the scanned page, and their entry in the Julie Winch Names Reference with citations.

## Contents

- `index.html` — the self-contained interactive viewer (no server needed)
- `black_metropolis.db` — SQLite database: `people`, `winch_references`, `issues`, `articles`, `events`, `appearances`
- `pages/` — scanned page images for every processed newspaper page
- `ocr_text/` — raw OCR text of each page, for verification
- `pipeline/` — the scripts that build the database from the newspaper PDFs

## Coverage (growing)

The Julie Winch 1838 Black Metropolis Names Reference (~2,900 people, 4,565 sourced notes) plus digitized issues of the *Colored American* and *Pennsylvania Freeman* (1838), with the *Pencil Pusher Points* columns (Philadelphia Tribune) and *Freedom's Journal* in progress.

Name matches marked "uncertain" in the viewer are ambiguous OCR-era matches; every entry links to its source page so it can be checked against the original.

## Attribution & license

The biographical reference data derives from **The 1838 Black Metropolis Julie Winch Database © 2025 by 1838 Black Metropolis and Julie Winch**, licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). This derived database and site are shared under the same license. Newspaper page images derive from digitized historic newspapers in the project's collection.
