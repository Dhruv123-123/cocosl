"""Digital products: outline with the LLM, render a multi-page guide to HTML/PDF.

Files go to output_dir/products/<brand>/<slug>/ and a row is stored in the
products table (status 'ready'; flip to 'listed' once it's on your store).
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from ..config import BrandProfile
from ..db import DB
from ..schemas import ProductOutline, Segment
from ._util import pick, read_csv_rows, slugify, to_cents
from .invoices import template_env
from .pdf import html_to_pdf

PRODUCT_KINDS = ["guide", "template", "checklist", "prompt_pack", "preset"]

KIND_SPECS = {
    "guide": "A practical guide: 6-9 sections, each 150-300 words of concrete, actionable teaching with examples.",
    "checklist": "A checklist: 5-8 sections, each a short intro plus 5-10 checkbox items, one per line starting '- '.",
    "template": "A fill-in template pack: 5-8 sections, each explains when to use the template, then the "
                "template itself with [placeholders], lines starting '- ' for fields.",
    "prompt_pack": "A prompt pack: 5-8 themed sections, each with 4-8 ready-to-copy prompts, one per line "
                   "starting '- ', plus a sentence on how to adapt them.",
    "preset": "A settings/preset guide: 5-8 sections describing each preset, when to use it and its values.",
}

SYSTEM = (
    "You design small, genuinely useful digital products for a niche audience. Rules: original writing; no "
    "fabricated statistics or fake testimonials; no promises of income, health or guaranteed results; "
    "practical over fluffy. Each section: heading = section title, on_screen_text = one-line key takeaway, "
    "narration = the section body (paragraphs separated by blank lines; list items as lines starting '- '), "
    "visual_prompt = an optional illustration idea (no text, no real people)."
)


def outline_product(llm, brand: BrandProfile, idea: str, kind: str = "guide") -> ProductOutline:
    """Draft a product outline + full section text for `idea`."""
    if kind not in KIND_SPECS:
        raise ValueError(f"Unknown product kind '{kind}'. Options: {', '.join(KIND_SPECS)}")
    prompt = f"""Brand: {brand.name} ({brand.niche})
Audience: {brand.audience}
Voice: {brand.voice.tone}
Avoid: {', '.join(brand.avoid_topics + brand.voice.banned_phrases) or 'n/a'}

Product idea: {idea}
Format: {KIND_SPECS[kind]}
Suggest a fair price (most small digital products sell for $5-$39). sales_blurb: 2-3 honest sentences."""
    return llm.structured(ProductOutline, system=SYSTEM, prompt=prompt, purpose=f"product:{kind}",
                          offline=lambda: _offline_outline(brand, idea, kind))


def _offline_outline(brand: BrandProfile, idea: str, kind: str) -> ProductOutline:
    topic = idea.strip().rstrip(".")
    steps = ["Start here", "The core idea", "Set it up", "Your first week", "Common mistakes",
             "Make it stick", "Next steps"]
    sections = []
    for i, step in enumerate(steps, start=1):
        body = (f"This section covers {step.lower()} for {topic.lower()}, written for {brand.audience}.\n\n"
                f"Work through it in order and keep notes as you go.\n\n"
                f"- Action {i}.1: write down where you are today\n- Action {i}.2: pick one change to try\n"
                f"- Action {i}.3: review it after seven days")
        sections.append(Segment(heading=f"{i}. {step}", narration=body,
                                on_screen_text=f"{step}: one small, specific action beats a big plan.",
                                visual_prompt=f"{brand.visual.image_style}; {step.lower()}"))
    return ProductOutline(
        title=topic[:1].upper() + topic[1:], subtitle=f"A {kind.replace('_', ' ')} from {brand.name}",
        audience=brand.audience, sections=sections, price_suggestion_usd=12.0,
        sales_blurb=f"A short, practical {kind.replace('_', ' ')} on {topic.lower()} for {brand.audience}.",
    )


def _paragraphs(text: str) -> list[dict]:
    """Split section text into paragraph and list blocks for the template."""
    blocks: list[dict] = []
    for chunk in re.split(r"\n\s*\n", text.strip()):
        lines = [ln.strip() for ln in chunk.splitlines() if ln.strip()]
        if lines and all(re.match(r"^([-*•]|\[ \]|\d+[.)])\s+", ln) for ln in lines):
            items = [re.sub(r"^([-*•]|\[ \]|\d+[.)])\s+", "", ln) for ln in lines]
            blocks.append({"type": "list", "items": items})
        elif lines:
            blocks.append({"type": "p", "text": " ".join(lines)})
    return blocks


def _contrast(hex_color: str) -> str:
    """Black or white text for a background colour."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        return "#ffffff"
    return "#111111" if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "#ffffff"


