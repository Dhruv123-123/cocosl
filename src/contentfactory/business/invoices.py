"""Invoices: numbering (INV-YYYY-####), line items, HTML/PDF rendering, payment.

`mark_paid` records exactly one revenue row (source 'ugc', external_id = the
invoice number), marks the linked order paid and the client won.
"""
from __future__ import annotations

import sqlite3
from datetime import date
from pathlib import Path
from typing import Any

import jinja2

from ..db import DB, now_iso
from ._util import add_days, money, to_cents, today
from .pdf import html_to_pdf
from .revenue import add_revenue

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
INVOICE_STATUSES = ["draft", "sent", "paid", "void"]


def template_env() -> jinja2.Environment:
    """Standalone Jinja env for printable documents (invoices, product guides)."""
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATES_DIR)),
                             autoescape=jinja2.select_autoescape(["html"]))
    env.filters["money"] = money
    return env


def next_invoice_number(db: DB, year: int | None = None) -> str:
    year = year or today().year
    last = db.scalar("SELECT number FROM invoices WHERE number LIKE ? ORDER BY number DESC LIMIT 1",
                     [f"INV-{year}-%"])
    n = int(last.rsplit("-", 1)[1]) + 1 if last else 1
    return f"INV-{year}-{n:04d}"


def normalize_items(items: list[dict]) -> list[dict]:
    """Accept {description, qty, unit_cents} or {description, qty, unit_price}; compute amounts."""
    out = []
    for it in items:
        desc = str(it.get("description", "")).strip()
        if not desc:
            raise ValueError("Every line item needs a description")
        qty = int(it.get("qty", 1) or 1)
        unit = it.get("unit_cents")
        unit = int(unit) if unit is not None else to_cents(it.get("unit_price", 0))
        out.append({"description": desc, "qty": qty, "unit_cents": unit, "amount_cents": qty * unit})
    return out


def totals(items: list[dict], tax_pct: float = 0) -> dict:
    subtotal = sum(int(i["amount_cents"]) for i in items)
    tax = round(subtotal * tax_pct / 100)
    return {"subtotal_cents": subtotal, "tax_cents": tax, "total_cents": subtotal + tax}


def create_invoice(db: DB, client_id: int, items: list[dict], *, order_id: int | None = None,
                   currency: str = "USD", due_days: int = 14, tax_pct: float = 0,
                   issue: bool = False) -> int:
    """Create a draft invoice (or issued, with issue=True). Tax becomes its own line item."""
    if not db.get("clients", client_id):
        raise KeyError(f"No client #{client_id}")
    lines = normalize_items(items)
    if not lines:
        raise ValueError("An invoice needs at least one line item")
    t = totals(lines, tax_pct)
    if t["tax_cents"]:
        lines.append({"description": f"Tax ({tax_pct:g}%)", "qty": 1, "unit_cents": t["tax_cents"],
                      "amount_cents": t["tax_cents"]})
    for _ in range(5):  # retry on a numbering race
        number = next_invoice_number(db)
        try:
            inv_id = db.insert("invoices", {
                "client_id": client_id, "order_id": order_id, "number": number, "items": lines,
                "total_cents": t["total_cents"], "currency": currency.upper(), "status": "draft",
                "due_at": add_days(today(), due_days),
            })
            break
        except sqlite3.IntegrityError:
            continue
    else:
        raise RuntimeError("Could not allocate an invoice number")
    db.log("invoice.created", "invoice", inv_id, {"number": number, "total": t["total_cents"]})
    if issue:
        mark_sent(db, inv_id)
    return inv_id


def invoice_from_order(db: DB, order_id: int, due_days: int = 14) -> int:
    """Invoice an order using its quote's line items. Reuses an open invoice if one exists."""
    order = db.get("orders", order_id)
    if not order:
        raise KeyError(f"No order #{order_id}")
    existing = db.one("SELECT id FROM invoices WHERE order_id = ? AND status != 'void' ORDER BY id DESC LIMIT 1",
                      [order_id])
    if existing:
        return existing["id"]
    quote = (order.get("brief") or {}).get("quote") or {}
    items = quote.get("items") or [{"description": f"{order['package']} package", "qty": 1,
                                    "unit_cents": order["price_cents"]}]
    return create_invoice(db, order["client_id"], items, order_id=order_id, due_days=due_days)


def get_invoice(db: DB, invoice_id: int) -> dict:
    inv = db.get("invoices", invoice_id)
    if not inv:
        raise KeyError(f"No invoice #{invoice_id}")
    return inv


