#!/usr/bin/env python3
"""inline_assets.py — make a single self-contained HTML file from a lesson
(fallback when GitHub publishing is not possible: publish the result as an Artifact).

Usage: python3 inline_assets.py <lesson_dir>/index.html <out.html>
"""
import sys
from pathlib import Path
src, dst = Path(sys.argv[1]), Path(sys.argv[2])
skill = Path(__file__).resolve().parent.parent / "assets"
h = src.read_text(encoding="utf-8")
css = (skill / "manual.css").read_text(encoding="utf-8")
js = (skill / "manual.js").read_text(encoding="utf-8")
h = h.replace('<link rel="stylesheet" href="../../assets/manual.css">', f"<style>\n{css}\n</style>")
h = h.replace('<script src="../../assets/manual.js" defer></script>', "")
h = h.replace("</body>", f"<script>\n{js}\n</script>\n</body>")
h = h.replace('href="../../"', 'href="#"')
dst.write_text(h, encoding="utf-8")
print("wrote", dst)
