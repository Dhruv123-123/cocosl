"""Build the upload-ready kit for Money Dashboard Pro (English) and Tablero de dinero Pro (Spanish).

    python launch/dashboard-pro/kit.py [--out /mnt/project-files/content-factory/templates]

For each language writes <out>/<folder>/: the .xlsx, Start-Here.pdf (with the Google Sheets copy link from links.json),
cover.png (1280x720), cover-square.png (600x600), screenshot-1..3.png, a zip of the buyer files, LISTING.md and SETUP.md.
Needs LibreOffice (screenshots), poppler's pdftoppm, Pillow and Node with Playwright (covers and the PDF).
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PIL import Image, ImageChops

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from build import build  # noqa: E402
from listing import KIT  # noqa: E402


def crop(img: Image.Image, pad: int = 24) -> Image.Image:
    bg = Image.new(img.mode, img.size, (255, 255, 255))
    box = ImageChops.difference(img, bg).getbbox()
    if not box:
        return img
    l, t, r, b = box
    return img.crop((max(0, l - pad), max(0, t - pad), min(img.width, r + pad), min(img.height, b + pad)))


def screenshots(xlsx: Path, out: Path, pages: list[int]) -> list[Path]:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", str(xlsx), "--outdir", tmp], check=True, capture_output=True)
        pdf = next(Path(tmp).glob("*.pdf"))
        paths = []
        for i, page in enumerate(pages, 1):
            subprocess.run(["pdftoppm", "-r", "150", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf), f"{tmp}/p{i}"], check=True)
            img = crop(Image.open(f"{tmp}/p{i}.png").convert("RGB"))
            canvas = Image.new("RGB", (max(img.width, 1600), img.height + 0), (255, 255, 255))
            canvas.paste(img, (0, 0))
            p = out / f"screenshot-{i}.png"
            canvas.save(p, optimize=True)
            paths.append(p)
        return paths


def find_page(xlsx: Path, needles: list[str]) -> list[int]:
    """Page numbers whose first line matches each tab title, from the same LibreOffice PDF the screenshots use."""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", str(xlsx), "--outdir", tmp], check=True, capture_output=True)
        pdf = next(Path(tmp).glob("*.pdf"))
        n = int(next(l for l in subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout.splitlines() if l.startswith("Pages")).split()[-1])
        firsts = [subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), str(pdf), "-"], capture_output=True, text=True).stdout.strip().split("\n")[0] for i in range(1, n + 1)]
    return [firsts.index(t) + 1 for t in needles]


def render(html_path: Path, png: Path | None, pdf: Path | None, size: tuple[int, int] | None) -> None:
    js = HERE / "render.mjs"
    args = ["node", str(js), str(html_path)] + (["--png", str(png), "--size", f"{size[0]}x{size[1]}"] if png else ["--pdf", str(pdf)])
    subprocess.run(args, check=True)


CSS = """
:root{--ink:#0b1d13;--paper:#f4f1e8;--gold:#f2b134;--green:#2fbf71;--muted:#5b6b61}
*{box-sizing:border-box}body{margin:0;font-family:Arial,Helvetica,sans-serif;color:var(--ink)}
"""


def cover_html(k: dict, shot: Path, square: bool) -> str:
    w, h = (600, 600) if square else (1280, 720)
    img = shot.resolve().as_uri()
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:{w}px;height:{h}px;background:var(--ink);overflow:hidden;position:relative}}
.t{{position:absolute;left:{36 if square else 64}px;top:{40 if square else 64}px;right:{36 if square else 640}px;color:#fff}}
.tag{{display:inline-block;background:var(--gold);color:var(--ink);font-weight:800;border-radius:999px;padding:6px 14px;font-size:{14 if square else 18}px}}
h1{{font-size:{38 if square else 58}px;line-height:1.05;margin:16px 0 10px}}
p{{font-size:{17 if square else 22}px;line-height:1.35;color:#d9e4dc;margin:0}}
.shot{{position:absolute;{'left:36px;right:-60px;bottom:-40px;height:300px' if square else 'right:-40px;top:70px;width:640px;height:auto'};border-radius:14px;box-shadow:0 20px 50px rgba(0,0,0,.45);background:#fff;overflow:hidden;border:6px solid #fff}}
.shot img{{width:{'640px' if square else '100%'};display:block}}
.brand{{position:absolute;left:{36 if square else 64}px;bottom:{330 if square else 48}px;color:var(--gold);font-weight:700;font-size:{14 if square else 18}px}}
</style></head><body>
<div class="t"><span class="tag">{html.escape(k['cover_tag'])}</span><h1>{html.escape(k['cover_title'])}</h1><p>{html.escape(k['cover_sub'])}</p></div>
<div class="brand">Money Made Simple</div>
<div class="shot"><img src="{img}" alt=""></div>
</body></html>"""


def start_here_html(k: dict, link: str) -> str:
    ok = link.startswith("https://docs.google.com/") and link.rstrip("/").endswith("/copy")
    link_block = (f'<p class="btn"><a href="{html.escape(link)}">{html.escape(k["pdf_button"])}</a></p><p class="small">{html.escape(link)}</p>' if ok
                  else f'<p class="todo">{html.escape(k["pdf_todo"])}</p>')
    steps = "".join(f"<li>{html.escape(s)}</li>" for s in k["pdf_steps"])
    excel = "".join(f"<li>{html.escape(s)}</li>" for s in k["pdf_excel"])
    tips = "".join(f"<li>{html.escape(s)}</li>" for s in k["pdf_tips"])
    return f"""<!doctype html><html lang="{k['lang']}"><head><meta charset="utf-8"><style>{CSS}
@page{{size:Letter;margin:0.6in}}
h1{{font-size:30px;margin:0 0 6px}}.sub{{color:var(--muted);margin:0 0 22px;font-size:15px}}
h2{{font-size:18px;margin:26px 0 8px;border-bottom:2px solid var(--gold);padding-bottom:4px}}
li{{margin:6px 0;line-height:1.45;font-size:14px}}
.btn a{{display:inline-block;background:var(--gold);color:var(--ink);font-weight:800;text-decoration:none;border-radius:999px;padding:12px 22px;font-size:17px}}
.small{{font-size:11px;color:var(--muted);word-break:break-all}}
.todo{{background:#fde8e6;border:2px dashed #c0392b;padding:12px;font-weight:700}}
.foot{{margin-top:30px;font-size:11px;color:var(--muted)}}
</style></head><body>
<h1>{html.escape(k['pdf_title'])}</h1><p class="sub">{html.escape(k['pdf_sub'])}</p>
<h2>{html.escape(k['pdf_h_copy'])}</h2>{link_block}<ol>{steps}</ol>
<h2>{html.escape(k['pdf_h_excel'])}</h2><ul>{excel}</ul>
<h2>{html.escape(k['pdf_h_tips'])}</h2><ul>{tips}</ul>
<p class="foot">{html.escape(k['legal'])}</p>
</body></html>"""


def make(lang: str, out_root: Path, links: dict) -> Path:
    k = KIT[lang]
    out = out_root / k["folder"]
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    xlsx = build(lang, out)
    pages = find_page(xlsx, k["shot_titles"])
    shots = screenshots(xlsx, out, pages)
    with tempfile.TemporaryDirectory() as tmp:
        for square, name in ((False, "cover.png"), (True, "cover-square.png")):
            h = Path(tmp) / f"{name}.html"
            h.write_text(cover_html(k, shots[0], square), encoding="utf-8")
            render(h, out / name, None, (600, 600) if square else (1280, 720))
        h = Path(tmp) / "start.html"
        h.write_text(start_here_html(k, links.get(k["link_key"], "")), encoding="utf-8")
        render(h, None, out / "Start-Here.pdf" if lang == "en" else out / "Empieza-Aqui.pdf", None)
    pdf = out / ("Start-Here.pdf" if lang == "en" else "Empieza-Aqui.pdf")
    with zipfile.ZipFile(out / k["zip"], "w", zipfile.ZIP_DEFLATED) as z:
        z.write(pdf, pdf.name)
        z.write(xlsx, xlsx.name)
    (out / "LISTING.md").write_text(k["listing"], encoding="utf-8")
    (out / "SETUP.md").write_text(KIT["setup"], encoding="utf-8")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/mnt/project-files/content-factory/templates")
    ap.add_argument("--lang", default="both", choices=["en", "es", "both"])
    a = ap.parse_args()
    links = json.loads((HERE / "links.json").read_text())
    for lang in (["en", "es"] if a.lang == "both" else [a.lang]):
        print(make(lang, Path(a.out), links))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
