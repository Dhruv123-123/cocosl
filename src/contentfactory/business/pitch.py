"""Outreach DRAFTS for the UGC service. Nothing here sends email.

Drafts are stored on the client (meta.pitch_drafts) and exported as .eml files
(open in your mail client, review, send yourself) plus a CSV for mail-merge.
Every draft carries CAN-SPAM basics: real sender identity, a physical postal
address and a clear opt-out line. Leads come from CSVs you compile yourself
(public business contact pages); this module never scrapes or guesses emails.
"""
from __future__ import annotations

import csv
import os
import re
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from pydantic import BaseModel

from ..db import DB, now_iso
from ..schemas import PitchEmail
from ._util import pick, read_csv_rows, slugify
from .ugc import PACKAGES, add_client, find_client, get_client

ADDRESS_PLACEHOLDER = "[YOUR PHYSICAL MAILING ADDRESS]"
OPT_OUT_LINE = "Not interested? Just reply \"no thanks\" and I won't email you again."
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


class SenderProfile(BaseModel):
    name: str = ""
    business_name: str = ""
    email: str = ""
    website: str = ""
    portfolio_url: str = ""
    physical_address: str = ""
    payment_instructions: str = ""

    @classmethod
    def from_env(cls) -> "SenderProfile":
        """FACTORY_SENDER_NAME/_BUSINESS/_EMAIL/_WEBSITE/_ADDRESS, FACTORY_PORTFOLIO_URL,
        FACTORY_PAYMENT_INSTRUCTIONS."""
        e = os.environ.get
        return cls(
            name=e("FACTORY_SENDER_NAME", ""), business_name=e("FACTORY_SENDER_BUSINESS", ""),
            email=e("FACTORY_SENDER_EMAIL", ""), website=e("FACTORY_SENDER_WEBSITE", ""),
            portfolio_url=e("FACTORY_PORTFOLIO_URL", ""), physical_address=e("FACTORY_SENDER_ADDRESS", ""),
            payment_instructions=e("FACTORY_PAYMENT_INSTRUCTIONS", ""),
        )


def _sender(sender: SenderProfile | dict | None) -> SenderProfile:
    if sender is None:
        return SenderProfile.from_env()
    return sender if isinstance(sender, SenderProfile) else SenderProfile.model_validate(sender)


def compliance_footer(sender: SenderProfile) -> str:
    """CAN-SPAM footer: identity, postal address, opt-out."""
    who = " | ".join(x for x in [sender.name or "[YOUR NAME]", sender.business_name, sender.website] if x)
    return f"--\n{who}\n{sender.physical_address or ADDRESS_PLACEHOLDER}\n{OPT_OUT_LINE}"


SYSTEM = (
    "You write short, honest cold emails for a one-person studio that makes AI-generated UGC-style video "
    "ads (spokesperson and product-demo style, clearly disclosed as AI). Rules: under 120 words; one "
    "specific, true observation about the prospect based only on the fields given (never invent facts "
    "about them); a concrete offer; one low-friction question as CTA; no fake urgency, no deceptive "
    "subject lines, no 'Re:' or 'Fwd:' tricks, no claims about results we can't prove. Do not add a "
    "signature or footer; it is appended automatically. follow_up is a 2-3 sentence polite nudge sent ~3 "
    "days later; don't call it the last email (one short final note follows ~4 days after it)."
)


def _prompt(client: dict, sender: SenderProfile) -> str:
    starter = PACKAGES["starter"]
    return f"""Prospect:
- Business: {client.get('name')}
- Contact: {client.get('contact_name') or 'unknown'}
- Website: {client.get('website') or 'n/a'}
- Niche: {client.get('niche') or 'n/a'}
- Notes: {(client.get('notes') or '')[-500:] or 'none'}

Sender: {sender.name or '[name]'} from {sender.business_name or 'an AI video studio'}
Portfolio: {sender.portfolio_url or 'available on request'}
Entry offer: {starter.name} - {starter.description} ${starter.price_cents / 100:.0f}.

Write the email."""


