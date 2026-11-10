#!/usr/bin/env python3
"""Render high-resolution ad crops straight from the source microfilm PDF (added 2026-11-10: Michiko found the
ad images hard to read; they were being cut from the 2000px page JPEGs and came out about 320px wide).

Usage: render_ad_hires.py <source.pdf> <jobs.txt>
  jobs.txt holds 'frame:slug:page' entries (one per line or space separated), the same map used for OCR.
For every box in ad_crops.json whose issue and page are in the map, the box is rendered from the PDF at about
1100px wide and saved to ads_hires/<issue>_p<page>_<x0>-<y0>-<x1>-<y1>.jpg (box fractions x 1000).
build_ads.py uses that file when it exists and falls back to cropping the page JPEG. The paper-area rule is the
same as cr_single_process.py, so the box fractions mean the same thing in both. Re-run after changing a box."""
import json, os, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageOps
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
TARGET_W = 1100

def name(iss, pg, box):
    return f"{iss}_p{pg}_" + "-".join(str(int(round(v * 1000))) for v in box) + ".jpg"

def main():
    pdf, jobs = sys.argv[1], sys.argv[2]
    fmap = {}
    for tok in open(jobs).read().split():
        fr, slug, pg = tok.split(":"); fmap[(slug, int(pg))] = fr
    out = os.path.join(ROOT, "ads_hires"); os.makedirs(out, exist_ok=True)
    n = 0
    for c in json.load(open(os.path.join(HERE, "ad_crops.json"), encoding="utf-8"))["ads"]:
        if not c.get("box") or (c["issue"], c["page"]) not in fmap: continue
        fr = fmap[(c["issue"], c["page"])]; x0, y0, x1, y1 = c["box"]
        dst = os.path.join(out, name(c["issue"], c["page"], c["box"]))
        if os.path.exists(dst): continue
        with tempfile.TemporaryDirectory() as wd:
            subprocess.run(["pdftoppm", "-f", fr, "-l", fr, "-r", "100", "-gray", "-singlefile", pdf, wd + "/lo"], check=True)
            b = np.asarray(Image.open(wd + "/lo.pgm")) >= 120
            cols = np.flatnonzero(b.mean(0) >= .25); rows = np.flatnonzero(b.mean(1) >= .25)
            X0, X1, Y0, Y1 = cols[0], cols[-1], rows[0], rows[-1]
            dpi = int(min(1600, max(300, TARGET_W / ((x1 - x0) * (X1 - X0)) * 100)))
            s = dpi / 100.0; PW, PH = (X1 - X0) * s, (Y1 - Y0) * s
            subprocess.run(["pdftoppm", "-f", fr, "-l", fr, "-r", str(dpi), "-gray", "-singlefile",
                            "-x", str(int(X0 * s + x0 * PW)), "-y", str(int(Y0 * s + y0 * PH)),
                            "-W", str(int((x1 - x0) * PW)), "-H", str(int((y1 - y0) * PH)), pdf, wd + "/hi"], check=True)
            im = Image.open(wd + "/hi.pgm").convert("L")
            if im.size[0] > TARGET_W * 1.3:
                im = im.resize((TARGET_W, int(im.size[1] * TARGET_W / im.size[0])), Image.LANCZOS)
            im.save(dst, "JPEG", quality=85)
        n += 1; print("rendered", os.path.basename(dst), im.size, "dpi", dpi)
    print(n, "ad crops rendered")

if __name__ == "__main__":
    main()
