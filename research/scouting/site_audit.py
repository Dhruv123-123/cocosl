"""Measure how much wording the pages of a built static site share (thin/scaled-content check).

    python research/scouting/site_audit.py site/public budget cost-of-living debt-payoff blog compare

For each section, compares every page's main text (digits removed, so only wording counts) with the
other pages in that section using 5-word sequences. Prints the median word count, the median and highest
overlap with another page, and the median "unique share": the fraction of a page's 5-word sequences found
on no other page. A unique share near 0 means the pages differ only in their numbers.
"""
from __future__ import annotations

import html
import itertools
import re
import statistics
import sys
from pathlib import Path


def page_text(path: Path) -> str:
    s = path.read_text(errors="ignore")
    if 'http-equiv="refresh"' in s:
        return ""  # redirect stub
    m = re.search(r"<main.*?</main>", s, re.S) or re.search(r"<body.*?</body>", s, re.S)
    s = m.group(0) if m else s
    s = re.sub(r"<(script|style|nav|header|footer)[^>]*>.*?</\1>", " ", s, flags=re.S)
    return html.unescape(re.sub(r"<[^>]+>", " ", s)).lower()


def shingles(text: str, n: int = 5) -> tuple[set, int]:
    words = re.findall(r"[a-z]+", text)
    return set(zip(*[words[i:] for i in range(n)])), len(words)


def audit(root: Path, section: str) -> dict | None:
    pages = {p.parent.name: shingles(page_text(p)) for p in sorted((root / section).glob("*/index.html"))}
    pages = {k: v for k, v in pages.items() if v[1] > 50}
    if len(pages) < 2:
        return None
    pairs = [(len(a[0] & b[0]) / max(1, len(a[0] | b[0])), x, y)
             for (x, a), (y, b) in itertools.combinations(pages.items(), 2)]
    unique = []
    for k, (s, _) in pages.items():
        others = set().union(*(v[0] for kk, v in pages.items() if kk != k))
        unique.append(len(s - others) / max(1, len(s)))
    top = max(pairs)
    return {"section": section, "pages": len(pages), "words": statistics.median(v[1] for v in pages.values()),
            "overlap_median": statistics.median(p[0] for p in pairs), "overlap_max": top[0],
            "closest_pair": f"{top[1]} / {top[2]}", "unique_median": statistics.median(unique)}


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    root = Path(argv[1])
    for section in argv[2:]:
        r = audit(root, section)
        if not r:
            print(f"{section}: fewer than 2 pages")
            continue
        print(f"{r['section']}: {r['pages']} pages, {r['words']:.0f} words median, overlap median "
              f"{r['overlap_median']:.0%} max {r['overlap_max']:.0%} ({r['closest_pair']}), "
              f"unique share median {r['unique_median']:.0%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
