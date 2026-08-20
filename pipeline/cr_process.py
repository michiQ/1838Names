#!/usr/bin/env python3
"""Process CR Vol I reel frames: OCR (4-col psm 4, [column N] separators) + hi-res
page JPEG (q85), using the ocr_christian_recorder.py geometry (paper bbox, center split).

Usage: cr_process.py <pdf> <txtdir> <jpgdir> <frame>:<half>:<slug>:<pg> [...]
  half = L | R | S (single-frame page: uses full paper bbox)
Each frame is rendered once at 300dpi even if both halves are requested.
"""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image

Image.MAX_IMAGE_PIXELS = None
DPI, NCOLS, PAD, BRIGHT, FRAC, Q = 300, 4, 30, 120, 25, 85

def paper_bbox(arr):
    b = arr >= BRIGHT
    cols = np.flatnonzero(b.mean(axis=0) >= FRAC/100)
    rows = np.flatnonzero(b.mean(axis=1) >= FRAC/100)
    return cols[0], cols[-1], rows[0], rows[-1]

def ocr_page(arr, x0, x1, y0, y1, out_txt, wd, tag):
    step = (x1 - x0) / NCOLS
    chunks = []
    for c in range(NCOLS):
        cx0 = max(x0, int(x0 + c*step) - PAD); cx1 = min(x1, int(x0 + (c+1)*step) + PAD)
        p = os.path.join(wd, f"{tag}c{c}.png")
        Image.fromarray(arr[y0:y1, cx0:cx1]).save(p)
        r = subprocess.run(["tesseract", p, "-", "--psm", "4"], capture_output=True, text=True)
        chunks.append(f"[column {c+1}]\n{r.stdout.strip()}")
        os.remove(p)
    open(out_txt, "w").write("\n\n".join(chunks) + "\n")

def main():
    pdf, txtdir, jpgdir = sys.argv[1], sys.argv[2], sys.argv[3]
    jobs = {}
    for spec in sys.argv[4:]:
        fr, half, slug, pg = spec.split(":")
        jobs.setdefault(int(fr), []).append((half, slug, int(pg)))
    for fr in sorted(jobs):
        with tempfile.TemporaryDirectory() as wd:
            subprocess.run(["pdftoppm", "-f", str(fr), "-l", str(fr), "-r", str(DPI),
                            "-gray", pdf, wd + "/t"], check=True)
            pgm = [x for x in os.listdir(wd) if x.endswith(".pgm")][0]
            arr = np.asarray(Image.open(os.path.join(wd, pgm)), dtype=np.uint8)
            x0, x1, y0, y1 = paper_bbox(arr)
            gx = (x0 + x1) // 2
            for half, slug, pg in jobs[fr]:
                a, b = {"L": (x0, gx), "R": (gx, x1), "S": (x0, x1)}[half]
                name = f"{slug}_p{pg}"
                jp = os.path.join(jpgdir, name + ".jpg")
                Image.fromarray(arr[y0:y1, a:b]).save(jp, "JPEG", quality=Q, optimize=True)
                ocr_page(arr, a, b, y0, y1, os.path.join(txtdir, name + ".txt"), wd, half)
                sz = os.path.getsize(os.path.join(txtdir, name + ".txt"))
                print(f"F{fr}{half} -> {name} jpg={os.path.getsize(jp)//1024}KB txt={sz}B", flush=True)

if __name__ == "__main__":
    main()
