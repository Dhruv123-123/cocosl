"""Business pages for the dashboard (/business/...) and the public /go/{slug} redirect.

`router` needs the dashboard's auth; `public_router` must stay open (it's what
viewers click). Templates extend the dashboard's "base.html".
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import quote_plus

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse, RedirectResponse, Response

from . import affiliates, invoices as inv_mod, onboarding, pitch, products as prod_mod, proposals, revenue as rev_mod, ugc
from ._util import money

router = APIRouter(prefix="/business", tags=["business"])
public_router = APIRouter(tags=["public"])


def _factory(request: Request):
    from ..web.deps import get_factory
    return get_factory(request)


def _render(request: Request, name: str, **ctx: Any) -> HTMLResponse:
    from ..web.deps import templates
    ctx.setdefault("money", money)
    return templates.TemplateResponse(request, name, ctx)


def _go(url: str, msg: str = "", err: str = "") -> RedirectResponse:
    if msg or err:
        sep = "&" if "?" in url else "?"
        url += sep + ("msg=" + quote_plus(msg) if msg else "err=" + quote_plus(err))
    return RedirectResponse(url, status_code=303)


async def _upload_bytes(file: UploadFile | None) -> bytes:
    if file is None or not file.filename:
        raise ValueError("Choose a CSV file first")
    data = await file.read()
    if not data:
        raise ValueError("The uploaded file is empty")
    return data


# --------------------------------------------------------------------------- index
@router.get("", include_in_schema=False)
@router.get("/", include_in_schema=False)
def business_index():
    return RedirectResponse("/business/revenue", status_code=307)


# --------------------------------------------------------------------------- clients
@router.get("/clients", response_class=HTMLResponse)
def clients_page(request: Request, f=Depends(_factory)):
    outreach = pitch.outreach_today(f.db)
    in_plan = {x["client"]["id"] for x in outreach["follow_ups"] + outreach["first_touch"]}
    return _render(request, "biz_clients.html", title="Clients", board=ugc.pipeline(f.db),
                   statuses=ugc.CLIENT_STATUSES, due=[c for c in ugc.due_follow_ups(f.db) if c["id"] not in in_plan],
                   today=datetime.now().date().isoformat(), outreach=outreach, mailto=_mailto)


def _mailto(client: dict, subject: str, body: str) -> str:
    """mailto: link that opens a pre-filled draft in the user's own mail app (nothing is sent from here)."""
    from urllib.parse import quote
    return f"mailto:{quote(client.get('email') or '')}?subject={quote(subject)}&body={quote(body)}"


@router.post("/clients/{client_id}/sent")
def client_sent(client_id: int, back: str = Form(""), f=Depends(_factory)):
    """'I sent the next email': first pitch (schedules +3/+7 follow-ups) or the next follow-up."""
    target = _safe_back(back) if back else f"/business/clients/{client_id}"
    try:
        res = pitch.mark_sent(f.db, client_id)
    except (ValueError, KeyError) as e:
        return _go(target, err=str(e))
    if res["kind"] == "pitch":
        dues = ", ".join(st["due"] for st in res["cadence"]["steps"])
        return _go(target, msg=f"Pitch marked sent. Follow-up drafts scheduled for {dues}.")
    return _go(target, msg=f"Follow-up {res['step']['n']} marked sent.")


@router.post("/clients/{client_id}/proposal")
def client_proposal(client_id: int, package: str = Form("growth"), addons: list[str] = Form([]),
                    rush: str = Form(""), products: str = Form(""), discount: str = Form(""),
                    f=Depends(_factory)):
    try:
        proposals.build_proposal(f.db, client_id, package, addons, llm=f.llm, settings=f.settings, rush=bool(rush),
                                 discount_pct=float(discount or 0),
                                 products=[p.strip() for p in products.split(",") if p.strip()] or None)
    except (KeyError, ValueError, ugc.TestimonialError) as e:
        return _go(f"/business/clients/{client_id}", err=f"Proposal failed: {e}")
    return _go(f"/business/clients/{client_id}", msg="Proposal ready. Open it, review it, then send it yourself.")


