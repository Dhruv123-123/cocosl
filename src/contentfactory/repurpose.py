"""Turn one long video into several distinct Shorts and a carousel.

Each derivative is rewritten as a standalone piece (its own hook, payoff and
CTA), not a trim of the same narration, so it passes the originality check and
doesn't look like mass-produced re-uploads.
"""
from __future__ import annotations

import json

from pydantic import BaseModel, Field

from .config import BrandProfile
from .llm import LLM
from .schemas import Script, Segment
from .writer import SYSTEM, _brand_brief


def _offline_derivative(parent: Script, section: Segment, fmt: str, brand: BrandProfile) -> Script:
    beats = {"short": 6, "mid": 9}.get(fmt, 7)
    sentences = [s.strip() for s in section.narration.replace("!", ".").split(".") if s.strip()]
    segs = [Segment(heading="Hook", narration=f"{section.heading}: the part of {parent.title.lower()} nobody mentions.",
                    on_screen_text=section.heading[:50], visual_prompt=section.visual_prompt)]
    for i in range(1, beats - 1):
        line = sentences[(i - 1) % len(sentences)] if sentences else f"Detail {i} about {section.heading.lower()}"
        segs.append(Segment(heading=f"Beat {i}", narration=line + ".", on_screen_text=f"{i}.",
                            visual_prompt=f"{section.visual_prompt}, variation {i}"))
    segs.append(Segment(heading="Takeaway", narration=f"Full story on the channel. {brand.cta}",
                        on_screen_text="Full story on the channel", visual_prompt=section.visual_prompt))
    return Script(title=f"{section.heading} ({parent.title})"[:90], hook=segs[0].narration, segments=segs,
                  cta=brand.cta, caption=f"{section.heading}. From our video: {parent.title}.\n\n{brand.cta}",
                  hashtags=parent.hashtags, description=parent.description, thumbnail_text=section.heading[:30],
                  sources=parent.sources, claims_to_verify=parent.claims_to_verify[:3])


def derive(llm: LLM, brand: BrandProfile, parent: Script, section_index: int, fmt: str = "short") -> Script:
    section = parent.segments[section_index]
    prompt = f"""{_brand_brief(brand)}

Below is a long-form script. Write a standalone {fmt} built from section {section_index + 1}
("{section.heading}"). It must work for someone who never saw the long video: new hook, its own
payoff, and a CTA that points to the full video. Do not copy sentences verbatim; rewrite.

Long script:
{parent.model_dump_json(indent=2)}"""
    return llm.structured(Script, system=SYSTEM, prompt=prompt, purpose=f"repurpose:{fmt}",
                          offline=lambda: _offline_derivative(parent, section, fmt, brand))


def pick_sections(parent: Script, k: int = 3) -> list[int]:
    """The k meatiest sections (most narration), skipping intro and outro."""
    inner = list(range(1, max(1, len(parent.segments) - 1))) or [0]
    inner.sort(key=lambda i: -len(parent.segments[i].narration))
    return sorted(inner[:k])


def repurpose_post(factory, post_id: int, n_shorts: int = 3, carousel: bool = True, render: bool = True) -> list[int]:
    post = factory.db.get("posts", post_id)
    if post["format"] != "long":
        raise ValueError("Only long-form posts can be repurposed")
    brand = factory.brand(post["brand"])
    parent = Script.model_validate(post["script"])
    plan = [(i, "short") for i in pick_sections(parent, n_shorts)]
    if any(a.enabled and "mid" in a.formats for a in brand.accounts):  # a TikTok-only 65-90 s cut
        plan.append((pick_sections(parent, 1)[0], "mid"))
    if carousel and "carousel" in brand.formats:
        plan.append((pick_sections(parent, 1)[0], "carousel"))
    new_ids = []
    for idx, fmt in plan:
        script = derive(factory.llm, brand, parent, idx, fmt)
        pid = factory.db.insert("posts", {
            "brand": brand.slug, "idea_id": post["idea_id"], "format": fmt, "status": "scripted",
            "title": script.title, "script": script.model_dump(), "caption": script.caption,
            "hashtags": script.hashtags, "disclosure": brand.ai_disclosure,
            "meta": {"parent_post": post_id, "section": idx, "llm": factory.llm.provider},
        })
        factory.db.log("post.repurposed", "post", pid, {"parent": post_id, "format": fmt})
        if render:
            factory.render(pid)
        else:
            factory.check(pid)
        new_ids.append(pid)
    return new_ids


