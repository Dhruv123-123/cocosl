"""Structured shapes the LLM produces and the pipeline passes around."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class IdeaDraft(BaseModel):
    title: str = Field(description="Working title, under 70 characters")
    angle: str = Field(description="The specific, non-obvious take that makes this worth watching")
    format: str = Field(description="One of: short, long, carousel")
    pillar: str = Field(description="Which content pillar this belongs to")
    hook: str = Field(description="First line the viewer hears or reads")
    why_now: str = Field(description="Why the audience cares about this now")
    monetization: str = Field(description="How this idea can lead to income: affiliate, product, lead, none")
    search_demand: int = Field(description="Estimated search/interest demand 1-10")
    competition: int = Field(description="Estimated competition 1-10 (10 = saturated)")
    effort: int = Field(description="Production effort 1-10")


class IdeaBatch(BaseModel):
    ideas: list[IdeaDraft]


class ChartSpec(BaseModel):
    kind: Literal["bars", "line"] = Field(description="bars to compare amounts, line for growth over time")
    title: str = Field(description="Chart title, under 8 words")
    labels: list[str] = Field(description="One short label per value (e.g. years or option names)")
    values: list[float] = Field(description="The exact numbers to plot, in the same order as labels")
    unit_prefix: str = Field(default="", description="e.g. $")
    unit_suffix: str = Field(default="", description="e.g. % or /mo")
    note: str = Field(default="", description="Assumptions or source, e.g. '7% a year, illustrative'")


class Segment(BaseModel):
    heading: str = Field(description="Short label for this beat or slide")
    narration: str = Field(description="Voiceover text for this beat (empty for silent carousels)")
    on_screen_text: str = Field(description="Big text shown on screen or slide, under 12 words")
    visual_prompt: str = Field(description="Prompt for an original illustration for this beat; no real people, no logos, no text")
    chart: ChartSpec | None = Field(default=None, description="Optional: a data chart drawn with exact numbers "
                                    "instead of an illustration (only when the beat is about numbers)")
    footage: str = Field(default="", description="Leave empty. Set by a person: path to their own screen "
                         "recording or camera clip shown on this beat instead of an illustration")


class Script(BaseModel):
    title: str
    hook: str = Field(description="Opening line, must create curiosity in under 3 seconds")
    segments: list[Segment]
    cta: str = Field(description="Closing call to action")
    caption: str = Field(description="Platform caption, 1-3 short paragraphs, no hashtags")
    hashtags: list[str] = Field(description="3-5 descriptive topic hashtags (Instagram allows 5) without the # sign")
    description: str = Field(description="Long description for YouTube with chapters if long-form")
    thumbnail_text: str = Field(description="2-5 word thumbnail text")
    sources: list[str] = Field(description="URLs or references a human should check")
    claims_to_verify: list[str] = Field(description="Factual claims a human must verify before publishing")
    title_variants: list[str] = Field(default_factory=list,
                                      description="2-3 alternative titles for A/B tests (YouTube Test & Compare)")
    hook_variants: list[str] = Field(default_factory=list,
                                     description="2-3 alternative opening lines to test in later reposts or cutdowns")
    calcs: list[dict] = Field(default_factory=list, description=(
        "Every computed money figure the script states, so it can be recomputed automatically. One object each: "
        "{kind: loan_payment|total_interest|payoff_months|future_value|federal_tax|payroll_tax, the inputs "
        "(principal/balance, rate as a percent, months or years, payment, monthly, initial, wages, married, year), "
        "claimed: the number the script says}"))
    related_video: str = Field(default="", description="Shorts: the title of this brand's long video the Short "
                               "should link to (YouTube's related video, set by hand in Studio). Empty otherwise")
    playlist: str = Field(default="", description="Long videos: the series playlist it belongs in, if known")
    original_element: str = Field(default="", description="Long videos: the one thing a template can't make, e.g. "
                                  "a worked example charted with this video's own numbers, or a screen recording of "
                                  "a real tool a person should record (say exactly what to record). Empty for shorts")


class ReviewVerdict(BaseModel):
    """An LLM 'editor' pass that critiques a draft before the human sees it."""
    score: int = Field(description="Overall quality 1-10")
    hook_strength: int = Field(description="1-10")
    originality: int = Field(description="1-10, how distinct from generic content on this topic")
    accuracy_risk: int = Field(description="1-10, 10 = many claims likely wrong")
    problems: list[str]
    suggested_fixes: list[str]


class AdScript(BaseModel):
    """A UGC-style product ad that an AI avatar or voiceover presents as a
    spokesperson or demo, never as a fake customer testimonial."""
    concept: str
    hook: str
    segments: list[Segment]
    cta: str
    on_screen_disclosure: str = Field(description="Short disclosure shown on screen, e.g. 'AI-generated spokesperson'")
    variations: list[str] = Field(description="Alternative hooks for A/B tests")


class PitchEmail(BaseModel):
    subject: str
    body: str
    follow_up: str


class ProductOutline(BaseModel):
    title: str
    subtitle: str
    audience: str
    sections: list[Segment]
    price_suggestion_usd: float
    sales_blurb: str