@router.get("/clients/{client_id}/proposal")
def client_proposal_view(client_id: int, pdf: int = 0, f=Depends(_factory)):
    try:
        latest = proposals.latest_proposal(ugc.get_client(f.db, client_id))
    except KeyError:
        return HTMLResponse("Client not found", status_code=404)
    if not latest:
        return HTMLResponse("No proposal yet. Generate one from the client page.", status_code=404)
    path = _output_file(f, latest.get("pdf") if pdf else latest.get("html"))
    if path is None:
        return HTMLResponse("Proposal file not found (PDF needs Chromium; the HTML version is always saved).",
                            status_code=404)
    if pdf:
        return FileResponse(path, media_type="application/pdf", filename=path.name)
    return HTMLResponse(path.read_text(encoding="utf-8"))


def _output_file(f, stored: str | None):
    """Resolve a stored path, only if it lives inside the output folder."""
    from pathlib import Path
    if not stored:
        return None
    root = Path(f.settings.output_dir).resolve()
    p = Path(stored)
    p = (p if p.is_absolute() else root / p).resolve()
    return p if p.is_file() and p.is_relative_to(root) else None


@router.post("/clients")
def client_add(name: str = Form(...), email: str = Form(""), website: str = Form(""), niche: str = Form(""),
               contact_name: str = Form(""), notes: str = Form(""), f=Depends(_factory)):
    try:
        cid = ugc.add_client(f.db, name, email=email, website=website, niche=niche, contact_name=contact_name,
                             notes=notes, source="dashboard")
    except ValueError as e:
        return _go("/business/clients", err=str(e))
    return _go(f"/business/clients/{cid}", msg="Client saved")


@router.post("/clients/import")
async def clients_import(file: UploadFile = File(None), f=Depends(_factory)):
    try:
        res = pitch.import_leads_csv(f.db, await _upload_bytes(file), lead_source=f"csv:{file.filename}")
    except ValueError as e:
        return _go("/business/clients", err=str(e))
    msg = f"Imported {res['added']} lead(s), {res['duplicates']} duplicate(s) skipped"
    if res["errors"]:
        msg += f", {len(res['errors'])} error(s): " + "; ".join(res["errors"][:3])
    return _go("/business/clients", msg=msg)


@router.post("/pitches/draft-all")
def pitches_draft_all(f=Depends(_factory)):
    ids = pitch.draft_all(f.db, f.llm, status="lead")
    return _go("/business/clients", msg=f"Drafted {len(ids)} pitch(es). Review them on each client page.")


@router.post("/pitches/export")
def pitches_export(f=Depends(_factory)):
    out = f.settings.output_dir / "outreach" / datetime.now().strftime("%Y%m%d-%H%M%S")
    res = pitch.export_drafts(f.db, out)
    return _go("/business/clients", msg=f"Exported {res['count']} draft(s) to {out} (.eml + drafts.csv). "
                                          f"Nothing was sent.")


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def client_page(request: Request, client_id: int, f=Depends(_factory)):
    try:
        client = ugc.get_client(f.db, client_id)
    except KeyError:
        return _go("/business/clients", err=f"No client #{client_id}")
    return _render(request, "biz_client.html", title=client["name"], client=client,
                   statuses=ugc.CLIENT_STATUSES, draft=pitch.latest_draft(client),
                   cadence=client["meta"].get("cadence"), proposal=proposals.latest_proposal(client),
                   orders=ugc.orders(f.db, client_id=client_id), invoices=inv_mod.invoices(f.db, client_id=client_id),
                   packages=ugc.PACKAGES, addons=ugc.ADDONS, order_statuses=ugc.ORDER_STATUSES,
                   revenue_cents=f.db.scalar("SELECT COALESCE(SUM(amount_cents),0) FROM revenue WHERE client_id = ?",
                                             [client_id]))


