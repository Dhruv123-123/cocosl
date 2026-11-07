"""Funnel and brand-kit commands."""
from __future__ import annotations

import json


def register(sub, factory_fn) -> None:
    register_sequences(sub, factory_fn)
    s = sub.add_parser("brandkit", help="profile picture, banners, highlight covers, style sheet, bios")
    s.add_argument("brand")

    def brandkit(a):
        from ..brandkit import build_brand_kit
        f = factory_fn(a)
        for name, path in build_brand_kit(f.settings, f.brand(a.brand), f.llm).items():
            print(f"{name}: {path}")
    s.set_defaults(func=brandkit)

    s = sub.add_parser("linkpage", help="build the static link-in-bio page for a brand")
    s.add_argument("brand")
    s.add_argument("--base-url")

    def linkpage(a):
        from .linkpage import build_link_page
        f = factory_fn(a)
        print(build_link_page(f.settings, f.brand(a.brand), db=f.db, base_url=a.base_url, llm=f.llm))
    s.set_defaults(func=linkpage)

    s = sub.add_parser("digest", help="draft the weekly newsletter from recent posts")
    s.add_argument("brand")
    s.add_argument("--days", type=int, default=7)
    s.set_defaults(func=lambda a: print(f"draft #{__import__('contentfactory.funnel.newsletter', fromlist=['x']).draft_digest(factory_fn(a), a.brand, days=a.days)}"))

    s = sub.add_parser("digest-send", help="send a newsletter draft (dry run unless --confirm)")
    s.add_argument("draft_id", type=int)
    s.add_argument("--confirm", action="store_true")

    def digest_send(a):
        from .newsletter import send_digest
        print(json.dumps(send_digest(factory_fn(a), a.draft_id, confirm=a.confirm), indent=2, default=str))
    s.set_defaults(func=digest_send)

    s = sub.add_parser("subscribers-export", help="CSV of confirmed subscribers (Beehiiv/ConvertKit import)")
    s.add_argument("brand")
    s.set_defaults(func=lambda a: print(__import__('contentfactory.funnel.newsletter', fromlist=['x']).export_subscribers_csv(factory_fn(a), a.brand)))

    s = sub.add_parser("payment-link", help="create a Stripe Payment Link for a brand product")
    s.add_argument("brand")
    s.add_argument("index", type=int, help="position in the brand's products list (0-based)")

    def payment_link(a):
        from .payments import stripe_payment_link
        f = factory_fn(a)
        print(stripe_payment_link(f.brand(a.brand).products[a.index], brand=a.brand))
    s.set_defaults(func=payment_link)

    s = sub.add_parser("funnel", help="views -> clicks -> subscribers -> sales per brand")
    s.set_defaults(func=lambda a: print(json.dumps(
        __import__('contentfactory.funnel.analytics', fromlist=['x']).funnel_stats(factory_fn(a).db), indent=2, default=str)))


def register_sequences(sub, factory_fn) -> None:
    """Welcome-sequence and sales-page commands. Not called by register(): wire it
    from cli.py (`funnel.cli.register_sequences(sub, _factory)`) if you want these."""
    s = sub.add_parser("sequences", help="send due welcome-sequence emails (dry run unless --confirm)")
    s.add_argument("--brand")
    s.add_argument("--confirm", action="store_true", help="really send (also needs FACTORY_DRY_RUN=0, SMTP, address)")
    s.add_argument("--limit", type=int, default=500)

    def run(a):
        from .sequences import run_sequences
        print(json.dumps(run_sequences(factory_fn(a), confirm=a.confirm, brand=a.brand, limit=a.limit,
                                       strict=a.confirm), indent=2, default=str))
    s.set_defaults(func=run)

    s = sub.add_parser("sequence-check", help="validate a brand's welcome sequence and show per-step counts")
    s.add_argument("brand")

    def check(a):
        from .sequences import sequence_status, validate_sequence
        f = factory_fn(a)
        problems = validate_sequence(f.settings, f.brand(a.brand))
        print(json.dumps({"problems": problems, **sequence_status(f, a.brand)}, indent=2, default=str))
        if problems:
            raise SystemExit(1)
    s.set_defaults(func=check)

    s = sub.add_parser("sequence-preview", help="render every welcome email to .html/.eml for review")
    s.add_argument("brand")
    s.set_defaults(func=lambda a: [print(p) for p in __import__(
        "contentfactory.funnel.sequences", fromlist=["x"]).preview_sequence(factory_fn(a), a.brand)])

    s = sub.add_parser("salespage", help="build static sales pages for a brand's products")
    s.add_argument("brand")
    s.add_argument("--base-url")

    def sales(a):
        from .salespage import build_all_sales_pages
        f = factory_fn(a)
        for p in build_all_sales_pages(f.settings, f.db, f.brand(a.brand), base_url=a.base_url):
            print(p)
    s.set_defaults(func=sales)