# ---------------------------------------------------------------- text drafts
class TextPack(BaseModel):
    """Written spin-offs of one long video. Drafts only: a person edits and posts them."""
    blog_title: str = Field(description="SEO-friendly article title, under 65 characters")
    blog_markdown: str = Field(description="800-1300 word article in Markdown with ## headings, written for "
                                          "reading (not a transcript), ending with a link to the video")
    newsletter_section: str = Field(description="120-200 word newsletter section: one idea, one example, one action")
    pins: list[str] = Field(description="Exactly 3 Pinterest pin texts: each a title line and a 1-2 sentence "
                                        "description, different angles, no hashtag spam")
    thread: list[str] = Field(description="5-8 posts for an X/Threads thread, each under 280 characters; first one "
                                          "is the hook, last one points to the video")


def _offline_pack(parent: Script, video_url: str) -> TextPack:
    body = [f"# {parent.title}", "", parent.hook, ""]
    for s in parent.segments[1:]:
        body += [f"## {s.heading}", "", s.narration, ""]
    body.append(f"Watch the full video: {video_url}")
    key = [s for s in parent.segments[1:-1]] or parent.segments
    return TextPack(
        blog_title=parent.title[:65], blog_markdown="\n".join(body),
        newsletter_section=f"**{parent.title}**\n\n{key[0].narration}\n\nThe full walkthrough: {video_url}",
        pins=[f"{s.heading}\n{s.narration[:180]}" for s in (key * 3)[:3]],
        thread=[parent.hook[:270], *[f"{i}. {s.narration[:260]}" for i, s in enumerate(key[:5], 1)],
                f"The full video: {video_url}"[:280]])


def text_drafts(factory, post_id: int, force: bool = False) -> dict:
    """Blog post, newsletter section, 3 pins and a thread from a long video, saved as drafts for a
    person to edit and post. Nothing is published. Returns {name: path}."""
    from .funnel.attribution import with_utm
    from .writer import _brand_brief
    post = factory.db.get("posts", post_id)
    if not post:
        raise KeyError(f"No post #{post_id}")
    if post["format"] != "long":
        raise ValueError("Text drafts come from long videos")
    pub = factory.db.one("SELECT url FROM publications WHERE post_id = ? AND status = 'published' AND url != '' "
                         "ORDER BY platform = 'youtube' DESC, id LIMIT 1", [post_id])
    if not pub and not force:
        raise ValueError(f"Post #{post_id} isn't published yet; use --force to draft from the script anyway")
    brand = factory.brand(post["brand"])
    parent = Script.model_validate(post["script"])
    url = (pub or {}).get("url") or "VIDEO_LINK_HERE"
    prompt = f"""{_brand_brief(brand)}

Turn this published video script into written drafts: a blog article, a newsletter section, 3 Pinterest
pins and an X/Threads thread. Each must read naturally in its own medium (no "in this video"). Keep every
number exactly as in the script; do not add new statistics. No first-person product testimonials.
Link to the video as: {url}

Script:
{parent.model_dump_json(indent=2)}"""
    pack = factory.llm.structured(TextPack, system=SYSTEM, prompt=prompt, purpose="repurpose:text",
                                  offline=lambda: _offline_pack(parent, url))
    out = factory.settings.output_dir / "drafts" / brand.slug / f"post-{post_id}"
    out.mkdir(parents=True, exist_ok=True)
    note = ("DRAFT for you to edit and post by hand. Nothing here has been published. Check the numbers "
            "against the video and keep the disclosures.")
    site = brand.link_in_bio or ""
    video_link = with_utm(url, "blog", "owned", f"post-{post_id}") if url.startswith("http") else url
    disclosure = brand.ai_disclosure or ""
    files = {
        "blog.md": "---\n" + "\n".join([f"title: {json.dumps(pack.blog_title)}", "draft: true",
                                       f"source_post: {post_id}", f"video: {video_link}"]) + "\n---\n\n"
                   + f"<!-- {note} -->\n\n" + pack.blog_markdown.strip()
                   + (f"\n\n_{disclosure}_" if disclosure else "") + "\n",
        "newsletter.md": f"<!-- {note} -->\n\n" + pack.newsletter_section.strip() + "\n",
        "pins.md": f"<!-- {note} Link each pin to {site or 'your site'}. -->\n\n"
                   + "\n\n".join(f"## Pin {i}\n\n{p.strip()}" for i, p in enumerate(pack.pins[:3], 1)) + "\n",
        "thread.md": f"<!-- {note} -->\n\n" + "\n\n---\n\n".join(
            f"{i}/{len(pack.thread)} {t.strip()}" for i, t in enumerate(pack.thread, 1)) + "\n",
    }
    paths = {}
    for name, text in files.items():
        (out / name).write_text(text)
        paths[name] = out / name
    meta = post.get("meta") or {}
    meta["text_drafts"] = {k: str(v.relative_to(factory.settings.output_dir)) for k, v in paths.items()}
    factory.db.update("posts", post_id, {"meta": meta})
    factory.db.log("post.text_drafts", "post", post_id, {"files": list(paths)})
    return paths
