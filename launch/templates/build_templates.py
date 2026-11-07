"""Build the Google Sheets + Notion template line into launch/templates/dist/.

    python launch/templates/build_templates.py            # everything
    python launch/templates/build_templates.py --only notion-budget
    python launch/templates/build_templates.py --no-images  # skip screenshots/covers (fast)

Per template, dist/<slug>/ gets: the files to upload to Gumroad (a Start Here PDF with the copy/duplicate
link, plus the .xlsx for Sheets templates), 3 screenshots (1600x1000), store covers (1280x720 + 600x600)
and LISTING.md. Notion templates also get BUILD.md (how to build it in Notion, by script or by hand) and
example-data CSVs. Links come from links.json: fill it in once the templates are published, then rebuild.

Fails if a workbook has a formula error after LibreOffice recalculates it, if a Notion formula names a
property that doesn't exist, or if the Start Here PDF overflows its page.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "launch" / "products"))
sys.path.insert(0, str(ROOT / "launch" / "etsy"))

import catalog as C  # noqa: E402
import notion_spec as N  # noqa: E402
import previews as V  # noqa: E402
import sheets_templates as ST  # noqa: E402
from build import recalc_check  # noqa: E402  (launch/products/build.py)
from build_etsy import run_jobs  # noqa: E402  (launch/etsy/build_etsy.py)

LINKS = HERE / "links.json"
GUMROAD_FEE = (0.10, 0.50)      # Gumroad direct sale: 10% + $0.50, plus card processing
CARD_FEE = (0.029, 0.30)
NOTION_FEE = (0.08, 0.40)       # selling directly on Notion Marketplace (approved creators)


def net(price: float, fee: tuple, card: tuple | None = None) -> float:
    if price == 0:
        return 0.0
    out = price - (price * fee[0] + fee[1])
    if card:
        out -= price * card[0] + card[1]
    return round(out, 2)


def formula_refs(expr: str) -> tuple[set[str], set[str]]:
    """(names in prop("..."), names in current.prop("..."))."""
    cur = set(re.findall(r'current\.prop\("([^"]+)"\)', expr))
    allp = set(re.findall(r'(?<![.\w])prop\("([^"]+)"\)', expr))
    return allp, cur


def check_notion(t: dict) -> list[str]:
    bad = []
    dbs = N.all_dbs(t)
    every = set().union(*(N.prop_names(d, t) for d in dbs))
    for d in dbs:
        names = N.prop_names(d, t)
        for name, kind, cfg in d["props"]:
            if kind != "formula":
                continue
            own, cur = formula_refs(cfg["expr"])
            bad += [f"{d['title']}.{name}: no property {p!r}" for p in own - names]
            bad += [f"{d['title']}.{name}: no related property {p!r}" for p in cur - every]
            if cfg["expr"].count("(") != cfg["expr"].count(")") or cfg["expr"].count('"') % 2:
                bad.append(f"{d['title']}.{name}: unbalanced brackets or quotes")
    return bad


# ---- Notion BUILD.md + CSVs --------------------------------------------------------------------------------
TYPE_NAME = {"title": "Title (rename to Name)", "number": "Number", "select": "Select", "date": "Date",
             "checkbox": "Checkbox", "rich_text": "Text", "relation": "Relation", "formula": "Formula"}


def build_md(t: dict) -> str:
    out = [f"# Build {t['name']} in Notion", "",
           "Two ways. **A** takes about 5 minutes and is what we recommend. **B** is the same thing by hand (about 40 minutes).", "",
           "## A. With the builder script", "",
           "1. One time: notion.so/profile/integrations > **New integration** (Internal) > copy the secret. "
           "In your terminal: `export NOTION_TOKEN=...` (never commit it or paste it anywhere).",
           "2. In Notion make an empty page called *Templates*. ••• > **Connections** > add your integration.",
           f"3. `python launch/templates/notion_build.py {t['slug']} --parent \"<link to the Templates page>\"`",
           "4. Open the new page and do the **finishing touches** below (views + dollar formats), then publish (see SETUP.md).", "",
           "## Finishing touches (both ways)", ""]
    for d in N.all_dbs(t):
        dollars = [n for n, k, c in d["props"] if k == "formula" and c.get("format") == "dollar"]
        out.append(f"**{d['icon']} {d['title']}**")
        for v in d["views"]:
            out.append(f"- {v}")
        if dollars:
            out.append(f"- Click each of these columns > Edit property > Number format > **US dollar**: {', '.join(dollars)}.")
        rels = [n for n, k, c in d["props"] if k == "relation" and c.get("single")]
        if rels:
            out.append(f"- {', '.join(rels)}: Edit property > Limit > **1 page**.")
        out.append("")
    out += ["Then: page ••• > **Customize page** > turn off *Backlinks* and *Page discussions* (looks cleaner when duplicated). "
            "Turn on **Full width**.", "", "## B. By hand", ""]
    step = 1
    if t.get("children"):
        out.append(f"{step}. Build each of these first, as sub-pages of this page (each has its own BUILD.md): "
                   + ", ".join(c["name"] for c in t["children"]) + ".")
        step += 1
    out.append(f"{step}. New page, icon {t['icon']}, title **{t['name'].replace(' (free)', '')}**. Add the text blocks in the order "
               "shown in the screenshots (callouts, headings, to-dos). The exact text is in `notion_spec.py` (`layout`).")
    step += 1
    for d in t["dbs"]:
        out += [f"{step}. Type `/database inline`, name it **{d['icon']} {d['title']}**, and add these properties in order:", "",
                "| Property | Type | Settings |", "|---|---|---|"]
        for name, kind, cfg in d["props"]:
            if kind == "formula":
                continue
            s = ""
            if kind == "number":
                s = "US dollar" if cfg.get("format") == "dollar" else "Number"
            elif kind == "select":
                s = "Options: " + ", ".join(cfg["options"])
            elif kind == "relation":
                s = f"Relates to **{next(x['title'] for x in N.all_dbs(t) if x['key'] == cfg['db'])}**; turn on *Show on that database* and name it **{cfg['reverse']}**"
            out.append(f"| {name} | {TYPE_NAME[kind]} | {s} |")
        out.append("")
        step += 1
    for d in t["dbs"]:
        f = [(n, c) for n, k, c in d["props"] if k == "formula"]
        if not f:
            continue
        out.append(f"{step}. In **{d['title']}**, add these Formula properties in this order (paste each formula as is):")
        out.append("")
        for n, c in f:
            out += [f"**{n}**", "```", c["expr"], "```"]
        out.append("")
        step += 1
    out += [f"{step}. Example rows: in each database, ••• > **Merge with CSV** and pick the file from `example-data/` "
            "(do the databases without relations first). Or just type a few rows.", "",
            f"{step + 1}. Finishing touches above, then publish (SETUP.md).", ""]
    return "\n".join(out)


def write_csvs(t: dict, folder: Path, today: date) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for d in N.all_dbs(t):
        cols = [n for n, k, _ in d["props"] if k != "formula"]
        kinds = {n: k for n, k, _ in d["props"]}
        with open(folder / f"{d['title'].replace(' ', '-')}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(cols)
            for r in d["rows"]:
                row = []
                for c in cols:
                    v = r.get(c, "")
                    if kinds[c] == "date":
                        v = N.resolve_date(v, today).isoformat()
                    elif kinds[c] == "checkbox":
                        v = "Yes" if v else "No"
                    row.append(v)
                w.writerow(row)


# ---- listing copy ------------------------------------------------------------------------------------------
def listing_md(it: dict, files: list[str]) -> str:
    price = it["price"]
    kind = it["kind"]
    notion = kind in ("notion", "notion-bundle", "free")
    how = C.NOTION_HOW if notion else C.SHEETS_HOW
    nxt = C.BY_SLUG.get(it.get("next") or "")
    lines = [f"# {it['name']}: listing kit", "",
             f"**Price:** {'Free ($0+, email required)' if price == 0 else f'${price}'}"
             + (f" · you keep about **${net(price, GUMROAD_FEE, CARD_FEE):.2f}** per Gumroad sale"
                f"{f' (or ${net(price, NOTION_FEE):.2f} selling directly on Notion Marketplace)' if notion else ''}" if price else ""),
             ""]
    if it.get("bundle"):
        worth = sum(C.BY_SLUG[s]["price"] for s in it["bundle"])
        lines += [f"**Bundle:** {', '.join(C.BY_SLUG[s]['name'] for s in it['bundle'])} (${worth} separately).", ""]
    lines += ["## Files to upload to Gumroad", "", "| File | What it is |", "|---|---|"]
    for f in files:
        what = ("One download with everything (upload this)" if f.endswith(".zip") else
                "The copy/duplicate link and setup steps" if f.startswith("Start-Here") else
                "The spreadsheet, for Excel or Numbers (also inside the zip)")
        lines.append(f"| `{f}` | {what} |")
    lines += ["", "Images: upload `cover.png` as the cover and `cover-square.png` as the thumbnail, then the screenshots in order.", "",
              "## Gumroad", "", f"**Name:** {it['title']}", "", f"**Summary:** {it['tagline']}", "", "**Description:**", ""]
    desc = [it["hook"], "", f"**{it['name']}** " + it["tagline"][0].lower() + it["tagline"][1:], "", "**What you get**"]
    desc += [f"- {g}" for g in it["gets"]]
    desc += ["", "**How it works**"] + [f"{i}. {h}" for i, h in enumerate(how, 1)]
    desc += ["", f"**Who it's for:** {it['who']}", ""]
    for q, a in it["faq"]:
        desc += [f"**{q}** {a}", ""]
    if price == 0:
        desc += ["You'll also get the free weekly Money Made Simple email. Unsubscribe any time.", ""]
    desc += [C.LEGAL]
    lines += ["> " + d if d else ">" for d in desc]
    lines += ["", f"**Tags:** {', '.join(it['tags'])}", "",
              "**Settings:** Product type *Digital product*. Content: upload the files above. "
              + ("Price $0, tick *Allow customers to pay what they want* off, and leave email collection on (Gumroad always asks for "
                 "an email); tick *Add buyers to my audience*." if price == 0 else
                 "Turn off *Allow customers to pay what they want*.")]
    if nxt:
        lines += ["", f"**Upsell:** Checkout > Upsells > offer **{nxt['name']}** (${nxt['price']})."]
    if notion:
        lines += ["", "## Notion Marketplace", "",
                  f"**Title:** {it['name'].replace(' (free)', '')}", "",
                  f"**Short description:** {it['tagline']}", "",
                  f"**Category:** {it['notion_category']} · **Tags:** {', '.join(it['tags'][:5])}", "",
                  "**Description:** use the Gumroad description above (Marketplace descriptions are plain text, so drop the bold).", ""]
        if price == 0:
            lines += ["**Price:** Free. **Email capture:** *Require*. That's the email list; download the CSV from your "
                      "creator profile weekly and import it to your email tool. Only send the weekly email people signed up "
                      "for, and honour unsubscribes.", ""]
        else:
            lines += [f"**Price:** ${price}. **Sell with:** your Gumroad product URL (works today), or *Notion* once your "
                      "seller application is approved (8% + $0.40 per sale, paid out through Stripe).", ""]
        lines += ["**Images:** the screenshots in order. Notion reviews every template; replace them with your own "
                  "screenshots of the built template once it's live (the builder fills in the same example data)."]
    return "\n".join(lines) + "\n"


# ---- main -----------------------------------------------------------------------------------------------
def tips_for(it: dict) -> list[str]:
    if it["kind"] in ("sheets", "sheets-bundle"):
        return ["The link makes **your own copy**. Nobody (including us) can see what you type.",
                "Prefer Excel or Numbers? Open the .xlsx in your download. Everything works the same.",
                "Every tab has yellow input cells. Type over the example data, or select it and press Delete.",
                "Keep it open in a browser tab and log spending for two minutes a day, or ten minutes a week."]
    return ["Not on Notion yet? Make a free account at notion.com first, then click the link.",
            "**Duplicate** makes your own copy in your workspace. Nobody (including us) can see it.",
            "The example rows show how it works. Delete them (select rows > Delete) when you're ready.",
            "On your phone? The Notion app works great for logging; set up on a computer."]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--out", default=str(HERE / "dist"))
    ap.add_argument("--no-images", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    links = json.loads(LINKS.read_text())
    today = date.today()
    items = [i for i in C.ITEMS if not a.only or i["slug"] in a.only]
    failures, missing = [], []
    work = Path(tempfile.mkdtemp(prefix="tpl-"))
    shot_jobs, cover_jobs, pdf_jobs = [], [], []
    sheet_files: dict[str, Path] = {}

    # 1. spreadsheets (always built, bundles need them)
    for slug, (fn, builder) in ST.SHEETS.items():
        d = out / slug
        d.mkdir(exist_ok=True)
        p = builder(d / fn, today)
        bad = recalc_check(p)
        if bad:
            failures.append(f"{fn}: {bad[:5]}")
        sheet_files[slug] = p
    recalc_dir = work / "recalc"
    subprocess.run(["soffice", "--headless", "--calc", "--convert-to", "xlsx", "--outdir", str(recalc_dir),
                    *map(str, sheet_files.values())], capture_output=True, timeout=300, check=True)

    for it in items:
        d = out / it["slug"]
        d.mkdir(exist_ok=True)
        kind = it["kind"]
        # links for the Start Here PDF
        subs = [C.BY_SLUG[s] for s in it.get("bundle", [])] if kind == "sheets-bundle" else [it]
        lk = []
        for s in subs:
            url = links.get(s["link"], "")
            if not url or url.startswith("TODO"):
                missing.append(s["link"])
            lk.append((f"{s['name']}: {'make your copy' if kind.startswith('sheets') else 'duplicate the template'}", url))
        nxt = C.BY_SLUG.get(it.get("next") or "")
        how = C.NOTION_HOW if kind in ("notion", "notion-bundle", "free") else C.SHEETS_HOW
        src = work / f"start-{it['slug']}.html"
        pdf_how = [how[1].replace("Click the link and press", "Click your link above (a computer is easiest) and press"), how[2]]
        src.write_text(V.start_here_html(it, lk, pdf_how, tips_for(it), nxt))
        pdf_jobs.append({"src": str(src), "pdf": str(d / "Start-Here.pdf")})
        files = ["Start-Here.pdf"]

        if kind in ("sheets", "sheets-bundle"):
            slugs = it.get("bundle", [it["slug"]])
            for s in slugs:
                if s != it["slug"]:
                    shutil.copy(sheet_files[s], d / sheet_files[s].name)
            files += [sheet_files[s].name for s in slugs]
            zname = it["name"].replace(" ", "-") + ".zip"
            files.insert(0, zname)
            shots = []
            for s in slugs:
                for k, (sheet, rng) in enumerate(C.BY_SLUG[s]["shots"]):
                    if it["slug"] != s and k > 0:
                        continue
                    h = work / f"shot-{it['slug']}-{s}-{k}.html"
                    h.write_text(V.sheet_html(str(sheet_files[s]), str(recalc_dir / sheet_files[s].name), sheet, rng,
                                              C.BY_SLUG[s]["name"]))
                    shots.append(h)
        else:
            t = N.TEMPLATES[it["slug"]]
            bad = check_notion(t)
            failures += [f"{it['slug']}: {b}" for b in bad]
            (d / "BUILD.md").write_text(build_md(t))
            write_csvs(t, d / "example-data", today)
            shots = []
            for k, (label, h) in enumerate(V.notion_shots(t, today)):
                f = work / f"shot-{it['slug']}-{k}.html"
                f.write_text(h)
                shots.append(f)
        pngs = [d / f"screenshot-{k + 1}.png" for k in range(len(shots))]
        for old in d.glob("screenshot-*.png"):
            if old not in pngs:
                old.unlink()
        shot_jobs += [{"src": str(h), "png": str(p), "w": V.W, "h": V.H} for h, p in zip(shots, pngs)]
        for name, w, h in (("cover.png", 1280, 720), ("cover-square.png", 600, 600)):
            ch = work / f"cover-{it['slug']}-{w}.html"
            ch.write_text(V.cover_html(it, str(pngs[0]), w, h))
            cover_jobs.append({"src": str(ch), "png": str(d / name), "w": w, "h": h})
        (d / "LISTING.md").write_text(listing_md(it, files))
        it["_files"] = files
        it["_dir"] = d

    for r in run_jobs(pdf_jobs):
        if r["overflow"]:
            failures.append(f"{r['out']}: page overflows by {r['overflow']}")
    if not a.no_images:
        run_jobs(shot_jobs)
        run_jobs(cover_jobs)
    for it in items:
        z = [f for f in it["_files"] if f.endswith(".zip")]
        if z:
            with zipfile.ZipFile(it["_dir"] / z[0], "w", zipfile.ZIP_DEFLATED) as zf:
                for f in it["_files"]:
                    if not f.endswith(".zip"):
                        zf.write(it["_dir"] / f, f)
    # catalog table for SETUP.md readers
    with open(out / "templates.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["slug", "name", "kind", "price", "gumroad_net", "notion_direct_net", "title", "tagline", "tags"])
        for it in C.ITEMS:
            notion = it["kind"] in ("notion", "notion-bundle", "free")
            w.writerow([it["slug"], it["name"], it["kind"], it["price"], net(it["price"], GUMROAD_FEE, CARD_FEE),
                        net(it["price"], NOTION_FEE) if notion else "", it["title"], it["tagline"], "; ".join(it["tags"])])
    shutil.copy(HERE / "SETUP.md", out / "SETUP.md")
    shutil.rmtree(work, ignore_errors=True)
    if missing:
        print(f"Note: links.json still needs: {', '.join(sorted(set(missing)))} (Start Here PDFs show a placeholder).")
    if failures:
        print("FAILED:\n  " + "\n  ".join(failures))
        return 1
    print(f"Built {len(items)} templates into {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
