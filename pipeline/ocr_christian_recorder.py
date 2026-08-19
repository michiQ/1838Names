#!/usr/bin/env python3
"""
OCR recipe for the Christian Recorder microfilm/bound-volume scans (added 2026-08-19).

These PDFs are two-page SPREADS photographed on dark film: wide black borders,
two paper pages side by side, ~4 columns per page. Method per spread:
1. Render at 300dpi gray.
2. Find the paper region: rows/cols whose bright-pixel (>=120) fraction >= 0.25.
3. Split the paper region into two pages at the darkest vertical seam within
   the middle 20% of the paper width (the gutter), falling back to the center.
4. Each page: divide into NCOLS equal columns with +/-30px overlap padding,
   `tesseract --psm 4` per strip, "[column N]" separators (NS-style output).

Usage: python3 ocr_christian_recorder.py <spreads.pdf> <slug> <outdir> <spread> [firstPageNo]
Writes <outdir>/<slug>_p<N>.txt for the LEFT page (N=firstPageNo) and RIGHT
page (N=firstPageNo+1) of that spread. firstPageNo defaults to 2*spread-1.
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
DPI = 300
NCOLS = 4
PAD = 30
BRIGHT = 120
FRAC = 0.25

def paper_bbox(arr):
    bright = arr >= BRIGHT
    cols = bright.mean(axis=0) >= FRAC
    rows = bright.mean(axis=1) >= FRAC
    xs = np.flatnonzero(cols); ys = np.flatnonzero(rows)
    return xs[0], xs[-1], ys[0], ys[-1]

def gutter_x(arr, x0, x1, y0, y1):
    # The two pages are equal width and tightly bound -- there is no reliable dark
    # gutter seam on these films (argmin just found convolution edge artifacts).
    # The paper-bbox center IS the page boundary; +/-PAD overlap covers any skew.
    return (x0 + x1) // 2

def ocr_page(arr, x0, x1, y0, y1, out_path, workdir, tag):
    w = x1 - x0
    step = w / NCOLS
    chunks = []
    for c in range(NCOLS):
        cx0 = max(x0, int(x0 + c*step) - PAD)
        cx1 = min(x1, int(x0 + (c+1)*step) + PAD)
        crop = os.path.join(workdir, f"{tag}c{c+1}.png")
        Image.fromarray(arr[y0:y1, cx0:cx1]).save(crop)
        res = subprocess.run(["tesseract", crop, "-", "--psm", "4"],
                             capture_output=True, text=True)
        chunks.append(f"[column {c+1}]\n{res.stdout.strip()}")
    with open(out_path, "w") as fh:
        fh.write("\n\n".join(chunks) + "\n")
    print(f"    {os.path.basename(out_path)}: {sum(len(c) for c in chunks)} chars", flush=True)

def main():
    pdf, slug, outdir, spread = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
    first = int(sys.argv[5]) if len(sys.argv) > 5 else 2*spread - 1
    os.makedirs(outdir, exist_ok=True)
    with tempfile.TemporaryDirectory() as wd:
        stem = os.path.join(wd, "sp")
        subprocess.run(["pdftoppm", "-f", str(spread), "-l", str(spread),
                        "-r", str(DPI), "-gray", pdf, stem], check=True)
        pgm = os.path.join(wd, sorted(f for f in os.listdir(wd) if f.endswith(".pgm"))[0])
        arr = np.asarray(Image.open(pgm), dtype=np.uint8)
        x0, x1, y0, y1 = paper_bbox(arr)
        gx = gutter_x(arr, x0, x1, y0, y1)
        print(f"  spread {spread}: paper x={x0}..{x1} y={y0}..{y1}, gutter at {gx}", flush=True)
        ocr_page(arr, x0, gx, y0, y1, os.path.join(outdir, f"{slug}_p{first}.txt"), wd, "L")
        ocr_page(arr, gx, x1, y0, y1, os.path.join(outdir, f"{slug}_p{first+1}.txt"), wd, "R")

if __name__ == "__main__":
    main()
