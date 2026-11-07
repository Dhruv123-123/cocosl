"""PRODUCTS_START_HERE.md: the one page to read before putting any product up.

    python launch/catalog/start_here.py [--root /mnt/project-files/content-factory] [--out <root>/PRODUCTS_START_HERE.md]

Built from the catalog, the launch kit and a scan of the launch files, so it stays current:
- the recommended top 5 to start wave 1 with (the spend-nothing rule: Dhruv decides how much of wave 1 goes up);
- the wave 1 upload steps, in order;
- every price not set yet ([PRICE]) and every link blank, with where it lives and how to fill it;
- what Etsy and Gumroad charge, so the cost of each choice is plain.
Nothing is uploaded or changed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAUNCH = HERE.parent
sys.path[:0] = [str(HERE), str(LAUNCH / "storefront")]
DEFAULT_ROOT = Path("/mnt/project-files/content-factory")
ETSY_LISTING_FEE = 0.20

TOP5 = [("The 20-Minute Budget", "Gumroad", "Money Made Simple's featured product: the welcome emails, the site and most posts point here.", "Free to list"),
        ("The Bill Cut Kit", "Gumroad", "The $5 first purchase; its receipt points to The 20-Minute Budget.", "Free to list"),
        ("2027 Budget Planner", "Etsy", "Dated for 2027, so it sells from December to the January peak and not after. First in the Etsy sitting.", "$0.20"),
        ("Digital Budget Planner (undated, hyperlinked)", "Etsy", "The tablet planner scouting found missing from our shop; undated, so it keeps selling.", "$0.20"),
        ("The Family Scam-Proofing Kit", "Gumroad", "Scam Decoded's featured product (week 2): the site funnel and the scam checker sell it.", "Free to list")]

# Placeholder kinds: (pattern, what it is, how to fill it)
BLANKS = [
    (r"\[your store link\\?\]", "Gumroad store link in the Money Made Simple guides and Start Here pages",
     "Put the store URL in `launch/products/catalog.json`, then `python launch/products/build.py`"),
    (r"TODO: Google Sheets link", "A Google Sheets \"make a copy\" link for each sheet template",
     "Share each sheet as a /copy link and paste it into `launch/templates/links.json`, then `python launch/templates/build_templates.py`"),
    (r"TODO: published Notion page link", "A published Notion duplicate link for each Notion template",
     "Run `notion_build.py` once per template, paste the link into `launch/templates/links.json`, rebuild"),
    (r"\[link added before launch\]", "The template link line in a Start Here PDF (fills from links.json)", "Same as the Sheets links above"),
    (r"\[LINK: [^\]]*\]", "Product links in brand Gumroad copy (The Money Reset, the Schedule C pack)",
     "Replace in the Gumroad page text when you paste it, once the linked product is live"),
    (r"\[ENLACE: [^\]]*\]", "Product links in the Spanish storefront (Dinero Simple, wave 3)", "Only after the native review"),
    (r"\{\{[a-z_]+\}\}", "Merge fields in the post-purchase emails ({{download_url}}, {{planner_url}} and so on)",
     "Set them in Gumroad Workflows or the email tool when you set up each sequence"),
    (r"TODO: your Gumroad store URL|TODO: your newsletter sign", "Store and newsletter URLs in the site config",
     "Fill in when the store and the newsletter exist"),
]


def scan(base: Path) -> dict[str, dict[str, int]]:
    """{blank description: {file: count}} over the launch folder's text files."""
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for p in base.rglob("*"):
        if p.suffix not in (".md", ".py", ".json", ".html", ".txt") or "dist" in p.parts or "__pycache__" in p.parts \
                or p.name in ("start_here.py", "etsy_audit.py", "PRODUCTS_START_HERE.md", "PRODUCTS_CATALOG.md",
                              "ETSY_COMPLIANCE.md") or "chapters" in p.parts or not p.is_file():
            # generated reports repeat the blanks; ebook {{chapter-id}} cross-references resolve at build time
            continue
        t = p.read_text(errors="ignore")
        for pat, what, _how in BLANKS:
            n = len(re.findall(pat, t))
            if n:
                out[what][str(p.relative_to(base.parent))] += n
    return out


