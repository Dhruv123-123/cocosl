"""AI UGC ad videos for brands: packages, client CRM, orders and ad scripts.

Ads are spokesperson/demo style. The AI presenter may demonstrate, explain and
pitch a product, but never claims to have used it or to have personal results:
that would be a fake consumer review under the FTC rule (16 CFR Part 465).
Every script is checked against `guardrails.TESTIMONIAL_PATTERNS`; a failing
script gets one revision pass and otherwise raises `TestimonialError`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from pydantic import BaseModel, Field

from ..config import BrandProfile, VisualStyle
from ..db import DB, now_iso
from ..guardrails import HYPE_PATTERNS, TESTIMONIAL_PATTERNS, Check, check_patterns
from ..schemas import AdScript, Segment
from ._util import add_days, slugify, today


# --------------------------------------------------------------------------- packages
@dataclass(frozen=True)
class Package:
    key: str
    name: str
    price_cents: int
    videos: int
    hooks_per_video: int
    revisions: int
    turnaround_days: int
    usage_days: int          # organic usage licence included
    recurring: bool = False  # billed monthly
    description: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class AddOn:
    key: str
    name: str
    price_cents: int = 0      # flat price
    per_video: bool = False   # multiply by the package's video count
    percent: int = 0          # % of package price (rush fee)

    def as_dict(self) -> dict:
        return asdict(self)


PACKAGES: dict[str, Package] = {
    "starter": Package("starter", "Starter", 24_900, videos=4, hooks_per_video=1, revisions=1,
                       turnaround_days=7, usage_days=30,
                       description="4 AI spokesperson/demo ads (15-30s, 9:16), 1 hook each, captions, 1 revision round."),
    "growth": Package("growth", "Growth", 44_900, videos=8, hooks_per_video=3, revisions=2,
                      turnaround_days=10, usage_days=90,
                      description="8 ads with 3 hook variations each for A/B testing, captions, 2 revision rounds."),
    "retainer": Package("retainer", "Monthly Retainer", 79_900, videos=12, hooks_per_video=3, revisions=2,
                        turnaround_days=30, usage_days=180, recurring=True,
                        description="12 ads per month, 3 hooks each, monthly creative report and refreshes."),
}

ADDONS: dict[str, AddOn] = {
    "paid_usage_90d": AddOn("paid_usage_90d", "Paid-ads usage rights (90 days)", 10_000),
    "paid_usage_12m": AddOn("paid_usage_12m", "Paid-ads usage rights (12 months)", 40_000),
    "perpetual_usage": AddOn("perpetual_usage", "Perpetual usage rights, all channels", 75_000),
    "extra_hook": AddOn("extra_hook", "Extra hook variation (per video)", 2_500, per_video=True),
    "raw_files": AddOn("raw_files", "Raw project files and stems", 7_500),
    "subtitles_translation": AddOn("subtitles_translation", "Translated subtitles, 1 language (per video)",
                                   1_500, per_video=True),
    "rush": AddOn("rush", "Rush delivery (48 hours)", 7_500),
}


def quote(package: str, addons: list[str] | tuple[str, ...] = (), rush: bool = False,
          discount_pct: float = 0) -> dict:
    """Price a package with add-ons. Returns line items in invoice format
    ({description, qty, unit_cents, amount_cents}) and a total."""
    if package not in PACKAGES:
        raise KeyError(f"Unknown package '{package}'. Options: {', '.join(PACKAGES)}")
    pkg = PACKAGES[package]
    keys = [a for a in addons if a != "rush"] + (["rush"] if rush or "rush" in addons else [])
    items = [_item(f"{pkg.name} package: {pkg.description}", 1, pkg.price_cents)]
    for key in keys:
        if key not in ADDONS:
            raise KeyError(f"Unknown add-on '{key}'. Options: {', '.join(ADDONS)}")
        add = ADDONS[key]
        if add.percent:
            items.append(_item(f"{add.name} ({add.percent}%)", 1, pkg.price_cents * add.percent // 100))
        elif add.per_video:
            items.append(_item(add.name, pkg.videos, add.price_cents))
        else:
            items.append(_item(add.name, 1, add.price_cents))
    if discount_pct:
        subtotal = sum(i["amount_cents"] for i in items)
        items.append(_item(f"Discount ({discount_pct:g}%)", 1, -round(subtotal * discount_pct / 100)))
    turnaround = pkg.turnaround_days // 2 if "rush" in keys else pkg.turnaround_days
    return {"package": pkg.key, "addons": keys, "items": items,
            "total_cents": sum(i["amount_cents"] for i in items), "turnaround_days": max(1, turnaround)}


def _item(description: str, qty: int, unit_cents: int) -> dict:
    return {"description": description, "qty": qty, "unit_cents": unit_cents, "amount_cents": qty * unit_cents}


# --------------------------------------------------------------------------- clients CRM
CLIENT_STATUSES = ["lead", "contacted", "replied", "negotiating", "won", "lost", "churned"]
OPEN_STATUSES = {"lead", "contacted", "replied", "negotiating"}
FOLLOW_UP_DAYS = {"lead": 0, "contacted": 4, "replied": 2, "negotiating": 3}


def find_client(db: DB, email: str = "", website: str = "", name: str = "") -> dict | None:
    """Match an existing client by email, then website domain, then exact name."""
    if email:
        row = db.one("SELECT * FROM clients WHERE lower(email) = ?", [email.strip().lower()])
        if row:
            return row
    domain = _domain(website)
    if domain:
        for row in db.query("SELECT * FROM clients WHERE website != ''"):
            if _domain(row["website"]) == domain:
                return row
    if name:
        return db.one("SELECT * FROM clients WHERE lower(name) = ?", [name.strip().lower()])
    return None


def _domain(url: str) -> str:
    url = (url or "").strip().lower()
    for prefix in ("https://", "http://"):
        url = url.removeprefix(prefix)
    return url.removeprefix("www.").split("/")[0]


def add_client(db: DB, name: str, *, email: str = "", website: str = "", niche: str = "",
               contact_name: str = "", source: str = "manual", notes: str = "",
               status: str = "lead") -> int:
    """Create a client (or return the id of an existing match by email/website)."""
    if not name.strip():
        raise ValueError("Client name is required")
    if status not in CLIENT_STATUSES:
        raise ValueError(f"Unknown status '{status}'")
    existing = find_client(db, email=email, website=website)
    if existing:
        return existing["id"]
    cid = db.insert("clients", {
        "name": name.strip(), "email": email.strip(), "website": website.strip(), "niche": niche.strip(),
        "contact_name": contact_name.strip(), "source": source, "status": status,
        "notes": _stamp(notes) if notes else "",
        "meta": {"history": [{"status": status, "at": now_iso()}], "next_follow_up": today().isoformat()},
    })
    db.log("client.added", "client", cid, {"name": name, "source": source})
    return cid


def get_client(db: DB, client_id: int) -> dict:
    row = db.get("clients", client_id)
    if not row:
        raise KeyError(f"No client #{client_id}")
    row["meta"] = row.get("meta") if isinstance(row.get("meta"), dict) else {}
    return row


def update_client(db: DB, client_id: int, **fields: Any) -> None:
    """Edit plain client fields (name, email, website, niche, contact_name, source)."""
    allowed = {"name", "email", "website", "niche", "contact_name", "source"}
    changes = {k: v for k, v in fields.items() if k in allowed and v is not None}
    if changes:
        db.update("clients", client_id, changes)
        db.log("client.updated", "client", client_id, {"fields": list(changes)})


def set_client_status(db: DB, client_id: int, status: str, note: str = "",
                      follow_up: str | None = None, actor: str = "human") -> None:
    """Move a client through the pipeline. Open stages get a default follow-up date."""
    if status not in CLIENT_STATUSES:
        raise ValueError(f"Unknown status '{status}'. Options: {', '.join(CLIENT_STATUSES)}")
    client = get_client(db, client_id)
    meta = client["meta"]
    meta.setdefault("history", []).append({"status": status, "at": now_iso(), "from": client["status"]})
    if follow_up:
        meta["next_follow_up"] = follow_up
    elif status in OPEN_STATUSES:
        meta["next_follow_up"] = add_days(today(), FOLLOW_UP_DAYS[status])
    else:
        meta.pop("next_follow_up", None)
    cad = meta.get("cadence")
    if cad and not cad.get("stopped") and status not in ("lead", "contacted"):
        cad["stopped"] = f"status: {status}"  # replied / negotiating / won / lost: no more automatic nudges
        for st in cad.get("steps", []):
            if st.get("status") == "pending":
                st["status"] = "cancelled"
    changes: dict[str, Any] = {"status": status, "meta": meta}
    if note:
        changes["notes"] = _append_note(client["notes"], f"[{status}] {note}")
    db.update("clients", client_id, changes)
    db.log("client.status", "client", client_id, {"from": client["status"], "to": status}, actor=actor)


def add_note(db: DB, client_id: int, text: str) -> None:
    client = get_client(db, client_id)
    db.update("clients", client_id, {"notes": _append_note(client["notes"], text)})


def set_follow_up(db: DB, client_id: int, when: str | None) -> None:
    """Set (YYYY-MM-DD) or clear (None/'') the next follow-up date."""
    client = get_client(db, client_id)
    meta = client["meta"]
    if when:
        meta["next_follow_up"] = when
    else:
        meta.pop("next_follow_up", None)
    db.update("clients", client_id, {"meta": meta})


def due_follow_ups(db: DB, on: str | None = None) -> list[dict]:
    """Open clients whose next follow-up date is today or earlier."""
    cutoff = on or today().isoformat()
    out = []
    for row in db.query("SELECT * FROM clients ORDER BY id"):
        meta = row.get("meta") if isinstance(row.get("meta"), dict) else {}
        nxt = meta.get("next_follow_up")
        if row["status"] in OPEN_STATUSES and nxt and nxt <= cutoff and not meta.get("opted_out"):
            out.append(row)
    return out


def pipeline(db: DB) -> dict[str, list[dict]]:
    """Clients grouped by status, in pipeline order."""
    board: dict[str, list[dict]] = {s: [] for s in CLIENT_STATUSES}
    for row in db.query("SELECT * FROM clients ORDER BY updated_at DESC"):
        board.setdefault(row["status"], []).append(row)
    return board


def _stamp(text: str) -> str:
    return f"[{today().isoformat()}] {text.strip()}"


def _append_note(existing: str, text: str) -> str:
    return "\n".join(x for x in [(existing or "").rstrip(), _stamp(text)] if x)


# --------------------------------------------------------------------------- orders
ORDER_STATUSES = ["brief", "in_production", "delivered", "revision", "paid", "cancelled"]
ORDER_FLOW = {
    "brief": {"in_production", "cancelled"},
    "in_production": {"delivered", "cancelled"},
    "delivered": {"revision", "paid"},
    "revision": {"delivered", "cancelled"},
    "paid": set(),
    "cancelled": set(),
}


def create_order(db: DB, client_id: int, package: str, *, addons: list[str] | tuple[str, ...] = (),
                 rush: bool = False, brief: dict | None = None, due_date: str | None = None,
                 discount_pct: float = 0) -> int:
    """Create an order priced from a package quote. The quote is kept in brief['quote']."""
    get_client(db, client_id)
    q = quote(package, addons, rush=rush, discount_pct=discount_pct)
    oid = db.insert("orders", {
        "client_id": client_id, "package": package, "price_cents": q["total_cents"], "status": "brief",
        "brief": {**(brief or {}), "quote": q}, "deliverables": [],
        "due_date": due_date or add_days(today(), q["turnaround_days"]),
    })
    db.log("order.created", "order", oid, {"client": client_id, "package": package, "total": q["total_cents"]})
    from .onboarding import setup_order  # questionnaire state + delivery checklist
    setup_order(db, oid)
    return oid


def get_order(db: DB, order_id: int) -> dict:
    row = db.get("orders", order_id)
    if not row:
        raise KeyError(f"No order #{order_id}")
    return row


def set_order_status(db: DB, order_id: int, status: str, force: bool = False, actor: str = "human") -> None:
    """Advance an order: brief -> in_production -> delivered -> (revision -> delivered) -> paid.

    'paid' goes through `invoices.mark_order_paid`, which records revenue exactly once."""
    if status not in ORDER_STATUSES:
        raise ValueError(f"Unknown order status '{status}'")
    order = get_order(db, order_id)
    if not force and status != order["status"] and status not in ORDER_FLOW[order["status"]]:
        allowed = ", ".join(sorted(ORDER_FLOW[order["status"]])) or "none"
        raise ValueError(f"Order #{order_id} is '{order['status']}'; next can be: {allowed}")
    if status == "paid":
        from .invoices import mark_order_paid
        mark_order_paid(db, order_id)
        return
    db.update("orders", order_id, {"status": status})
    db.log("order.status", "order", order_id, {"from": order["status"], "to": status}, actor=actor)


def add_deliverable(db: DB, order_id: int, item: str | int, kind: str = "video", note: str = "") -> None:
    """Attach a deliverable: a file path (relative to output_dir) or a post id."""
    order = get_order(db, order_id)
    items = list(order.get("deliverables") or [])
    entry = {"kind": kind, "note": note, "added_at": now_iso()}
    entry["post_id" if isinstance(item, int) else "path"] = item
    items.append(entry)
    db.update("orders", order_id, {"deliverables": items})


def orders(db: DB, status: str | None = None, client_id: int | None = None) -> list[dict]:
    sql = "SELECT o.*, c.name AS client_name FROM orders o JOIN clients c ON c.id = o.client_id WHERE 1=1"
    params: list = []
    if status:
        sql += " AND o.status = ?"
        params.append(status)
    if client_id:
        sql += " AND o.client_id = ?"
        params.append(client_id)
    return db.query(sql + " ORDER BY o.id DESC", params)


# --------------------------------------------------------------------------- ad scripts
class AdBrief(BaseModel):
    """What a client tells us about the ad. Only `product` is required."""
    product: str
    brand_name: str = ""
    audience: str = ""
    benefits: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)
    offer: str = ""
    cta: str = ""
    tone: str = "energetic, clear, friendly"
    style: str = "spokesperson"          # spokesperson | demo | explainer
    duration_s: int = 25
    approved_claims: list[str] = Field(default_factory=list)  # claims the client can substantiate
    notes: str = ""


class TestimonialError(ValueError):
    """The ad script still contains first-person testimonial language."""


AD_SYSTEM = (
    "You write short-form UGC-style video ads that an AI-generated presenter or voiceover delivers as a "
    "SPOKESPERSON or product DEMO. Hard rules: the presenter may show, demonstrate, explain and recommend "
    "the product, but must NEVER claim to be a customer, to have used, tried, bought or tested it, or to "
    "have personal results or experiences with it (no 'I've been using', 'changed my life', 'my skin', "
    "'I lost 10 lbs'). That would be a fake testimonial (FTC 16 CFR Part 465). Speak in second person "
    "('you') or about the product ('it', 'this'). Use only the claims the client provided; no guarantees, "
    "no medical or income promises. Visual prompts describe original scenes, product close-ups and hands "
    "demonstrating the product; no real people's likeness, no third-party logos. Keep on-screen text under "
    "8 words. Always include an on-screen disclosure that the presenter is AI-generated."
)


def _as_brief(brief: AdBrief | dict) -> AdBrief:
    return brief if isinstance(brief, AdBrief) else AdBrief.model_validate(brief)


def _ad_prompt(b: AdBrief) -> str:
    return f"""Write a {b.duration_s}-second {b.style} ad (vertical 9:16, 4-6 beats).