@router.post("/clients/{client_id}/update")
def client_update(client_id: int, name: str = Form(None), email: str = Form(None), website: str = Form(None),
                  niche: str = Form(None), contact_name: str = Form(None), f=Depends(_factory)):
    ugc.update_client(f.db, client_id, name=name, email=email, website=website, niche=niche,
                      contact_name=contact_name)
    return _go(f"/business/clients/{client_id}", msg="Saved")


@router.post("/clients/{client_id}/status")
def client_status(client_id: int, status: str = Form(...), note: str = Form(""), follow_up: str = Form(""),
                  f=Depends(_factory)):
    try:
        ugc.set_client_status(f.db, client_id, status, note=note, follow_up=follow_up or None)
    except (ValueError, KeyError) as e:
        return _go(f"/business/clients/{client_id}", err=str(e))
    return _go(f"/business/clients/{client_id}", msg=f"Status: {status}")


@router.post("/clients/{client_id}/note")
def client_note(client_id: int, text: str = Form(...), f=Depends(_factory)):
    if text.strip():
        ugc.add_note(f.db, client_id, text)
    return _go(f"/business/clients/{client_id}", msg="Note added")


@router.post("/clients/{client_id}/followup")
def client_followup(client_id: int, when: str = Form(""), f=Depends(_factory)):
    ugc.set_follow_up(f.db, client_id, when or None)
    return _go(f"/business/clients/{client_id}", msg="Follow-up updated")


@router.post("/clients/{client_id}/pitch")
def client_pitch(client_id: int, f=Depends(_factory)):
    try:
        client = ugc.get_client(f.db, client_id)
        pitch.save_pitch_draft(f.db, client_id, pitch.draft_pitch(f.llm, client))
    except Exception as e:  # LLM errors surface as a flash message
        return _go(f"/business/clients/{client_id}", err=f"Pitch draft failed: {e}")
    return _go(f"/business/clients/{client_id}", msg="Pitch drafted. Review, then send it yourself.")


@router.post("/clients/{client_id}/optout")
def client_optout(client_id: int, f=Depends(_factory)):
    pitch.mark_opt_out(f.db, client_id)
    return _go(f"/business/clients/{client_id}", msg="Opted out: excluded from outreach")


@router.post("/clients/{client_id}/orders")
def client_order(client_id: int, package: str = Form(...), addons: list[str] = Form([]), rush: str = Form(""),
                 notes: str = Form(""), product: str = Form(""), f=Depends(_factory)):
    try:
        oid = ugc.create_order(f.db, client_id, package, addons=addons, rush=bool(rush),
                               brief={"notes": notes, "product": product})
    except (KeyError, ValueError) as e:
        return _go(f"/business/clients/{client_id}", err=str(e))
    return _go(f"/business/orders/{oid}/brief", msg=f"Order #{oid} created. Send the client the brief questionnaire.")


# --------------------------------------------------------------------------- orders
@router.get("/orders", response_class=HTMLResponse)
def orders_page(request: Request, status: str = "", f=Depends(_factory)):
    return _render(request, "biz_orders.html", title="Orders", orders=ugc.orders(f.db, status=status or None),
                   invoices=inv_mod.invoices(f.db), statuses=ugc.ORDER_STATUSES, status=status,
                   flow=ugc.ORDER_FLOW, packages=ugc.PACKAGES, addons=ugc.ADDONS,
                   overdue={i["id"] for i in inv_mod.overdue(f.db)})


@router.post("/orders/{order_id}/status")
def order_status(order_id: int, status: str = Form(...), back: str = Form("/business/orders"),
                 f=Depends(_factory)):
    try:
        ugc.set_order_status(f.db, order_id, status)
    except (ValueError, KeyError) as e:
        return _go(_safe_back(back), err=str(e))
    return _go(_safe_back(back), msg=f"Order #{order_id}: {status}")


