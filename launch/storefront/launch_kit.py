"""Storefront launch kit: every Gumroad and Etsy listing in upload order, with its copy, images and files, plus a
checklist for two sittings.

    python launch/storefront/launch_kit.py [--root /mnt/project-files/content-factory] [--out <root>/storefront/launch-kit]

It reads the upload-ready copies in the project files folder (`--root`, the folder that `PRODUCTS_CATALOG.md` paths are
relative to), so it covers the products from every branch, not just this one. For each listing it writes:
- a header: number, product, price, the folder, the images in upload order and the digital files to attach;
- the listing's own `LISTING.md`, verbatim (it already has the title, description, tags and settings to paste).
A listing whose folder is missing is marked MISSING rather than dropped, so a gap is visible.

Order:
- Sitting 1, Gumroad, one brand account at a time (Money Made Simple, 1099 Money, Scam Decoded): the storefront's
  section order, except that a product's cross-sell target goes up first, so its receipt link can point at a live page.
- Sitting 2, Etsy (Money Made Simple shop): the dated 2027 planner first, then the single printables, then the bundles
  (a bundle's "bought separately" line needs its parts live).
- Not in either sitting, each with the reason: Dinero Simple (native review), anything with a BLOCKER, the January
  Reset bundle (Dec 30), print-on-demand posters (a sample first), KDP (proof copies), and other brands' Etsy shops.
Nothing is uploaded or published: this only writes Markdown and a CSV.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "catalog"))
import build_catalog as CAT  # noqa: E402
import build_storefront as S  # noqa: E402
import listings as L  # noqa: E402

DEFAULT_ROOT = Path("/mnt/project-files/content-factory")
IMG = (".png", ".jpg", ".jpeg", ".gif", ".mp4")
FILES = (".pdf", ".xlsx", ".zip", ".csv", ".json", ".epub", ".docx")
GUMROAD_BRANDS = ["Money Made Simple", "1099 Money", "Scam Decoded"]
LATER_PRODUCTS = {"The January Reset Bundle": "Create Dec 30, publish Jan 1, unpublish Feb 1 (JANUARY_RESET.md)."}


def _img_key(p: Path) -> tuple:
    """Etsy mockups in their numbered order, then covers, then screenshots, then the rest."""
    n = p.name
    m = re.match(r"mockup-(\d+)", n)
    if m:
        return (0, int(m.group(1)), n)
    rank = {"cover.png": 1, "cover-square.png": 2}.get(n)
    if rank:
        return (1, rank, n)
    return (2, 0, n) if n.startswith(("screenshot", "listing-")) else (3, 0, n)


def folder_parts(root: Path, rel: str) -> tuple[list[str], list[str]]:
    d = root / rel
    if not d.is_dir():
        return [], []
    imgs = sorted((p for p in d.iterdir() if p.suffix.lower() in IMG and p.name != "pin.png"), key=_img_key)
    files = sorted(p.name for p in d.iterdir() if p.suffix.lower() in FILES)
    return [p.name for p in imgs], files


def blocked(r: dict) -> str:
    """Why a row is outside the two sittings, or ''."""
    if r["brand"] == "Dinero Simple":
        return "Native review first (REVIEW_CHECKLIST_ES.md)."
    if "BLOCKER" in r["notes"]:
        m = re.search(r"BLOCKER.*?\.(?=\s|$)", r["notes"])
        return m.group(0) if m else "BLOCKER (see the catalog notes)."
    if r["product"] in LATER_PRODUCTS:
        return LATER_PRODUCTS[r["product"]]
    if "print on demand" in r["platform"]:
        return "Print on demand: set the production partner and order one sample first."
    if "Amazon" in r["platform"]:
        return "KDP: proof copies and the AI questions first (KDP_NOTES.md)."
    if r["platform"].startswith("On hold"):
        return r["platform"]
    if "[PRICE]" in r["price"]:
        return "Price not set yet."
    return ""


def gumroad_order(rows: list[dict]) -> list[dict]:
    out, by = [], {}
    for r in rows:
        if "Gumroad" in r["platform"]:
            by.setdefault((r["brand"], r["product"]), r)
    for brand in GUMROAD_BRANDS:
        placed: list[str] = []
        visiting: set[str] = set()

        def put(name: str, depth: int = 0) -> None:
            if name in placed or name in visiting or (brand, name) not in by:
                return
            visiting.add(name)
            nxt = S.CROSS_SELL.get(name, ("",))[0]
            if nxt and nxt != name and not blocked(by.get((brand, nxt), {"brand": brand, "notes": "", "product": nxt,
                                                                          "platform": "Gumroad", "price": "$1"})):
                put(nxt, depth + 1)
            placed.append(name)

        featured = S.BRANDS[brand]["featured"]
        for name in [featured] + [p for _s, ps in S.BRANDS[brand]["sections"] for p in ps]:
            put(name)
        out += [by[(brand, n)] for n in placed]
    return out


def etsy_order(rows: list[dict]) -> list[dict]:
    mms = {r["product"]: r for r in rows if r["brand"] == "Money Made Simple" and r["platform"] == "Etsy"}
    names = [it["name"] for it in L.LISTINGS if it.get("dated")]
    names += [it["name"] for it in L.LISTINGS if it["kind"] == "printable" and not it.get("dated")]
    names += [it["name"] for it in L.LISTINGS if it["kind"] == "bundle"]
    out = [mms[n] for n in names if n in mms]
    # Money Made Simple products sold on both (their LISTING.md has an Etsy part), after the shop's own listings
    out += [r for r in rows if r["brand"] == "Money Made Simple" and "Etsy" in r["platform"] and "Gumroad" in r["platform"]
            and "optional" not in r["platform"]]
    return out


def later_rows(rows: list[dict], done: set) -> list[dict]:
    out = []
    for r in rows:
        if (r["brand"], r["product"], r["platform"]) in done:
            if r["brand"] != "Money Made Simple" and "Etsy" in r["platform"]:
                out.append(dict(r, platform="Etsy", why=f"Etsy edition (Gumroad is in sitting 1): needs {r['brand']}'s own "
                                                          "Etsy shop, or a section in an existing one."))
            continue
        why = blocked(r)
        if not why and "Etsy" in r["platform"] and r["brand"] != "Money Made Simple":
            why = f"Needs {r['brand']}'s own Etsy shop (or a section in an existing one)."
        if not why and "Etsy optional" in r["platform"]:
            continue
        out.append(dict(r, why=why or "Not placed in a sitting."))
    return out


def entry(n: int, r: dict, root: Path, platform: str, seen: dict) -> str:
    folder = r["files"].split(" ")[0]
    imgs, files = folder_parts(root, folder)
    lst = root / r["listing"]
    head = [f"### {n}. {r['product']} ({platform}, {r['price']})\n",
            f"- **Folder:** `content-factory/{folder}`"]
    if not lst.exists():
        head.append(f"- **MISSING:** `content-factory/{r['listing']}` isn't in the project files yet. {r['notes']}")
        return "\n".join(head) + "\n"
    head.append("- **Images, in this order:** " + (", ".join(f"`{i}`" for i in imgs) or "none in the folder"))
    head.append("- **Files to attach:** " + (", ".join(f"`{f}`" for f in files) or "see the listing"))
    if r["notes"]:
        head.append(f"- **Note:** {r['notes']}")
    key = str(lst)
    if key in seen:
        head.append(f"- **Copy:** the same `LISTING.md` as #{seen[key]} above; use its {platform} fields.")
        return "\n".join(head) + "\n"
    seen[key] = n
    body = lst.read_text().strip()
    body = re.sub(r"^(#{1,5}) ", lambda m: "#" * min(6, len(m.group(1)) + 3) + " ", body, flags=re.M)
    return "\n".join(head) + "\n\n<details><summary>Listing copy (LISTING.md)</summary>\n\n" + body + "\n\n</details>\n"


def title_and_tags(path: Path) -> tuple[str, str]:
    if not path.exists():
        return "", ""
    t = path.read_text()
    m = re.search(r"^##+ [^\n]*(?:Etsy title|Title|Name|Título)[^\n]*\n+(.+)", t, re.M)
    tags = re.search(r"^##+ [^\n]*(?:Tags|Etiquetas)[^\n]*\n((?:\s*(?:\d+\.|-) .+\n?)+)", t, re.M)
    tag_list = re.findall(r"^\s*(?:\d+\.|-) (.+)$", tags.group(1), re.M) if tags else []
    return (m.group(1).strip().strip("*`") if m else ""), "; ".join(x.strip("` ") for x in tag_list)


CHECKLIST = """## Before sitting 1 (10 minutes)

