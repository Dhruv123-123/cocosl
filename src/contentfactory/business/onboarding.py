"""Client onboarding for UGC orders: brief questionnaire + delivery checklist.

`ugc.create_order` calls `setup_order` automatically, which stores on the order
(orders.brief):
  questionnaire: {status: "waiting" | "complete", sent_at, completed_at}
  answers:       what the client told us (filled in at /business/orders/{id}/brief)
  checklist:     delivery steps from brief to final files, each {key, label, done}

Send the client the Markdown questionnaire (`questionnaire_markdown`) by email
or paste it into a shared doc; type their answers into the dashboard form.
The dashboard form is behind the dashboard login on purpose: it isn't a public
page clients can reach.
"""
from __future__ import annotations

from typing import Any

from ..db import DB, now_iso
from .ugc import ADDONS, PACKAGES, AdBrief, get_client, get_order

# kind: text | textarea | list (one item per line) | choice
QUESTIONS: list[dict[str, Any]] = [
    {"key": "product", "label": "Which product(s) should the ads feature?", "kind": "textarea", "required": True,
     "help": "Name and link for each. One per line."},
    {"key": "audience", "label": "Who buys it?", "kind": "textarea", "required": True,
     "help": "Age range, situation, what they care about. e.g. 'new runners training for a first 10k'."},
    {"key": "problem", "label": "What problem does it solve for them?", "kind": "textarea", "required": True,
     "help": "In their words if you can."},
    {"key": "features", "label": "Key features", "kind": "list", "required": True,
     "help": "Facts about the product: size, materials, what it does. One per line."},
    {"key": "approved_claims", "label": "Claims you can back up", "kind": "list", "required": True,
     "help": "Only claims you have evidence for (tests, certifications, data). We script nothing else. "
             "No health cures, guaranteed results or income claims."},
    {"key": "offer", "label": "Offer or promotion (optional)", "kind": "text", "required": False,
     "help": "e.g. '15% off first order with code HELLO15', valid dates."},
    {"key": "cta", "label": "Call to action", "kind": "text", "required": True,
     "help": "e.g. 'Shop now', 'Book a class', 'Get yours at brand.com'."},
    {"key": "tone", "label": "Tone and words to avoid", "kind": "textarea", "required": False,
     "help": "e.g. 'calm, expert, no slang; never say cheap'."},
    {"key": "assets", "label": "Footage and photos", "kind": "textarea", "required": True,
     "help": "Link to a folder of product photos or short phone clips (unboxing, in use, close-ups). "
             "You confirm you own them or have the rights."},
    {"key": "brand_assets", "label": "Logo, colours, fonts", "kind": "textarea", "required": False,
     "help": "Link or hex codes."},
    {"key": "platforms", "label": "Where will the ads run?", "kind": "text", "required": True,
     "help": "TikTok, Instagram Reels, YouTube Shorts, Facebook. Organic, paid, or both."},
    {"key": "presenter", "label": "Presenter preference", "kind": "choice", "required": True,
     "options": ["AI presenter on camera", "AI voiceover only (product footage)", "Mix", "No preference"],
     "help": "Either way the ad carries an on-screen 'AI-generated' label."},
    {"key": "references", "label": "Ads you like (optional)", "kind": "textarea", "required": False,
     "help": "Links to ads you like, and what you like about them. For style only; we never copy."},
    {"key": "approver", "label": "Who approves scripts and final files?", "kind": "text", "required": True,
     "help": "Name and email."},
]

ACKNOWLEDGEMENTS = [
    ("ai_label", "I understand the ads use AI-generated presenters/voices and will carry an on-screen AI label."),
    ("no_testimonials", "I understand presenters speak as spokespeople and never claim to have used the product."),
    ("rights", "I own, or have the rights to, every photo, clip, logo and claim I provide."),
]


def _qmap() -> dict[str, dict]:
    return {q["key"]: q for q in QUESTIONS}


