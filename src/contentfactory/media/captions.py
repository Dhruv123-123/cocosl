"""Word-chunked captions: timing, .srt export and .ass (libass) for burn-in.

When the voice returns word timestamps (Kokoro) or FACTORY_ALIGN=whisper is set,
each chunk starts and ends exactly when its words are spoken (`time_segment_words`).
Otherwise timing is estimated: each segment's words are spread across that
segment's audio, weighted by word length.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .util import RGB

MAX_WORDS, MIN_WORDS, MAX_CHARS = 5, 2, 20


@dataclass
class Cue:
    start: float
    end: float
    text: str


def chunk_words(text: str) -> list[list[str]]:
    """Split narration into 2-5 word chunks, breaking at punctuation."""
    words = (text or "").split()
    chunks: list[list[str]] = []
    cur: list[str] = []
    for w in words:
        cur.append(w)
        chars = len(" ".join(cur))
        if len(cur) >= MAX_WORDS or (len(cur) >= MIN_WORDS and (re.search(r"[.!?,;:]$", w) or chars >= MAX_CHARS)):
            chunks.append(cur)
            cur = []
    if cur:
        if len(cur) < MIN_WORDS and chunks and len(chunks[-1]) < MAX_WORDS:
            chunks[-1].extend(cur)
        else:
            chunks.append(cur)
    return chunks


def time_segment(text: str, start: float, duration: float) -> list[Cue]:
    """Cues for one segment spread over [start, start+duration]."""
    chunks = chunk_words(text)
    if not chunks or duration <= 0:
        return []
    weights = [sum(len(w) + 2 for w in c) for c in chunks]
    total = sum(weights)
    cues, t = [], start
    for c, wgt in zip(chunks, weights):
        span = duration * wgt / total
        cues.append(Cue(t, t + span, " ".join(c)))
        t += span
    return cues


def _norm_word(w: str) -> str:
    return re.sub(r"[^a-z0-9]", "", w.lower())


def time_segment_words(text: str, start: float, duration: float,
                       words: list[tuple[str, float, float]] | None) -> list[Cue]:
    """Cues timed from real word timestamps (relative to the segment). Falls back to the estimate
    when the timestamps don't line up with the script's words."""
    chunks = chunk_words(text)
    timed = [(w, s, e) for w, s, e in (words or []) if _norm_word(w)]
    script_words = [w for c in chunks for w in c if _norm_word(w)]
    if not chunks or not timed or abs(len(timed) - len(script_words)) > max(2, 0.15 * len(script_words)):
        return time_segment(text, start, duration)
    cues, i = [], 0
    for c in chunks:
        n = sum(1 for w in c if _norm_word(w))
        if n == 0 or i >= len(timed):
            continue
        first, last = timed[i], timed[min(i + n, len(timed)) - 1]
        cues.append(Cue(start + first[1], start + last[2], " ".join(c)))
        i += n
    if not cues:
        return time_segment(text, start, duration)
    end_limit = start + duration
    for a, b in zip(cues, cues[1:]):  # no flicker: hold each chunk until the next one starts
        if b.start - a.end < 0.35:
            a.end = b.start
    for c in cues:
        c.start, c.end = min(c.start, end_limit), min(max(c.end, c.start + 0.2), end_limit + 0.3)
    return cues


# ---------------------------------------------------------------- SRT
def _srt_time(t: float) -> str:
    ms = int(round(max(0.0, t) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues: list[Cue], path: Path) -> None:
    blocks = [f"{i}\n{_srt_time(c.start)} --> {_srt_time(c.end)}\n{c.text}\n" for i, c in enumerate(cues, 1)]
    path.write_text("\n".join(blocks), encoding="utf-8")


# ---------------------------------------------------------------- ASS
@dataclass
class CaptionStyle:
    width: int
    height: int
    font: str = "Inter"
    size: int = 84
    margin_v: int = 520       # distance from the bottom edge
    margin_h: int = 90
    outline: int = 7
    shadow: int = 3
    primary: RGB = (255, 255, 255)
    outline_color: RGB = (0, 0, 0)
    bold: bool = True
    pop: bool = True          # small scale-in on each chunk

    @classmethod
    def for_format(cls, fmt: str, font: str, accent: RGB | None = None) -> "CaptionStyle":
        if fmt == "long":
            return cls(1920, 1080, font, size=60, margin_v=90, margin_h=200, outline=5, shadow=2, pop=False)
        return cls(1080, 1920, font)


def _ass_color(rgb: RGB, alpha: int = 0) -> str:
    r, g, b = rgb
    return f"&H{alpha:02X}{b:02X}{g:02X}{r:02X}"


def _ass_time(t: float) -> str:
    cs = int(round(max(0.0, t) * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h:d}:{m:02d}:{s:02d}.{cs:02d}"


def _ass_text(text: str) -> str:
    return text.replace("\\", "/").replace("{", "(").replace("}", ")").replace("\n", " ")


def write_ass(cues: list[Cue], style: CaptionStyle, path: Path, offset: float = 0.0) -> None:
    """Write an ASS file; cue times are shifted by -offset (per-clip files)."""
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {style.width}
PlayResY: {style.height}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{style.font},{style.size},{_ass_color(style.primary)},{_ass_color(style.primary)},{_ass_color(style.outline_color)},{_ass_color((0, 0, 0), 0x60)},{-1 if style.bold else 0},0,0,0,100,100,0,0,1,{style.outline},{style.shadow},2,{style.margin_h},{style.margin_h},{style.margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    pop = r"{\fscx86\fscy86\t(0,90,\fscx100\fscy100)}" if style.pop else ""
    lines = [f"Dialogue: 0,{_ass_time(c.start - offset)},{_ass_time(c.end - offset)},Cap,,0,0,0,,{pop}{_ass_text(c.text)}"
             for c in cues if c.end - offset > 0]
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
