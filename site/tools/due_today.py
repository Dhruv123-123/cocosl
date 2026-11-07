"""Does anything on the site go live on this date? Used by .github/workflows/netlify-rebuild.yml so the daily
rebuild only spends a Netlify deploy (15 credits on the free plan's 300 a month) on days when a scheduled
article, newsletter issue or seasonal page actually changes the site.

    python3 site/tools/due_today.py [YYYY-MM-DD]   -> prints what's due; exit 0 if something is, 1 if not
"""
from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

CONTENT = Path(__file__).resolve().parents[1] / "content"
# The home page shows the holiday planner only in November and December (build.py), so rebuild when that flips.
SEASON_FLIPS = {(11, 1), (1, 1)}


def due(day: str) -> list[str]:
    found = []
    for folder, key in (("blog", "date"), ("newsletter", "date"), ("compare", "date")):
        for p in sorted((CONTENT / folder).glob("*.md")):
            m = re.search(rf"^{key}:\s*['\"]?(\d{{4}}-\d{{2}}-\d{{2}})", p.read_text(), re.M)
            if m and m.group(1) == day:
                found.append(f"{folder}/{p.name}")
    for p in sorted(CONTENT.glob("*.md")):  # landing pages with a `live:` date (e.g. new-year.md)
        m = re.search(r"^live:\s*['\"]?(\d{4}-\d{2}-\d{2})", p.read_text(), re.M)
        if m and m.group(1) == day:
            found.append(p.name)
    d = date.fromisoformat(day)
    if (d.month, d.day) in SEASON_FLIPS:
        found.append("seasonal home page change")
    return found


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else date.today().isoformat()
    items = due(day)
    print("\n".join(items) if items else f"nothing goes live on {day}")
    sys.exit(0 if items else 1)
