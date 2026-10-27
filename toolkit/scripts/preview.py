#!/usr/bin/env python3
"""preview.py — screenshot a lesson locally (desktop light, desktop dark, phone).

Usage: python3 preview.py <lesson_dir> <out_dir>
Copies the skill assets next to the lesson the way the repo lays them out,
serves it on 127.0.0.1, and writes desktop-*.png / dark-*.png / phone.png.
Needs: pip install playwright --break-system-packages && python3 -m playwright install chromium
Note: Google Fonts, Chart.js (cdnjs) and remote photos may be blocked in the
sandbox, so the preview can show fallback fonts and empty charts. Check those
on the live page.
"""
import asyncio, shutil, subprocess, sys, tempfile, time
from pathlib import Path

lesson, out = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
skill = Path(__file__).resolve().parent.parent
out.mkdir(parents=True, exist_ok=True)
site = Path(tempfile.mkdtemp())
(site / "assets").mkdir()
for f in ("manual.css", "manual.js"):
    shutil.copy(skill / "assets" / f, site / "assets" / f)
shutil.copytree(lesson, site / "lessons" / lesson.name)
port = 8790
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port)], cwd=site,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)

async def main():
    from playwright.async_api import async_playwright
    url = f"http://127.0.0.1:{port}/lessons/{lesson.name}/"
    async with async_playwright() as p:
        b = await p.chromium.launch()
        errs = []
        for scheme in ("light", "dark"):
            pg = await b.new_page(viewport={"width": 1440, "height": 900}, color_scheme=scheme)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(url); await pg.wait_for_timeout(1200)
            ids = await pg.eval_on_selector_all("section.chapter[id]", "els => els.map(e => e.id)")
            await pg.screenshot(path=str(out / f"{'desktop' if scheme == 'light' else 'dark'}-00.png"))
            for i, sid in enumerate(ids if scheme == "light" else ids[:2]):
                await pg.eval_on_selector(f"#{sid}", "e => e.scrollIntoView()")
                await pg.wait_for_timeout(300)
                await pg.screenshot(path=str(out / f"{'desktop' if scheme == 'light' else 'dark'}-{i+1:02d}.png"))
        m = await b.new_page(viewport={"width": 390, "height": 844})
        await m.goto(url); await m.wait_for_timeout(800)
        await m.screenshot(path=str(out / "phone.png"))
        await b.close()
        print("page errors:", errs or "none")
try:
    asyncio.run(main())
finally:
    srv.terminate()
print("screenshots in", out)
