"""Audience funnel: link-in-bio page, double opt-in email list, lead magnet,
weekly digest, payment webhooks and funnel analytics.

    from contentfactory.funnel.linkpage import build_link_page
    from contentfactory.funnel.newsletter import draft_digest, send_digest, export_subscribers_csv
    from contentfactory.funnel.payments import stripe_payment_link
    from contentfactory.funnel.analytics import funnel_stats
    from contentfactory.funnel.routes import public_router, router

Submodules are imported lazily; importing this package stays cheap.
"""
