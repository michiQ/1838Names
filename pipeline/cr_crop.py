#!/usr/bin/env python3
"""Render a crop of one reel frame at 400dpi for reading.
Usage: crop.py <frame> <x0> <y0> <x1> <y1> <out.png>   (fractions 0-1 of the paper area)
Output is capped at 1600px on its longest side (readable; keeps image reads light)."""
import os, subprocess, sys, tempfile
import numpy as np
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
fr, x0, y0, x1, y1, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
with tempfile.TemporaryDirectory() as wd:
    subprocess.run(["pdftoppm", "-f", fr, "-l", fr, "-r", "400", "-gray",
                    os.path.join(HERE, "reel.pdf"), wd + "/t"], check=True)
    p = [x for x in os.listdir(wd) if x.endswith(".pgm")][0]
    a = np.asarray(Image.open(os.path.join(wd, p)))
b = a >= 120
cols = np.flatnonzero(b.mean(0) >= .25); rows = np.flatnonzero(b.mean(1) >= .25)
X0, X1, Y0, Y1 = cols[0], cols[-1], rows[0], rows[-1]
W, H = X1 - X0, Y1 - Y0
im = Image.fromarray(a[Y0 + int(y0 * H):Y0 + int(y1 * H), X0 + int(x0 * W):X0 + int(x1 * W)])
m = max(im.size)
if m > 1600:
    im = im.resize((int(im.size[0] * 1600 / m), int(im.size[1] * 1600 / m)), Image.LANCZOS)
im.save(out)
print(out, im.size)