def render_product_html(brand: BrandProfile, outline: ProductOutline, kind: str = "guide") -> str:
    pal = (brand.visual.palette + ["#0f172a", "#f8fafc", "#22d3ee", "#f59e0b"])[:4]
    colors = {"dark": pal[0], "light": pal[1], "accent": pal[2], "accent2": pal[3],
              "on_dark": _contrast(pal[0]), "on_accent": _contrast(pal[2])}
    sections = [{"heading": re.sub(r"^\s*\d+\s*[.):-]\s*", "", s.heading), "takeaway": s.on_screen_text, "blocks": _paragraphs(s.narration)}
                for s in outline.sections]
    return template_env().get_template("product_guide.html").render(
        brand=brand, outline=outline, sections=sections, colors=colors, kind=kind.replace("_", " "),
        font=html.escape(brand.visual.font or "Inter"))


def build_product(settings, brand: BrandProfile, outline: ProductOutline, *, db: DB | None = None,
                  kind: str = "guide", pdf: bool = True, price_cents: int | None = None) -> dict:
    """Render the product to HTML (+PDF if Chromium works) and store it in `products`.

    Returns {id, html, pdf, path, dir}; paths are relative to settings.output_dir."""
    out_root = Path(settings.output_dir)
    folder = out_root / "products" / brand.slug / slugify(outline.title, 50)
    folder.mkdir(parents=True, exist_ok=True)
    html_path = folder / "index.html"
    html_path.write_text(render_product_html(brand, outline, kind), encoding="utf-8")
    (folder / "outline.json").write_text(outline.model_dump_json(indent=2), encoding="utf-8")
    pdf_path = folder / f"{slugify(outline.title, 50)}.pdf"
    has_pdf = pdf and html_to_pdf(html_path, pdf_path)
    rel_html = str(html_path.relative_to(out_root))
    rel_pdf = str(pdf_path.relative_to(out_root)) if has_pdf else None
    own_db = db is None
    db = db or DB(settings.db_path)
    try:
        price = price_cents if price_cents is not None else to_cents(outline.price_suggestion_usd)
        pid = db.insert("products", {
            "brand": brand.slug, "name": outline.title, "kind": kind if kind in PRODUCT_KINDS else "guide",
            "price_cents": price, "status": "ready", "path": rel_pdf or rel_html,
            "meta": {"subtitle": outline.subtitle, "audience": outline.audience, "sales_blurb": outline.sales_blurb,
                     "html": rel_html, "pdf": rel_pdf, "sections": len(outline.sections)},
        })
        db.log("product.built", "product", pid, {"brand": brand.slug, "pdf": bool(rel_pdf)})
    finally:
        if own_db:
            db.conn.close()
    return {"id": pid, "html": rel_html, "pdf": rel_pdf, "path": rel_pdf or rel_html,
            "dir": str(folder.relative_to(out_root))}


def set_product_listing(db: DB, product_id: int, url: str, price_cents: int | None = None) -> None:
    """Record where the product is listed (Gumroad, Payhip, your site...)."""
    changes: dict = {"url": url, "status": "listed"}
    if price_cents is not None:
        changes["price_cents"] = price_cents
    db.update("products", product_id, changes)


def products(db: DB, brand: str | None = None) -> list[dict]:
    rows = db.query("SELECT * FROM products " + ("WHERE brand = ? " if brand else "") + "ORDER BY id DESC",
                    [brand] if brand else [])
    sales = {r["note"]: (r["n"], r["c"]) for r in db.query(
        "SELECT note, COUNT(*) AS n, SUM(amount_cents) AS c FROM revenue WHERE source = 'product' GROUP BY note")}
    for r in rows:
        n, c = sales.get(r["name"], (0, 0))
        r["sales"], r["revenue_cents"] = n, int(c or 0)
    return rows


def import_gumroad_sales(db: DB, source, brand: str = "", mapping: dict | None = None) -> dict:
    """Import a Gumroad sales CSV as 'product' revenue (deduped by purchase id).

    Rows whose item name matches a known product inherit that product's brand."""
    from .revenue import import_csv
    known = {p["name"].lower(): p["brand"] for p in db.query("SELECT name, brand FROM products")}
    result = import_csv(db, source, "gumroad", brand=brand, mapping=mapping)
    if known:
        for row in read_csv_rows(source, header_hints=["purchase", "item name", "sale"]):
            name = pick(row, ["Item Name", "Product Name", "Product"])
            if name and known.get(name.lower()):
                db.execute("UPDATE revenue SET brand = ? WHERE source = 'product' AND note = ? AND brand = ''",
                           [known[name.lower()], name[:200]])
    return result