Product: {b.product}
Brand: {b.brand_name or 'n/a'}
Audience: {b.audience or 'general'}
Benefits: {'; '.join(b.benefits) or 'n/a'}
Features: {'; '.join(b.features) or 'n/a'}
Offer: {b.offer or 'none'}
CTA: {b.cta or 'Shop now'}
Tone: {b.tone}
Claims the client can substantiate (use only these): {'; '.join(b.approved_claims) or 'none: describe features only'}
Notes: {b.notes or 'none'}

Give 3 alternative hooks in `variations`. on_screen_disclosure must say the presenter is AI-generated
and that this is an ad."""


def _offline_ad(b: AdBrief) -> AdScript:
    """Template ad used without an LLM. The beat structure follows `b.style`
    (spokesperson, demo, or offer/explainer) so concepts for one product differ."""
    name = b.product
    who = b.audience or "anyone short on time"
    benefits = b.benefits or ["a simpler routine"]
    feature = (b.features or [f"a clean design built for {b.audience or 'everyday use'}"])[0]
    cta = b.cta or "Tap the link to shop"
    style = (b.style or "spokesperson").lower()
    if style == "demo":
        concept = f"Hands-on demo of {name}: one problem, solved on camera step by step."
        beats = [
            ("Hook", f"Watch what {name} does.", "Watch this",
             f"{name} centred on a plain surface, hands entering frame"),
            ("Step 1", f"Step one: {feature}.", feature[:60], f"hands showing the first step with {name}"),
            ("Step 2", f"Step two: {benefits[0]}.", benefits[0][:60], f"close-up of {name} in use"),
            ("Result", f"That's {name}, start to finish.", "Start to finish", f"{name} after use, tidy setting"),
            ("CTA", f"{b.offer + '. ' if b.offer else ''}{cta}.", cta[:60], f"{name} product shot with space for a button"),
        ]
        variations = [f"Here's {name} in two steps.", "There's an easier way to do this.",
                      f"Here's {name}, start to finish."]
    elif style in ("offer", "explainer", "promo"):
        offer = b.offer or f"{name} is available now"
        concept = f"Offer-led explainer for {name}: who it's for, what you get, and one clear offer."
        beats = [
            ("Hook", f"Quick one for {who}.", f"For {who}"[:60],
             f"bright lifestyle scene that suits {who}"),
            ("What it is", f"{name} is {feature}.", "What it is", f"{name} on a clean background"),
            ("Why it matters", f"Why it matters: {benefits[0]}.", benefits[0][:60], f"{name} in an everyday setting"),
            ("Offer", f"{offer}.", offer[:60], f"offer card next to {name}"),
            ("CTA", f"{cta}.", cta[:60], f"{name} with space for a button"),
        ]
        variations = [f"{offer}. Here's what you get.", f"Who {name} is for, in 15 seconds.",
                      f"Before you scroll past {name}, read this."]
    else:
        concept = f"Spokesperson demo for {name}: show the product solving one clear problem."
        beats = [
            ("Hook", f"Here's what {name} actually does.", f"Meet {name}"[:60],
             f"close-up of {name} on a clean bright surface"),
            ("Problem", f"If you're {b.audience or 'busy'}, you know the usual options take too long.",
             "The usual way is slow", "hands sorting through cluttered alternatives, soft daylight"),
            ("Demo", f"Watch: {name} gives you {feature}.", "See it in action",
             f"hands demonstrating {name}, step by step"),
            ("Benefit", f"The point is simple: {benefits[0]}.", benefits[0][:60],
             f"{name} in use in a tidy everyday setting"),
            ("CTA", f"{b.offer + '. ' if b.offer else ''}{cta}.", cta[:60],
             f"{name} product shot with empty space for a button"),
        ]
        variations = [f"Stop scrolling if you need {benefits[0]}.", f"This is {name}. Here's what it does.",
                      f"3 seconds to see why {name} works differently."]
    segs = [Segment(heading=h, narration=n, on_screen_text=o, visual_prompt=v) for h, n, o, v in beats]
    return AdScript(concept=concept, hook=segs[0].narration, segments=segs, cta=cta,
                    on_screen_disclosure=_default_disclosure(b), variations=variations)


def _default_disclosure(b: AdBrief) -> str:
    return f"AI-generated presenter. Paid ad{' for ' + b.brand_name if b.brand_name else ''}."


def ad_text(ad: AdScript) -> str:
    parts = [ad.concept, ad.hook, ad.cta, *ad.variations]
    for s in ad.segments:
        parts += [s.heading, s.narration, s.on_screen_text]
    return "\n".join(p for p in parts if p)


def check_ad_script(ad: AdScript) -> list[Check]:
    """Testimonial language blocks (AI presenter); hype claims warn."""
    text = ad_text(ad)
    return [
        check_patterns(text, TESTIMONIAL_PATTERNS, "fake_testimonial", "block", "First-person product claims"),
        check_patterns(text, HYPE_PATTERNS, "claims", "warn", "Risky claims"),
    ]


def _revise_prompt(b: AdBrief, ad: AdScript, problem: str) -> str:
    return f"""{_ad_prompt(b)}