@router.get("/orders/{order_id}/brief", response_class=HTMLResponse)
def order_brief_page(request: Request, order_id: int, f=Depends(_factory)):
    try:
        order = ugc.get_order(f.db, order_id)
    except KeyError:
        return _go("/business/orders", err=f"No order #{order_id}")
    client = ugc.get_client(f.db, order["client_id"])
    onboarding.setup_order(f.db, order_id)  # orders created before onboarding existed
    order = ugc.get_order(f.db, order_id)
    brief = order.get("brief") or {}
    return _render(request, "biz_brief.html", title=f"Brief: order #{order_id}", order=order, client=client,
                   brief=brief, answers=brief.get("answers") or {}, acks=brief.get("acknowledgements") or [],
                   questions=onboarding.QUESTIONS, acknowledgements=onboarding.ACKNOWLEDGEMENTS,
                   checklist=brief.get("checklist") or [], progress=onboarding.progress(order),
                   package=ugc.PACKAGES.get(order["package"]),
                   markdown=onboarding.questionnaire_markdown(order, client, pitch.SenderProfile.from_env().name))


@router.post("/orders/{order_id}/brief")
async def order_brief_save(request: Request, order_id: int, f=Depends(_factory)):
    form = await request.form()
    answers = {q["key"]: form.get(q["key"], "") for q in onboarding.QUESTIONS}
    try:
        res = onboarding.save_answers(f.db, order_id, answers, acknowledgements=form.getlist("ack"))
    except KeyError as e:
        return _go("/business/orders", err=str(e))
    if res["complete"]:
        return _go(f"/business/orders/{order_id}/brief", msg="Brief complete. Next: write the scripts.")
    return _go(f"/business/orders/{order_id}/brief", err="Saved. Still missing: " + ", ".join(res["missing"]))


@router.get("/orders/{order_id}/brief.md")
def order_brief_markdown(order_id: int, f=Depends(_factory)):
    try:
        order = ugc.get_order(f.db, order_id)
    except KeyError:
        return PlainTextResponse("Order not found", status_code=404)
    text = onboarding.questionnaire_markdown(order, ugc.get_client(f.db, order["client_id"]),
                                             pitch.SenderProfile.from_env().name)
    return PlainTextResponse(text, media_type="text/markdown; charset=utf-8",
                             headers={"Content-Disposition": f'inline; filename="order-{order_id}-brief.md"'})


@router.post("/orders/{order_id}/checklist")
def order_checklist(order_id: int, key: str = Form(...), done: str = Form(""), f=Depends(_factory)):
    try:
        onboarding.set_check(f.db, order_id, key, done=bool(done))
    except KeyError as e:
        return _go(f"/business/orders/{order_id}/brief", err=str(e))
    return _go(f"/business/orders/{order_id}/brief#checklist")


@router.post("/orders/{order_id}/ad-script-from-brief")
def order_ad_script_from_brief(order_id: int, f=Depends(_factory)):
    try:
        brief = onboarding.ad_brief_from_answers(f.db, order_id)
        ad = ugc.write_ad_script(f.llm, brief)
    except ugc.TestimonialError as e:
        return _go(f"/business/orders/{order_id}/brief", err=str(e))
    except Exception as e:
        return _go(f"/business/orders/{order_id}/brief", err=f"Ad script failed: {e}")
    order = ugc.get_order(f.db, order_id)
    data = order.get("brief") or {}
    data.setdefault("ad_scripts", []).append({"brief": brief.model_dump(), "script": ad.model_dump(),
                                              "created_at": datetime.now().isoformat(timespec="seconds")})
    f.db.update("orders", order_id, {"brief": data})
    return _go(f"/business/orders/{order_id}/brief", msg="Ad script written from the brief (see Orders page).")


@router.post("/orders/{order_id}/invoice")
def order_invoice(order_id: int, f=Depends(_factory)):
    try:
        iid = inv_mod.invoice_from_order(f.db, order_id)
    except KeyError as e:
        return _go("/business/orders", err=str(e))
    return _go(f"/business/invoices/{iid}")


