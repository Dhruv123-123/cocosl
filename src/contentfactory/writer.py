"""Script writing: draft, self-critique, revise.

The human edit after this is what makes content 'authentic' under YouTube's
rules and copyrightable in the US, so the writer's job is a strong first
draft plus a list of claims the human must check, not a finished product.
"""
from __future__ import annotations

from .config import BrandProfile
from .llm import LLM
from .schemas import ChartSpec, ReviewVerdict, Script, Segment

FORMAT_SPECS = {
    "short": "A 30-55 second vertical video. 5-8 beats of 1-2 sentences. Total narration 90-140 words. "
             "Hook in the first sentence; pay it off; one clear takeaway; end on the CTA.",
    "long": "A 6-10 minute narrated explainer. 8-14 sections of 80-150 words each, story-driven, with "
            "concrete examples and numbers. Include chapter headings. Total 1000-1600 words. "
            "It must contain one thing a template can't make: at least one worked example with this video's "
            "own numbers as a `chart`, and/or name in original_element a screen recording a person should make "
            "(e.g. 'record the IRS payment page while filling in the example'). Not a slideshow of generic "
            "illustrations with narration.",
    "mid": "A 65-90 second vertical video for TikTok only (its Creator Rewards count videos over one minute). "
           "8-11 beats; total narration 190-250 words. Hook in the first sentence, then one idea developed "
           "with a concrete example, ending on the CTA. Must stand on its own, not a stretched short.",
    "carousel": "A 7-10 slide Instagram carousel. Slide 1 is the hook headline. Each slide: a short headline "
                "(on_screen_text) and a 1-3 sentence body (narration). Last slide is the CTA and a save prompt.",
    "image": "A single image post: one bold on_screen_text, a caption that delivers the value.",
}


def _brand_brief(brand: BrandProfile) -> str:
    aff = "\n".join(f"- {a.name}: {a.url} (use only when genuinely relevant: {', '.join(a.keywords)})"
                    for a in brand.affiliates) or "- none"
    return f"""Channel: {brand.name} ({brand.niche})
Audience: {brand.audience}
Promise: {brand.promise}
Voice: {brand.voice.tone}; persona: {brand.voice.persona}
Never say: {', '.join(brand.voice.banned_phrases) or 'n/a'}
Visual style for illustrations: {brand.visual.image_style}{'; recurring mascot: ' + brand.visual.mascot if brand.visual.mascot else ''}
Default CTA: {brand.cta}
Affiliate offers:
{aff}"""


SYSTEM = (
    "You are a senior scriptwriter for a faceless educational channel. You write tight, specific, "
    "accurate scripts with a real point of view. Rules: no fabricated statistics (if unsure, say so or "
    "omit); list every factual claim that needs checking in claims_to_verify; list every computed money figure (loan payment, "
    "interest, payoff time, growth, federal or payroll tax) in calcs with its inputs so it is recomputed; never write first-person "
    "product testimonials ('I used this and...'); no real people's likeness in visual prompts; no "
    "logos or brand marks in visual prompts; no text inside visual prompts; no engagement bait."
)


def _offline_script(brand: BrandProfile, title: str, angle: str, fmt: str) -> Script:
    beats = {"short": 6, "mid": 9, "long": 10, "carousel": 8, "image": 1}[fmt if fmt in FORMAT_SPECS else "short"]
    topic = title.rstrip("?.!")
    segs = []
    for i in range(beats):
        if i == 0:
            head, line = "Hook", f"Here's the thing about {topic.lower()} that most people miss."
        elif i == beats - 1:
            head, line = "Takeaway", f"So the one thing to remember: {angle.lower()}."
        else:
            head = f"Point {i}"
            line = (f"Point {i}: a concrete example about {topic.lower()} that shows {angle.lower()}, "
                    f"explained plainly for {brand.audience}.")
        segs.append(Segment(
            heading=head, narration=line,
            on_screen_text=(topic if i == 0 else head)[:60],
            visual_prompt=f"{brand.visual.image_style}; scene illustrating '{head.lower()}' about {topic.lower()}",
        ))
    original = ""
    if fmt == "long":  # a worked example drawn from the script's own (placeholder) numbers
        segs[2].chart = ChartSpec(kind="bars", title=f"Worked example: {topic}"[:60], labels=["Before", "After"],
                                  values=[100, 160], note="Placeholder numbers: replace with the real example")
        original = "The worked-example chart (replace its placeholder numbers)"
    tags = (brand.hashtags or [brand.slug])[:5]
    return Script(
        title=title, hook=segs[0].narration, segments=segs, cta=brand.cta, original_element=original,
        caption=f"{title}\n\n{angle}.\n\n{brand.cta}",
        hashtags=tags, description=f"{title}. {angle}.",
        thumbnail_text=" ".join(topic.split()[:4]),
        sources=[], claims_to_verify=[f"Check every example in '{title}' before publishing"],
        title_variants=[f"{topic}: the short version", f"What I'd tell a friend about {topic.lower()}"],
        hook_variants=[f"Quick one about {topic.lower()}.", f"Nobody explains {topic.lower()} like this."],
    )