The draft below FAILED the testimonial check: {problem}
Rewrite every line so the presenter speaks as a spokesperson or demonstrator (second person or about
the product), never as someone who used it. Keep the structure and the good ideas.

Draft:
{ad.model_dump_json(indent=2)}"""


def write_ad_script(llm, brief: AdBrief | dict, max_revisions: int = 1) -> AdScript:
    """Write a spokesperson/demo ad script and enforce the no-testimonial rule.

    Raises TestimonialError if the script still has first-person product claims
    after `max_revisions` revision passes."""
    b = _as_brief(brief)
    ad = llm.structured(AdScript, system=AD_SYSTEM, prompt=_ad_prompt(b), purpose="ugc:ad_script",
                        offline=lambda: _offline_ad(b))
    for attempt in range(max_revisions + 1):
        verdict = check_ad_script(ad)[0]
        if verdict.level == "ok":
            break
        if attempt == max_revisions:
            raise TestimonialError(f"Ad script failed the testimonial check after {max_revisions} revision(s): "
                                   f"{verdict.message}")
        ad = llm.structured(AdScript, system=AD_SYSTEM, prompt=_revise_prompt(b, ad, verdict.message),
                            purpose="ugc:ad_revise", offline=lambda: _offline_ad(b))
    if "ai" not in ad.on_screen_disclosure.lower():
        ad = ad.model_copy(update={"on_screen_disclosure": _default_disclosure(b)})
    return ad


# --------------------------------------------------------------------------- render handoff
def ad_brand_profile(brand_like: BrandProfile | dict | str) -> BrandProfile:
    """Build a BrandProfile for rendering a client's ad (from a profile, a client row/dict, or a name)."""
    if isinstance(brand_like, BrandProfile):
        return brand_like
    data = {"name": brand_like} if isinstance(brand_like, str) else dict(brand_like)
    name = data.get("name") or data.get("brand_name") or "Client"
    visual = data.get("visual") or {}
    if isinstance(data.get("palette"), list):
        visual = {**visual, "palette": data["palette"]}
    return BrandProfile(
        slug=data.get("slug") or "ugc-" + slugify(name, 40), name=name,
        niche=data.get("niche") or "product ads", audience=data.get("audience") or "shoppers",
        cta=data.get("cta") or "Shop now", hashtags=[],
        visual=VisualStyle(**visual) if isinstance(visual, dict) else visual,
        ai_disclosure=data.get("ai_disclosure") or "AI-generated presenter. Paid advertisement.",
        realistic_synthetic_media=bool(data.get("realistic_synthetic_media", True)),
        require_human_review=True,
    )


