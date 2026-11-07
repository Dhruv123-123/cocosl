"""HTTP routes for the funnel.

* `public_router` (no auth): /l/{brand}, /p/{brand}/{product}, /subscribe/{brand},
  /confirm/{token}, /freebie/{token}, /unsubscribe/{token}, /webhooks/stripe,
  /webhooks/gumroad.
* `router` (dashboard auth, prefix /funnel): subscribers, CSV export, digest
  drafts + send, link page and brand kit rebuilds.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

import jinja2
from fastapi import APIRouter, BackgroundTasks, Depends, Form, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from ..pipeline import Factory
from . import analytics, attribution, linkpage, newsletter, payments, salespage, sequences, store

try:
    from ..web.deps import get_factory, templates as _web_templates
except ImportError:  # dashboard not installed: still serve the public routes
    _web_templates = None

    def get_factory(request: Request) -> Factory:  # type: ignore[misc]
        return request.app.state.factory

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"
SUBSCRIBE_LIMITER = store.RateLimiter(limit=int(os.environ.get("FUNNEL_RATE_LIMIT", "5") or 5), window=600)

public_router = APIRouter(tags=["funnel-public"])
router = APIRouter(prefix="/funnel", tags=["funnel"])


def _admin_templates() -> Jinja2Templates:
    """Dashboard templates (base.html, filters, nav) plus funnel/templates."""
    if _web_templates is None:
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)), autoescape=True)
        return Jinja2Templates(env=env)
    base_env = _web_templates.env
    env = base_env.overlay(loader=jinja2.ChoiceLoader([jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
                                                       base_env.loader]))
    return Jinja2Templates(env=env, context_processors=list(_web_templates.context_processors))


templates = _admin_templates()


def _base_url(request: Request) -> str:
    return os.environ.get("FUNNEL_PUBLIC_URL", "").strip().rstrip("/") or str(request.base_url).rstrip("/")


def _client_ip(request: Request) -> str:
    if os.environ.get("FUNNEL_TRUST_PROXY", "").lower() in ("1", "true", "yes"):
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _brand_or_404(factory: Factory, slug: str):
    brands = factory.brands()
    if slug not in brands:
        return None
    return brands[slug]


def _page(html: str, status: int = 200) -> HTMLResponse:
    return HTMLResponse(html, status_code=status, headers={"Cache-Control": "no-store",
                                                          "X-Robots-Tag": "noindex"})


def _wants_json(request: Request) -> bool:
    return "application/json" in request.headers.get("accept", "")


# ====================================================================== public
@public_router.get("/l/{brand}", response_class=HTMLResponse)
def link_page(brand: str, request: Request, factory: Factory = Depends(get_factory)):
    b = _brand_or_404(factory, brand)
    if not b:
        return _page(linkpage.render_message(None, "Page not found", "This link page doesn't exist.",
                                             status="error"), 404)
    html = linkpage.render_link_page(factory.settings, factory.db, b, _base_url(request))
    return HTMLResponse(html, headers={"Cache-Control": "public, max-age=300"})


@public_router.get("/p/{brand}/{product}", response_class=HTMLResponse)
def sales_page(brand: str, product: str, request: Request, factory: Factory = Depends(get_factory)):
    b = _brand_or_404(factory, brand)
    item = salespage.find_product(factory.settings, factory.db, b, product) if b else None
    if not b or not item:
        return _page(linkpage.render_message(b, "Page not found", "This product page doesn't exist.",
                                             status="error"), 404)
    utm = attribution.utm_from_query(dict(request.query_params))
    html = salespage.render_sales_page(factory.settings, b, item, base_url=_base_url(request), utm=utm)
    return HTMLResponse(html, headers={"Cache-Control": "no-store" if utm else "public, max-age=300"})


def _welcome_now(factory: Factory, subscriber_id: int, base_url: str) -> None:
    """Send the day-0 welcome email right after confirming (same gates as the worker)."""
    try:
        sequences.run_sequences(factory, confirm=True, subscriber_id=subscriber_id, base_url=base_url)
    except Exception:  # never break the confirm page; the hourly worker retries
        import logging
        logging.getLogger("factory.funnel").exception("welcome email failed")


@public_router.post("/subscribe/{brand}")
def subscribe(brand: str, request: Request, background: BackgroundTasks,
              email: str = Form(""), website: str = Form(""), source: str = Form("link-page"),
              factory: Factory = Depends(get_factory)):
    b = _brand_or_404(factory, brand)
    if not b:
        return _page(linkpage.render_message(None, "Unknown newsletter", "This signup form isn't set up.",
                                             status="error"), 404)
    ip = _client_ip(request)
    if not SUBSCRIBE_LIMITER.allow(ip):
        msg = "Too many signups from your network. Please try again in a few minutes."
        if _wants_json(request):
            return JSONResponse({"ok": False, "error": msg}, status_code=429)
        return _page(linkpage.render_message(b, "Slow down a little", msg, status="error"), 429)
    try:
        result = store.subscribe(factory.db, b.slug, email, source=source[:100], ip=ip, honeypot=website)
    except store.SubscribeError as e:
        if _wants_json(request):
            return JSONResponse({"ok": False, "error": str(e)}, status_code=400)
        return _page(linkpage.render_message(b, "That email didn't look right", str(e), status="error",
                                             button=("Try again", f"{_base_url(request)}/l/{b.slug}")), 400)
    if result.needs_confirmation and result.subscriber:
        background.add_task(newsletter.send_confirmation, factory, b, result.subscriber,
                            base_url=_base_url(request))
    # Same answer for new, existing and bot signups: never reveal who is subscribed.
    if _wants_json(request):
        return JSONResponse({"ok": True, "message": "Check your inbox to confirm."})
    return _page(linkpage.render_message(
        b, "Check your inbox", "We just sent you a confirmation link. Tap it to confirm and get your free "
        f"{linkpage.lead_magnet(b, factory.settings)['title']}. (Check spam or promotions if you don't see it.)"))


@public_router.get("/confirm/{token}", response_class=HTMLResponse)
def confirm(token: str, request: Request, background: BackgroundTasks, factory: Factory = Depends(get_factory)):
    before = store.by_token(factory.db, token)
    row = store.confirm(factory.db, token)
    b = _brand_or_404(factory, row["brand"]) if row else None
    if not row or not b:
        return _page(linkpage.render_message(None, "Link expired", "This confirmation link isn't valid any "
                                             "more. Sign up again from the link page.", status="error"), 404)
    if before and before["status"] == "pending":
        background.add_task(_welcome_now, factory, row["id"], _base_url(request))
    magnet = linkpage.lead_magnet(b, factory.settings)
    url = magnet["url"] or f"{_base_url(request)}/freebie/{token}"
    return _page(linkpage.render_message(b, "You're in!", f"Thanks for confirming. Here's {magnet['title']}.",
                                         button=("Download your free guide", url)))


@public_router.get("/freebie/{token}", response_class=HTMLResponse)
def freebie(token: str, factory: Factory = Depends(get_factory)):
    row = store.by_token(factory.db, token)
    b = _brand_or_404(factory, row["brand"]) if row else None
    if not row or not b or row["status"] != "confirmed":
        return _page(linkpage.render_message(None, "Confirm first", "This download unlocks after you confirm "
                                             "your email.", status="error"), 403)
    return _page(linkpage.render_checklist(factory.settings, b, factory.llm))


@public_router.get("/unsubscribe/{token}", response_class=HTMLResponse)
def unsubscribe_page(token: str, factory: Factory = Depends(get_factory)):
    """Shows one button (a GET alone doesn't unsubscribe, so link scanners
    can't remove people by prefetching)."""
    row = store.by_token(factory.db, token)
    b = _brand_or_404(factory, row["brand"]) if row else None
    if not row:
        return _page(linkpage.render_message(None, "Link not found", "We couldn't find that subscription.",
                                             status="error"), 404)
    if row["status"] == "unsubscribed":
        return _page(linkpage.render_message(b, "You're unsubscribed", "You won't get any more emails from us."))
    form = (f'<form method="post" action="/unsubscribe/{quote(token)}"><button type="submit" '
            'style="font:inherit;font-weight:700;padding:12px 20px;border-radius:12px;border:0;cursor:pointer">'
            'Unsubscribe</button></form>')
    return _page(linkpage.render_message(b, "Unsubscribe?", f"Stop all emails to {row['email']}.",
                                         extra_html=form))


@public_router.post("/unsubscribe/{token}", response_class=HTMLResponse)
def unsubscribe(token: str, factory: Factory = Depends(get_factory)):
    """Unsubscribe; also the RFC 8058 one-click endpoint mail clients POST to."""
    row = store.unsubscribe(factory.db, token)
    if not row:
        return _page(linkpage.render_message(None, "Link not found", "We couldn't find that subscription.",
                                             status="error"), 404)
    b = _brand_or_404(factory, row["brand"])
    return _page(linkpage.render_message(b, "You're unsubscribed", "Done. You won't get any more emails from us."))


@public_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, factory: Factory = Depends(get_factory)):
    payload = await request.body()
    try:
        payments.verify_stripe_signature(payload, request.headers.get("stripe-signature", ""),
                                         os.environ.get("STRIPE_WEBHOOK_SECRET", ""))
        event = json.loads(payload)
    except payments.SignatureError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)
    return JSONResponse({"received": True, **payments.handle_stripe_event(factory.db, event)})


