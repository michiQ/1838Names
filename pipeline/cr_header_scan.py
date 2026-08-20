#!/usr/bin/env python3
"""OCR the header band of each half of each frame of the CR Vol I reel, to map
frames -> printed page numbers / masthead dates. Usage: cr_header_scan.py <pdf> <f0> <f1>"""
import os, re, subprocess, sys, tempfile
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
BRIGHT, FRAC = 120, 0.25
R, f0, f1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
for f in range(f0, f1 + 1):
    with tempfile.TemporaryDirectory() as wd:
        subprocess.run(["pdftoppm", "-f", str(f), "-l", str(f), "-r", "300", "-gray", R, wd + "/t"], check=True)
        pgm = [x for x in os.listdir(wd) if x.endswith(".pgm")][0]
        arr = np.asarray(Image.open(os.path.join(wd, pgm)), dtype=np.uint8)
        if arr.shape[1] < 1500:
            print(f"F{f}: TINY/JUNK {arr.shape}"); continue
        b = arr >= BRIGHT
        cols = np.flatnonzero(b.mean(axis=0) >= FRAC); rows = np.flatnonzero(b.mean(axis=1) >= FRAC)
        if not len(cols) or not len(rows):
            print(f"F{f}: DARK/BLANK"); continue
        x0, x1, y0, y1 = cols[0], cols[-1], rows[0], rows[-1]
        w, h = x1 - x0, y1 - y0
        halves = [("L", x0, (x0+x1)//2), ("R", (x0+x1)//2, x1)] if w > h * 1.05 else [("S", x0, x1)]
        for tag, a, bx in halves:
            strip = arr[y0:y0 + int(h * 0.20), a:bx]
            p = os.path.join(wd, f"s{tag}.png"); Image.fromarray(strip).save(p)
            res = subprocess.run(["tesseract", p, "-", "--psm", "3"], capture_output=True, text=True)
            txt = " | ".join(l.strip() for l in res.stdout.splitlines() if l.strip())[:300]
            print(f"F{f}{tag}: {txt}", flush=True)
