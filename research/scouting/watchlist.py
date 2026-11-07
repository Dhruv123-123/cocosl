"""Weekly snapshot of public numbers for accounts on watchlist.csv.

Official APIs only. No scraping, no logins, no downloads of other people's media.
- instagram rows: Instagram's Business Discovery API, called with our own
  Instagram Business/Creator account. Only Business/Creator accounts can be
  looked up; personal accounts come back as errors and are skipped.
- youtube rows: YouTube Data API v3 channels.list (public subscriber, view and
  video counts) with an API key in YT_API_KEY. Costs 1 quota unit per channel.
- tiktok rows are skipped: TikTok has no official API for looking up other
  accounts outside its academic Research API. Check those by hand.

Instagram needs (same values `factory auth meta` writes to .env):
  IG_USER_ID       our Instagram professional account id
  IG_ACCESS_TOKEN  a Facebook Login user token with instagram_basic,
                   instagram_manage_insights and pages_read_engagement
Business Discovery is a Facebook Login feature: it does not work with
IG_API_HOST=graph.instagram.com (Instagram Login tokens).

YouTube needs YT_API_KEY (Google Cloud console -> YouTube Data API v3 -> API key).

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
SHORT = {"instagram": "ig", "youtube": "yt", "tiktok": "tt"}
YT_CHANNELS = "https://www.googleapis.com/youtube/v3/channels"
COLUMNS = ["date", "platform", "username", "followers", "posts", "avg_likes_12", "avg_comments_12",
           "eng_rate_pct", "reels_share", "carousel_share", "last_post", "error"]


def snapshot_one(client: httpx.Client, user_id: str, token: str, username: str) -> dict:
    row = {c: "" for c in COLUMNS}
    row.update(date=dt.date.today().isoformat(), platform="instagram", username=username)
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


def snapshot_youtube(client: httpx.Client, key: str, handle: str) -> dict:
    row = {c: "" for c in COLUMNS}
    row.update(date=dt.date.today().isoformat(), platform="youtube", username=handle)
    resp = client.get(YT_CHANNELS, params={"part": "statistics", "forHandle": "@" + handle, "key": key})
    try:
        data = resp.json()
    except ValueError:
        data = {}
    items = data.get("items") or []
    if resp.status_code != 200 or not items:
        row["error"] = ((data.get("error") or {}).get("message") or
                        ("no channel with that handle" if resp.status_code == 200 else f"HTTP {resp.status_code}"))[:160]
        return row
    st = items[0].get("statistics", {})
    row.update(followers="" if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
               posts=int(st.get("videoCount", 0)))
    return row


def read_watchlist(path: Path) -> list[tuple[str, str]]:
    """(platform, username) pairs; rows without a platform column are Instagram."""
    with path.open(newline="") as f:
        return [((r.get("platform") or "instagram").strip().lower(), r["username"].strip().lstrip("@"))
                for r in csv.DictReader(f) if r.get("username", "").strip()]


def last_snapshot(out_dir: Path, today: str) -> dict[str, int]:
    files = sorted(p for p in out_dir.glob("*.csv") if p.stem < today)
    if not files:
        return {}
    with files[-1].open(newline="") as f:
        return {f'{r.get("platform") or "instagram"}:{r["username"]}': int(r["followers"])
                for r in csv.DictReader(f) if r.get("followers")}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--watchlist", type=Path, default=HERE / "watchlist.csv")
    ap.add_argument("--out", type=Path, default=HERE / "snapshots")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--pause", type=float, default=2.0, help="seconds between lookups (be gentle on rate limits)")
    args = ap.parse_args(argv)

    user_id, token = os.environ.get("IG_USER_ID"), os.environ.get("IG_ACCESS_TOKEN")
    yt_key = os.environ.get("YT_API_KEY")
    if not (user_id and token) and not yt_key:
        print("Set IG_USER_ID and IG_ACCESS_TOKEN (run `factory auth meta` first) and/or YT_API_KEY.",
              file=sys.stderr)
        return 2

    entries = read_watchlist(args.watchlist)
    rows = []
    with httpx.Client(timeout=30) as client:
        for i, (platform, name) in enumerate(entries):
            if i:
                time.sleep(args.pause)
            if platform == "instagram" and user_id and token:
                rows.append(snapshot_one(client, user_id, token, name))
            elif platform == "youtube" and yt_key:
                rows.append(snapshot_youtube(client, yt_key, name))
            else:
                why = ("no official lookup API; check by hand" if platform == "tiktok"
                       else "credentials for this platform not set")
                rows.append({**{c: "" for c in COLUMNS}, "date": dt.date.today().isoformat(),
                             "platform": platform, "username": name, "error": why})

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
            print(f"{SHORT.get(r['platform'], r['platform'][:2])} @{r['username']:<24} skipped: {r['error']}")
            continue
        delta = ""
        key = f"{r['platform']}:{r['username']}"
        if r["followers"] != "" and prev.get(key):
            change = r["followers"] - prev[key]
            delta = f"  {change:+,} ({change / prev[key] * 100:+.1f}%)"
        followers = f"{r['followers']:>11,}" if r["followers"] != "" else "     hidden"
        extra = (f"  eng {r['eng_rate_pct']}%  reels {r['reels_share']}  carousels {r['carousel_share']}"
                 if r["platform"] == "instagram" else f"  videos {r['posts']}")
        print(f"{SHORT.get(r['platform'], r['platform'][:2])} @{r['username']:<24} {followers} followers{extra}{delta}")
    print(f"saved {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