@router.post("/orders/{order_id}/ad-script")
def order_ad_script(order_id: int, product: str = Form(...), benefits: str = Form(""), offer: str = Form(""),
                    cta: str = Form(""), audience: str = Form(""), style: str = Form("spokesperson"),
                    back: str = Form("/business/orders"), f=Depends(_factory)):
    try:
        order = ugc.get_order(f.db, order_id)
        client = ugc.get_client(f.db, order["client_id"])
        brief = ugc.AdBrief(product=product, brand_name=client["name"], audience=audience, offer=offer, cta=cta,
                            style=style, benefits=[b.strip() for b in benefits.split(",") if b.strip()])
        ad = ugc.write_ad_script(f.llm, brief)
    except ugc.TestimonialError as e:
        return _go(_safe_back(back), err=str(e))
    except Exception as e:
        return _go(_safe_back(back), err=f"Ad script failed: {e}")
    data = order.get("brief") or {}
    data.setdefault("ad_scripts", []).append({"brief": brief.model_dump(), "script": ad.model_dump(),
                                              "created_at": datetime.now().isoformat(timespec="seconds")})
    f.db.update("orders", order_id, {"brief": data})
    return _go(_safe_back(back), msg="Ad script written and passed the testimonial check")


def _safe_back(url: str) -> str:
    return url if url.startswith("/business/") else "/business/orders"


# --------------------------------------------------------------------------- invoices
@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
def invoice_view(invoice_id: int, f=Depends(_factory)):
    try:
        return HTMLResponse(inv_mod.render_invoice_html(f.db, invoice_id))
    except KeyError:
        return HTMLResponse("Invoice not found", status_code=404)


@router.post("/invoices/{invoice_id}/{action}")
def invoice_action(invoice_id: int, action: str, back: str = Form(""), f=Depends(_factory)):
    target = _safe_back(back) if back else "/business/orders"
    try:
        if action == "sent":
            inv_mod.mark_sent(f.db, invoice_id)
        elif action == "paid":
            inv_mod.mark_paid(f.db, invoice_id)
        elif action == "void":
            inv_mod.void_invoice(f.db, invoice_id)
        elif action == "save":
            res = inv_mod.save_invoice(f.settings, f.db, invoice_id)
            return _go(target, msg=f"Saved {res['path']}" + ("" if res["pdf"] else " (PDF unavailable; HTML saved)"))
        else:
            return _go(target, err=f"Unknown action {action}")
    except (ValueError, KeyError) as e:
        return _go(target, err=str(e))
    return _go(target, msg=f"Invoice marked {action}")


# --------------------------------------------------------------------------- products
@router.get("/products", response_class=HTMLResponse)
def products_page(request: Request, f=Depends(_factory)):
    return _render(request, "biz_products.html", title="Products", products=prod_mod.products(f.db),
                   brands=list(f.brands()), kinds=prod_mod.PRODUCT_KINDS)


@router.post("/products/new")
def product_new(brand: str = Form(...), idea: str = Form(...), kind: str = Form("guide"), f=Depends(_factory)):
    try:
        b = f.brand(brand)
        outline = prod_mod.outline_product(f.llm, b, idea, kind)
        res = prod_mod.build_product(f.settings, b, outline, db=f.db, kind=kind)
    except Exception as e:
        return _go("/business/products", err=f"Product build failed: {e}")
    return _go("/business/products", msg=f"Built '{outline.title}' -> {res['path']}")


@router.post("/products/{product_id}/listing")
def product_listing(product_id: int, url: str = Form(...), price: str = Form(""), f=Depends(_factory)):
    try:
        prod_mod.set_product_listing(f.db, product_id, url, rev_mod.to_cents(price) if price else None)
    except ValueError as e:
        return _go("/business/products", err=str(e))
    return _go("/business/products", msg="Listing saved")


@router.post("/products/import-gumroad")
async def product_import(file: UploadFile = File(None), brand: str = Form(""), f=Depends(_factory)):
    try:
        res = prod_mod.import_gumroad_sales(f.db, await _upload_bytes(file), brand=brand)
    except ValueError as e:
        return _go("/business/products", err=str(e))
    return _go("/business/products", msg=_import_msg(res))


