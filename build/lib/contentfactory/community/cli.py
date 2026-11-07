"""`factory comments ...`: collect comments, draft replies. Sending stays a human click in the inbox."""
from __future__ import annotations


def register(sub, factory_fn) -> None:
    c = sub.add_parser("comments", help="comment inbox: collect and draft replies (you send them in /inbox)")
    csub = c.add_subparsers(dest="comments_cmd", required=True)

    s = csub.add_parser("collect", help="fetch new comments from Instagram and YouTube via official APIs")
    s.add_argument("--days", type=int, default=30, help="only posts published in the last N days")

    def collect(a):
        from . import collect_comments
        res = collect_comments(factory_fn(a), max_age_days=a.days)
        print({k: v for k, v in res.items() if k != "errors"})
        for e in res.get("errors", []):
            print(f"  note: {e}")
    s.set_defaults(func=collect)

    s = csub.add_parser("draft", help="draft replies for new comments (never sends)")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--brand")

    def draft(a):
        from . import draft_replies
        ids = draft_replies(factory_fn(a), limit=a.limit, brand=a.brand)
        print(f"drafted {len(ids)} replies; review and send them at /inbox")
    s.set_defaults(func=draft)
