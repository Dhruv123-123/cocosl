"""Dinero Simple lean launch: the smallest set that can go live after about 10-15 hours of native-speaker review and
about 3 hours with the attorney. Everything else is phase 2 and stays off until it has been reviewed.

    python3 launch/dinero-simple/lean/lean_launch.py

writes
  launch/dinero-simple/content-lean.json          the 16 lean posts (render them with `factory handoff-pack`)
  launch/dinero-simple/POSTING_PLAN_LEAN.md       the 4-week lean calendar (the only plan that is phase 1)
  launch/dinero-simple/lean/LEAN_LAUNCH.md        what is in, what is phase 2, and the go-live order
and stamps a PHASE 2 banner under the title of every other POSTING_PLAN*.md, and tags every content*.json item with
"phase" (1 or 2) and, when it is flagged ATTORNEY REVIEW, "review": "legal_review" for the factory's review gate. A month builder rewrites its plan
without the banner, so run this again after any month builder (tests/test_dinero_products.py checks it).

The lean set (this file is the single source: the site hold, the review packets and the tests all read it):
  site core   home, /free/, /links/, the blog index ("Muy pronto"), about, disclosures, privacy, terms
  freebie     "Tu dinero en orden en 7 días" (sites/dinero-simple/lead-magnet/, the 10-page PDF)
  emails      the 5-email welcome series in brands/sequences/dinero-simple.yaml (days 0, 1, 3, 5, 7)
  products    El Kit para Recortar Gastos ($5, the day-7 offer, site + Gumroad) and the Registro de Cuentas y
              Pagos bill tracker (imprimibles/, Etsy-safe, Etsy + Gumroad). Tu Fecha Sin Deudas ($17) would add
              about 3,100 words (2+ review hours), so it opens phase 2.
  posts       4 weeks from the evergreen launch set (content.json): 3 Shorts a week + a carousel every
              other Saturday, no long videos. Evergreen on purpose: nothing expires if review runs late.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
DS = HERE.parent
ROOT = DS.parents[1]
SITE = ROOT / "sites" / "dinero-simple"

# Site pages (sites/dinero-simple/content/pages/*.md) that go live. Every other page is held.
SITE_PAGES = ["about", "disclosures", "privacy", "terms"]
# Site product slug -> launch/dinero-simple/products/dist/<slug>/ (the paid PDF behind it).
PRODUCTS = {"el-kit-para-recortar-gastos": "recorte-de-gastos"}
# Printables (launch/dinero-simple/imprimibles/dist/<slug>/): sold on Etsy and Gumroad, not on the site.
PRINTABLES = ["registro-de-cuentas"]
FREEBIE = SITE / "lead-magnet" / "tu-dinero-en-orden-en-7-dias.html"
SEQUENCE = ROOT / "brands" / "sequences" / "dinero-simple.yaml"
SITE_EMAILS: list[str] = []          # the site's own 10-email sequence is phase 2; the YAML series is the welcome

# The lean calendar: (week, weekday, time, content.json position, 1-based). Shorts Mon/Wed/Fri 12:30,
# carousels Sat 20:00 in weeks 1 and 3. Weeks are relative so the start day can move with the review.
WEEKDAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
CALENDAR = [
    (1, "lun", "12:30", 1),    # El truco de las dos cuentas que evita sobregiros
    (1, "mié", "12:30", 14),   # Encuentra tus suscripciones olvidadas en 10 minutos (ties to the Kit)
    (1, "vie", "12:30", 10),   # Activa estas 3 alertas del banco hoy (freebie day 3)
    (1, "sáb", "20:00", 15),   # carousel: Tu cita mensual de 20 minutos con tu dinero
    (2, "lun", "12:30", 2),    # Haz tu presupuesto por semana, no por mes (freebie day 7)
    (2, "mié", "12:30", 7),    # Congela tu crédito gratis esta noche (freebie day 5)
    (2, "vie", "12:30", 11),   # Esa cuenta 'sorpresa' estaba en el calendario
    (3, "lun", "12:30", 8),    # $60 contra $150 en una tarjeta de $3,000
    (3, "mié", "12:30", 6),    # ¿Pagaste completo y tu puntaje bajó?
    (3, "vie", "12:30", 9),    # ¿Tu app de ahorro de verdad está asegurada?
    (3, "sáb", "20:00", 20),   # carousel: Avalancha contra bola de nieve, con números reales
    (4, "lun", "12:30", 13),   # No canceles esa tarjeta vieja todavía
    (4, "mié", "12:30", 4),    # El aumento que estás ignorando: el match de tu 401(k)
    (4, "vie", "12:30", 5),    # La comisión que se come $18,000
]
WHERE = {"short": "TikTok + YouTube Shorts + Instagram Reels", "carousel": "Instagram + TikTok (carousel)"}
EXAMPLE_START = "lunes 30 de noviembre de 2026"

PHASE2_MARK = "**PHASE 2: DO NOT POST.**"
PHASE2_BANNER = (f"> {PHASE2_MARK} Nothing in this plan is part of the lean launch (`POSTING_PLAN_LEAN.md`). "
                 "It stays unposted until each piece passes native-speaker review (and attorney review where it is "
                 "flagged) and Dhruv moves it into a live calendar.")


def launch_items() -> list[dict]:
    return json.loads((DS / "content.json").read_text())


def lean_items() -> list[dict]:
    items = launch_items()
    return [items[pos - 1] for _, _, _, pos in CALENDAR]


def lean_titles() -> set[str]:
    return {it["script"]["title"] for it in lean_items()}


def site_hold() -> dict:
    """The site.json "hold" block that keeps everything outside the lean set off the site."""
    pages = sorted(p.stem for p in (SITE / "content" / "pages").glob("*.md") if p.stem not in SITE_PAGES)
    products = sorted(p.stem for p in (SITE / "content" / "products").glob("*.md") if p.stem not in PRODUCTS)
    return {"enabled": True,
            "_note": "Lean launch (launch/dinero-simple/lean/LEAN_LAUNCH.md): only the core pages, the freebie "
                     "and El Kit para Recortar Gastos are live. Remove a name here once that "
                     "piece has passed native review (and attorney review where flagged). Rebuild with "
                     "lean_launch.py, which rewrites this block.",
            "blog": ["*"], "products": products, "emails": ["*"] if not SITE_EMAILS else SITE_EMAILS,
            "pages": pages}


def plan_md() -> str:
    items = launch_items()
    rows = []
    for n, (week, day, time, pos) in enumerate(CALENDAR, 1):
        it = items[pos - 1]
        sub = "carousels" if it["format"] == "carousel" else "videos"
        rows.append(f"| Semana {week} · {day} | {time} | {WHERE[it['format']]} | {sub}/{n:02d}-… | {it['format']} | "
                    f"{it['script']['title']} |")
    n_short = sum(1 for *_, p in CALENDAR if items[p - 1]["format"] == "short")
    return f"""# Dinero Simple: lean launch posting plan (4 weeks, phase 1)