def _offline_pitch(client: dict, sender: SenderProfile) -> PitchEmail:
    first = (client.get("contact_name") or "").split(" ")[0] or "there"
    niche = f"{client['niche']} brands" if client.get("niche") else "brands like yours"
    name = client.get("name") or "your brand"
    starter = PACKAGES["starter"]
    body = (
        f"Hi {first},\n\n"
        f"I came across {name} while looking at {niche} and thought your products would suit short "
        f"demo-style video ads.\n\n"
        f"I make AI-presented UGC-style ads (clearly labelled as AI, spokesperson and product-demo format, no "
        f"fake reviews). The {starter.name} pack is {starter.videos} vertical ads for ${starter.price_cents / 100:.0f}, "
        f"ready for TikTok, Reels and Shorts.\n\n"
        f"{'Examples: ' + sender.portfolio_url + chr(10) + chr(10) if sender.portfolio_url else ''}"
        f"Would it be useful if I made one sample ad for one of your products so you can judge the quality?\n\n"
        f"Thanks,\n{sender.name or '[Your name]'}"
    )
    return PitchEmail(
        subject=f"Short video ads for {name}",
        body=body,
        follow_up=f"Hi {first}, just checking whether a free sample ad for {name} would be useful. "
                  f"Happy to make one for whichever product you'd like to test first.",
    )


def draft_pitch(llm, client: dict, sender_profile: SenderProfile | dict | None = None) -> PitchEmail:
    """Personalised cold email draft for one client row. Appends the compliance footer."""
    sender = _sender(sender_profile)
    email = llm.structured(PitchEmail, system=SYSTEM, prompt=_prompt(client, sender), purpose="pitch",
                           offline=lambda: _offline_pitch(client, sender))
    footer = compliance_footer(sender)
    body = email.body.rstrip()
    if footer not in body:
        body = f"{body}\n\n{footer}"
    follow = email.follow_up.rstrip()
    if OPT_OUT_LINE not in follow:
        follow = f"{follow}\n\n{footer}"
    return PitchEmail(subject=email.subject.strip(), body=body, follow_up=follow)


def save_pitch_draft(db: DB, client_id: int, pitch: PitchEmail) -> None:
    """Store a draft on the client (latest last)."""
    client = get_client(db, client_id)
    meta = client["meta"]
    meta.setdefault("pitch_drafts", []).append({**pitch.model_dump(), "created_at": now_iso(), "exported": False})
    db.update("clients", client_id, {"meta": meta})
    db.log("pitch.drafted", "client", client_id, {"subject": pitch.subject})


def latest_draft(client: dict) -> dict | None:
    meta = client.get("meta") if isinstance(client.get("meta"), dict) else {}
    drafts = meta.get("pitch_drafts") or []
    return drafts[-1] if drafts else None


def draft_all(db: DB, llm, sender: SenderProfile | dict | None = None, status: str = "lead",
              limit: int = 25) -> list[int]:
    """Draft pitches for clients in `status` that have an email and no draft yet."""
    done = []
    for client in db.query("SELECT * FROM clients WHERE status = ? AND email != '' ORDER BY id", [status]):
        meta = client.get("meta") or {}
        if meta.get("pitch_drafts") or meta.get("opted_out"):
            continue
        save_pitch_draft(db, client["id"], draft_pitch(llm, client, sender))
        done.append(client["id"])
        if len(done) >= limit:
            break
    return done


def mark_opt_out(db: DB, client_id: int) -> None:
    """Record an opt-out: excluded from exports and follow-ups from now on."""
    client = get_client(db, client_id)
    meta = client["meta"]
    meta["opted_out"] = now_iso()
    meta.pop("next_follow_up", None)
    _cancel_cadence(meta, "opted out")
    db.update("clients", client_id, {"meta": meta, "status": "lost" if client["status"] != "won" else "won"})
    db.log("client.opted_out", "client", client_id)