def build(root: Path) -> str:
    import build_catalog as CAT
    import launch_kit as K
    rows = CAT.all_rows()
    docs, csv_rows = K.build(root, rows)
    w1 = [r for r in csv_rows if r["wave"] == 1]
    w1_etsy = [r for r in w1 if r["sitting"] == "Etsy"]
    by_name = {r["product"]: r for r in csv_rows}
    out = ["# Products: start here\n",
           "Read this before listing anything. It covers what to put up first, every price and link still blank, and "
           "what each platform charges. Built by `launch/catalog/start_here.py` from `PRODUCTS_CATALOG.md` and the launch "
           "kit; nothing has been listed, uploaded or paid for.\n",
           "## 1. Decide how much of wave 1 goes up (your call)\n",
           "Gumroad costs nothing until something sells. Etsy charges **$0.20 per listing** up front. Under the "
           "spend-nothing rule, you decide whether wave 1 starts small. **Recommendation: start with these 5**, then add "
           "the rest of wave 1 as the first ones sell or the weeks come round.\n",
           "| # | Product | Where | Why first | Cost to list | Kit # |", "|---|---|---|---|---|---|"]
    for i, (name, plat, why, cost) in enumerate(TOP5, 1):
        r = next((x for x in csv_rows if x["product"] == name and x["sitting"] == plat), by_name.get(name, {}))
        out.append(f"| {i} | {name} | {plat} | {why} | {cost} | {r.get('n', '?')} |")
    n_et = len(w1_etsy)
    out += ["",
            f"The top 5 cost **$0.40** on Etsy (two listings). All of wave 1 on Etsy is {n_et} listings, about "
            f"**${n_et * ETSY_LISTING_FEE:.2f}** in listing fees. A new Etsy shop may also ask for a one-time setup fee "
            "(it has been $15 in the US); check at sign-up before deciding.\n",
            "## 2. Wave 1 upload steps\n",
            "Wave 1 is Money Made Simple and Scam Decoded (scouting's two-brand plan, PR #2). 1099 Money is wave 2 "
            "(after the brand-3 check, about Jan 10 2027) and Dinero Simple wave 3 (after a paid Spanish review).\n",
            "1. **Before anything (10 minutes):** set the prices (section 3) and fill the link blanks (section 4) that your first listings need, and decide "
            "the top 5 question above.",
            "2. **Week 0 (Nov 9), Gumroad, Money Made Simple:** open `storefront/launch-kit/WAVE1_LISTINGS.md` and go "
            "down the \"Week 0\" table. Each row's \"Kit #\" is the entry in `SITTING_1_GUMROAD.md` with the images, the "
            "files and the copy to paste. Cross-sell targets come first, so every receipt link points at a live page.",
            "3. **Set up the profile and emails** from `storefront/money-made-simple/STOREFRONT.md` and `storefront/emails/`.",
            "4. **Week 2 (Nov 23), Gumroad, Scam Decoded:** the \"Week 2\" table, from its own Gumroad account.",
            "5. **Week 4 (Dec 7), Etsy, Money Made Simple shop:** `etsy/SHOP_SETUP.md`, then the \"Week 4\" table in "
            "order (the 2027 planner first, singles, then bundles). Create the saved replies in "
            "`storefront/NEXT_STEP_ALL_PRODUCTS.md`.",
            "6. **Tick each listing off** in `storefront/launch-kit/launch_kit.csv` (the `done` column).",
            "7. **Dated items** in the \"Wave 1, but not yet\" table of `WAVE1_LISTINGS.md` go up on their own dates "
            "(the January Reset on Dec 30, the Valentine's pack by Feb 1, the moving products by Mar 1).\n",
            "Before you list on Etsy, `ETSY_COMPLIANCE.md` (next to this file) shows the final check of every Etsy "
            "listing and its files.\n",
            "## 3. Prices not set yet\n",
            "| Brand | Product | Platform | Where it stands | Where the price lives |", "|---|---|---|---|---|"]
    seen = set()
    for r in rows:
        if "[PRICE]" in r["price"] and (r["brand"], r["product"]) not in seen:
            seen.add((r["brand"], r["product"]))
            out.append(f"| {r['brand']} | {r['product']} | {r['platform']} | {r['price']} | `{r['listing']}` and "
                       f"`launch/catalog/build_catalog.py` (OTHER_BRANCHES) |")
    out += ["", "Set each price in its listing first, then in `build_catalog.py`, and rebuild the catalog and the launch kit.\n",
            "## 4. Link blanks\n",
            "Every placeholder still in the launch files, grouped by kind. Fill a group when the thing it points to is "
            "live; the builds keep the placeholders visible so nothing ships with a broken link.\n",
            "| Blank | How to fill it | Count | Where (top files) |", "|---|---|---|---|"]
    found = scan(LAUNCH)
    for _pat, what, how in BLANKS:
        files = found.get(what, {})
        if not files:
            continue
        top = sorted(files.items(), key=lambda kv: -kv[1])[:3]
        where = "; ".join(f"`{f}` ({n})" for f, n in top) + (f"; and {len(files) - 3} more" if len(files) > 3 else "")
        out.append(f"| {what} | {how} | {sum(files.values())} | {where} |")
    links = json.loads((LAUNCH / "templates" / "links.json").read_text())
    todo = sorted(k for k, v in links.items() if str(v).startswith("TODO"))
    out += ["", f"`launch/templates/links.json` has **{len(todo)} links to fill**: " + ", ".join(f"`{k}`" for k in todo) + ".",
            "The free apps (PR #8) hold upsell slots with `REPLACE_ME` Gumroad URLs in `apps/budget/config.js` "
            "(for example `sinking-funds-sheet`); use the same slugs when you create the Gumroad products, or tell the "
            "apps thread the real ones.\n",
            "## 5. What each platform charges\n",
            "| | Etsy | Gumroad |", "|---|---|---|",
            "| To list | $0.20 per listing, renewed every 4 months or after each sale | Free |",
            "| Per sale | 6.5% transaction fee, plus payment processing (US: 3% + $0.25) | 10% + $0.50 on direct sales, "
            "plus card processing; 30% on sales through Gumroad Discover |",
            "| Setup | A one-time fee for new shops in some countries ($15 in the US so far) | None |",
            "| Example: a $12 item | about $0.78 + $0.61 + $0.20 listing = **$1.59**, you keep about $10.41 | about "
            "$1.70 + processing, you keep about $10 |",
            "",
            "These are the published fees as of Nov 2026 (Etsy's fee schedule and Gumroad's pricing page, plus "
            "[Checkout Page on Etsy fees](https://checkoutpage.com/blog/etsy-fees) and "
            "[on Gumroad fees](https://checkoutpage.com/blog/gumroad-fees)). Check both pages on the day you sign up; "
            "they change. `launch/etsy/listings.py` `fees()` has the Etsy maths for every listing.\n"]
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    root = Path(a.root)
    md = build(root)
    out = Path(a.out) if a.out else root / "PRODUCTS_START_HERE.md"
    out.write_text(md)
    (LAUNCH / "PRODUCTS_START_HERE.md").write_text(md)
    print(f"-> {out} and launch/PRODUCTS_START_HERE.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
