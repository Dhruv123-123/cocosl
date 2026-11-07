"""Shared pieces for the brand shops (Scam Decoded, 1099 Money): theme, page frame, listing copy and checks.

Each brand reuses the Etsy printables stylesheet (launch/etsy/printables.css) with its own colours and footer, the
same Playwright renderer and the same mockup generator, so every brand's files are built and checked the same way.
"""
from __future__ import annotations

import contextlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ETSY = ROOT / "launch" / "etsy"
sys.path.insert(0, str(ETSY))

import listings as etsy_listings  # noqa: E402

SIZES = {"Letter": ("8.5in", "11in", "Letter"), "A4": ("210mm", "297mm", "A4")}


class Brand:
    def __init__(self, name: str, handle: str, ink: str, cream: str, accent: str, accent_d: str, warm: str, tint: str,
                 muted: str = "#5b6470", line: str = "#c8c6bd"):
        self.name, self.handle = name, handle
        self.ink, self.cream, self.accent, self.accent_d, self.warm, self.tint = ink, cream, accent, accent_d, warm, tint
        self.muted, self.line = muted, line

    @property
    def foot(self) -> str:
        return f"&copy; {self.name} &middot; for personal use only, please don't resell or share the file"

    def css(self, w: str = "8.5in", h: str = "11in") -> str:
        base = (ETSY / "printables.css").read_text().replace("--w:8.5in; --h:11in;", f"--w:{w}; --h:{h};")
        return base + (f":root{{ --ink:{self.ink}; --cream:{self.cream}; --green:{self.accent}; --green-d:{self.accent_d};"
                       f" --gold:{self.warm}; --tint:{self.tint}; --muted:{self.muted}; --line:{self.line}; }}\n" + EXTRA_CSS)

    def page(self, title: str, meta: str = "", body: str = "", kicker: str = "") -> str:
        return (f'<div class="top"><div>{f"<div class=kick>{kicker}</div>" if kicker else ""}<h1>{title}</h1></div>'
                f'<div class="meta">{meta}</div></div><div class="fill">{body}</div><div class="foot"><span>{self.foot}</span>'
                f'<span>{self.handle}</span></div>')

    def html(self, pages: list[str], title: str, w: str, h: str, page_name: str, extra_css: str = "",
             cls: str = "page") -> str:
        body = "".join(f'<section class="{cls}">{p}</section>\n' for p in pages)
        return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><style>'
                f'@page{{size:{page_name};margin:0}}\n{self.css(w, h)}{extra_css}</style></head><body>{body}</body></html>')

    @contextlib.contextmanager
    def mockup_theme(self):
        """Point the shared mockup generator at this brand's colours while it renders."""
        import mockgen
        saved = (mockgen.INK, mockgen.CREAM, mockgen.GREEN, mockgen.GREEN_D, mockgen.GOLD)
        mockgen.INK, mockgen.CREAM, mockgen.GREEN, mockgen.GREEN_D, mockgen.GOLD = (
            self.ink, self.cream, self.accent, self.accent_d, self.warm)
        try:
            yield mockgen
        finally:
            mockgen.INK, mockgen.CREAM, mockgen.GREEN, mockgen.GREEN_D, mockgen.GOLD = saved


EXTRA_CSS = """
.big{ font-size:13pt; line-height:1.45; }
.flag{ border-left:5px solid var(--gold); background:var(--tint); padding:7px 11px; border-radius:0 8px 8px 0; margin:0 0 8px; }
.flag b{ display:block; font-size:10.5pt; }
.pill{ display:inline-block; background:var(--ink); color:var(--cream); border-radius:999px; padding:2px 10px; font-weight:800; font-size:8pt; }
.say{ border:1.5px solid var(--ink); border-radius:10px; padding:8px 12px; margin-bottom:8px; }
.say .q{ font-size:8pt; font-weight:800; text-transform:uppercase; letter-spacing:.08em; color:var(--muted); }
.say .a{ font-size:11.5pt; font-weight:700; margin-top:2px; }
.steps{ counter-reset:s; list-style:none; padding:0; margin:0; }
.steps li{ counter-increment:s; position:relative; padding:0 0 9px 34px; }
.steps li::before{ content:counter(s); position:absolute; left:0; top:-1px; width:23px; height:23px; border-radius:50%;
  background:var(--green); color:var(--ink); font-weight:900; font-size:10pt; display:flex; align-items:center; justify-content:center; }
.fineprint{ font-size:7.5pt; color:var(--muted); line-height:1.4; }
td.wrap{ height:auto; padding:5px 6px; vertical-align:top; font-size:8.6pt; line-height:1.3; }
"""

