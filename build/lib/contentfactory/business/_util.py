"""Small shared helpers for the business modules: money, dates, slugs, CSV."""
from __future__ import annotations

import csv
import io
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

CURRENCY_SYMBOLS = {"USD": "$", "EUR": "€", "GBP": "£", "INR": "₹", "CAD": "CA$", "AUD": "A$"}


def money(cents: Any, currency: str = "USD") -> str:
    """Integer cents -> '$1,234.56'."""
    try:
        value = int(cents or 0) / 100
    except (TypeError, ValueError):
        return str(cents)
    code = (currency or "USD").upper()
    sign = "-" if value < 0 else ""
    symbol = CURRENCY_SYMBOLS.get(code)
    body = f"{abs(value):,.2f}"
    return f"{sign}{symbol}{body}" if symbol else f"{sign}{body} {code}"


def to_cents(value: Any) -> int:
    """Parse '$1,234.56', '(12.00)', '-3', 12.5 or Decimal into integer cents.

    Raises ValueError on anything that isn't a number."""
    if value is None:
        raise ValueError("empty amount")
    if isinstance(value, bool):
        raise ValueError("bool is not an amount")
    if isinstance(value, int):
        return value * 100
    if isinstance(value, (float, Decimal)):
        return int((Decimal(str(value)) * 100).quantize(Decimal("1")))
    text = str(value).strip()
    if not text:
        raise ValueError("empty amount")
    negative = text.startswith("(") and text.endswith(")") or text.startswith("-") or text.endswith("-")
    cleaned = re.sub(r"[^0-9.,]", "", text)
    if "," in cleaned and "." in cleaned:
        # whichever separator comes last is the decimal point
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        head, _, tail = cleaned.rpartition(",")
        cleaned = f"{head.replace(',', '')}.{tail}" if len(tail) in (1, 2) else cleaned.replace(",", "")
    try:
        amount = Decimal(cleaned)
    except InvalidOperation as e:
        raise ValueError(f"not an amount: {value!r}") from e
    cents = int((amount * 100).quantize(Decimal("1")))
    return -cents if negative else cents


_DATE_FORMATS = [
    "%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y", "%m/%d/%y", "%d.%m.%Y", "%b %d, %Y", "%B %d, %Y",
    "%d %b %Y", "%d %B %Y", "%b %d %Y", "%Y%m%d", "%d-%b-%Y", "%m-%d-%Y",
]


def parse_date(value: Any) -> str:
    """Tolerant date parser -> 'YYYY-MM-DD'. Raises ValueError if unparseable."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    if not text:
        raise ValueError("empty date")
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        pass
    head = re.split(r"[T ](?=\d{1,2}:\d{2})", text)[0].strip().rstrip(",")
    for fmt in _DATE_FORMATS:
        for candidate in (head, text):
            try:
                return datetime.strptime(candidate, fmt).date().isoformat()
            except ValueError:
                continue
    raise ValueError(f"unrecognised date: {value!r}")


def today() -> date:
    return date.today()


def add_days(d: date | str, days: int) -> str:
    base = date.fromisoformat(d) if isinstance(d, str) else d
    return (base + timedelta(days=days)).isoformat()


def slugify(text: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return slug[:max_len].strip("-") or "item"


def read_csv_rows(source: str | Path | bytes, header_hints: list[str] | None = None) -> list[dict[str, str]]:
    """Read a CSV from a path, bytes or text. Skips preamble lines (e.g. report
    titles) until a row containing one of `header_hints` is found."""
    if isinstance(source, bytes):
        text = source.decode("utf-8-sig", errors="replace")
    elif isinstance(source, Path) or (isinstance(source, str) and "\n" not in source and len(source) < 1024
                                      and Path(source).exists()):
        text = Path(source).read_text(encoding="utf-8-sig", errors="replace")
    else:
        text = str(source).lstrip("﻿")
    lines = text.splitlines()
    if header_hints:
        hints = [h.lower() for h in header_hints]
        for i, line in enumerate(lines[:20]):
            if any(h in line.lower() for h in hints):
                lines = lines[i:]
                break
    reader = csv.DictReader(io.StringIO("\n".join(lines)))
    rows = []
    for row in reader:
        clean = {(k or "").strip(): (v or "").strip() if isinstance(v, str) else "" for k, v in row.items()}
        if any(clean.values()):
            rows.append(clean)
    return rows


def pick(row: dict[str, str], candidates: list[str]) -> str:
    """First non-empty value among candidate column names (case/space-insensitive)."""
    norm = {_norm(k): v for k, v in row.items()}
    for c in candidates:
        v = norm.get(_norm(c))
        if v not in (None, ""):
            return v
    return ""


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(name).lower())
