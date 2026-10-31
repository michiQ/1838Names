#!/usr/bin/env python3
"""Christian Recorder, single-page-per-frame files (1861 Vol I NS reel, 1861-63 quarterlies,
1863 Vol III reel -- Internet Archive scans, ~200ppi native, 6-column pages).

Unlike the Vol I (1854-56) reel these are NOT two-page spreads, so there is no centre split.
Per frame: render at 400dpi gray (2x native -- small blurry type OCRs much better upsampled),
find the paper bbox (bright-pixel fraction, same rule as cr_process.py), paint out solid-black
torn/border regions (they derail tesseract's layout analysis -- the single biggest quality win),
cut NCOLS equal columns +/-40px, tesseract --psm 4 per column with [column N] separators.
NCOLS: the 1861 Vol I NS reel prints SEVEN columns; check each new file before running. The page JPEG is the paper bbox
downscaled to 2000px wide, q85 (readable zoomed; ~1-1.5MB).

Usage: cr_single_process.py <pdf> <txtdir> <jpgdir> <frame>:<slug>:<pg> [...]
Env NCOLS sets the column count (default 6; the 1861 NS reel AND the 1861 quarterlies are 7).
Env DPI sets the render resolution (default 400). Aim for ~2x the scan's native pixels: the NS reel
(pages 1422pt wide, 200ppi) -> 400; the quarterlies (pages ~475pt wide, 600ppi) -> 1200. Check with
`pdfimages -list` before running a new file.
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
DPI, PAD, BRIGHT, FRAC, Q, JPG_W = int(os.environ.get("DPI", "400")), 40, 120, 0.25, 85, 2000
NCOLS = int(os.environ.get("NCOLS", "6"))
from PIL import ImageFilter


def mask_black(arr):
    """Paint solid-black regions (torn film, scan borders) white so tesseract's layout
    analysis is not derailed by them. Text strokes survive: a 41px box blur of real
    type never drops below ~90, while torn areas sit near 0."""
    blur = np.asarray(Image.fromarray(arr).filter(ImageFilter.BoxBlur(20)))
    out = arr.copy(); out[blur < 60] = 255
    return out


def paper_bbox(arr):
    b = arr >= BRIGHT
    cols = np.flatnonzero(b.mean(axis=0) >= FRAC)
    rows = np.flatnonzero(b.mean(axis=1) >= FRAC)
    return cols[0], cols[-1], rows[0], rows[-1]


def main():
    pdf, txtdir, jpgdir = sys.argv[1], sys.argv[2], sys.argv[3]
    for spec in sys.argv[4:]:
        fr, slug, pg = spec.split(":")
        name = f"{slug}_p{pg}"
        with tempfile.TemporaryDirectory() as wd:
            subprocess.run(["pdftoppm", "-f", fr, "-l", fr, "-r", str(DPI), "-gray", pdf, wd + "/t"], check=True)
            pgm = [x for x in os.listdir(wd) if x.endswith(".pgm")][0]
            arr = np.asarray(Image.open(os.path.join(wd, pgm)), dtype=np.uint8)
            x0, x1, y0, y1 = paper_bbox(arr)
            page = Image.fromarray(arr[y0:y1, x0:x1])
            w, h = page.size
            page.resize((JPG_W, int(h * JPG_W / w)), Image.LANCZOS).save(
                os.path.join(jpgdir, name + ".jpg"), "JPEG", quality=Q, optimize=True)
            ocr_arr = mask_black(arr)
            step = (x1 - x0) / NCOLS
            chunks = []
            for c in range(NCOLS):
                cx0 = max(x0, int(x0 + c * step) - PAD)
                cx1 = min(x1, int(x0 + (c + 1) * step) + PAD)
                p = os.path.join(wd, f"c{c}.png")
                Image.fromarray(ocr_arr[y0:y1, cx0:cx1]).save(p)
                r = subprocess.run(["tesseract", p, "-", "--psm", "4"], capture_output=True, text=True)
                chunks.append(f"[column {c + 1}]\n{r.stdout.strip()}")
            out = os.path.join(txtdir, name + ".txt")
            open(out, "w").write("\n\n".join(chunks) + "\n")
            print(f"F{fr} -> {name} jpg={os.path.getsize(os.path.join(jpgdir, name + '.jpg'))//1024}KB "
                  f"txt={os.path.getsize(out)}B", flush=True)


if __name__ == "__main__":
    main()