@public_router.post("/webhooks/gumroad")
async def gumroad_webhook(request: Request, factory: Factory = Depends(get_factory)):
    if not payments.gumroad_secret_ok(request.query_params.get("secret", "")):
        return JSONResponse({"error": "Bad or missing secret"}, status_code=403)
    form = dict(await request.form())
    result = payments.handle_gumroad_ping(factory.db, form, factory.brands(), request.query_params.get("brand", ""))
    return JSONResponse({"received": True, **result})


# ====================================================================== admin
def _back(path: str, msg: str = "", err: str = "") -> RedirectResponse:
    q = f"?msg={quote(msg)}" if msg else (f"?err={quote(err)}" if err else "")
    return RedirectResponse(path + q, status_code=303)


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def overview(request: Request, factory: Factory = Depends(get_factory)):
    brands = factory.brands()
    counts = store.counts(factory.db)
    rows = []
    for slug, b in brands.items():
        site = factory.settings.output_dir / slug / "site" / "index.html"
        kit = factory.settings.output_dir / slug / "brand-kit" / "manifest.json"
        rows.append({"slug": slug, "name": b.name, "counts": counts.get(slug, {}),
                     "growth": [r["n"] for r in store.growth(factory.db, slug, 30)],
                     "site": site.exists(), "site_rel": f"{slug}/site/index.html",
                     "kit": kit.exists(), "kit_rel": f"{slug}/brand-kit"})
    return templates.TemplateResponse(request, "funnel/index.html", {
        "rows": rows, "stats": analytics.funnel_stats(factory.db, list(brands)),
        "drafts": newsletter.list_drafts(factory.db, limit=10),
        "public_url": os.environ.get("FUNNEL_PUBLIC_URL", ""),
        "smtp": bool(os.environ.get("SMTP_HOST")), "address": bool(os.environ.get("BUSINESS_ADDRESS")),
        "stripe": bool(os.environ.get("STRIPE_WEBHOOK_SECRET")), "gumroad": bool(os.environ.get("GUMROAD_PING_SECRET")),
    })


