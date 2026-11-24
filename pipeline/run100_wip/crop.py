#!/usr/bin/env python3
"""Run #100 reader crop tool: Christian Recorder, Apr-Jun 1867 (small-page, 600 ppi scan).
Usage: python3 crop.py <frame> <x0frac> <y0frac> <x1frac> <y1frac> <out.png>
Fractions are of the PAPER area (black film border trimmed), 0-1, left/top origin.
Renders at DPI=1000 by default (one column ~900px wide). For a VERIFY recheck: DPI=1600 python3 crop.py ...
(going above ~1600 adds nothing; the scan itself is 600 ppi).
Each page render is cached per (frame, dpi): the first crop of a page takes ~20-60s, later crops are fast.
Look up frames in jobs.txt ('frame:slug:page'); frames not listed there are not pages."""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
PDF = "/tmp/claude-0/-home-claude/8f46bdc5-7aa7-5a99-9c93-97b7c6b3014b/scratchpad/cr67q2/q.pdf"
CACHE = "/tmp/claude-0/-home-claude/8f46bdc5-7aa7-5a99-9c93-97b7c6b3014b/scratchpad/cr67q2/cache"
DPI = int(os.environ.get("DPI", "1000"))
MAXSIDE = 2400

fr = sys.argv[1]
x0, y0, x1, y1 = map(float, sys.argv[2:6])
out = sys.argv[6]
if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
    sys.exit("fractions must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1")

os.makedirs(CACHE, exist_ok=True)
cpath = os.path.join(CACHE, f"f{int(fr):02d}_d{DPI}.png")
if os.path.exists(cpath):
    a = np.asarray(Image.open(cpath))
else:
    with tempfile.TemporaryDirectory() as wd:
        subprocess.run(["pdftoppm", "-f", fr, "-l", fr, "-r", str(DPI), "-gray", PDF, wd + "/t"], check=True)
        p = [x for x in os.listdir(wd) if x.endswith(".pgm")][0]
        a = np.asarray(Image.open(os.path.join(wd, p)))
    tmp = cpath + f".tmp{os.getpid()}.png"
    Image.fromarray(a).save(tmp, optimize=False, compress_level=1)
    os.replace(tmp, cpath)

b = a >= 120
cols = np.flatnonzero(b.mean(0) >= .25); rows = np.flatnonzero(b.mean(1) >= .25)
X0, X1, Y0, Y1 = cols[0], cols[-1], rows[0], rows[-1]
W, H = X1 - X0, Y1 - Y0
im = Image.fromarray(a[Y0 + int(y0 * H):Y0 + int(y1 * H), X0 + int(x0 * W):X0 + int(x1 * W)])
m = max(im.size)
if m > MAXSIDE:
    im = im.resize((int(im.size[0] * MAXSIDE / m), int(im.size[1] * MAXSIDE / m)), Image.LANCZOS)
os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
im.save(out)
print(out, im.size)