- [ ] Merge the PRs in the go-live safe order, then re-run `python launch/storefront/launch_kit.py` so this kit matches.
- [ ] Have the brand email logins ready: one Gumroad account per brand (Money Made Simple, 1099 Money, Scam Decoded).
- [ ] Open this file and the project files folder side by side.

## Sitting 1: Gumroad (about 3 hours: 39 listings at 4 to 5 minutes each)

- [ ] For each brand: Settings > Profile. Paste the name, bio and about text from `storefront/<brand>/STOREFRONT.md`, upload
      `avatar.png` and `cover.png`.
- [ ] Create the discount codes listed in each `STOREFRONT.md` (and BF25/BF10/BF5/YEAREND10 with their Nov 27-30 dates).
- [ ] Add each product below **in order**. For each: New product > Digital product, paste the name, price and description,
      upload the files, add the images in the order shown, set the receipt note to the next step in
      `NEXT_STEP_ALL_PRODUCTS.md`, then publish.
- [ ] Put the products into the profile sections in `STOREFRONT.md`, and feature the featured product.
- [ ] Paste each real Gumroad link into `launch/products/` and `launch/templates/links.json`, then rebuild and replace the
      `[LINK: ...]` placeholders.
- [ ] Buy your own cheapest product with a 100% code to check the delivery email, then refund it.