# --------------------------------------------------------------------------- questionnaire
def questionnaire_markdown(order: dict, client: dict, sender_name: str = "") -> str:
    """Plain-text questionnaire to email the client (they reply inline)."""
    pkg = PACKAGES.get(order["package"])
    lines = [
        f"# Ad brief for {client['name']}",
        "",
        f"Order #{order['id']} · {pkg.name if pkg else order['package']} package"
        + (f" · {pkg.videos} ads, {pkg.hooks_per_video} hook(s) each" if pkg else ""),
        "",
        "Thanks for booking. Please answer below (reply to this email is fine) so we can write your scripts. "
        "It takes about 10 minutes. You'll approve every script before anything is produced.",
        "",
    ]
    for i, q in enumerate(QUESTIONS, 1):
        req = "" if q["required"] else " (optional)"
        label = q["label"].replace(" (optional)", "")
        lines += [f"## {i}. {label}{req}", f"_{q['help']}_", ""]
        if q["kind"] == "choice":
            lines += [f"- [ ] {o}" for o in q["options"]] + [""]
        else:
            lines += ["> ", ""]
    lines += ["## Please confirm", ""] + [f"- [ ] {text}" for _, text in ACKNOWLEDGEMENTS] + [""]
    if sender_name:
        lines += [f"Thanks,\n{sender_name}", ""]
    return "\n".join(lines)


def save_answers(db: DB, order_id: int, answers: dict[str, Any], acknowledgements: list[str] | None = None) -> dict:
    """Store the client's answers. Returns {missing: [...], complete: bool}.

    List questions accept a list or newline-separated text. The questionnaire is
    complete when every required answer and every acknowledgement is present."""
    order = get_order(db, order_id)
    brief = dict(order.get("brief") or {})
    qmap = _qmap()
    clean: dict[str, Any] = {}
    for key, value in answers.items():
        q = qmap.get(key)
        if not q:
            continue
        if q["kind"] == "list":
            items = value if isinstance(value, list) else str(value or "").splitlines()
            clean[key] = [str(x).strip(" -•\t") for x in items if str(x).strip(" -•\t")]
        else:
            clean[key] = str(value or "").strip()
    acks = [a for a in (acknowledgements or []) if a in dict(ACKNOWLEDGEMENTS)]
    missing = [q["key"] for q in QUESTIONS if q["required"] and not clean.get(q["key"])]
    missing += [f"ack:{k}" for k, _ in ACKNOWLEDGEMENTS if k not in acks]
    complete = not missing
    q_state = dict(brief.get("questionnaire") or {})
    q_state.update(status="complete" if complete else "waiting", updated_at=now_iso())
    if complete:
        q_state.setdefault("completed_at", now_iso())
    brief.update(answers=clean, acknowledgements=acks, questionnaire=q_state)
    if clean.get("product") and not brief.get("product"):
        brief["product"] = clean["product"].splitlines()[0]
    if complete:
        brief["checklist"] = _tick(brief.get("checklist") or [], "brief")
    db.update("orders", order_id, {"brief": brief})
    db.log("order.brief_saved", "order", order_id, {"complete": complete, "missing": missing})
    return {"missing": missing, "complete": complete}


def ad_brief_from_answers(db: DB, order_id: int, product: str | None = None) -> AdBrief:
    """Turn the questionnaire answers into an AdBrief for `ugc.write_ad_script`."""
    order = get_order(db, order_id)
    client = get_client(db, order["client_id"])
    a = (order.get("brief") or {}).get("answers") or {}
    style = {"AI voiceover only (product footage)": "demo"}.get(a.get("presenter", ""), "spokesperson")
    listed = [line.strip() for line in (a.get("product") or "").splitlines() if line.strip()]
    name = product or (listed[0] if listed else "") or (order.get("brief") or {}).get("product") or client["name"]
    return AdBrief(product=name, brand_name=client["name"], audience=a.get("audience", ""),
                   features=a.get("features") or [], approved_claims=a.get("approved_claims") or [],
                   benefits=[a["problem"]] if a.get("problem") else [], offer=a.get("offer", ""),
                   cta=a.get("cta", ""), tone=a.get("tone") or "energetic, clear, friendly", style=style,
                   notes=a.get("references", ""))


