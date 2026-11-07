#!/usr/bin/env python3
"""Render one month of issues for one client, with their name and logo, ready to email to them.

    cd launch/b2b
    # a client you've already set up (brand file from the onboarding intake):
    python3 deliver.py credit-union-alert --client credit-union-alert/clients/big-sky-cu.json --month 2027-02

    # quick start from just a name and logo (other details as KEY=VALUE tokens):
    python3 deliver.py credit-union-alert --month 2027-02 --name "Big Sky Credit Union" --short "Big Sky CU" \
        --logo ~/Downloads/bigsky-logo.png --color "#1D4E89" --set CU_PHONE="(406) 123-4567" \
        --set CU_WEBSITE=https://www.bigskycu.example --promise "..." --footer "..."

The quick start writes <product>/clients/<slug>.json from the product's sample brand, so the next month
is just `--client`. It refuses to build while any fictional sample detail (a 555-01xx number, example.com,
"Sample ...") is still in the brand, so a client never gets the demo's phone number.

Output: <product>/out/deliveries/<slug>-<month>.zip (every format for each issue that month) and the
unzipped folder next to it. Nothing is sent anywhere. Weekly products get every issue whose member send
date falls in that month; monthly products get the one issue.
"""
import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import build as engine

ROOT = Path(__file__).resolve().parent
FICTIONAL = re.compile(r"\(555\)|555[-) ]*01\d\d|example\.(com|org)|\bSample\b")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def quick_brand(pdir: Path, a: argparse.Namespace) -> Path:
    """Make clients/<slug>.json from the product's sample brand plus the name, logo and tokens given."""
    brand = json.loads((pdir / "brands/example.json").read_text())
    name, short = a.name, a.short or a.name
    slug = slugify(short if a.short else name)
    brand.update(slug=slug, name=name, tier=a.tier or brand.get("tier", ""),
                 initials="".join(w[0] for w in name.split() if w[0].isalnum())[:3].upper())
    brand["_about"] = f"Client brand for {name}, made by deliver.py. Edit freely; then use --client."
    keys = list(brand["tokens"])
    # the first two tokens of every product are its full name and short name
    if keys:
        brand["tokens"][keys[0]] = name
    if len(keys) > 1:
        brand["tokens"][keys[1]] = short
    for kv in a.set or []:
        k, _, v = kv.partition("=")
        brand["tokens"][k.strip()] = v
    if a.color:
        brand["color"] = a.color
    if a.accent:
        brand["accent"] = a.accent
    if a.promise is not None:
        brand["promise"] = a.promise
    if a.footer:
        brand["footer_lines"] = a.footer
    if a.unsubscribe:
        brand["unsubscribe"] = a.unsubscribe
    clients = pdir / "clients"
    clients.mkdir(exist_ok=True)
    if a.logo:
        if re.match(r"https?://", a.logo):
            brand["logo"] = a.logo
        else:
            src = Path(a.logo).expanduser().resolve()
            if not src.exists():
                sys.exit(f"logo not found: {src}")
            dest = clients / f"{slug}-logo{src.suffix.lower()}"
            shutil.copy(src, dest)
            brand["logo"] = str(dest.resolve())
    path = clients / f"{slug}.json"
    path.write_text(json.dumps(brand, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {path.relative_to(ROOT)} (clients/ is gitignored; edit it for next time)")
    return path


def check_brand(path: Path) -> dict:
    brand = json.loads(path.read_text())
    text = json.dumps({k: v for k, v in brand.items() if k not in ("_about", "logo")}, ensure_ascii=False)
    left = sorted(set(m.group(0) for m in FICTIONAL.finditer(text)))
    if left:
        sys.exit(f"{path.name} still has sample details {left}. Replace them (--set KEY=VALUE, --promise, "
                 f"--footer, or edit the file) before delivering.")
    logo = brand.get("logo", "")
    if logo and not re.match(r"https?://", logo):
        print("note: the logo is a local file. Images and PDFs use it, but email.html points at your disk. "
              "Before the client loads the email, swap in their hosted logo URL (or leave logo empty "
              "for the initials badge).", file=sys.stderr)
    return brand


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("product", help="product folder, e.g. credit-union-alert or community-scam-watch/es")
    ap.add_argument("--month", required=True, help="YYYY-MM of the member/employee send dates")
    ap.add_argument("--client", type=Path, help="an existing client brand JSON")
    ap.add_argument("--name", help="quick start: client's full name")
    ap.add_argument("--short", help="quick start: short name used in sentences")
    ap.add_argument("--logo", help="quick start: logo file (PNG/SVG) or https URL")
    ap.add_argument("--color", help="quick start: main brand color, e.g. #1D4E89")
    ap.add_argument("--accent", help="quick start: accent color")
    ap.add_argument("--tier", help="quick start: plan, e.g. essentials / standard / plus")
    ap.add_argument("--promise", help="quick start: the client's approved promise line")
    ap.add_argument("--footer", action="append", help="quick start: a footer line (repeat for more)")
    ap.add_argument("--unsubscribe", help="quick start: the email platform's unsubscribe merge tag")
    ap.add_argument("--set", action="append", metavar="KEY=VALUE", help="quick start: a brand token")
    a = ap.parse_args()

    pdir = ROOT / a.product
    if not (pdir / "product.json").exists():
        sys.exit(f"no product at {pdir}")
    if not re.fullmatch(r"\d{4}-\d{2}", a.month):
        sys.exit("--month must look like 2027-02")
    if a.client:
        brand_path = a.client if a.client.is_absolute() else (ROOT / a.client if (ROOT / a.client).exists() else a.client)
    elif a.name:
        brand_path = quick_brand(pdir, a)
    else:
        sys.exit("give --client <brand.json>, or --name (and --logo, --set ...) for a quick start")
    brand = check_brand(brand_path)

    prod = json.loads((pdir / "product.json").read_text())
    issues = [i for i in json.loads((pdir / "issues.json").read_text())["issues"]
              if i["send_date"].startswith(a.month)]
    if not issues:
        months = sorted({i["send_date"][:7] for i in json.loads((pdir / "issues.json").read_text())["issues"]})
        sys.exit(f"no issues for {a.month} in {a.product}. Written so far: {', '.join(months)}")
    if any(i.get("review") for i in issues):
        print("warning: these issues are still marked for native-language review; don't deliver them yet",
              file=sys.stderr)

    images = engine.have_renderer()
    pack = engine.build(pdir, prod, brand_path, issues, False, images)
    engine.finish([pack])

    out = pdir / "out"
    deliveries = out / "deliveries"
    deliveries.mkdir(exist_ok=True)
    name = f"{brand['slug']}-{a.month}"
    folder = deliveries / name
    if folder.exists():
        shutil.rmtree(folder)
    shutil.copytree(out / brand["slug"], folder)
    (out / f"{brand['slug']}.zip").unlink(missing_ok=True)
    zpath = deliveries / f"{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(deliveries))
    print(f"\n{len(issues)} issue(s) for {brand['name']}, {a.month}:")
    for i in issues:
        print(f"  {i['send_date']}  {i['topic']}  (deliver by {i['deliver_by']})")
    print(f"ready to email to the client: {zpath.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
