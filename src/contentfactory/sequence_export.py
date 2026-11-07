"""`factory sequence-export <brand> --for sender`: the welcome sequence as an automation to build in Sender.

    factory sequence-export money-made-simple --for sender
    -> output/sequences/<brand>/<date>-sender/
         01-day0/subject.txt  body.html  email.txt  DELAY.txt
         02-day1/...
         CHECKLIST.md           how to build the automation, step by step
       Steps with {if launch} / {if no_launch} text are written twice (03-day2/launch/ and 03-day2/no-launch/),
       because Sender has no date conditions: use the launch copy while the launch code is live, then swap.

Links, prices and placeholders are rendered the way the factory would send them (with the email UTM tags).
Our own footer (why you're getting this, unsubscribe, address) is removed: Sender adds its own. The
brand's footer_note (not financial advice, AI help) stays. Set `welcome_via: sender` in the brand file
once the automation is live, so the factory's worker stops sending its own welcome emails for that brand.
Nothing is sent.
"""
from __future__ import annotations

import re
from contextlib import contextmanager
from datetime import date, datetime, timezone

FOOTER_HTML_RE = re.compile(r"\s*<p[^>]*>You're getting this because.*?</p>\s*<p[^>]*>.*?</p>", re.S)
FOOTER_TEXT_RE = re.compile(r"\nYou're getting this because.*\Z", re.S)
FAKE_SUB = {"id": 0, "email": "subscriber@example.invalid", "token": "SENDER", "source": "export"}


@contextmanager
def _forced_launch(active: bool | None):
    """Render as if the launch offer were live (True) or over (False); None leaves it to the date."""
    from .funnel import sequences
    orig = sequences._launch
    if active is None:
        yield
        return

    def fake(settings, brand, seq, now):
        info = orig(settings, brand, seq, now)
        return {**info, "active": active}
    sequences._launch = fake
    try:
        yield
    finally:
        sequences._launch = orig


def _strip_footer(r: dict) -> tuple[str, str]:
    html = FOOTER_HTML_RE.sub("", r["html"], count=1)
    text = FOOTER_TEXT_RE.sub("\n", r["text"])
    return html, text


def export(factory, slug: str, platform: str = "sender", when: date | None = None):
    from .funnel import mailer
    from .funnel.sequences import _IF_RE, load_sequence, render_step
    brand = factory.brand(slug)
    seq = load_sequence(factory.settings, slug)
    if seq is None:
        raise SystemExit(f"{slug} has no welcome sequence (brands/sequences/{slug}.yaml)")
    base = mailer.public_url(factory.settings, "")
    now = datetime.now(timezone.utc)
    out = factory.settings.output_dir / "sequences" / slug / f"{(when or date.today()).isoformat()}-{platform}"
    out.mkdir(parents=True, exist_ok=True)
    prev, rows = 0, []
    for n, step in enumerate(seq.steps, 1):
        delay = step.day_offset - prev if n > 1 else step.day_offset
        prev = step.day_offset
        d = out / f"{n:02d}-day{step.day_offset}"
        conditional = any(_IF_RE.search(t or "") for t in (step.subject, step.preheader, step.body_markdown, step.cta_label))
        variants = [("launch", True), ("no-launch", False)] if conditional else [("", None)]
        for name, active in variants:
            vd = d / name if name else d
            vd.mkdir(parents=True, exist_ok=True)
            with _forced_launch(active):
                r = render_step(factory.settings, brand, seq, step, dict(FAKE_SUB), base=base, now=now)
            html, text = _strip_footer(r)
            (vd / "subject.txt").write_text(f"Subject: {r['subject']}\nPreview text: {r['preheader']}\n")
            (vd / "body.html").write_text(html)
            (vd / "email.txt").write_text(text)
        (d / "DELAY.txt").write_text(f"Wait {delay} day(s) after the {'signup' if n == 1 else 'previous email'}, "
                                     f"then send this (day {step.day_offset} of the sequence).\n")
        rows.append((n, step.day_offset, delay, r["subject"], conditional))
    lines = [f"# Build {brand.name}'s welcome automation in Sender", "",
             "1. Sender > Automation > Create > Start from scratch. Trigger: **Subscriber joins a group** (the group "
             "your signup form adds people to).",
             "2. For each email below, in order: add a **Delay** step with the days shown, then an **Email** step. "
             "In the email, choose Custom HTML and paste body.html (or the HTML block of a template), and paste the "
             "subject and preview text from subject.txt.",
             "3. Custom HTML doesn't add the unsubscribe link: make sure the footer has {$unsubscribe} in a link and "
             "your postal address (CAN-SPAM). A drag-and-drop template's footer has both.",
             "4. Send each email to yourself as a test. Open every link.",
             f"5. Turn the automation on, then set `welcome_via: sender` in brands/{slug}.yaml so the factory stops "
             "sending its own welcome emails for this brand.",
             f"6. Import existing subscribers with `factory subscribers-export {slug} --for sender`: the -welcomed file "
             "with \"Trigger active automations upon import\" UNTICKED.", "",
             "| # | Delay | Day | Subject | Versions |", "|---|---|---|---|---|"]
    for n, day, delay, subject, cond in rows:
        lines.append(f"| {n} | {delay} day(s) | {day} | {subject} | {'launch + no-launch' if cond else 'one'} |")
    if any(r[4] for r in rows):
        lines += ["", "Launch / no-launch: Sender has no date conditions. Paste the launch/ version while the launch "
                  "code is live, and swap in no-launch/ the day it ends."]
    if "localhost" in base:
        lines += ["", "Links point at localhost: set your public site URL (see .env.example) and export again."]
    (out / "CHECKLIST.md").write_text("\n".join(lines) + "\n")
    return out, rows


def register(sub, factory_fn) -> None:
    s = sub.add_parser("sequence-export", help="the welcome sequence as an automation to build in Sender (never sends)")
    s.add_argument("brand")
    s.add_argument("--for", dest="platform", choices=["sender"], default="sender")

    def cmd(a):
        out, rows = export(factory_fn(a), a.brand, a.platform)
        print(f"{len(rows)} email(s), delays {', '.join(str(r[2]) for r in rows)} day(s) -> {out}")
    s.set_defaults(func=cmd)