# --------------------------------------------------------------------------- delivery checklist
def delivery_checklist(order: dict) -> list[dict]:
    """Steps from booking to final files, sized to the order's package and add-ons."""
    pkg = PACKAGES.get(order["package"])
    quote = (order.get("brief") or {}).get("quote") or {}
    addons = quote.get("addons") or []
    videos = pkg.videos if pkg else 1
    hooks = pkg.hooks_per_video if pkg else 1
    items = [
        ("deposit", "Deposit (50%) invoice paid" if not (pkg and pkg.recurring) else "Month's invoice paid"),
        ("brief", "Brief questionnaire complete, incl. AI-label and rights acknowledgements"),
        ("assets", "Client photos/footage received and rights confirmed"),
        ("claims", "Every product claim matches the client's approved list (no extras)"),
        ("scripts", f"{videos} scripts × {hooks} hook(s) written and passed the testimonial check"),
        ("scripts_approved", "Scripts approved in writing by the client's approver"),
        ("produce", f"{videos * hooks} files produced: 1080×1920 MP4, captions checked for typos"),
        ("label", "On-screen 'AI-generated' label visible for the full length of every file"),
        ("likeness", "No real person's face or voice (unless a signed licence is on file)"),
        ("music", "Music and any stock footage licensed for ads; sources noted in the project folder"),
        ("names", "Files named brand_product_hookA_v1.mp4 and organised by hook"),
        ("preview", "Watermarked previews sent"),
    ]
    if "subtitles_translation" in addons:
        items.append(("translation", "Translated subtitle files checked by a fluent speaker"))
    if "raw_files" in addons:
        items.append(("raw", "Raw project files and stems packaged"))
    if pkg and pkg.recurring:
        items.append(("report", "Monthly creative report and next month's plan sent"))
    items += [
        ("revisions", f"Revisions done ({pkg.revisions if pkg else 1} round(s) included)"),
        ("balance", "Balance invoice paid" if not (pkg and pkg.recurring) else "Next month invoiced"),
        ("final", "Final un-watermarked files delivered, with posting notes: switch on the platform AI label"),
        ("usage", "Usage-rights end date recorded"
                  + (f" ({', '.join(ADDONS[a].name for a in addons if a.startswith(('paid_usage', 'perpetual')))})"
                     if any(a.startswith(("paid_usage", "perpetual")) for a in addons) else "")),
    ]
    return [{"key": k, "label": label, "done": False} for k, label in items]


def _tick(items: list[dict], key: str, done: bool = True) -> list[dict]:
    return [{**i, "done": done, **({"done_at": now_iso()} if done else {})} if i["key"] == key else i for i in items]


def set_check(db: DB, order_id: int, key: str, done: bool = True) -> None:
    order = get_order(db, order_id)
    brief = dict(order.get("brief") or {})
    items = brief.get("checklist") or delivery_checklist(order)
    if key not in {i["key"] for i in items}:
        raise KeyError(f"No checklist item '{key}'")
    brief["checklist"] = _tick(items, key, done)
    db.update("orders", order_id, {"brief": brief})


def progress(order: dict) -> dict:
    items = (order.get("brief") or {}).get("checklist") or []
    done = sum(1 for i in items if i.get("done"))
    return {"done": done, "total": len(items), "pct": round(100 * done / len(items)) if items else 0}


# --------------------------------------------------------------------------- setup
def setup_order(db: DB, order_id: int) -> dict:
    """Attach the questionnaire state and delivery checklist to a new order (idempotent)."""
    order = get_order(db, order_id)
    brief = dict(order.get("brief") or {})
    changed = False
    if not brief.get("questionnaire"):
        brief["questionnaire"] = {"status": "waiting", "created_at": now_iso()}
        changed = True
    if not brief.get("checklist"):
        brief["checklist"] = delivery_checklist(order)
        changed = True
    if changed:
        db.update("orders", order_id, {"brief": brief})
        db.log("order.onboarding", "order", order_id, {"checklist": len(brief["checklist"])})
    return brief
