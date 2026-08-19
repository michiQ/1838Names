#!/usr/bin/env python3
"""Re-render Christian Recorder page JPEGs at high resolution from the spread PDF.

Same paper-bbox + center-split geometry as pipeline/ocr_christian_recorder.py,
but outputs full-resolution page JPEGs (300dpi render, quality 85) instead of
the old low-res pages. Usage: render_cr_pages.py <pdf> <outdir>
Spread map for the Vol I Nos 38-39 file:
  sp1 R -> CR_1856-01-18_p1 ; sp2 L/R -> p2/p3 ; sp3 L -> p4
  sp3 R -> CR_1856-03-04_p1 ; sp4 L/R -> p2/p3 ; sp5 L -> p4
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
DPI, BRIGHT, FRAC, Q = 300, 120, 0.25, 85

MAP = {  # spread -> (left_target, right_target)
    1: (None, "CR_1856-01-18_p1"),
    2: ("CR_1856-01-18_p2", "CR_1856-01-18_p3"),
    3: ("CR_1856-01-18_p4", "CR_1856-03-04_p1"),
    4: ("CR_1856-03-04_p2", "CR_1856-03-04_p3"),
    5: ("CR_1856-03-04_p4", None),
}

def paper_bbox(arr):
    bright = arr >= BRIGHT
    cols = bright.mean(axis=0) >= FRAC
    rows = bright.mean(axis=1) >= FRAC
    xs = np.flatnonzero(cols); ys = np.flatnonzero(rows)
    return xs[0], xs[-1], ys[0], ys[-1]

def main():
    pdf, outdir = sys.argv[1], sys.argv[2]
    for spread, (lt, rt) in MAP.items():
        with tempfile.TemporaryDirectory() as wd:
            stem = os.path.join(wd, "sp")
            subprocess.run(["pdftoppm", "-f", str(spread), "-l", str(spread),
                            "-r", str(DPI), "-gray", pdf, stem], check=True)
            pgm = os.path.join(wd, sorted(f for f in os.listdir(wd) if f.endswith(".pgm"))[0])
            arr = np.asarray(Image.open(pgm), dtype=np.uint8)
            x0, x1, y0, y1 = paper_bbox(arr)
            gx = (x0 + x1) // 2
            for tgt, (a, b) in ((lt, (x0, gx)), (rt, (gx, x1))):
                if not tgt: continue
                out = os.path.join(outdir, tgt + ".jpg")
                Image.fromarray(arr[y0:y1, a:b]).save(out, "JPEG", quality=Q, optimize=True)
                w, h = b - a, y1 - y0
                print(f"sp{spread} -> {tgt}.jpg {w}x{h} {os.path.getsize(out)//1024}KB", flush=True)

if __name__ == "__main__":
    main()
