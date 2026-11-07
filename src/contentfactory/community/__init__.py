"""Human-in-the-loop community inbox: read comments through official APIs,
triage them, draft replies in the brand voice, and send only when a human
clicks Send. No auto-replies, likes or DMs.

Worker / CLI entry points:
    collect_comments(factory, *, platforms=None, max_age_days=30, max_pages=4, transport=None) -> dict
    draft_replies(factory, limit=20, *, brand=None) -> list[int]
"""
from .service import (MAX_REPLIES_PER_HOUR, RateLimited, collect_comments, draft_replies,  # noqa: F401
                      redraft, save_as_idea, save_draft, send_reply, triage_comments)
from .store import ensure_schema, set_status  # noqa: F401