def export_drafts(db: DB, out_dir: Path | str, sender: SenderProfile | dict | None = None,
                  client_ids: list[int] | None = None, follow_ups: bool = False) -> dict:
    """Write the latest draft for each client as an .eml (X-Unsent so mail apps open
    it as a draft) plus `drafts.csv` for mail-merge. Skips opted-out clients."""
    s = _sender(sender)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, files = [], []
    clients = db.query("SELECT * FROM clients ORDER BY id")
    for client in clients:
        if client_ids and client["id"] not in client_ids:
            continue
        meta = client.get("meta") or {}
        draft = latest_draft(client)
        if not draft or meta.get("opted_out") or not client.get("email"):
            continue
        body = draft["follow_up"] if follow_ups else draft["body"]
        subject = draft["subject"]  # follow-ups go in the same thread; no fake "Re:" on first contact
        path = out / f"{client['id']:04d}-{slugify(client['name'], 40)}.eml"
        path.write_bytes(_eml(s, client, subject, body))
        files.append(str(path))
        rows.append({"client_id": client["id"], "name": client["name"], "contact_name": client["contact_name"],
                     "email": client["email"], "website": client["website"], "subject": subject, "body": body})
        draft["exported"] = now_iso()
        db.update("clients", client["id"], {"meta": meta})
    csv_path = out / "drafts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["client_id", "name", "contact_name", "email", "website",
                                                "subject", "body"])
        writer.writeheader()
        writer.writerows(rows)
    db.log("pitch.exported", "client", None, {"count": len(rows), "dir": str(out)})
    return {"eml": files, "csv": str(csv_path), "count": len(rows)}


def _eml(sender: SenderProfile, client: dict, subject: str, body: str) -> bytes:
    msg = EmailMessage()
    msg["From"] = formataddr((sender.name or sender.business_name, sender.email or "you@example.com"))
    msg["To"] = formataddr((client.get("contact_name") or client["name"], client["email"]))
    msg["Subject"] = subject
    msg["X-Unsent"] = "1"
    msg.set_content(body)
    return bytes(msg)


# --------------------------------------------------------------------------- lead import
LEAD_COLUMNS = {
    "name": ["name", "company", "business", "brand", "store", "company name"],
    "website": ["website", "url", "site", "domain", "homepage"],
    "email": ["email", "email address", "contact email", "e-mail"],
    "niche": ["niche", "category", "industry", "vertical"],
    "contact_name": ["contact_name", "contact", "contact name", "first name", "person"],
    "notes": ["notes", "note", "comment"],
}


def import_leads_csv(db: DB, source: str | Path | bytes, lead_source: str = "csv") -> dict:
    """Import leads (name, website, email, niche[, contact_name, notes]).

    Dedupes against existing clients by email and website domain. Rows with an
    invalid email are skipped; rows without email are kept (contact form leads)."""
    added, duplicates, errors = [], 0, []
    for i, row in enumerate(read_csv_rows(source, header_hints=["name", "email", "website"]), start=2):
        f = {k: pick(row, cols) for k, cols in LEAD_COLUMNS.items()}
        if not f["name"]:
            f["name"] = f["website"].split("//")[-1].split("/")[0] if f["website"] else ""
        if not f["name"]:
            errors.append(f"line {i}: no name or website")
            continue
        if f["email"] and not EMAIL_RE.match(f["email"]):
            errors.append(f"line {i}: invalid email {f['email']!r}")
            continue
        if find_client(db, email=f["email"], website=f["website"]):
            duplicates += 1
            continue
        added.append(add_client(db, f["name"], email=f["email"], website=f["website"], niche=f["niche"],
                                contact_name=f["contact_name"], notes=f["notes"], source=lead_source))
    return {"added": len(added), "ids": added, "duplicates": duplicates, "errors": errors}


