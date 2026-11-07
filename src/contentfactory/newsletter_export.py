"""`factory newsletter`: a week's posts as a draft email to paste into Sender or Kit.

    factory newsletter --brand money-made-simple --for kit        # last 7 days of published posts
    factory newsletter --brand money-made-simple --for sender --upcoming   # before launch: next week's posts

Builds on the weekly digest (funnel/newsletter.py: intro, one blurb per post, at most one product or
affiliate mention with its disclosure, the AI disclosure) and writes, under
output/newsletter/<brand>/<date>-<kit|sender>/:
    email.html     the whole email, with the platform's own unsubscribe and address merge tags
    body.html      just the content, for the platform's HTML block inside your saved template
    email.txt      plain-text version
    subject.txt    subject line and preview text
    CHECKLIST.md   what to check before you press send in the platform

Nothing is sent: it's a draft for you to paste and send from the platform. Kit and Sender add their own
unsubscribe link and postal address in the footer; the checklist reminds you to confirm it in the preview.
Merge tags can be overridden with NEWSLETTER_UNSUB_TAG / NEWSLETTER_ADDRESS_TAG if your template differs.
"""
from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path

TAGS = {  # platform merge tags for the footer
    "kit": ("{{ unsubscribe_url }}", "{{ address }}"),
    "sender": ("", ""),  # Sender's campaign footer carries the unsubscribe link and address: ours is removed
}
FOOTER_RE = re.compile(r"\s*<p[^>]*>You're getting this because.*?</p>\s*<p[^>]*>.*?%%BUSINESS_ADDRESS%%</p>", re.S)
BODY_RE = re.compile(r"(<table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" "
                     r"style=\"max-width:600px.*?</table>)\s*</td></tr>\s*</table>\s*</body>", re.S)


def export(factory, brand_slug: str, platform: str = "kit", days: int = 7, upcoming: bool = False) -> dict:
    from .funnel import mailer
    from .funnel.newsletter import ADDRESS_PLACEHOLDER, draft_digest, get_draft
    if platform not in TAGS:
        raise ValueError("platform: kit or sender")
    draft_id = draft_digest(factory, brand_slug, days, upcoming=upcoming)
    d = get_draft(factory.db, draft_id)
    unsub, addr = TAGS[platform]
    unsub = os.environ.get("NEWSLETTER_UNSUB_TAG", unsub)
    addr = os.environ.get("NEWSLETTER_ADDRESS_TAG", addr)
    html, text = d["html"], d["text"]
    if unsub:
        html = html.replace(mailer.UNSUB_PLACEHOLDER, unsub).replace(ADDRESS_PLACEHOLDER, addr or "")
        text = text.replace(mailer.UNSUB_PLACEHOLDER, unsub).replace(ADDRESS_PLACEHOLDER, addr or "")
    else:
        html = FOOTER_RE.sub("", html)
        text = "\n".join(line for line in text.splitlines()
                         if mailer.UNSUB_PLACEHOLDER not in line and ADDRESS_PLACEHOLDER not in line) + "\n"
    m = BODY_RE.search(html)
    body = m.group(1) if m else html
    out = factory.settings.output_dir / "newsletter" / brand_slug / f"{date.today().isoformat()}-{platform}"
    out.mkdir(parents=True, exist_ok=True)
    (out / "email.html").write_text(html)
    (out / "body.html").write_text(body + "\n")
    (out / "email.txt").write_text(text)
    (out / "subject.txt").write_text(f"Subject: {d['subject']}\nPreview text: {d['preheader']}\n")
    n_posts = len((d.get("meta") or {}).get("posts") or [])
    where = {"kit": "Kit: Broadcasts > New broadcast > choose your template > add an HTML block, paste body.html "
                    "(or paste email.html into a Custom HTML template)",
             "sender": "Sender: Campaigns > Create > Custom HTML (paste email.html) or the HTML block of your "
                       "template (paste body.html)"}[platform]
    (out / "CHECKLIST.md").write_text(
        f"# Before you send ({platform.title()})\n\n"
        f"Draft #{draft_id}: {n_posts} post(s){' (upcoming: add each link once it is live)' if upcoming else ''}.\n\n"
        f"- [ ] {where}\n- [ ] Subject and preview text from subject.txt\n"
        "- [ ] Every link opens the right post" + (" (links are empty until the posts are live)" if upcoming else "") + "\n"
        "- [ ] The footer shows an unsubscribe link and your postal address (CAN-SPAM) in the preview\n"
        "- [ ] Any affiliate or product mention keeps its disclosure; the AI disclosure line stays\n"
        + ("- [ ] Links point at localhost: set your public site URL (see .env.example) and run this again\n"
           if "localhost" in html else "")
        + "- [ ] Send a test to yourself, then send or schedule it in the platform\n")
    factory.db.log("newsletter.exported", "newsletter_draft", draft_id, {"platform": platform, "dir": str(out)})
    return {"dir": out, "draft_id": draft_id, "posts": n_posts, "subject": d["subject"]}


def register(sub, factory_fn) -> None:
    s = sub.add_parser("newsletter", help="a week's posts as a draft email to paste into Kit or Sender (never sent)")
    s.add_argument("--brand", required=True)
    s.add_argument("--for", dest="platform", choices=sorted(TAGS), default="kit")
    s.add_argument("--days", type=int, default=7)
    s.add_argument("--upcoming", action="store_true", help="use next week's scheduled/approved posts (before launch)")

    def cmd(a):
        res = export(factory_fn(a), a.brand, a.platform, a.days, a.upcoming)
        print(f"{res['posts']} post(s), subject “{res['subject']}” -> {res['dir']}")
    s.set_defaults(func=cmd)