# --------------------------------------------------------------------------- revenue
@router.get("/revenue", response_class=HTMLResponse)
def revenue_page(request: Request, f=Depends(_factory)):
    return _render(request, "biz_revenue.html", title="Revenue", s=rev_mod.summary(f.db),
                   ledger=rev_mod.ledger(f.db, limit=30), sources=rev_mod.REVENUE_SOURCES,
                   categories=rev_mod.EXPENSE_CATEGORIES, kinds=[k for k in rev_mod.SPECS if k != "affiliate"],
                   brands=list(f.brands()), today=datetime.now().date().isoformat())


@router.post("/revenue/add")
def revenue_add(source: str = Form(...), amount: str = Form(...), date: str = Form(""), brand: str = Form(""),
                note: str = Form(""), post_id: str = Form(""), f=Depends(_factory)):
    try:
        rev_mod.add_revenue(f.db, source, amount, date=date or None, brand=brand, note=note,
                            post_id=int(post_id) if post_id.strip().isdigit() else None)
    except ValueError as e:
        return _go("/business/revenue", err=str(e))
    return _go("/business/revenue", msg="Revenue added")


@router.post("/revenue/expense")
def expense_add(category: str = Form(...), amount: str = Form(...), date: str = Form(""), note: str = Form(""),
                f=Depends(_factory)):
    try:
        rev_mod.add_expense(f.db, category, amount, date=date or None, note=note)
    except ValueError as e:
        return _go("/business/revenue", err=str(e))
    return _go("/business/revenue", msg="Expense added")


@router.post("/revenue/import")
async def revenue_import(file: UploadFile = File(None), kind: str = Form("generic"), brand: str = Form(""),
                         f=Depends(_factory)):
    try:
        res = rev_mod.import_csv(f.db, await _upload_bytes(file), kind, brand=brand)
    except ValueError as e:
        return _go("/business/revenue", err=str(e))
    return _go("/business/revenue", msg=_import_msg(res))


def _import_msg(res: dict) -> str:
    msg = (f"Imported {res['imported']} row(s) ({money(res['total_cents'])}), {res['duplicates']} duplicate(s), "
           f"{res['skipped']} skipped")
    if res["errors"]:
        msg += f", {len(res['errors'])} error(s): " + "; ".join(res["errors"][:3])
    return msg


# --------------------------------------------------------------------------- affiliates
@router.get("/affiliates", response_class=HTMLResponse)
def affiliates_page(request: Request, f=Depends(_factory)):
    return _render(request, "biz_affiliates.html", title="Affiliate links", links=affiliates.links(f.db),
                   by_post=affiliates.clicks_by_post(f.db)[:30], base=affiliates.link_base_url(),
                   brands=list(f.brands()))


@router.post("/affiliates/sync")
def affiliates_sync(f=Depends(_factory)):
    res = affiliates.sync_from_brands(f.db, f.brands())
    return _go("/business/affiliates", msg=f"{len(res['added'])} added, {len(res['updated'])} updated")


@router.post("/affiliates/add")
def affiliates_add(name: str = Form(...), url: str = Form(...), slug: str = Form(""), brand: str = Form(""),
                   commission: str = Form(""), f=Depends(_factory)):
    try:
        affiliates.add_link(f.db, name, url, slug=slug, brand=brand, commission=commission)
    except ValueError as e:
        return _go("/business/affiliates", err=str(e))
    return _go("/business/affiliates", msg="Link saved")


# --------------------------------------------------------------------------- public
@public_router.get("/go/{slug}", include_in_schema=False)
def go(slug: str, request: Request, p: str = "", s: str = "", f=Depends(_factory)):
    """Public tracked redirect: count the click, 302 to the merchant URL (incoming utm_* are passed on)."""
    utm = {k: v for k, v in request.query_params.items() if k.startswith("utm_")}
    url = affiliates.resolve_click(f.db, slug, post_id=p or None, platform=s, utm=utm)
    if not url:
        return Response("Link not found", status_code=404, media_type="text/plain")
    return RedirectResponse(url, status_code=302, headers={"Cache-Control": "no-store",
                                                          "X-Robots-Tag": "noindex"})
