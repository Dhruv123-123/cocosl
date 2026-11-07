"""Client proposals for the UGC ad service: 2-3 printable pages, HTML + PDF.

`build_proposal(db, client_id, package, addons)` assembles:
  cover + summary, the opportunity (from the client's CRM notes), the offer,
  3 ad concepts written by `ugc.write_ad_script` (works offline), a timeline,
  the pricing table from `ugc.quote`, next steps with payment instructions,
  and the AI disclosure. Numbers come only from `ugc.quote`, so the proposal,
  the order and the invoice always agree.

Nothing is sent: you review the file and send it yourself. Each build is
recorded on the client (meta.proposals) and in the event log.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..db import DB, now_iso
from ._util import add_days, money, slugify, today
from .invoices import template_env
from .pdf import html_to_pdf
from .ugc import ADDONS, PACKAGES, AdBrief, get_client, orders, quote, write_ad_script

CONCEPT_STYLES = [
    ("spokesperson", "Spokesperson", "An AI presenter introduces the product and the problem it solves."),
    ("demo", "Product demo", "Your own footage or photos, step by step, with voiceover and captions."),
    ("offer", "Offer explainer", "Who it's for, what they get, and one clear offer to act on."),
]
DEPOSIT_PCT = 50
VALID_DAYS = 14
SCRIPT_DAYS = 2   # business days to first scripts after the brief and deposit


class _OfflineLLM:
    """Stand-in used when no LLM is passed: always takes the offline template."""
    provider = "offline"

    def structured(self, schema, *, system, prompt, offline, purpose="", max_tokens=0):  # noqa: ARG002
        return offline()


# --------------------------------------------------------------------------- content
def client_insights(client: dict, limit: int = 4) -> list[str]:
    """Readable notes from the CRM (timestamps and [status] tags stripped), newest first."""
    out = []
    for line in reversed((client.get("notes") or "").splitlines()):
        text = re.sub(r"^\[\d{4}-\d{2}-\d{2}\]\s*", "", line.strip())
        text = re.sub(r"^\[[a-z_]+\]\s*", "", text).strip()
        if text and text not in out:
            out.append(text)
        if len(out) >= limit:
            break
    return out


def opportunity_text(client: dict) -> str:
    niche = (client.get("niche") or "").strip()
    who = f"{niche} brands" if niche else "brands like yours"
    return (f"Short vertical video is where many {who} now get discovered: TikTok, Reels and Shorts reward "
            f"advertisers who test many creatives, and every test needs a fresh hook. Studio shoots make that "
            f"slow and expensive. Clearly labeled AI spokesperson and demo ads let {client['name']} test more "
            f"angles for less, then put budget behind the ones that work for your audience.")


def _product_for(db: DB, client: dict, products: list[str] | None) -> list[str]:
    if products:
        return [p for p in products if p.strip()] or [client["name"]]
    found = [(o.get("brief") or {}).get("product") for o in orders(db, client_id=client["id"])]
    found = [p for p in found if p]
    return found or [f"{client['name']}'s best-seller"]


def ad_concepts(llm, client: dict, products: list[str], audience: str = "", offer: str = "",
                benefits: list[str] | None = None) -> list[dict]:
    """Three concepts (one per style), each a checked AdScript from `write_ad_script`."""
    concepts = []
    for i, (style, label, blurb) in enumerate(CONCEPT_STYLES):
        product = products[i % len(products)]
        brief = AdBrief(product=product, brand_name=client["name"], audience=audience,
                        style=style, offer=offer, benefits=benefits or [], duration_s=20 if style == "demo" else 25,
                        notes="; ".join(client_insights(client, 2)))
        ad = write_ad_script(llm, brief)
        concepts.append({"style": style, "label": label, "blurb": blurb, "product": product,
                         "script": ad.model_dump()})
    return concepts


def timeline(package: str, turnaround_days: int, start: str | None = None) -> list[dict]:
    """Milestones from a start date. Delivery counts from approved scripts."""
    pkg = PACKAGES[package]
    day0 = start or today().isoformat()
    scripts = add_days(day0, SCRIPT_DAYS)
    if pkg.recurring:
        return [
            {"when": day0, "what": "Kick-off", "detail": "First month's invoice paid, brief form completed."},
            {"when": scripts, "what": "Month's scripts", "detail": f"{pkg.videos} scripts with hooks for your approval."},
            {"when": add_days(scripts, 14), "what": "First batch", "detail": "About half the month's ads delivered."},
            {"when": add_days(day0, 30), "what": "Second batch + report",
             "detail": "Remaining ads, creative report and next month's plan."},
        ]
    return [
        {"when": day0, "what": "Kick-off", "detail": f"{DEPOSIT_PCT}% deposit paid, brief form completed."},
        {"when": scripts, "what": "Scripts for approval",
         "detail": f"{pkg.videos} scripts × {pkg.hooks_per_video} hook{'s' if pkg.hooks_per_video > 1 else ''}. "
                   f"Nothing is produced until you approve."},
        {"when": add_days(scripts, turnaround_days), "what": "Delivery",
         "detail": f"Watermarked previews, then final MP4s on balance payment ({turnaround_days} days from approval)."},
        {"when": add_days(scripts, turnaround_days + 5), "what": "Revisions",
         "detail": f"{pkg.revisions} revision round{'s' if pkg.revisions > 1 else ''} included."},
    ]


def proposal_context(db: DB, client_id: int, package: str, addons: list[str] | tuple[str, ...] = (), *,
                     llm=None, rush: bool = False, discount_pct: float = 0, sender=None,
                     products: list[str] | None = None, audience: str = "", offer: str = "",
                     start: str | None = None) -> dict:
    """Everything the template needs, with all money figures from `ugc.quote`."""
    from .pitch import SenderProfile, _sender
    client = get_client(db, client_id)
    q = quote(package, list(addons), rush=rush, discount_pct=discount_pct)
    pkg = PACKAGES[package]
    sender = _sender(sender) if sender is not None else SenderProfile.from_env()
    prods = _product_for(db, client, products)
    deposit = q["total_cents"] if pkg.recurring else round(q["total_cents"] * DEPOSIT_PCT / 100)
    paid_usage = pkg.usage_days
    if "paid_usage_90d" in q["addons"]:
        paid_usage += 90
    usage = ("Perpetual, all channels" if "perpetual_usage" in q["addons"] else
             "12 months of paid ads" if "paid_usage_12m" in q["addons"] else f"{paid_usage} days of paid ads")
    issued = today().isoformat()
    number = f"P-{today():%Y%m%d}-{client_id:03d}"
    used = {p.get("number") for p in client["meta"].get("proposals") or []}
    n = 1
    while (number if n == 1 else f"{number}-{n}") in used:
        n += 1
    number = number if n == 1 else f"{number}-{n}"
    return {
        "number": number, "issued": issued, "valid_until": add_days(issued, VALID_DAYS),
        "client": client, "sender": sender, "package": pkg, "quote": q,
        "addon_names": [ADDONS[a].name for a in q["addons"]],
        "insights": client_insights(client), "opportunity": opportunity_text(client), "products": prods,
        "concepts": ad_concepts(llm or _OfflineLLM(), client, prods, audience=audience, offer=offer),
        "timeline": timeline(package, q["turnaround_days"], start=start),
        "deposit_cents": deposit, "balance_cents": q["total_cents"] - deposit,
        "deposit_pct": 100 if pkg.recurring else DEPOSIT_PCT, "usage": usage,
        "files": pkg.videos * pkg.hooks_per_video,
        "payment_instructions": sender.payment_instructions, "script_days": SCRIPT_DAYS,
        "generated_at": now_iso(),
    }


def render_proposal_html(ctx: dict) -> str:
    return template_env().get_template("proposal.html").render(**ctx)


def build_proposal(db: DB, client_id: int, package: str, addons: list[str] | tuple[str, ...] = (), *,
                   llm=None, settings=None, out_dir: str | Path | None = None, pdf: bool = True,
                   rush: bool = False, discount_pct: float = 0, sender=None, products: list[str] | None = None,
                   audience: str = "", offer: str = "") -> dict:
    """Render the proposal. With `settings` or `out_dir`, writes
    <out>/proposals/<client>-<number>.html (+ .pdf when Chromium is available)
    and records it on the client. Returns {html_text, html, pdf, path, total_cents, ...}."""
    ctx = proposal_context(db, client_id, package, addons, llm=llm, rush=rush, discount_pct=discount_pct,
                           sender=sender, products=products, audience=audience, offer=offer)
    page = render_proposal_html(ctx)
    result: dict[str, Any] = {"number": ctx["number"], "html_text": page, "total_cents": ctx["quote"]["total_cents"],
                              "deposit_cents": ctx["deposit_cents"], "html": None, "pdf": None, "path": None}
    base = Path(out_dir) if out_dir else (Path(settings.output_dir) if settings else None)
    if base is not None:
        folder = base / "proposals"
        folder.mkdir(parents=True, exist_ok=True)
        stem = f"{slugify(ctx['client']['name'], 40)}-{ctx['number']}"
        html_path = folder / f"{stem}.html"
        html_path.write_text(page, encoding="utf-8")
        pdf_path = folder / f"{stem}.pdf"
        has_pdf = pdf and html_to_pdf(html_path, pdf_path)
        result.update(html=str(html_path), pdf=str(pdf_path) if has_pdf else None)
        best = pdf_path if has_pdf else html_path
        result["path"] = str(best.relative_to(settings.output_dir)) if settings and not out_dir else str(best)
    client = get_client(db, client_id)
    meta = client["meta"]
    meta.setdefault("proposals", []).append({
        "number": ctx["number"], "package": package, "addons": ctx["quote"]["addons"],
        "total_cents": ctx["quote"]["total_cents"], "html": result["html"], "pdf": result["pdf"],
        "valid_until": ctx["valid_until"], "created_at": now_iso()})
    db.update("clients", client_id, {"meta": meta})
    db.log("proposal.built", "client", client_id, {"number": ctx["number"], "package": package,
                                                   "total": ctx["quote"]["total_cents"]})
    return result


def latest_proposal(client: dict) -> dict | None:
    meta = client.get("meta") if isinstance(client.get("meta"), dict) else {}
    items = meta.get("proposals") or []
    return items[-1] if items else None


__all__ = ["build_proposal", "proposal_context", "render_proposal_html", "latest_proposal", "client_insights",
           "ad_concepts", "timeline", "money"]
