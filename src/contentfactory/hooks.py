"""Hook template library for the writer.

`hooks_library.json` holds hook patterns with {slots} (see
research/scouting/creators.md for where they come from). For brands whose
niche matches the library, the writer gets a few templates that fit the title
and format as inspiration for `hook` and `hook_variants`. The model adapts
them, never pastes them, and the originality guardrail still applies.

Set FACTORY_HOOK_LIBRARY=0 to turn it off.
"""
from __future__ import annotations

import json
import os
import random
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from .config import BrandProfile

LIBRARY_PATH = Path(__file__).with_name("hooks_library.json")
SLOT_RE = re.compile(r"\{([a-z_]+)\}")

TOPIC_KEYWORDS = {
    "budgeting": ("budget", "spend", "paycheck", "bill", "subscription", "saving", "savings", "emergency fund",
                  "overdraft", "sinking", "expense"),
    "investing": ("invest", "index", "fund", "roth", "ira", "401", "retire", "stock", "etf", "brokerage",
                  "compound", "fee"),
    "credit-debt": ("credit", "debt", "card", "loan", "score", "apr", "interest", "avalanche", "snowball"),
    "tools": ("app", "account", "bank", "tool", "spreadsheet", "insured", "fdic", "alert", "high yield"),
    "scams": ("scam", "fraud", "phishing", "fake", "identity", "freeze", "stolen", "impersonat"),
}


@dataclass(frozen=True)
class HookTemplate:
    id: str
    pattern: str
    slots: tuple[str, ...]
    example: str
    mechanic: str
    topics: tuple[str, ...]
    formats: tuple[str, ...]
    needs_verified_number: bool = False
    inspired_by: str = ""

    def render(self, **values: str) -> str:
        missing = [s for s in self.slots if s not in values]
        if missing:
            raise KeyError(f"hook '{self.id}' needs slots: {', '.join(missing)}")
        return self.pattern.format(**values)


@dataclass
class HookLibrary:
    templates: list[HookTemplate]
    niche_keywords: tuple[str, ...] = field(default_factory=tuple)

    def get(self, hook_id: str) -> HookTemplate:
        for t in self.templates:
            if t.id == hook_id:
                return t
        raise KeyError(hook_id)

    def applies_to(self, brand: BrandProfile) -> bool:
        text = f"{brand.niche} {brand.name}".lower()
        return any(k in text for k in self.niche_keywords)

    def suggest(self, title: str, fmt: str, k: int = 4, seed: str = "") -> list[HookTemplate]:
        """Templates for this format whose topics match the title, varied per title but deterministic."""
        low = title.lower()
        topics = {t for t, words in TOPIC_KEYWORDS.items() if any(w in low for w in words)}
        pool = [t for t in self.templates if fmt in t.formats or (fmt == "image" and "carousel" in t.formats)]
        matched = [t for t in pool if topics & set(t.topics)]
        rest = [t for t in pool if t not in matched]
        rng = random.Random(f"{seed}|{title}|{fmt}")
        rng.shuffle(matched)
        rng.shuffle(rest)
        picked: list[HookTemplate] = []
        for t in matched + rest:  # one per mechanic, so the variants test genuinely different angles
            if all(p.mechanic != t.mechanic for p in picked):
                picked.append(t)
            if len(picked) == k:
                break
        return picked


@lru_cache(maxsize=4)
def load_library(path: str | None = None) -> HookLibrary:
    data = json.loads(Path(path or LIBRARY_PATH).read_text(encoding="utf-8"))
    templates = []
    for t in data["templates"]:
        slots = tuple(t.get("slots") or SLOT_RE.findall(t["pattern"]))
        templates.append(HookTemplate(
            id=t["id"], pattern=t["pattern"], slots=slots, example=t["example"], mechanic=t["mechanic"],
            topics=tuple(t.get("topics", ())), formats=tuple(t.get("formats", ())),
            needs_verified_number=bool(t.get("needs_verified_number")), inspired_by=t.get("inspired_by", "")))
    return HookLibrary(templates, tuple(data.get("niche_keywords", ())))


def prompt_block(brand: BrandProfile, title: str, fmt: str, k: int = 4) -> str:
    """Text for the writer prompt, or "" when the library is off or doesn't fit the brand."""
    if os.environ.get("FACTORY_HOOK_LIBRARY", "1").lower() in ("0", "false", "no", "off"):
        return ""
    lib = load_library()
    if not lib.applies_to(brand):
        return ""
    picks = lib.suggest(title, fmt, k=k, seed=brand.slug)
    if not picks:
        return ""
    lines = []
    for t in picks:
        note = " (any number you use goes in claims_to_verify)" if t.needs_verified_number else ""
        lines.append(f"- [{t.id}] {t.mechanic}: \"{t.pattern}\" e.g. \"{t.example}\"{note}")
    return ("Hook patterns that work in this niche. Use them as inspiration for the hook and the "
            "hook_variants (one mechanic per variant); fill them with this script's specifics and "
            "rewrite freely, never copy an example:\n" + "\n".join(lines))
