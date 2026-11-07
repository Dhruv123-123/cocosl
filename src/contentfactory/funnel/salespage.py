"""Product sales pages.

`build_sales_page(settings, brand, product)` writes a self-contained,
mobile-first HTML page to output/<slug>/site/<product-slug>.html; the same
page is served live at /p/<brand>/<product-slug> (routes.public_router).

`product` is a brand product dict ({name, url, price}, from the brand YAML or
the business products table). Long-form copy comes from the matching entry
under `products:` in brands/sequences/<brand>.yaml:

    products:
      - slug: 20-minute-budget
        match: "20-Minute Budget"          # substring of the product name or url
        name, headline, subhead, problem: [..], how: [{title, text}],
        inside: [..], previews: [image paths or URLs], for_who: [..],
        not_for: [..], faq: [{q, a}], price, launch_price, launch_code,
        launch_ends, refund, includes, disclaimer, ai_disclosure, button

The page shows only what you give it: no countdown timers, no stock counters,
no testimonials, and a launch price only while launch_ends hasn't passed.
"""
from __future__ import annotations

import base64
import io
import os
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode, urlsplit

from PIL import Image

from ..config import BrandProfile, Settings
from ..db import now_iso
from . import attribution
from .brandfunnel import launch_state, load_funnel
from .linkpage import _price, public_env, slugify, theme
from .mailer import public_url

DEFAULT_AI = "Product written and designed with help from AI tools, then checked and edited by a human."
DEFAULT_REFUND = ("Not what you expected? Email {support} within 14 days of purchase and you'll get a full "
                  "refund. No forms.")


def support_email() -> str:
    from email.utils import parseaddr
    raw = os.environ.get("SUPPORT_EMAIL", "") or os.environ.get("SMTP_FROM", "")
    return parseaddr(raw)[1] if raw else ""


def _overrides(settings: Settings | None, brand: BrandProfile, product: dict) -> dict:
    name = str(product.get("name", "")).lower()
    url = str(product.get("url", "")).lower()
    slug = str(product.get("slug", "")) or slugify(product.get("name", ""))
    for entry in load_funnel(settings, brand.slug).get("products") or []:
        if not isinstance(entry, dict):
            continue
        match = str(entry.get("match", "")).lower()
        if entry.get("slug") and entry["slug"] in (slug, product.get("slug")):
            return entry
        if match and (match in name or match in url):
            return entry
    return {}


def product_slug(settings: Settings | None, brand: BrandProfile, product: dict) -> str:
    o = _overrides(settings, brand, product)
    return slugify(str(o.get("slug") or product.get("slug") or product.get("name", "product")))


def find_product(settings: Settings, db, brand: BrandProfile, slug: str) -> dict | None:
    """The brand product (YAML or listed in the products table) with this page slug."""
    from .linkpage import products
    for p in products(db, brand, settings=settings):
        if p["slug"] == slug:
            return p["raw"]
    return None