def render_ad(settings, brand_like: BrandProfile | dict | str, ad_script: AdScript,
              order_id: int | None = None, variation: int | None = None,
              output_subdir: str | None = None, headline_disclosure: bool = True) -> dict:
    """Build a post-like dict (format 'short') that `media.render_post` can render.

    `variation` swaps the hook for `ad_script.variations[variation]`. Nothing is
    rendered or stored here; see `render_ad_video` for the media call.
    `headline_disclosure=False` leaves the first headline alone: use it when the
    disclosure is shown for the whole ad another way (e.g. brand.visual.watermark)."""
    brand = ad_brand_profile(brand_like)
    hook = ad_script.variations[variation] if variation is not None else ad_script.hook
    segments = [s.model_dump() for s in ad_script.segments]
    if segments:
        segments[0]["narration"] = hook if variation is not None else segments[0]["narration"]
        if headline_disclosure:
            segments[0]["on_screen_text"] = f"{segments[0]['on_screen_text']} · {ad_script.on_screen_disclosure}"
    title = f"{brand.name} ad: {ad_script.concept[:60]}"
    script = {
        "title": title, "hook": hook, "segments": segments, "cta": ad_script.cta,
        "caption": f"{ad_script.cta}\n\n{ad_script.on_screen_disclosure}", "hashtags": ["ad"],
        "description": ad_script.concept, "thumbnail_text": " ".join(hook.split()[:4]),
        "sources": [], "claims_to_verify": ["Client must confirm every product claim in this ad"],
    }
    sub = output_subdir or (f"ugc/{brand.slug}/order-{order_id}" if order_id else f"ugc/{brand.slug}")
    return {
        "id": None, "brand": brand.slug, "format": "short", "status": "scripted", "title": title,
        "script": script, "caption": script["caption"], "hashtags": ["ad"],
        "disclosure": ad_script.on_screen_disclosure,
        "meta": {"ugc_ad": True, "ai_presenter": True, "sponsored": True, "order_id": order_id,
                 "variation": variation, "on_screen_disclosure": ad_script.on_screen_disclosure,
                 "variations": ad_script.variations, "output_subdir": sub,
                 "brand_profile": brand.model_dump()},
    }


def render_ad_video(settings, brand_like: BrandProfile | dict | str, ad_script: AdScript,
                    order_id: int | None = None, variation: int | None = None,
                    output_subdir: str | None = None, headline_disclosure: bool = True) -> dict:
    """Render the ad with the media module (imported lazily). Returns its assets dict."""
    from ..media import render_post
    post = render_ad(settings, brand_like, ad_script, order_id=order_id, variation=variation,
                     output_subdir=output_subdir, headline_disclosure=headline_disclosure)
    post["id"] = f"order{order_id or 0}-v{variation if variation is not None else 0}"
    return render_post(settings, ad_brand_profile(brand_like), post)