@router.get("/digest/{draft_id}", response_class=HTMLResponse)
def digest_preview(draft_id: int, request: Request, factory: Factory = Depends(get_factory)):
    draft = newsletter.get_draft(factory.db, draft_id)
    sends = factory.db.query("SELECT status, COUNT(*) n FROM emails_sent WHERE draft_id = ? GROUP BY status",
                             [draft_id])
    confirmed = store.counts(factory.db, draft["brand"]).get(draft["brand"], {}).get("confirmed", 0)
    return templates.TemplateResponse(request, "funnel/digest.html", {
        "draft": draft, "sends": {r["status"]: r["n"] for r in sends}, "confirmed": confirmed,
        "preview_html": newsletter.fill(draft["html"], "#unsubscribe-preview",
                                        os.environ.get("BUSINESS_ADDRESS", "") or newsletter.MISSING_ADDRESS,
                                        html=True),
        "smtp": bool(os.environ.get("SMTP_HOST")), "address": bool(os.environ.get("BUSINESS_ADDRESS")),
    })


@router.post("/digest/{draft_id}/send")
def digest_send(draft_id: int, confirm: str = Form(""), factory: Factory = Depends(get_factory)):
    live = confirm == "send-for-real"
    try:
        r = newsletter.send_digest(factory, draft_id, confirm=live)
    except (ValueError, RuntimeError) as e:
        return _back(f"/funnel/digest/{draft_id}", err=str(e))
    if live:
        return _back(f"/funnel/digest/{draft_id}", msg=f"Sent {r['sent']}, failed {r['failed']}, "
                                                      f"skipped {r['skipped_already_sent']} (already sent).")
    return _back(f"/funnel/digest/{draft_id}", msg=f"Dry run: wrote {len(r['files'])} .eml files "
                                                  f"(output/{factory.db.get('newsletter_drafts', draft_id)['brand']}"
                                                  f"/newsletter/draft-{draft_id}/dry-run).")