def write_script(llm: LLM, brand: BrandProfile, title: str, angle: str, fmt: str,
                 notes: str = "", research: str = "") -> Script:
    prompt = f"""{_brand_brief(brand)}

{research}

Write a {fmt} script.
Format spec: {FORMAT_SPECS.get(fmt, FORMAT_SPECS['short'])}

Title: {title}
Angle: {angle}
{('Editor notes: ' + notes) if notes else ''}

Caption: write it for Instagram/TikTok (value first, then CTA). If you mention an affiliate offer,
the caption must say it's an affiliate link. Hashtags: specific, not generic spam.
Also give 2-3 title_variants and 2-3 hook_variants that test genuinely different angles (not synonyms).
Charts: when a beat compares numbers (fees, interest, a balance over time), you may give that segment a
`chart` (kind "bars" or "line", 2-12 values, short labels). It is drawn exactly from your numbers, so use
illustrative round figures, say "example" in its note, and list each chart's figures in claims_to_verify.
At most two charts per script; leave `chart` out everywhere else."""
    return llm.structured(Script, system=SYSTEM, prompt=prompt, purpose=f"script:{fmt}",
                          offline=lambda: _offline_script(brand, title, angle, fmt))


def critique(llm: LLM, brand: BrandProfile, script: Script) -> ReviewVerdict:
    prompt = f"""{_brand_brief(brand)}

Critique this draft as a tough editor. Score honestly; 7+ means ready for a human final pass.
Flag: weak hook, generic content, claims likely wrong, anything that reads like mass-produced filler,
fake testimonials, missing disclosure.

{script.model_dump_json(indent=2)}"""
    return llm.structured(ReviewVerdict, system="You are an exacting content editor.", prompt=prompt,
                          purpose="critique",
                          offline=lambda: ReviewVerdict(score=7, hook_strength=7, originality=6, accuracy_risk=3,
                                                        problems=[], suggested_fixes=[]))


def revise(llm: LLM, brand: BrandProfile, script: Script, verdict: ReviewVerdict) -> Script:
    if not verdict.problems:
        return script
    prompt = f"""{_brand_brief(brand)}

Revise this script to fix the editor's problems. Keep what works.

Problems:
{chr(10).join('- ' + p for p in verdict.problems)}
Suggested fixes:
{chr(10).join('- ' + f for f in verdict.suggested_fixes)}

Draft:
{script.model_dump_json(indent=2)}"""
    return llm.structured(Script, system=SYSTEM, prompt=prompt, purpose="revise", offline=lambda: script)


def write_with_review(llm: LLM, brand: BrandProfile, title: str, angle: str, fmt: str,
                      min_score: int = 7, max_rounds: int = 2, notes: str = "",
                      research: str = "") -> tuple[Script, ReviewVerdict]:
    script = write_script(llm, brand, title, angle, fmt, notes, research)
    verdict = critique(llm, brand, script)
    rounds = 0
    while verdict.score < min_score and rounds < max_rounds:
        script = revise(llm, brand, script, verdict)
        verdict = critique(llm, brand, script)
        rounds += 1
    return script, verdict