# --------------------------------------------------------------------------- follow-up cadence
FOLLOW_UP_OFFSETS = (3, 7)          # days after the first email
CADENCE_STATUSES = {"lead", "contacted"}  # any other status (replied, negotiating, won, lost...) stops it


def _final_nudge(client: dict, sender: SenderProfile) -> str:
    first = (client.get("contact_name") or "").split(" ")[0] or "there"
    return (f"Hi {first},\n\nLast note from me on this. If short AI-presented video ads for "
            f"{client.get('name') or 'your products'} become useful later, just reply and I'll make you one free "
            f"sample ad to judge.\n\nThanks,\n{sender.name or '[Your name]'}")


def _with_footer(text: str, sender: SenderProfile) -> str:
    text = text.rstrip()
    return text if OPT_OUT_LINE in text else f"{text}\n\n{compliance_footer(sender)}"


def cadence_active(client: dict) -> bool:
    meta = client.get("meta") if isinstance(client.get("meta"), dict) else {}
    cad = meta.get("cadence") or {}
    return bool(cad) and not cad.get("stopped") and not meta.get("opted_out") \
        and client.get("status") in CADENCE_STATUSES


def mark_pitch_sent(db: DB, client_id: int, sent_on: str | None = None,
                    sender: SenderProfile | dict | None = None) -> dict:
    """Record that YOU sent the first email (nothing is sent from here) and schedule
    follow-up drafts at +3 and +7 days. Moves a lead to 'contacted'. Returns the cadence."""
    from ._util import add_days, today
    from .ugc import set_client_status
    s = _sender(sender)
    client = get_client(db, client_id)
    meta = client["meta"]
    if meta.get("opted_out"):
        raise ValueError(f"Client #{client_id} opted out; don't email them")
    draft = latest_draft(client)
    if not draft:
        raise ValueError(f"Client #{client_id} has no pitch draft yet; draft one first")
    day0 = sent_on or today().isoformat()
    draft["sent_at"] = day0
    bodies = [_with_footer(draft.get("follow_up") or "", s) if draft.get("follow_up") else None,
              _with_footer(_final_nudge(client, s), s)]
    steps = [{"n": i + 1, "due": add_days(day0, off), "subject": draft["subject"],
              "body": bodies[i] or _with_footer(_final_nudge(client, s), s), "status": "pending"}
             for i, off in enumerate(FOLLOW_UP_OFFSETS)]
    meta["cadence"] = {"sent_at": day0, "subject": draft["subject"], "steps": steps}
    meta["next_follow_up"] = steps[0]["due"]
    db.update("clients", client_id, {"meta": meta})
    if client["status"] == "lead":
        set_client_status(db, client_id, "contacted", note="First pitch sent", follow_up=steps[0]["due"])
    db.log("pitch.sent", "client", client_id, {"on": day0, "follow_ups": [x["due"] for x in steps]})
    return meta["cadence"]


def _cancel_cadence(meta: dict, reason: str) -> bool:
    """Stop a cadence in a client's meta dict (caller saves). True if it was running."""
    cad = meta.get("cadence")
    if not cad or cad.get("stopped"):
        return False
    cad["stopped"] = reason
    for st in cad.get("steps", []):
        if st["status"] == "pending":
            st["status"] = "cancelled"
    return True


def stop_cadence(db: DB, client_id: int, reason: str) -> None:
    client = get_client(db, client_id)
    if _cancel_cadence(client["meta"], reason):
        db.update("clients", client_id, {"meta": client["meta"]})
        db.log("pitch.cadence_stopped", "client", client_id, {"reason": reason})


