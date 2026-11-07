"""Caption/title fitting shared by adapters.

Rule: drop hashtags first (from the end), then shorten the body, and never
cut a protected span such as the AI/ad disclosure.
"""
from __future__ import annotations

import re

HASHTAG = re.compile(r"(?<![\w#])#\w+", re.UNICODE)


def count_hashtags(text: str) -> int:
    return len(HASHTAG.findall(text))


def _drop_last_hashtag(text: str, protected: list[str]) -> str | None:
    spans = _protected_spans(text, protected)
    for m in reversed(list(HASHTAG.finditer(text))):
        if any(a <= m.start() < b for a, b in spans):
            continue
        start, end = m.start(), m.end()
        if start > 0 and text[start - 1] == " ":
            start -= 1
        return text[:start] + text[end:]
    return None


def _protected_spans(text: str, protected: list[str]) -> list[tuple[int, int]]:
    out = []
    for p in protected:
        if p and (i := text.find(p)) >= 0:
            out.append((i, i + len(p)))
    return out


def _tidy(text: str) -> str:
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fit_caption(text: str, max_chars: int, max_hashtags: int | None = None,
                protected: list[str] | None = None, length=len) -> str:
    """Fit `text` to platform limits.

    1. Remove trailing hashtags until at most `max_hashtags` remain.
    2. Remove more hashtags while longer than `max_chars`.
    3. Shorten unprotected text before the first protected span (with an
       ellipsis); protected spans (disclosures) are always kept verbatim.
    `length` lets callers count differently (e.g. UTF-8 bytes).
    """
    protected = [p for p in (protected or []) if p and p in text]
    if max_hashtags is not None:
        while count_hashtags(text) > max_hashtags:
            nxt = _drop_last_hashtag(text, protected)
            if nxt is None:
                break
            text = nxt
    text = _tidy(text)
    while length(text) > max_chars:
        nxt = _drop_last_hashtag(text, protected)
        if nxt is None:
            break
        text = _tidy(nxt)
    if length(text) <= max_chars:
        return text
    keep = "\n\n".join(protected)
    if length(keep) >= max_chars:
        return keep  # disclosure alone is at the limit; never cut it
    body = text
    for p in protected:
        body = body.replace(p, "")
    body = _tidy(body)
    budget = max_chars - length(keep) - (length("\n\n") if keep else 0)
    while body and length(body + "…") > budget:
        body = body[: max(0, len(body) - max(1, (length(body + "…") - budget)))]
        body = body.rstrip()
    body = (body + "…") if body else ""
    return _tidy("\n\n".join(x for x in [body, keep] if x))


def clean_youtube_text(text: str) -> str:
    """YouTube rejects '<' and '>' in titles and descriptions."""
    return text.replace("<", "‹").replace(">", "›")


def utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))


def utf16_len(text: str) -> int:
    return len(text.encode("utf-16-le")) // 2


_DISCLOSURE_LINE = re.compile(r"(#ad\b|#sponsored|#affiliate|affiliate|paid partnership|sponsored|commission|made with ai|ai[- ]generated)", re.I)


def disclosures(caption: str, brand_disclosure: str = "") -> list[str]:
    """Spans that must survive trimming: the brand's AI disclosure plus any
    caption line that reads like an ad/affiliate/AI disclosure."""
    out = [brand_disclosure] if brand_disclosure else []
    for line in caption.splitlines():
        s = line.strip()
        if s and _DISCLOSURE_LINE.search(s) and s not in out and not all(w.startswith("#") for w in s.split()):
            out.append(s)
    return out
