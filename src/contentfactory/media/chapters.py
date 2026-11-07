"""YouTube chapters from the real beat timings of a rendered long video.

Scripts are written before the voice exists, so any timestamps a writer puts
in the description are guesses. After rendering we know when each beat starts,
so the uploaded description gets a chapter list that matches the video.
YouTube's rules: the first chapter at 0:00, at least three chapters, each at
least 10 seconds long.
"""
from __future__ import annotations

import re

MIN_CHAPTER = 10.0
_STAMP = re.compile(r"^\s*[-•*]?\s*\(?(\d{1,2}:)?\d{1,2}:\d{2}\)?\s*[-–—:]?\s*")


def build(starts: list[tuple[float, str]], total: float, min_len: float = MIN_CHAPTER) -> list[tuple[float, str]]:
    """[(start_seconds, title)] -> chapters YouTube will accept, or [] if there can't be three."""
    merged: list[list] = []
    for t, title in sorted(starts):
        title = " ".join((title or "").split())[:80]
        if not title:
            continue
        if merged and merged[-1][1].lower() == title.lower():
            continue  # same heading continues
        merged.append([float(t), title])
    if not merged:
        return []
    merged[0][0] = 0.0
    # Fold chapters that are too short into the one before (or, for the first, into the next).
    changed = True
    while changed and len(merged) > 1:
        changed = False
        for i, (t, _) in enumerate(merged):
            end = merged[i + 1][0] if i + 1 < len(merged) else total
            if end - t < min_len:
                if i == 0:
                    merged[1][0] = 0.0
                    merged.pop(0)
                else:
                    merged.pop(i)
                changed = True
                break
    return [(t, title) for t, title in merged] if len(merged) >= 3 else []


def stamp(seconds: float, long: bool = False) -> str:
    s = int(seconds)
    h, m, sec = s // 3600, s % 3600 // 60, s % 60
    return f"{h}:{m:02d}:{sec:02d}" if long or h else f"{m}:{sec:02d}"


def format_block(chapters: list) -> str:
    if not chapters:
        return ""
    long = chapters[-1][0] >= 3600
    return "Chapters\n" + "\n".join(f"{stamp(t, long)} {title}" for t, title in chapters)


def with_chapters(description: str, chapters: list) -> str:
    """Drop guessed timestamp lines from a description and add the real chapter list after the first paragraph."""
    if not chapters:
        return description
    lines = [ln for ln in (description or "").splitlines() if not _STAMP.match(ln)]
    lines = [ln for ln in lines if ln.strip().lower().rstrip(":") not in ("chapters", "timestamps")]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    first, _, rest = text.partition("\n\n")
    return "\n\n".join(x for x in [first, format_block(chapters), rest] if x)