The only posting plan that is phase 1. {n_short} Shorts and {len(CALENDAR) - n_short} carousels from the evergreen launch set, chosen to back up the freebie ("Tu dinero en orden en 7 días") and the two live products (El Kit para Recortar Gastos and the Registro de Cuentas y Pagos printable). No long videos and nothing seasonal, so nothing expires if the review runs late. Every other `POSTING_PLAN_*.md` is **phase 2** and carries a DO NOT POST banner.

Weeks are relative: week 1 starts the Monday after the lean native review is back (for example {EXAMPLE_START}). Times America/New_York.

Rules: post a piece only after the native reviewer has signed it off in `review/dist/Lean-Revision-Espanol-Nativo.pdf` and the facts under CHECK BEFORE POSTING in its caption.txt are confirmed. Record the review in the factory with `factory review-gate pass <id> native_review --by NAME`.

Source: `launch/dinero-simple/content-lean.json` (built by `lean/lean_launch.py`). Folder numbers match the rendered pack in project files `content-factory/dinero-simple/lean-launch/`.

| Day | Time | Platform(s) | Folder | Format | Pieza |
|---|---|---|---|---|---|
""" + "\n".join(rows) + "\n"


def stamp_phase2() -> list[str]:
    stamped = []
    for f in sorted(DS.glob("POSTING_PLAN*.md")):
        if f.name == "POSTING_PLAN_LEAN.md":
            continue
        text = f.read_text()
        if PHASE2_MARK in text:
            continue
        head, _, rest = text.partition("\n")
        f.write_text(f"{head}\n\n{PHASE2_BANNER}\n{rest}")
        stamped.append(f.name)
    return stamped


def lean_md(est: dict | None = None) -> str:
    items = launch_items()
    held = site_hold()
    post_rows = "\n".join(f"| Semana {w} · {d} {t} | {items[p - 1]['format']} | {items[p - 1]['script']['title']} |"
                          for w, d, t, p in CALENDAR)
    est_line = ""
    if est:
        n, a = est["native"], est["attorney"]
        est_line = (f"\n**Review size:** native {n['words']:,} words, {n['hours'][0]}–{n['hours'][1]} hours; attorney "
                    f"{a['entries']} pieces, {a['words']:,} words, {a['hours'][0]}–{a['hours'][1]} hours. The packets are "
                    "`review/dist/Lean-Revision-Espanol-Nativo.pdf` and `review/dist/Lean-Attorney-Review-Packet.pdf` "
                    "(project files `content-factory/dinero-simple/review-packets/`).\n")
    plans = "\n".join(f"- `{f.name}`" for f in sorted(DS.glob("POSTING_PLAN*.md")) if f.name != "POSTING_PLAN_LEAN.md")
    return f"""# Dinero Simple lean launch

