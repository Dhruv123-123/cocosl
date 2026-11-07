"""Email building and delivery.

Delivery is SMTP (any provider: SES, Postmark, Mailgun, Fastmail, Gmail app
password...) configured by env vars. Without SMTP, or in dry runs, messages
are written as .eml files you can open in any mail client.

Env: SMTP_HOST, SMTP_PORT (587 STARTTLS; 465 implicit TLS), SMTP_USER,
SMTP_PASSWORD, SMTP_FROM ("Name <you@domain>"), BUSINESS_ADDRESS (CAN-SPAM
postal address), FUNNEL_PUBLIC_URL (https base where /confirm etc. are served).
"""
from __future__ import annotations

import html
import os
import re
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr, make_msgid, parseaddr
from pathlib import Path

from ..config import BrandProfile, Settings
from ..publish.base import MissingCredentials

UNSUB_PLACEHOLDER = "%%UNSUBSCRIBE_URL%%"


def public_url(settings: Settings | None = None, fallback: str = "") -> str:
    """Base URL for links in emails and the static link page."""
    base = os.environ.get("FUNNEL_PUBLIC_URL", "").strip() or fallback or "http://localhost:8000"
    return base.rstrip("/")


def business_address() -> str:
    return os.environ.get("BUSINESS_ADDRESS", "").strip()


@dataclass
class SMTPConfig:
    host: str
    port: int
    user: str
    password: str
    sender: str

    @classmethod
    def from_env(cls) -> "SMTPConfig | None":
        host = os.environ.get("SMTP_HOST", "").strip()
        if not host:
            return None
        return cls(host=host, port=int(os.environ.get("SMTP_PORT", "587") or 587),
                   user=os.environ.get("SMTP_USER", ""), password=os.environ.get("SMTP_PASSWORD", ""),
                   sender=os.environ.get("SMTP_FROM", "") or os.environ.get("SMTP_USER", ""))

    def missing(self) -> list[str]:
        return [k for k, v in (("SMTP_FROM", self.sender),) if not v]


def require_smtp() -> SMTPConfig:
    cfg = SMTPConfig.from_env()
    if cfg is None:
        raise MissingCredentials("email", ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"])
    if cfg.missing():
        raise MissingCredentials("email", cfg.missing())
    return cfg


def sender_for(brand: BrandProfile, cfg: SMTPConfig | None) -> str:
    raw = (cfg.sender if cfg else "") or os.environ.get("SMTP_FROM", "") or "newsletter@localhost"
    name, addr = parseaddr(raw)
    return formataddr((name or brand.name, addr or raw))


def build_message(*, brand: BrandProfile, to: str, subject: str, text: str, html_body: str | None,
                  unsubscribe_url: str, cfg: SMTPConfig | None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender_for(brand, cfg)
    msg["To"] = to
    msg["Subject"] = subject
    domain = parseaddr(msg["From"])[1].rpartition("@")[2] or "localhost"
    msg["Message-ID"] = make_msgid(domain=domain)
    # RFC 2369 / RFC 8058 one-click unsubscribe (Gmail/Yahoo bulk sender rules).
    msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
    msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
    msg.set_content(text.replace(UNSUB_PLACEHOLDER, unsubscribe_url))
    if html_body:
        msg.add_alternative(html_body.replace(UNSUB_PLACEHOLDER, html.escape(unsubscribe_url, quote=True)),
                            subtype="html")
    return msg


def write_eml(msg: EmailMessage, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(msg))
    return path


def smtp_send(cfg: SMTPConfig, messages: list[EmailMessage]) -> list[str | None]:
    """Send messages over one connection. Returns an error string (or None) per message."""
    ctx = ssl.create_default_context()
    errors: list[str | None] = []
    if cfg.port == 465:
        server: smtplib.SMTP = smtplib.SMTP_SSL(cfg.host, cfg.port, context=ctx, timeout=30)
    else:
        server = smtplib.SMTP(cfg.host, cfg.port, timeout=30)
        server.ehlo()
        if server.has_extn("starttls"):
            server.starttls(context=ctx)
            server.ehlo()
    try:
        if cfg.user:
            server.login(cfg.user, cfg.password)
        for m in messages:
            try:
                server.send_message(m)
                errors.append(None)
            except smtplib.SMTPException as e:
                errors.append(f"{type(e).__name__}: {e}")
    finally:
        try:
            server.quit()
        except smtplib.SMTPException:
            pass
    return errors


def safe_filename(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9@._-]+", "_", text)[:80]
