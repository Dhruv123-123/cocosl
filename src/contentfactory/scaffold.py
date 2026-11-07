"""`factory brand new <slug>`: a new brand, ready for its first review session, in about 5 minutes.

    factory brand new rent-smart --name "Rent Smart" --niche "money for renters" \
        --audience "renters in their 20s and 30s" --timezone America/Chicago
    factory brand new rent-smart ... --import        # also load and render the 3 sample posts
    factory brand remove rent-smart --yes            # undo a scaffold that has nothing scheduled or published

It creates:
* brands/<slug>.yaml: conservative caps (3 shorts, 2 carousels a week, 1 post a day per platform),
  dry-run friendly placeholder links (launch-check flags them yellow), review required;
* voice/<slug>/ and footage/<slug>/ with a README each (where your own narration and screen
  recordings go; see `factory voice` and `factory recordings`);
* launch/<slug>/content.json: 3 sample posts (short, carousel, long with a worked-example chart)
  in the `factory import` format. They're placeholders: rewrite them or let `factory daily` replace them.

Nothing is posted. Edit the YAML (palette, handles, products), then `factory doctor` and `factory launch-check`.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import yaml

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")
PALETTES = [["#13212e", "#f5f2ea", "#3aa0ff", "#ffb547"], ["#1d1326", "#f7f1ea", "#b26bff", "#ffd166"],
            ["#0f2420", "#f2f5ef", "#28c2a0", "#ff8a5b"], ["#26140f", "#faf3ea", "#e8743b", "#5bc0be"]]


def brand_yaml(slug: str, name: str, niche: str, audience: str, timezone: str, handle: str) -> dict:
    palette = PALETTES[sum(map(ord, slug)) % len(PALETTES)]
    return {
        "name": name, "niche": niche, "audience": audience,
        "promise": f"one practical {niche.split(' for ')[0]} move you can make this week, without the jargon",
        "pillars": [f"{niche}: the basics nobody explains", "mistakes that cost real money",
                    "tools and options, honestly compared", "step-by-step how-tos"],
        "formats": ["short", "carousel", "long"],
        "seed_topics": [niche], "avoid_topics": ["get rich quick", "guaranteed returns"],
        "subreddits": [], "hashtags": [slug.replace("-", ""), "moneytips"],
        "cta": f"Follow {handle} for one useful move a week.",
        "link_in_bio": f"https://example.com/{slug}/links",
        "voice": {"tone": "calm, specific, zero hype", "persona": f"a friend who knows {niche} and hates jargon",
                  "tts_voice": "", "banned_phrases": ["this one trick", "guaranteed"]},
        "visual": {"palette": palette, "font": "Inter",
                   "image_style": "clean flat vector illustration, brand palette, simple shapes, no text, no logos",
                   "watermark": handle,
                   # the one constant across every thumbnail, intro and cover; looks rotate around it
                   "signature": {"device": ["corner_block", "stripe", "ring", "bracket", "dot_grid"][sum(map(ord, slug)) % 5],
                                 "color": "accent", "corner": "top-right", "size": 0.14,
                                 "label": "".join(w[0] for w in name.split())[:4].upper()}},
        "cadence": {"shorts_per_week": 3, "long_per_week": 0, "carousels_per_week": 2,
                    "max_posts_per_day_per_platform": 1, "post_times": ["12:30", "19:00"], "platform_times": {},
                    "timezone": timezone, "daily_at": "07:00", "daily_drafts": 1, "paused": False},
        "accounts": [{"platform": "instagram", "handle": handle, "formats": ["short", "carousel", "image"]},
                     {"platform": "youtube", "handle": handle, "formats": ["short", "long"]},
                     {"platform": "tiktok", "handle": handle, "formats": ["short", "mid"]}],
        "affiliates": [], "products": [],
        "require_human_review": True, "own_voice": False,
    }


def sample_posts(name: str, niche: str, cta: str) -> list[dict]:
    seg = lambda h, n, o, v, **kw: {"heading": h, "narration": n, "on_screen_text": o, "visual_prompt": v, **kw}  # noqa: E731
    base = {"caption": "", "hashtags": [], "description": "", "sources": [], "title_variants": [], "hook_variants": [],
            "claims_to_verify": ["PLACEHOLDER sample: rewrite with real, checked facts before approving"]}
    return [
        {"format": "short", "pillar": "mistakes that cost real money", "script": {**base,
            "title": f"The {niche} mistake that quietly costs you", "hook": f"Most people get this part of {niche} wrong.",
            "segments": [seg("Hook", f"Most people get this part of {niche} wrong.", "The quiet mistake", "a puzzled person at a desk, flat vector"),
                         seg("The mistake", "Sample line: describe one specific, common mistake.", "The mistake", "a leaking bucket"),
                         seg("The fix", "Sample line: the fix, in one concrete step.", "The fix", "a wrench fixing a pipe"),
                         seg("Do it today", "Sample line: what to do in the next ten minutes.", "Do it today", "a checklist with one tick")],
            "cta": cta, "thumbnail_text": "The quiet mistake",
            "caption": f"Sample caption for {name}. Replace before approving.\n\n{cta}"}},
        {"format": "carousel", "pillar": "step-by-step how-tos", "script": {**base,
            "title": f"A 5-step {niche} checklist", "hook": "Save this for later.",
            "segments": [seg("Hook", "", f"A 5-step {niche} checklist", "a clipboard")] +
                        [seg(f"Step {i}", f"Sample step {i}: one action with one example.", f"Step {i}", "a numbered card")
                         for i in range(1, 6)] + [seg("Save", "", "Save this and share it with a friend", "a bookmark")],
            "cta": cta, "thumbnail_text": "5 steps",
            "caption": f"Sample caption for {name}. Replace before approving.\n\n{cta}"}},
        {"format": "long", "pillar": f"{niche}: the basics nobody explains", "script": {**base,
            "title": f"{niche[:1].upper() + niche[1:]}, explained with real numbers", "hook": "Let's do the math together.",
            "original_element": "The worked-example chart: replace its placeholder numbers with a real, checked example",
            "segments": [seg("Intro", "Sample intro: what this video covers and why it matters.", "Let's do the math", "a calculator"),
                         seg("The example", "Sample: walk through one realistic example with numbers.", "A real example", "a notebook",
                             chart={"kind": "bars", "title": "Worked example", "labels": ["Option A", "Option B"],
                                    "values": [100, 140], "note": "PLACEHOLDER numbers"}),
                         seg("What to do", "Sample: the decision rule the viewer can use.", "Your rule of thumb", "a signpost"),
                         seg("Recap", "Sample recap in two sentences.", "Recap", "a sunrise")],
            "cta": cta, "thumbnail_text": "The real numbers",
            "caption": f"Sample caption for {name}. Replace before approving.\n\n{cta}"}},
    ]


def create(home: Path, slug: str, name: str = "", niche: str = "", audience: str = "",
           timezone: str = "America/New_York", handle: str = "", force: bool = False) -> dict:
    if not SLUG_RE.match(slug) or slug.startswith("_"):
        raise ValueError("slug: lowercase letters, digits and dashes, e.g. rent-smart")
    from zoneinfo import ZoneInfo
    ZoneInfo(timezone)  # raises on a typo
    brands_dir = home / "brands"
    path = brands_dir / f"{slug}.yaml"
    if path.exists() and not force:
        raise FileExistsError(f"{path} already exists (use --force to overwrite)")
    name = name or slug.replace("-", " ").title()
    niche = niche or f"{name.lower()} money tips"
    audience = audience or "people who want clear, practical money help"
    handle = handle or "@" + slug.replace("-", "")
    data = brand_yaml(slug, name, niche, audience, timezone, handle)
    brands_dir.mkdir(parents=True, exist_ok=True)
    header = (f"# {name}: scaffolded by `factory brand new`. Edit freely; links are placeholders that\n"
              "# `factory launch-check` flags until you put real ones in.\n")
    path.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=110))
    made = {"brand": path}
    for folder, text in (("voice", "Your own narration goes here: `factory voice <post id> take.m4a` copies it in.\n"
                                   "Set own_voice: true in the brand file to hold videos until you've recorded them.\n"),
                         ("footage", "Your screen recordings and camera clips go here. Point a script beat at one with\n"
                                     "`footage: footage/" + slug + "/<file>.mp4`. `factory recordings` lists what's needed.\n")):
        d = home / folder / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.txt").write_text(text)
        made[folder] = d
    launch = home / "launch" / slug
    launch.mkdir(parents=True, exist_ok=True)
    (launch / "content.json").write_text(json.dumps(sample_posts(name, niche, data["cta"]), indent=2))
    made["samples"] = launch / "content.json"
    from .config import load_brand
    load_brand(brands_dir, slug)  # proves the file is valid
    return made


def remove(factory, slug: str) -> list[Path]:
    """Undo a scaffold: refuses if the brand has anything scheduled or published."""
    live = factory.db.scalar("SELECT COUNT(*) FROM publications p JOIN posts s ON s.id = p.post_id WHERE s.brand = ? "
                             "AND p.status IN ('queued','publishing','published','needs_check','manual')", [slug])
    if live:
        raise PermissionError(f"{slug} has {live} scheduled or published publication(s); not removing it")
    home = factory.settings.home
    gone = []
    for p in (home / "brands" / f"{slug}.yaml", home / "voice" / slug, home / "footage" / slug, home / "launch" / slug,
              factory.settings.output_dir / slug):
        if p.is_dir():
            shutil.rmtree(p)
            gone.append(p)
        elif p.exists():
            p.unlink()
            gone.append(p)
    factory.db.execute("UPDATE posts SET status = 'rejected', review_notes = 'brand removed' WHERE brand = ? "
                       "AND status NOT IN ('published')", [slug])
    return gone


def register(sub, factory_fn) -> None:
    b = sub.add_parser("brand", help="scaffold or remove a brand")
    bs = b.add_subparsers(dest="brand_cmd", required=True)
    s = bs.add_parser("new", help="create brands/<slug>.yaml, voice/footage folders and 3 sample posts")
    s.add_argument("slug")
    s.add_argument("--name", default="")
    s.add_argument("--niche", default="")
    s.add_argument("--audience", default="")
    s.add_argument("--timezone", default="America/New_York")
    s.add_argument("--handle", default="")
    s.add_argument("--force", action="store_true")
    s.add_argument("--import", dest="do_import", action="store_true", help="also import and render the samples")

    def new(a):
        f = factory_fn(a)
        made = create(f.settings.home, a.slug, a.name, a.niche, a.audience, a.timezone, a.handle, a.force)
        for k, p in made.items():
            print(f"{k:8s} {p}")
        if a.do_import:
            for item in json.loads(made["samples"].read_text()):
                pid = f.import_script(a.slug, item["script"], item["format"], item.get("pillar", ""), "", render=True)
                print(f"sample post #{pid} ({item['format']})")
        print(f"\nNext: edit {made['brand'].name} (handles, palette, products), then "
              f"`factory doctor --offline` and `factory launch-check`.")
    s.set_defaults(func=new)

    s = bs.add_parser("remove", help="delete a scaffolded brand (refuses if anything is scheduled or published)")
    s.add_argument("slug")
    s.add_argument("--yes", action="store_true")

    def rm(a):
        if not a.yes:
            raise SystemExit(f"This deletes brands/{a.slug}.yaml and its voice/, footage/ and launch/ folders. "
                             "Add --yes to confirm.")
        for p in remove(factory_fn(a), a.slug):
            print(f"removed {p}")
    s.set_defaults(func=rm)