def mark_sent(db: DB, invoice_id: int, issued_at: str | None = None) -> None:
    """Record that you sent the invoice yourself (nothing is emailed from here)."""
    inv = get_invoice(db, invoice_id)
    if inv["status"] in ("paid", "void"):
        raise ValueError(f"Invoice {inv['number']} is {inv['status']}")
    db.update("invoices", invoice_id, {"status": "sent", "issued_at": issued_at or today().isoformat()})
    db.log("invoice.sent", "invoice", invoice_id, {"number": inv["number"]})


def mark_paid(db: DB, invoice_id: int, paid_at: str | None = None, note: str = "") -> int | None:
    """Mark paid and record revenue (source 'ugc'). Idempotent: returns the revenue id."""
    inv = get_invoice(db, invoice_id)
    if inv["status"] == "void":
        raise ValueError(f"Invoice {inv['number']} is void")
    paid_on = paid_at or today().isoformat()
    if inv["status"] != "paid":
        db.update("invoices", invoice_id, {"status": "paid", "paid_at": paid_on,
                                           "issued_at": inv["issued_at"] or paid_on})
    add_revenue(db, "ugc", amount_cents=inv["total_cents"], date=paid_on, client_id=inv["client_id"],
                currency=inv["currency"], external_id=inv["number"],
                note=note or f"Invoice {inv['number']}")
    rev = db.one("SELECT id FROM revenue WHERE source = 'ugc' AND external_id = ?", [inv["number"]])
    if inv["order_id"]:
        db.update("orders", inv["order_id"], {"status": "paid"})
    client = db.get("clients", inv["client_id"])
    if client and client["status"] != "won":
        from .ugc import set_client_status
        set_client_status(db, client["id"], "won", note=f"Paid {inv['number']}", actor="system")
    db.log("invoice.paid", "invoice", invoice_id, {"number": inv["number"], "revenue_id": rev["id"]})
    return rev["id"]


def mark_order_paid(db: DB, order_id: int, paid_at: str | None = None) -> int | None:
    """Ensure the order has an invoice and mark it paid (records revenue once)."""
    return mark_paid(db, invoice_from_order(db, order_id), paid_at=paid_at)


def void_invoice(db: DB, invoice_id: int) -> None:
    inv = get_invoice(db, invoice_id)
    if inv["status"] == "paid":
        raise ValueError("Paid invoices can't be voided; record a refund as a negative revenue entry instead")
    db.update("invoices", invoice_id, {"status": "void"})
    db.log("invoice.void", "invoice", invoice_id, {"number": inv["number"]})


def invoices(db: DB, status: str | None = None, client_id: int | None = None) -> list[dict]:
    sql = "SELECT i.*, c.name AS client_name FROM invoices i JOIN clients c ON c.id = i.client_id WHERE 1=1"
    params: list[Any] = []
    if status:
        sql += " AND i.status = ?"
        params.append(status)
    if client_id:
        sql += " AND i.client_id = ?"
        params.append(client_id)
    return db.query(sql + " ORDER BY i.id DESC", params)


def overdue(db: DB, on: date | None = None) -> list[dict]:
    cutoff = (on or today()).isoformat()
    return [i for i in invoices(db, status="sent") if i["due_at"] and i["due_at"] < cutoff]


# --------------------------------------------------------------------------- rendering
def render_invoice_html(db: DB, invoice_id: int, sender=None) -> str:
    """Printable HTML for an invoice (business/templates/invoice.html)."""
    from .pitch import SenderProfile
    inv = get_invoice(db, invoice_id)
    client = db.get("clients", inv["client_id"]) or {}
    sender = sender or SenderProfile.from_env()
    items = inv.get("items") or []
    order = db.get("orders", inv["order_id"]) if inv.get("order_id") else None
    return template_env().get_template("invoice.html").render(
        inv=inv, client=client, sender=sender, items=items, order=order,
        subtotal=sum(int(i.get("amount_cents", 0)) for i in items), generated_at=now_iso())


def save_invoice(settings, db: DB, invoice_id: int, pdf: bool = True, sender=None) -> dict:
    """Write output_dir/invoices/<number>.html (+ .pdf when Chromium is available).
    Stores the best file's path (relative to output_dir) on the invoice."""
    inv = get_invoice(db, invoice_id)
    folder = Path(settings.output_dir) / "invoices"
    folder.mkdir(parents=True, exist_ok=True)
    html_path = folder / f"{inv['number']}.html"
    html_path.write_text(render_invoice_html(db, invoice_id, sender), encoding="utf-8")
    pdf_path = folder / f"{inv['number']}.pdf"
    has_pdf = pdf and html_to_pdf(html_path, pdf_path)
    best = pdf_path if has_pdf else html_path
    rel = str(best.relative_to(settings.output_dir))
    db.update("invoices", invoice_id, {"path": rel})
    return {"html": str(html_path), "pdf": str(pdf_path) if has_pdf else None, "path": rel}
