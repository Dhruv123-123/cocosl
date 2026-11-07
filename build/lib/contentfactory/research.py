"""Grounding material for scripts.

Pulls short, citable background from Wikipedia's public REST API so the writer
works from sources instead of memory, and the reviewer gets links to check.
Network failures return nothing; the writer then flags more claims to verify.
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx

UA = {"User-Agent": "contentfactory/0.1 (research; https://github.com/)"}


@dataclass
class Source:
    title: str
    url: str
    extract: str


def wikipedia(query: str, k: int = 3, lang: str = "en", timeout: float = 8.0) -> list[Source]:
    try:
        r = httpx.get(f"https://{lang}.wikipedia.org/w/rest.php/v1/search/page",
                      params={"q": query, "limit": k}, headers=UA, timeout=timeout)
        r.raise_for_status()
        pages = r.json().get("pages", [])
        out = []
        for p in pages[:k]:
            key = p["key"]
            s = httpx.get(f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{key}", headers=UA, timeout=timeout)
            if s.status_code != 200:
                continue
            data = s.json()
            out.append(Source(title=data.get("title", key),
                              url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                              extract=data.get("extract", "")[:1500]))
        return out
    except (httpx.HTTPError, ValueError, KeyError):
        return []


def gather(topic: str, online: bool = True) -> list[Source]:
    return wikipedia(topic) if online else []


def as_prompt(sources: list[Source]) -> str:
    if not sources:
        return ""
    body = "\n\n".join(f"[{i + 1}] {s.title} ({s.url})\n{s.extract}" for i, s in enumerate(sources))
    return ("Background sources (prefer these over memory; cite their URLs in `sources`; anything not "
            f"supported here goes in claims_to_verify):\n\n{body}")