The smallest set that can go live: core site, one freebie, the welcome emails, 4 weeks of posts and 2 products.
Everything else is phase 2: written, kept, and switched off until it has been reviewed. The set is defined in
`lean/lean_launch.py`; the site hold, the review packets and the tests all read it from there.
{est_line}
## Phase 1 (lean launch)

| Piece | Where |
|---|---|
| Site core: home, `/free/`, `/links/`, blog index ("Muy pronto"), {", ".join(f"`/{p}/`" for p in SITE_PAGES)} | `sites/dinero-simple/` with `site.json` hold on |
| Freebie: Tu dinero en orden en 7 días (10-page PDF) | `sites/dinero-simple/lead-magnet/` → `/downloads/` |
| Welcome emails: days 0, 1, 3, 5, 7 + the Kit sales page | `brands/sequences/dinero-simple.yaml` (load into Sender) |
| Products: El Kit para Recortar Gastos ($5) and the Registro de Cuentas y Pagos printable ([PRICE], $5–7 suggested) | site product page + `products/dist/recorte-de-gastos/`; `imprimibles/dist/registro-de-cuentas/` (Etsy-safe: labels only) |
| Posts: {len(CALENDAR)} pieces over 4 weeks | `POSTING_PLAN_LEAN.md`, `content-lean.json` |

### The 4 weeks

| When | Format | Pieza |
|---|---|---|
{post_rows}

## Phase 2 (held)

- **Site:** every article (`blog: *`), the site's own 10-email sequence (`emails: *`), the products
  {", ".join(f"`{p}`" for p in held["products"])}, and the pages {", ".join(f"`/{p}/`" for p in held["pages"])}.
  Links to held pages drop to plain text, so nothing on the live site points at a missing page.
- **Posting plans:** every plan below carries a PHASE 2: DO NOT POST banner.
{plans}
- **Everything else in `launch/dinero-simple/`:** the free guides (taxes, credit, seniors), the workbook, the Etsy
  printables, the newsletter, WhatsApp kit, answer bank and workshops.

To move something into phase 1: get it reviewed with the full packets (`review/REVIEW_PACKETS.md`, ordered by go-live
date), then take its name out of the `site.json` hold, or add it to a live calendar and remove the banner.

## Go-live order

1. Send `Lean-Revision-Espanol-Nativo.pdf` to the native reviewer and `Lean-Attorney-Review-Packet.pdf` to the
   attorney. Make their fixes in the source files and rebuild.
2. Turn on the site with the hold as it is (`site.json` "hold" is already enabled).
3. Load the 5 welcome emails into Sender with the template language set to Spanish.
4. Publish the Kit on Gumroad and set its URL; list the Registro de Cuentas y Pagos on Etsy and Gumroad
   (set its price first).
5. Render the lean pack and post from `POSTING_PLAN_LEAN.md`, starting the Monday after the review is back.
"""


def is_attorney_flagged(item: dict) -> bool:
    return any(c.startswith(("ATTORNEY REVIEW", "HIGH RISK, ATTORNEY")) for c in item["script"].get("claims_to_verify") or [])


def tag_content() -> int:
    """Stamp every pack item with its phase (1 = lean launch, 2 = held) and the review gate it needs on import:
    the brand already requires native_review (brands/dinero-simple.yaml review_stages); items flagged ATTORNEY REVIEW
    add "review": "legal_review", so `factory import` puts them in the legal queue too."""
    lean = lean_titles()
    n = 0
    for f in sorted(DS.glob("content*.json")):
        items = json.loads(f.read_text())
        for it in items:
            it["phase"] = 1 if (f.name in ("content.json", "content-lean.json") and it["script"]["title"] in lean) else 2
            if is_attorney_flagged(it):
                it["review"] = "legal_review"
                n += 1
            else:
                it.pop("review", None)
        f.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n")
    return n


def write_site_hold() -> None:
    """Rewrite only the "hold" block (the last key of site.json), keeping the file's hand formatting."""
    p = SITE / "site.json"
    text = p.read_text()
    start = text.index('\n  "hold": {')
    block = ",\n".join(f"    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}" for k, v in site_hold().items())
    p.write_text(text[:start] + '\n  "hold": {\n' + block + "\n  }\n}\n")
    json.loads(p.read_text())


def main(est: dict | None = None) -> None:
    (DS / "content-lean.json").write_text(json.dumps(lean_items(), ensure_ascii=False, indent=1) + "\n")
    (DS / "POSTING_PLAN_LEAN.md").write_text(plan_md())
    write_site_hold()
    stamped = stamp_phase2()
    legal = tag_content()
    (HERE / "LEAN_LAUNCH.md").write_text(lean_md(est))
    print(f"lean: {len(CALENDAR)} posts; stamped phase 2 on {len(stamped)} plans; {legal} items need legal_review")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(DS / "review"))
    import build_packets
    b = build_packets.build_lean()
    main({"native": b["native"], "attorney": b["attorney"]})
