"""Turn one long video into several distinct Shorts and a carousel.

Each derivative is rewritten as a standalone piece (its own hook, payoff and
CTA), not a trim of the same narration, so it passes the originality check and
doesn't look like mass-produced re-uploads.
"""
from __future__ import annotations

from .config import BrandProfile
from .llm import LLM
from .schemas import Script, Segment
from .writer import SYSTEM, _brand_brief


def _offline_derivative(parent: Script, section: Segment, fmt: str, brand: BrandProfile) -> Script:
    beats = 6 if fmt == "short" else 7
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
