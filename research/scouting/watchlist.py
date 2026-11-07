"""Weekly snapshot of public numbers for accounts on watchlist.csv.

Uses only Instagram's official Business Discovery API, called with our own
Instagram Business/Creator account. No scraping, no logins, no downloads of
other people's media. Only Business/Creator accounts can be looked up; personal
accounts come back as errors and are skipped.

Needs (same values `factory auth meta` writes to .env):
  IG_USER_ID       our Instagram professional account id
  IG_ACCESS_TOKEN  a Facebook Login user token with instagram_basic,
                   instagram_manage_insights and pages_read_engagement
Business Discovery is a Facebook Login feature: it does not work with
IG_API_HOST=graph.instagram.com (Instagram Login tokens).

Usage:
  python research/scouting/watchlist.py                     # writes snapshots/<date>.csv
  python research/scouting/watchlist.py --compare           # also prints follower change vs the last snapshot

Run it weekly. Per account it records followers, post count, and for the last
12 posts the average likes and comments and the share of Reels vs carousels.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import sys
import time
from pathlib import Path

import httpx

HERE = Path(__file__).resolve().parent
GRAPH = "https://graph.facebook.com/v25.0"
FIELDS = ("followers_count,media_count,"
          "media.limit(12){timestamp,media_type,media_product_type,like_count,comments_count}")
# Fallback if the Graph API version rejects media_product_type on discovered media
# (then Reels are counted from media_type == VIDEO instead).
FIELDS_BASIC = "followers_count,media_count,media.limit(12){timestamp,media_type,like_count,comments_count}"
COLUMNS = ["date", "username", "followers", "posts", "avg_likes_12", "avg_comments_12",
           "eng_rate_pct", "reels_share", "carousel_share", "last_post", "error"]


def snapshot_one(client: httpx.Client, user_id: str, token: str, username: str) -> dict:
    row = {c: "" for c in COLUMNS}
    row.update(date=dt.date.today().isoformat(), username=username)
    for fields in (FIELDS, FIELDS_BASIC):
        resp = client.get(f"{GRAPH}/{user_id}", params={
            "fields": f"business_discovery.username({username}){{{fields}}}", "access_token": token})
        try:
            data = resp.json()
        except ValueError:
            data = {}
        msg = str((data.get("error") or {}).get("message", ""))
        if resp.status_code == 200 or "media_product_type" not in msg:
            break
    if resp.status_code != 200 or "business_discovery" not in data:
        row["error"] = (data.get("error") or {}).get("message", f"HTTP {resp.status_code}")[:160]
        return row
    bd = data["business_discovery"]
    media = (bd.get("media") or {}).get("data", [])
    n = len(media) or 1
    likes = sum(m.get("like_count") or 0 for m in media) / n
    comments = sum(m.get("comments_count") or 0 for m in media) / n
    followers = bd.get("followers_count") or 0
    row.update(
        followers=followers, posts=bd.get("media_count", ""),
        avg_likes_12=round(likes, 1), avg_comments_12=round(comments, 1),
        eng_rate_pct=round((likes + comments) / followers * 100, 2) if followers else "",
        reels_share=round(sum((m.get("media_product_type") or ("REELS" if m.get("media_type") == "VIDEO" else ""))
                              == "REELS" for m in media) / n, 2),
        carousel_share=round(sum(m.get("media_type") == "CAROUSEL_ALBUM" for m in media) / n, 2),
        last_post=(media[0].get("timestamp", "")[:10] if media else ""),
    )
    return row


def read_watchlist(path: Path) -> list[str]:
    with path.open(newline="") as f:
        return [r["username"].strip().lstrip("@") for r in csv.DictReader(f) if r.get("username", "").strip()]


def last_snapshot(out_dir: Path, today: str) -> dict[str, int]:
    files = sorted(p for p in out_dir.glob("*.csv") if p.stem < today)
    if not files:
        return {}
    with files[-1].open(newline="") as f:
        return {r["username"]: int(r["followers"]) for r in csv.DictReader(f) if r.get("followers")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--watchlist", type=Path, default=HERE / "watchlist.csv")
    ap.add_argument("--out", type=Path, default=HERE / "snapshots")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--pause", type=float, default=2.0, help="seconds between lookups (be gentle on rate limits)")
    args = ap.parse_args(argv)

    user_id, token = os.environ.get("IG_USER_ID"), os.environ.get("IG_ACCESS_TOKEN")
    if not user_id or not token:
        print("Set IG_USER_ID and IG_ACCESS_TOKEN (run `factory auth meta` first).", file=sys.stderr)
        return 2

    names = read_watchlist(args.watchlist)
    rows = []
    with httpx.Client(timeout=30) as client:
        for i, name in enumerate(names):
            if i:
                time.sleep(args.pause)
            rows.append(snapshot_one(client, user_id, token, name))

    args.out.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    prev = last_snapshot(args.out, today) if args.compare else {}
    out = args.out / f"{today}.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)

    for r in rows:
        if r["error"]:
            print(f"@{r['username']:<24} skipped: {r['error']}")
            continue
        delta = ""
        if r["username"] in prev and prev[r["username"]]:
            change = r["followers"] - prev[r["username"]]
            delta = f"  {change:+,} ({change / prev[r['username']] * 100:+.1f}%)"
        print(f"@{r['username']:<24} {r['followers']:>11,} followers  eng {r['eng_rate_pct']}%  "
              f"reels {r['reels_share']}  carousels {r['carousel_share']}{delta}")
    print(f"saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
