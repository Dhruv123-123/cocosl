"""Payments in: Stripe webhooks, Gumroad pings and Stripe Payment Links.

Stripe signature check follows https://docs.stripe.com/webhooks (verify
manually): header `t=<unix>,v1=<hex>[,v1=...][,v0=...]`; signed payload is
`<t>.<raw body>`; expected = HMAC-SHA256(endpoint secret, signed payload);
compare constant-time against every v1 (other schemes ignored); reject if the
timestamp is outside the tolerance (Stripe libraries default to 300 s).

Gumroad pings are not signed. We protect the endpoint with a long random
shared secret in the ping URL (`/webhooks/gumroad?secret=...`, value from
GUMROAD_PING_SECRET) and treat the data as a notification only: amounts are
what Gumroad sends, deduped by sale_id. Reconcile against Gumroad's sales CSV
(business.revenue.import_csv) for accounting.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

import httpx

from ..config import BrandProfile
from ..db import DB
from ..publish.base import MissingCredentials

REVENUE_SOURCES = {"affiliate", "adsense", "creator_fund", "sponsorship", "ugc", "product", "other"}
DEFAULT_TOLERANCE = 300
STRIPE_API = "https://api.stripe.com/v1"


class SignatureError(ValueError):
    """Webhook authenticity check failed."""


# ---------------------------------------------------------------- stripe verify
def stripe_signature(payload: bytes, secret: str, timestamp: int) -> str:
    signed = f"{timestamp}.".encode() + payload
    return hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()


def verify_stripe_signature(payload: bytes, header: str, secret: str, *, tolerance: int = DEFAULT_TOLERANCE,
                            now: float | None = None) -> int:
    """Raise SignatureError unless `header` is a valid, fresh Stripe-Signature
    for `payload` (the raw request body). Returns the signed timestamp."""
    if not secret:
        raise SignatureError("STRIPE_WEBHOOK_SECRET is not set")
    if not header:
        raise SignatureError("Missing Stripe-Signature header")
    timestamp, sigs = None, []
    for part in header.split(","):
        key, _, value = part.strip().partition("=")
        if key == "t":
            try:
                timestamp = int(value)
            except ValueError:
                raise SignatureError("Bad timestamp in Stripe-Signature") from None
        elif key == "v1":
            sigs.append(value)
    if timestamp is None or not sigs:
        raise SignatureError("Stripe-Signature has no timestamp or v1 signature")
    expected = stripe_signature(payload, secret, timestamp)
    if not any(hmac.compare_digest(expected, s) for s in sigs):
        raise SignatureError("No signatures found matching the expected signature for payload")
    if tolerance > 0 and abs((now if now is not None else time.time()) - timestamp) > tolerance:
        raise SignatureError("Timestamp outside the tolerance zone (possible replay)")
    return timestamp


def stripe_test_header(payload: bytes, secret: str, timestamp: int | None = None) -> str:
    """Build a valid header (for tests and local replays)."""
    ts = int(timestamp if timestamp is not None else time.time())
    return f"t={ts},v1={stripe_signature(payload, secret, ts)}"


# ---------------------------------------------------------------- revenue
def record_revenue(db: DB, *, source: str, amount_cents: int, currency: str, brand: str, external_id: str,
                   note: str, date: str) -> int | None:
    """Insert into `revenue`; None when (source, external_id) already exists."""
    if source not in REVENUE_SOURCES:
        source = "product"
    try:
        return db.insert("revenue", {"date": date, "source": source, "brand": brand or "",
                                     "amount_cents": int(amount_cents), "currency": (currency or "USD").upper(),
                                     "note": note[:500], "external_id": external_id})
    except sqlite3.IntegrityError:
        if brand:  # e.g. charge.succeeded (no metadata) arrived before checkout.session.completed
            db.execute("UPDATE revenue SET brand = ? WHERE source = ? AND external_id = ? AND brand = ''",
                       [brand, source, external_id])
        return None


def _date(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts), timezone.utc).date().isoformat()
    except (TypeError, ValueError, OSError):
        return datetime.now(timezone.utc).date().isoformat()


def handle_stripe_event(db: DB, event: dict) -> dict:
    """Record paid checkout sessions and successful charges.

    Both events can fire for one payment, so the dedupe key is the
    PaymentIntent id when present (else the object id). Brand and revenue
    source come from metadata (`brand`, `source`); default source 'product'."""
    etype = event.get("type", "")
    obj = (event.get("data") or {}).get("object") or {}
    if etype == "checkout.session.completed":
        if obj.get("payment_status") not in ("paid", "no_payment_required"):
            return {"recorded": False, "reason": f"payment_status={obj.get('payment_status')}"}
        amount = obj.get("amount_total") or 0
        name = (obj.get("metadata") or {}).get("product") or "Stripe checkout"
    elif etype == "charge.succeeded":
        if not obj.get("paid", True) or obj.get("status", "succeeded") != "succeeded":
            return {"recorded": False, "reason": "charge not paid"}
        amount = obj.get("amount") or 0
        name = obj.get("description") or (obj.get("metadata") or {}).get("product") or "Stripe charge"
    else:
        return {"recorded": False, "reason": f"ignored event type {etype}"}
    if not amount:
        return {"recorded": False, "reason": "zero amount"}
    meta = obj.get("metadata") or {}
    pi = obj.get("payment_intent")
    pi = pi.get("id") if isinstance(pi, dict) else pi
    ext = f"stripe:{pi or obj.get('id') or event.get('id')}"
    row = record_revenue(db, source=meta.get("source", "product"), amount_cents=int(amount),
                         currency=obj.get("currency", "usd"), brand=meta.get("brand", ""), external_id=ext,
                         note=f"Stripe {etype}: {name}"[:200], date=_date(obj.get("created") or event.get("created")))
    db.log("funnel.stripe_event", "revenue", row, {"type": etype, "event": event.get("id"), "duplicate": row is None})
    return {"recorded": row is not None, "revenue_id": row, "external_id": ext,
            "reason": "" if row else "duplicate"}


# ---------------------------------------------------------------- gumroad
def gumroad_secret_ok(given: str) -> bool:
    secret = os.environ.get("GUMROAD_PING_SECRET", "")
    return bool(secret) and hmac.compare_digest(given.encode(), secret.encode())


def brand_for_product(brands: dict[str, BrandProfile], permalink: str, product_url: str = "") -> str:
    """Match a Gumroad product to the brand whose products list links to it."""
    for slug, b in brands.items():
        for p in b.products:
            url = str(p.get("url", ""))
            if not url:
                continue
            if product_url and url.rstrip("/") == product_url.rstrip("/"):
                return slug
            if permalink and urlparse(url).path.rstrip("/").split("/")[-1] == permalink:
                return slug
    return ""


def handle_gumroad_ping(db: DB, form: dict, brands: dict[str, BrandProfile], brand_hint: str = "") -> dict:
    """Record a Gumroad sale ping.

    Fields used (Gumroad Ping, form-encoded): sale_id, price (cents),
    currency, product_name, permalink / product_permalink, refunded, test,
    sale_timestamp. TODO: re-check names against Gumroad's current Ping docs
    (https://gumroad.com/ping) when going live; unknown fields are ignored."""
    sale_id = str(form.get("sale_id", "")).strip()
    if not sale_id:
        return {"recorded": False, "reason": "no sale_id"}
    if str(form.get("test", "")).lower() == "true":
        return {"recorded": False, "reason": "test ping"}
    if str(form.get("refunded", "")).lower() == "true":
        return {"recorded": False, "reason": "refunded sale"}
    try:
        cents = int(float(form.get("price", 0)))
    except (TypeError, ValueError):
        return {"recorded": False, "reason": "bad price"}
    if cents <= 0:
        return {"recorded": False, "reason": "zero amount"}
    permalink = str(form.get("permalink") or form.get("product_permalink") or "")
    if permalink.startswith("http"):
        product_url, permalink = permalink, urlparse(permalink).path.rstrip("/").split("/")[-1]
    else:
        product_url = ""
    brand = brand_hint if brand_hint in brands else brand_for_product(brands, permalink, product_url)
    ts = str(form.get("sale_timestamp", ""))[:10]
    row = record_revenue(db, source="product", amount_cents=cents, currency=str(form.get("currency", "usd")),
                         brand=brand, external_id=f"gumroad:{sale_id}",
                         note=f"Gumroad: {form.get('product_name', permalink)}"[:200],
                         date=ts if len(ts) == 10 and ts[4] == "-" else datetime.now(timezone.utc).date().isoformat())
    db.log("funnel.gumroad_ping", "revenue", row, {"sale_id": sale_id, "duplicate": row is None})
    return {"recorded": row is not None, "revenue_id": row, "reason": "" if row else "duplicate"}


# ---------------------------------------------------------------- payment links
def stripe_payment_link(product: dict, *, brand: str = "", api_key: str | None = None,
                        client: httpx.Client | None = None) -> str:
    """Create a Stripe Payment Link for `product` ({name, price} in currency
    units, optional currency/description) and return its URL.

    Two calls (https://docs.stripe.com/api/payment-link/create): POST /v1/prices
    with product_data[name], then POST /v1/payment_links with that price.
    Metadata `brand`/`source`/`product` flows to checkout sessions so the
    webhook can attribute revenue. Never called automatically."""
    key = api_key or os.environ.get("STRIPE_API_KEY", "")
    if not key:
        raise MissingCredentials("stripe", ["STRIPE_API_KEY"])
    name = str(product.get("name", "")).strip()
    if not name:
        raise ValueError("Product needs a name")
    try:
        cents = int(round(float(product.get("price", 0)) * 100))
    except (TypeError, ValueError):
        raise ValueError(f"Bad price {product.get('price')!r}") from None
    if cents <= 0:
        raise ValueError("Payment links need a price above zero")
    currency = str(product.get("currency", "usd")).lower()
    own = client is None
    client = client or httpx.Client(timeout=30)
    try:
        auth = {"Authorization": f"Bearer {key}"}
        price = client.post(f"{STRIPE_API}/prices", headers=auth, data={
            "currency": currency, "unit_amount": str(cents), "product_data[name]": name[:250]})
        _raise_stripe(price)
        meta = {"metadata[brand]": brand, "metadata[source]": "product", "metadata[product]": name[:450]}
        link = client.post(f"{STRIPE_API}/payment_links", headers=auth, data={
            "line_items[0][price]": price.json()["id"], "line_items[0][quantity]": "1", **meta})
        _raise_stripe(link)
        return link.json()["url"]
    finally:
        if own:
            client.close()


def _raise_stripe(resp: httpx.Response) -> None:
    if resp.status_code >= 400:
        try:
            msg = resp.json().get("error", {}).get("message", resp.text)
        except (ValueError, json.JSONDecodeError):
            msg = resp.text
        raise RuntimeError(f"Stripe API error {resp.status_code}: {msg}")