def mark_follow_up_sent(db: DB, client_id: int, step: int | None = None, sent_on: str | None = None) -> dict:
    """Record that you sent the next (or a given) follow-up. Returns that step."""
    from ._util import today
    client = get_client(db, client_id)
    meta = client["meta"]
    cad = meta.get("cadence")
    if not cad or not cadence_active(client):
        raise ValueError(f"Client #{client_id} has no active follow-up cadence")
    pending = [s for s in cad["steps"] if s["status"] == "pending" and (step is None or s["n"] == step)]
    if not pending:
        raise ValueError(f"No pending follow-up{f' #{step}' if step else ''} for client #{client_id}")
    current = pending[0]
    current.update(status="sent", sent_at=sent_on or today().isoformat())
    nxt = [s for s in cad["steps"] if s["status"] == "pending"]
    if nxt:
        meta["next_follow_up"] = nxt[0]["due"]
    else:
        cad["stopped"] = "completed"
        meta.pop("next_follow_up", None)
    db.update("clients", client_id, {"meta": meta})
    db.log("pitch.follow_up_sent", "client", client_id, {"step": current["n"]})
    return current


def mark_sent(db: DB, client_id: int, sent_on: str | None = None) -> dict:
    """One button for 'I sent the next email': the first pitch if it hasn't gone
    out yet, otherwise the next pending follow-up."""
    client = get_client(db, client_id)
    cad = client["meta"].get("cadence")
    if not cad:
        return {"kind": "pitch", "cadence": mark_pitch_sent(db, client_id, sent_on)}
    return {"kind": "follow_up", "step": mark_follow_up_sent(db, client_id, sent_on=sent_on)}


def outreach_today(db: DB, on: str | None = None) -> dict:
    """What to send today (drafts only; you send them yourself):

    - follow_ups: cadence steps due on or before today, for clients still in
      lead/contacted and not opted out (one step per client: the earliest).
    - first_touch: leads with an email and an unsent pitch draft.
    - to_draft: leads with an email and no draft yet.
    """
    from ._util import today
    day = on or today().isoformat()
    follow_ups, first_touch, to_draft = [], [], []
    for client in db.query("SELECT * FROM clients ORDER BY id"):
        meta = client.get("meta") if isinstance(client.get("meta"), dict) else {}
        client["meta"] = meta
        if meta.get("opted_out") or not client.get("email"):
            continue
        cad = meta.get("cadence")
        if cad:
            if cadence_active(client):
                due = [s for s in cad["steps"] if s["status"] == "pending" and s["due"] <= day]
                if due:
                    st = due[0]
                    follow_ups.append({"client": client, "step": st["n"], "due": st["due"], "subject": st["subject"],
                                       "body": st["body"], "days_late": _days_between(st["due"], day)})
            continue
        if client["status"] != "lead":
            continue
        draft = latest_draft(client)
        if draft and not draft.get("sent_at"):
            first_touch.append({"client": client, "subject": draft["subject"], "body": draft["body"]})
        elif not draft:
            to_draft.append({"client": client})
    return {"date": day, "follow_ups": follow_ups, "first_touch": first_touch, "to_draft": to_draft,
            "count": len(follow_ups) + len(first_touch)}


def _days_between(a: str, b: str) -> int:
    from datetime import date
    return (date.fromisoformat(b) - date.fromisoformat(a)).days


def export_today(db: DB, out_dir: Path | str, sender: SenderProfile | dict | None = None,
                 on: str | None = None) -> dict:
    """Write today's emails (first pitches + due follow-ups) as .eml drafts and a CSV."""
    s = _sender(sender)
    plan = outreach_today(db, on)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows, files = [], []
    items = [("pitch", x) for x in plan["first_touch"]] + [(f"followup{x['step']}", x) for x in plan["follow_ups"]]
    for kind, item in items:
        c = item["client"]
        path = out / f"{c['id']:04d}-{slugify(c['name'], 40)}-{kind}.eml"
        path.write_bytes(_eml(s, c, item["subject"], item["body"]))
        files.append(str(path))
        rows.append({"client_id": c["id"], "name": c["name"], "email": c["email"], "kind": kind,
                     "subject": item["subject"], "body": item["body"]})
    csv_path = out / "today.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["client_id", "name", "email", "kind", "subject", "body"])
        writer.writeheader()
        writer.writerows(rows)
    return {"eml": files, "csv": str(csv_path), "count": len(rows)}