## Sitting 2: Etsy (about 3 to 4 hours: shop setup, then the listings)

- [ ] Shop setup from `etsy/SHOP_SETUP.md` (shop name, banner, policies, the "message to buyers" for digital items).
- [ ] Add each listing below **in order**: Shop Manager > Listings > Add a listing. Paste the title, description and 13
      tags, fill the attributes, upload the images in the order shown (01 is the thumbnail) and the files under "Files to
      attach". No off-Etsy links.
- [ ] Set up the saved replies for the next steps in `NEXT_STEP_ALL_PRODUCTS.md` (Etsy section).
- [ ] Create BF25 (Nov 27-30, bundles only). Star the featured listings on Dec 26 (catalog, January push).
- [ ] List no guides: Etsy bans AI-generated functional guides, so they're Gumroad only.

## After both sittings

- [ ] Tick each listing in `launch_kit.csv` (the `done` column) and keep the file in the project files.
- [ ] The "Later" list below has a reason and a date for each product that isn't in a sitting.
"""


def build(root: Path, rows: list[dict] | None = None) -> tuple[dict[str, str], list[dict]]:
    """-> ({file name: Markdown}, csv rows). LAUNCH_KIT.md is the checklist and index; one file per sitting has the copy."""
    rows = rows if rows is not None else CAT.all_rows()
    g = [r for r in gumroad_order(rows) if not blocked(r)]
    e = [r for r in etsy_order(rows) if not blocked(r)]
    done = {(r["brand"], r["product"], r["platform"]) for r in g + e}
    later = later_rows(rows, done)
    seen: dict = {}
    n, csv_rows, missing, files = 0, [], [], {}
    index = []
    for fname, sitting, items, plat in (("SITTING_1_GUMROAD.md", "Sitting 1: Gumroad", g, "Gumroad"),
                                        ("SITTING_2_ETSY.md", "Sitting 2: Etsy (Money Made Simple shop)", e, "Etsy")):
        out = [f"# {sitting}\n", f"{len(items)} listings, in upload order. Checklist and the rest: `LAUNCH_KIT.md`.\n"]
        index.append(f"\n## {sitting} ({len(items)} listings, `{fname}`)\n\n| # | Brand | Product | Price | Listing copy |\n|---|---|---|---|---|")
        brand = None
        for r in items:
            if r["brand"] != brand:
                brand = r["brand"]
                out.append(f"\n## {brand}\n")
            n += 1
            out.append(entry(n, r, root, plat, seen))
            ok = (root / r["listing"]).exists()
            if not ok:
                missing.append(r["product"])
            index.append(f"| {n} | {r['brand']} | {r['product']} | {r['price']} | `{r['listing']}`{'' if ok else ' **MISSING**'} |")
            imgs, fl = folder_parts(root, r["files"].split(" ")[0])
            title, tags = title_and_tags(root / r["listing"])
            csv_rows.append(dict(n=n, sitting=plat, brand=r["brand"], product=r["product"], price=r["price"],
                                 title=title, tags=tags, images="; ".join(imgs), files="; ".join(fl),
                                 listing="content-factory/" + r["listing"], done=""))
        files[fname] = "\n".join(out) + "\n"
    head = ["# Storefront launch kit: every listing in upload order\n",
            f"{len(g)} Gumroad listings and {len(e)} Etsy listings in two sittings, then {len(later)} for later, each with "
            "its reason. The copy, images and files for each listing are in `SITTING_1_GUMROAD.md` and "
            "`SITTING_2_ETSY.md`; `launch_kit.csv` has one row per listing with a `done` column. Built from "
            "`PRODUCTS_CATALOG.md` and the upload-ready copies in the project files by `launch/storefront/launch_kit.py`. "
            "Nothing has been uploaded or published.\n"]
    if missing:
        head.append(f"> **Missing from the project files:** {', '.join(missing)}. Copy them in and rebuild.\n")
    head.append(CHECKLIST)
    head += index
    head.append(f"\n## Later ({len(later)})\n\n| Brand | Product | Platform | Price | Why not yet |\n|---|---|---|---|---|")
    head += [f"| {r['brand']} | {r['product']} | {r['platform']} | {r['price']} | {r['why']} |" for r in later]
    files["LAUNCH_KIT.md"] = "\n".join(head) + "\n"
    return files, csv_rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    root = Path(a.root)
    if not root.is_dir():
        print(f"no upload-ready folder at {root}; pass --root")
        return 1
    docs, rows = build(root)
    out = Path(a.out) if a.out else HERE / "dist" / "launch-kit"
    out.mkdir(parents=True, exist_ok=True)
    for name, md in docs.items():
        (out / name).write_text(md)
    with open(out / "launch_kit.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} listings in upload order -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