def _image_src(settings: Settings, ref: str, max_w: int = 1200) -> str:
    """Data URI for a local image (resized), or the URL itself for http(s)."""
    if ref.startswith(("https://", "data:")):
        return ref
    path = Path(ref)
    if not path.is_absolute():
        for root in (settings.home, settings.output_dir, settings.brands_dir):
            if (Path(root) / ref).exists():
                path = Path(root) / ref
                break
    if not path.exists():
        return ""
    with Image.open(path) as img:
        img = img.convert("RGB")
        if img.width > max_w:
            img = img.resize((max_w, round(img.height * max_w / img.width)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def buy_url(product_url: str, launch: dict, utm: dict) -> str:
    """Checkout link: launch code applied while active (Gumroad /l/<id>/<code>,
    Stripe prefilled_promo_code) and UTM / client_reference_id for attribution."""
    url = product_url
    if launch["active"] and launch["code"]:
        if attribution.is_gumroad_link(url):
            parts = urlsplit(url)
            segs = [s for s in parts.path.split("/") if s]
            if len(segs) == 2 and segs[0] == "l":  # /l/<permalink> -> /l/<permalink>/<offer code>
                url = parts._replace(path=f"/l/{segs[1]}/{quote(launch['code'])}").geturl()
        elif attribution.is_stripe_link(url):
            url += ("&" if urlsplit(url).query else "?") + urlencode({"prefilled_promo_code": launch["code"]})
    return attribution.tag_link(url, utm.get("utm_source", ""), utm.get("utm_medium", ""),
                                utm.get("utm_campaign", ""), utm.get("utm_content", ""))


def _list(v) -> list:
    if not v:
        return []
    return v if isinstance(v, list) else [v]


def sales_page_context(settings: Settings, brand: BrandProfile, product: dict, *, base_url: str | None = None,
                       utm: dict | None = None, now: datetime | None = None) -> dict:
    o = _overrides(settings, brand, product)
    base = (base_url or public_url(settings)).rstrip("/")
    slug = product_slug(settings, brand, product)
    name = str(o.get("name") or product.get("name") or "Product")
    price = str(o.get("price") or _price(product.get("price")) or "")
    launch = launch_state({**o, "price": price}, now)
    utm = {"utm_source": "salespage", "utm_medium": "web", "utm_campaign": slug, **(utm or {})}
    support = support_email()
    refund = str(o.get("refund") or DEFAULT_REFUND)
    refund = refund.replace("{support}", support or "the address on your receipt")
    inside = [i if isinstance(i, dict) else {"title": str(i), "text": ""} for i in _list(o.get("inside"))]
    how = [i if isinstance(i, dict) else {"title": str(i), "text": ""} for i in _list(o.get("how"))]
    faq = [f for f in _list(o.get("faq")) if isinstance(f, dict) and f.get("q")]
    previews = [{"src": s, "alt": f"Preview {i + 1} of {name}"}
                for i, s in enumerate(_image_src(settings, str(p)) for p in _list(o.get("previews"))) if s]
    shown_price = launch["launch_price"] if launch["active"] else price
    button = str(o.get("button") or (f"Get it for {shown_price}" if shown_price and shown_price != "Free"
                                     else "Get it now"))
    return {
        "brand": brand, "t": theme(brand), "slug": slug, "name": name,
        "headline": str(o.get("headline") or name), "subhead": str(o.get("subhead") or product.get("description")
                                                                   or brand.promise or ""),
        "problem_title": str(o.get("problem_title") or "The problem"), "problem": _list(o.get("problem")),
        "how_title": str(o.get("how_title") or "How it works"), "how": how,
        "inside": inside, "includes": str(o.get("includes") or ""), "previews": previews,
        "for_who": _list(o.get("for_who")), "not_for": _list(o.get("not_for")), "faq": faq,
        "price": price, "launch": launch, "shown_price": shown_price, "button": button,
        "buy_url": buy_url(str(product.get("url", "")), launch, utm), "refund": refund,
        "disclaimer": str(o.get("disclaimer") or ""), "ai_disclosure": str(o.get("ai_disclosure") or DEFAULT_AI),
        "link_page": f"{base}/l/{brand.slug}", "year": now_iso()[:4], "support": support,
        "page_url": f"{base}/p/{brand.slug}/{slug}",
    }


def render_sales_page(settings: Settings, brand: BrandProfile, product: dict, **kw) -> str:
    return public_env().get_template("sales_page.html").render(**sales_page_context(settings, brand, product, **kw))


def build_sales_page(settings: Settings, brand: BrandProfile, product: dict, *, base_url: str | None = None) -> Path:
    """Write output/<slug>/site/<product-slug>.html and return its path."""
    html = render_sales_page(settings, brand, product, base_url=base_url)
    out = settings.output_dir / brand.slug / "site" / f"{product_slug(settings, brand, product)}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    return out


def build_all_sales_pages(settings: Settings, db, brand: BrandProfile, *, base_url: str | None = None) -> list[Path]:
    """One page per product that has a checkout URL."""
    from .linkpage import products
    return [build_sales_page(settings, brand, p["raw"], base_url=base_url)
            for p in products(db, brand, settings=settings)]


__all__ = ["build_sales_page", "build_all_sales_pages", "render_sales_page", "sales_page_context", "product_slug",
           "find_product", "buy_url"]
