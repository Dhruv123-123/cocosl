"""`factory triage`: everything waiting on Dhruv, across every brand, most urgent first.

    factory triage            # text, grouped by urgency
    factory triage --save     # also output/triage.md

Sources (all local, nothing posted, no network):
* now:    post-by-hand items that are due (TikTok, Pinterest); publications interrupted mid-upload or
          failed; red launch-check items (something scheduled would go out wrong).
* soon:   posts waiting for review, with their blocking flags (number mismatches, repost, disclosures...);
          recordings (your narration, screen recordings) for posts that are scheduled or close to it.
* setup:  placeholders in brand files (example.com links, REPLACE_ME), missing keys or connections
          for platforms the brands post to, the voice and writing providers.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

ORDER = {"now": 0, "soon": 1, "setup": 2}


@dataclass
class Item:
    urgency: str  # now | soon | setup
    brand: str
    kind: str
    what: str
    how: str = ""


def collect(factory) -> list[Item]:
    items: list[Item] = []
    add = lambda *a: items.append(Item(*a))  # noqa: E731
    db = factory.db

    from .manual import pending
    for r in pending(factory):
        if r["due"]:
            add("now", r["brand"], f"post by hand ({r['platform']})", f"#{r['id']} {r['title'][:70]}",
                f"post it, then `factory manual done {r['id']} --url ...` (or the Today page)")
    for r in db.query("SELECT p.id, p.platform, p.status, p.error, s.brand, s.title FROM publications p "
                      "JOIN posts s ON s.id = p.post_id WHERE p.status IN ('needs_check', 'failed') "
                      "AND p.updated_at >= datetime('now', '-14 days') ORDER BY p.id DESC LIMIT 30"):
        add("now", r["brand"], f"{r['status'].replace('_', ' ')} ({r['platform']})", f"#{r['id']} {r['title'][:60]}",
            (r["error"] or "")[:140] or "check the platform, then resolve it on the post page")

    from .launch_check import run as launch_run
    try:
        rep = launch_run(factory)
        for f in rep.findings:
            if f.where.startswith("brand file"):
                add("setup", f.brand, "brand file", f"{f.where.split(': ', 1)[-1]}: {f.message}",
                    f"edit brands/{f.brand}.yaml")
            elif f.level == "red":
                add("now", f.brand, "launch check", f"{f.where}: {f.message}", "fix it on the post page")
    except Exception as e:
        add("setup", "-", "launch check", f"couldn't run: {e}")

    for post in db.query("SELECT id, brand, title, format, status, checks FROM posts "
                         "WHERE status IN ('in_review', 'blocked') ORDER BY created_at"):
        checks = post.get("checks") if isinstance(post.get("checks"), dict) else {}
        flags = [c for c in (checks.get("checks") or []) if c.get("level") in ("block", "warn")]
        blocks = [c for c in flags if c["level"] == "block"]
        detail = "; ".join(f"{c['name']}: {c['message'][:90]}" for c in (blocks or flags)[:2])
        add("soon", post["brand"], "review" + (" (blocked)" if blocks else ""),
            f"#{post['id']} {post['title'][:60]}" + (f" · {detail}" if detail else ""),
            "approve, edit or reject it in Review")

    from .planner import recordings
    for t in recordings(factory):
        add("soon" if t["publish_at"] else "setup", t["brand"], "recording", f"#{t['post_id']} {t['title'][:60]}",
            "; ".join(t["needs"])[:200])

    from .doctor import _llm, _publishing, _voice
    for r in [_llm(factory), _voice(factory, offline=True), *_publishing(factory, online=False)]:
        if r.level in ("warn", "fail") and r.name != "dry run" and "skipped offline" not in r.message:
            brand, _, plat = r.name.partition("/")
            add("setup", brand if plat else "-", r.name, r.message)
    return sorted(items, key=lambda i: (ORDER[i.urgency], i.brand, i.kind))


def to_text(items: list[Item]) -> str:
    if not items:
        return "Nothing is waiting on you."
    labels = {"now": "Do now", "soon": "Do this week", "setup": "Setup (once)"}
    out = []
    for level in ("now", "soon", "setup"):
        group = [i for i in items if i.urgency == level]
        if not group:
            continue
        out.append(f"{labels[level]} ({len(group)})")
        for i in group:
            out.append(f"  [{i.brand}] {i.kind}: {i.what}")
            if i.how:
                out.append(f"      → {i.how}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def to_markdown(items: list[Item]) -> str:
    labels = {"now": "Do now", "soon": "Do this week", "setup": "Setup (once)"}
    out = ["# Waiting on you", ""]
    for level in ("now", "soon", "setup"):
        group = [i for i in items if i.urgency == level]
        if group:
            out += [f"## {labels[level]} ({len(group)})", ""]
            out += [f"- [ ] **{i.brand}** · {i.kind}: {i.what}" + (f"  \n  {i.how}" if i.how else "") for i in group]
            out.append("")
    return "\n".join(out) if items else "# Waiting on you\n\nNothing.\n"


def register(sub, factory_fn) -> None:
    s = sub.add_parser("triage", help="everything waiting on you across brands: due posts, review flags, "
                                      "recordings, placeholders, missing keys")
    s.add_argument("--save", action="store_true", help="also write output/triage.md")
    s.add_argument("--json", action="store_true")

    def cmd(a):
        f = factory_fn(a)
        items = collect(f)
        if a.json:
            import json
            print(json.dumps([asdict(i) for i in items], indent=2))
            return
        print(to_text(items))
        if a.save:
            path = f.settings.output_dir / "triage.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(to_markdown(items))
            print(path)
    s.set_defaults(func=cmd)