@router.get("/{brand}/subscribers", response_class=HTMLResponse)
def subscribers(brand: str, request: Request, status: str = "", factory: Factory = Depends(get_factory)):
    b = factory.brand(brand)
    return templates.TemplateResponse(request, "funnel/subscribers.html", {
        "brand": b, "status": status, "counts": store.counts(factory.db, b.slug).get(b.slug, {}),
        "subs": store.list_subscribers(factory.db, b.slug, status or None, limit=1000),
        "growth": store.growth(factory.db, b.slug, 30),
        "drafts": newsletter.list_drafts(factory.db, b.slug, limit=10),
    })


@router.get("/{brand}/export.csv")
def export_csv(brand: str, factory: Factory = Depends(get_factory)):
    path = newsletter.export_subscribers_csv(factory, brand)
    return FileResponse(path, media_type="text/csv", filename=path.name)


@router.post("/{brand}/digest")
def digest_new(brand: str, days: int = Form(7), factory: Factory = Depends(get_factory)):
    draft_id = newsletter.draft_digest(factory, brand, days=max(1, min(days, 31)))
    return _back(f"/funnel/digest/{draft_id}", msg="Draft created. Review it, then dry-run or send.")


@router.post("/{brand}/link-page")
def rebuild_link_page(brand: str, factory: Factory = Depends(get_factory)):
    path = linkpage.build_link_page(factory.settings, factory.brand(brand), db=factory.db, llm=factory.llm)
    rel = path.relative_to(factory.settings.output_dir)
    return _back("/funnel", msg=f"Link page rebuilt: output/{rel} (also live at /l/{brand}).")


@router.post("/{brand}/brand-kit")
def rebuild_brand_kit(brand: str, factory: Factory = Depends(get_factory)):
    from ..brandkit import build_brand_kit
    paths = build_brand_kit(factory.settings, factory.brand(brand), llm=factory.llm)
    return _back("/funnel", msg=f"Brand kit built: {len(paths)} files in output/{brand}/brand-kit.")


@router.post("/{brand}/sales-pages")
def rebuild_sales_pages(brand: str, factory: Factory = Depends(get_factory)):
    paths = salespage.build_all_sales_pages(factory.settings, factory.db, factory.brand(brand))
    return _back("/funnel", msg=f"Built {len(paths)} sales page(s) in output/{brand}/site (live at /p/{brand}/...).")


@router.get("/{brand}/sequence.json")
def sequence_json(brand: str, factory: Factory = Depends(get_factory)) -> Response:
    b = factory.brand(brand)
    return JSONResponse({**sequences.sequence_status(factory, b.slug),
                         "problems": sequences.validate_sequence(factory.settings, b)})


@router.get("/stats.json")
def stats_json(since: str = "", factory: Factory = Depends(get_factory)) -> Response:
    return JSONResponse(analytics.funnel_stats(factory.db, list(factory.brands()), since or None))