# ---------------------------------------------------------------- listings

BANNED = ("guarantee", "risk-free", "100% safe", "never get scammed", "you've been hacked", "tax-free money",
          "write off everything", "the irs won't know", "bestseller", "best seller", "i've used")


def etsy_description(hook: str, get: list[str], how: list[str], good: list[str], disclosure: str) -> str:
    g = "\n".join(f"- {x}" for x in get)
    h = "\n".join(f"{i}. {x}" for i, x in enumerate(how, start=1))
    gd = "\n".join(f"- {x}" for x in good)
    return f"{hook}\n\nWHAT YOU GET\n{g}\n\nHOW IT WORKS\n{h}\n\nGOOD TO KNOW\n{gd}\n- {disclosure}"


def validate(items: list[dict]) -> list[str]:
    bad = []
    for it in items:
        s = it["slug"]
        if len(it["title"]) > 140 or len(it["title"].split()) > 15:
            bad.append(f"{s}: title too long ({len(it['title'].split())} words)")
        if len(it["tags"]) != 13 or len(set(it["tags"])) != 13 or any(len(t) > 20 for t in it["tags"]):
            bad.append(f"{s}: tags must be 13 unique, 20 characters or less")
        if any(not re.fullmatch(r"[a-z0-9 ]+", t) for t in it["tags"]):
            bad.append(f"{s}: tags use only lowercase letters, numbers and spaces")
        for field in ("description", "gumroad"):
            text = it[field].lower()
            hit = [w for w in BANNED if w in text]
            if hit:
                bad.append(f"{s}: banned wording in {field}: {hit}")
        d = it["description"]
        if "DIGITAL DOWNLOAD" not in d or "How it's made" not in d or "not " not in d.lower():
            bad.append(f"{s}: description needs the download note, How it's made and the advice disclaimer")
        if re.search(r"https?://|www\.|gumroad", d, re.I):
            bad.append(f"{s}: Etsy description must not link off Etsy")
    return bad


def listing_md(it: dict, brand: Brand) -> str:
    f = etsy_listings.fees(it["price"])
    tags = "\n".join(f"{i}. {t}" for i, t in enumerate(it["tags"], start=1))
    attrs = "\n".join(f"- **{k}:** {v}" for k, v in it.get("attributes", {}).items())
    files = "\n".join(f"- `{x}`" for x in it.get("files", []))
    return f"""# {brand.name}: {it['name']}

Nothing here has been listed. Copy each field into Etsy (Shop Manager > Listings > Add a listing) and Gumroad. Upload
the mockups in order (01 is the thumbnail).

## Etsy title ({len(it['title'])}/140, {len(it['title'].split())} words)
{it['title']}

## Price
${it['price']:.2f} on Etsy and Gumroad. Etsy fees per sale about ${f['total']:.2f}, so you keep about **${f['net']:.2f}**.
Gumroad takes 10% + $0.50 per direct sale, plus card processing (check its pricing page).

## Listing details
- **Type:** Digital files. **Who made it:** I did. **What is it:** A finished product.
- **Category:** {it['category']}
- **Renewal:** Automatic. **Quantity:** 999

## Attributes
{attrs}

## Tags (13, each 20 characters or less)
{tags}

## Digital files to upload
{files}

## Etsy description
```
{it['description']}
```

## Gumroad page
```
{it['gumroad']}
```
"""
