"""Funnel and brand-kit commands."""
from __future__ import annotations

import json


def register(sub, factory_fn) -> None:
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
