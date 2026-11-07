"""`factory scorecard`: GO_LIVE.md R8's weekly scorecard, filled in automatically, with stop / change / watch flags.

    factory scorecard                         # every brand, this week, printed
    factory scorecard --brand money-made-simple --save      # also output/scorecards/week-<monday>/<brand>.md
    factory scorecard --manual-template       # writes data/scorecard-manual.yaml to fill the rest by hand

Where the numbers come from (all local, no API calls):
* YouTube and TikTok: the latest `factory stats import` (YouTube Studio / TikTok exports).
* Site: the latest Plausible export (visitors, sign-ups, outbound clicks).
* Instagram reach, saves and sends (shares): the metrics the factory pulled for this brand's posts.
* Money: revenue and affiliate clicks the factory recorded in the last 7 days (log only in month 1).
* Everything only you can see (Pinterest, Etsy, Gumroad, email health, platform warnings) comes from
  data/scorecard-manual.yaml (`--manual-template` writes it with every field blank; blanks are fine).

Flags follow R8's table (research/scouting/launch-metrics-30-days.md): each rule has a minimum sample and a
first day, counted from the launch day (FACTORY_LAUNCH_DATE, else the first post that went out). A rule
without its sample or before its day is "not yet", never a flag. Day 30 adds the go / drop step.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

import yaml

MANUAL_FIELDS = {
    "instagram": ["reach", "sends", "non_follower_pct", "saves"],
    "pinterest": ["pins", "impressions", "saves", "outbound_clicks"],
    "etsy": ["visits", "listings", "listings_under_20_visits", "orders"],
    "gumroad": ["views", "sales"],
    "email": ["sent", "welcome_opens_pct", "clicks_pct", "unsubs_pct", "bounces_pct", "complaints_pct"],
    "warnings": ["any_warning"],
    "money": ["orders", "revenue", "affiliate_clicks"],
    "notes": ["one_change"],
}


@dataclass
class Flag:
    severity: str   # stop | change | watch | go
    rule: str
    value: str
    status: str = "flag"  # flag | ok | not_yet


def _num(v):
    try:
        return None if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return None


def manual_path(factory) -> Path:
    return factory.settings.home / "data" / "scorecard-manual.yaml"


def load_manual(factory, slug: str) -> dict:
    p = manual_path(factory)
    if not p.is_file():
        return {}
    data = yaml.safe_load(p.read_text()) or {}
    return data.get(slug) or {}


def template(factory) -> Path:
    p = manual_path(factory)
    p.parent.mkdir(parents=True, exist_ok=True)
    existing = yaml.safe_load(p.read_text()) if p.is_file() else {}
    data = {}
    for slug in factory.brands():
        cur = (existing or {}).get(slug) or {}
        data[slug] = {k: {f: (cur.get(k) or {}).get(f, None) for f in fields} for k, fields in MANUAL_FIELDS.items()}
    p.write_text("# Numbers only you can see, for `factory scorecard`. Fill in what you have each Monday;\n"
                 "# leave the rest blank. Percentages as plain numbers (2.5 = 2.5%). any_warning: true/false.\n"
                 + yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
    return p


def collect(factory, slug: str, day: date | None = None) -> dict:
    from .routine import launch_day
    from .stats import scorecard as stats_card
    day = day or date.today()
    monday = day - timedelta(days=day.weekday())
    card = stats_card(factory, slug)
    m = load_manual(factory, slug)
    yt = card["platforms"].get("youtube") or {}
    tt = card["platforms"].get("tiktok") or {}
    site = card["site"] or {}
    since = (day - timedelta(days=7)).isoformat()
    ig = factory.db.query(
        """SELECT COALESCE(SUM(m.reach), 0) reach, COALESCE(SUM(m.saves), 0) saves, COALESCE(SUM(m.shares), 0) shares
           FROM metrics m JOIN publications p ON p.id = m.publication_id JOIN posts s ON s.id = p.post_id
           WHERE s.brand = ? AND p.platform = 'instagram' AND m.id IN
             (SELECT MAX(id) FROM metrics GROUP BY publication_id) AND m.captured_at >= ?""", [slug, since])[0]
    mig = m.get("instagram") or {}
    reach = _num(mig.get("reach")) or ig["reach"] or None
    sends = _num(mig.get("sends")) if _num(mig.get("sends")) is not None else (ig["shares"] if ig["reach"] else None)
    money = factory.db.query("SELECT COUNT(*) n, COALESCE(SUM(amount_cents), 0) c FROM revenue WHERE brand = ? AND date >= ?",
                             [slug, since])[0]
    start = launch_day(factory)
    vals = {
        "yt_impressions": yt.get("impressions"), "yt_ctr": yt.get("ctr"), "yt_watch_hours": yt.get("watch_hours"),
        "yt_subs": yt.get("subscribers"),
        "tt_posts": tt.get("videos"), "tt_avg_views": round(tt["views"] / tt["videos"]) if tt.get("videos") else None,
        "ig_reach": reach, "ig_sends_per_1k": round(sends / reach * 1000, 1) if reach and sends is not None else None,
        "ig_non_follower_pct": _num(mig.get("non_follower_pct")),
        "ig_saves": _num(mig.get("saves")) if _num(mig.get("saves")) is not None else (ig["saves"] if ig["reach"] else None),
        "site_visitors": site.get("visitors"), "site_signups": site.get("signups"), "site_clicks": site.get("clicks"),
    }
    vals["site_signup_pct"] = round(vals["site_signups"] / vals["site_visitors"] * 100, 1) \
        if vals["site_visitors"] else None
    for k, fields in MANUAL_FIELDS.items():
        for f in fields:
            vals.setdefault(f"{k}_{f}", _num((m.get(k) or {}).get(f)) if f not in ("any_warning", "one_change")
                            else (m.get(k) or {}).get(f))
    if vals["money_orders"] is None and money["n"]:
        vals["money_orders"], vals["money_revenue"] = money["n"], money["c"] / 100
    if vals["money_affiliate_clicks"] is None:
        vals["money_affiliate_clicks"] = factory.db.scalar("SELECT COALESCE(SUM(clicks), 0) FROM affiliate_links WHERE brand = ?",
                                                           [slug]) or None
    if vals["etsy_listings"] and vals["etsy_listings_under_20_visits"] is not None:
        vals["etsy_under_20_pct"] = round(vals["etsy_listings_under_20_visits"] / vals["etsy_listings"] * 100)
    else:
        vals["etsy_under_20_pct"] = None
    vals["etsy_conv_pct"] = round(vals["etsy_orders"] / vals["etsy_visits"] * 100, 2) if vals["etsy_visits"] and vals["etsy_orders"] is not None else None
    vals["gumroad_conv_pct"] = round(vals["gumroad_sales"] / vals["gumroad_views"] * 100, 2) if vals["gumroad_views"] and vals["gumroad_sales"] is not None else None
    n = (day - start).days if start else None
    return {"brand": slug, "monday": monday, "day": n, "v": vals, "flags": flags(vals, n)}


def flags(v: dict, day: int | None) -> list[Flag]:
    d = day if day is not None else 0
    out: list[Flag] = []

    def rule(sev, text, first_day, have, bad, shown):
        if not have or d < first_day:
            out.append(Flag(sev, text, shown, "not_yet"))
        else:
            out.append(Flag(sev, text, shown, "flag" if bad else "ok"))

    g = lambda k: v.get(k)
    warn = g("warnings_any_warning")
    rule("stop", "any platform warning", 1, warn is not None, bool(warn), "yes" if warn else "no" if warn is not None else "-")
    rule("stop", "email bounces > 2%", 1, g("email_bounces_pct") is not None, (g("email_bounces_pct") or 0) > 2, f"{g('email_bounces_pct')}%")
    rule("stop", "spam complaints > 0.1%", 1, g("email_complaints_pct") is not None, (g("email_complaints_pct") or 0) > 0.1, f"{g('email_complaints_pct')}%")
    rule("change", "YouTube CTR < 2% (after 1,000 impressions)", 14, (g("yt_impressions") or 0) >= 1000 and g("yt_ctr") is not None,
         (g("yt_ctr") or 0) < 2, f"{g('yt_ctr')}%")
    rule("change", "site sign-ups < 2% (after 200 visitors)", 14, (g("site_visitors") or 0) >= 200, (g("site_signup_pct") or 0) < 2,
         f"{g('site_signup_pct')}%")
    rule("change", "Etsy: over half the listings < 20 visits", 14, g("etsy_under_20_pct") is not None, (g("etsy_under_20_pct") or 0) > 50,
         f"{g('etsy_under_20_pct')}%")
    rule("change", "welcome opens < 30%", 14, g("email_welcome_opens_pct") is not None, (g("email_welcome_opens_pct") or 0) < 30,
         f"{g('email_welcome_opens_pct')}%")
    rule("change", "Instagram sends < 2 per 1,000 reach (after 2,000 reach)", 14, (g("ig_reach") or 0) >= 2000 and g("ig_sends_per_1k") is not None,
         (g("ig_sends_per_1k") or 0) < 2, str(g("ig_sends_per_1k")))
    rule("change", "TikTok avg < 200 views (after 10+ posts)", 21, (g("tt_posts") or 0) >= 10, (g("tt_avg_views") or 0) < 200, str(g("tt_avg_views")))
    rule("change", "Etsy conversion < 0.5% (after 300 visits)", 21, (g("etsy_visits") or 0) >= 300, (g("etsy_conv_pct") or 0) < 0.5, f"{g('etsy_conv_pct')}%")
    rule("change", "Gumroad conversion < 1% (after 150 views)", 21, (g("gumroad_views") or 0) >= 150, (g("gumroad_conv_pct") or 0) < 1, f"{g('gumroad_conv_pct')}%")
    rule("change", "email clicks < 2%", 21, g("email_clicks_pct") is not None, (g("email_clicks_pct") or 0) < 2, f"{g('email_clicks_pct')}%")
    rule("change", "unsubscribes > 0.5% per send", 21, g("email_unsubs_pct") is not None, (g("email_unsubs_pct") or 0) > 0.5, f"{g('email_unsubs_pct')}%")
    rule("change", "YouTube < 500 impressions", 21, g("yt_impressions") is not None, (g("yt_impressions") or 0) < 500, str(g("yt_impressions")))
    rule("watch", "Instagram non-followers < 30% of reach", 21, g("ig_non_follower_pct") is not None, (g("ig_non_follower_pct") or 0) < 30,
         f"{g('ig_non_follower_pct')}%")
    rule("watch", "site < 100 visitors", 21, g("site_visitors") is not None, (g("site_visitors") or 0) < 100, str(g("site_visitors")))
    rule("watch", "YouTube < 50 watch hours", 21, g("yt_watch_hours") is not None, (g("yt_watch_hours") or 0) < 50, str(g("yt_watch_hours")))
    rule("watch", "Pinterest < 10 saves after 20+ pins", 21, (g("pinterest_pins") or 0) >= 20, (g("pinterest_saves") or 0) < 10, str(g("pinterest_saves")))
    imp = g("pinterest_impressions") or 0
    rule("watch", "Pinterest < 20 outbound clicks per 5,000 impressions", 21, imp >= 5000,
         (g("pinterest_outbound_clicks") or 0) / imp * 5000 < 20 if imp else False, str(g("pinterest_outbound_clicks")))
    if d >= 30:
        out.append(Flag("go", "day 30: double the 2 formats that cleared their thresholds, drop the 1 that missed most, "
                        "re-run revenue_model.py with real numbers", "", "flag"))
    return out


def _f(x, suffix=""):
    if x is None or x == "":
        return "____"
    if isinstance(x, float) and x.is_integer():
        x = int(x)
    return f"{x:,}{suffix}" if isinstance(x, int) else f"{x}{suffix}"


def to_text(c: dict) -> str:
    v = c["v"]
    lines = [f"Brand: {c['brand']}   Week of: {c['monday']}   Day since launch: {c['day'] if c['day'] is not None else '__'}", "",
             f"YouTube    impressions {_f(v['yt_impressions'])}  CTR {_f(v['yt_ctr'], '%')}  watch hours {_f(v['yt_watch_hours'])}  subs {_f(v['yt_subs'])}",
             f"TikTok     posts {_f(v['tt_posts'])}  avg views {_f(v['tt_avg_views'])}",
             f"Instagram  reach {_f(v['ig_reach'])}  sends/1,000 reach {_f(v['ig_sends_per_1k'])}  non-follower share {_f(v['ig_non_follower_pct'], '%')}  saves {_f(v['ig_saves'])}",
             f"Pinterest  pins {_f(v['pinterest_pins'])}  impressions {_f(v['pinterest_impressions'])}  saves {_f(v['pinterest_saves'])}  outbound clicks {_f(v['pinterest_outbound_clicks'])}",
             f"Site       visitors {_f(v['site_visitors'])}  sign-ups {_f(v['site_signups'])} (= {_f(v['site_signup_pct'], '%')})  outbound clicks {_f(v['site_clicks'])}",
             f"Etsy       visits {_f(v['etsy_visits'])}  listings under 20 visits {_f(v['etsy_under_20_pct'], '%')}  conversion {_f(v['etsy_conv_pct'], '%')}",
             f"Gumroad    views {_f(v['gumroad_views'])}  sales {_f(v['gumroad_sales'])} (= {_f(v['gumroad_conv_pct'], '%')})",
             f"Email      welcome opens {_f(v['email_welcome_opens_pct'], '%')}  clicks {_f(v['email_clicks_pct'], '%')}  unsubs {_f(v['email_unsubs_pct'], '%')}  "
             f"bounces {_f(v['email_bounces_pct'], '%')}  complaints {_f(v['email_complaints_pct'], '%')}",
             f"Warnings   any strike / reduced distribution / monetization notice?  "
             f"{'Y' if v['warnings_any_warning'] else 'N' if v['warnings_any_warning'] is not None else 'Y / N'}",
             f"Money      orders {_f(v['money_orders'])}  revenue ${_f(v['money_revenue'])}  affiliate clicks {_f(v['money_affiliate_clicks'])}   (log only in month 1)",
             "", f"The ONE change per platform this week: {v.get('notes_one_change') or '______________________________'}", ""]
    labels = {"stop": "STOP (fix today)", "change": "CHANGE (one fix this week)", "watch": "WATCH (act if it holds 2 weeks)", "go": "GO / DROP"}
    hits = [f for f in c["flags"] if f.status == "flag"]
    if hits:
        for sev in ("stop", "change", "watch", "go"):
            for f in [f for f in hits if f.severity == sev]:
                lines.append(f"[{labels[sev]}] {f.rule}" + (f": {f.value}" if f.value else ""))
    else:
        lines.append("No flags this week.")
    waiting = [f.rule for f in c["flags"] if f.status == "not_yet"]
    if waiting:
        lines.append(f"Not yet (sample too small or too early): {len(waiting)} rule(s)")
    return "\n".join(lines) + "\n"


def register(sub, factory_fn) -> None:
    s = sub.add_parser("scorecard", help="GO_LIVE R8 weekly scorecard filled from your imports, with stop/change/watch flags")
    s.add_argument("--brand", default="")
    s.add_argument("--date", type=date.fromisoformat, default=None, help="score as of this day (default today)")
    s.add_argument("--save", action="store_true", help="also write output/scorecards/week-<monday>/<brand>.md")
    s.add_argument("--manual-template", action="store_true", help="write data/scorecard-manual.yaml to fill by hand")

    def cmd(a):
        f = factory_fn(a)
        if a.manual_template:
            print(template(f))
            return
        cards = [collect(f, slug, a.date) for slug in f.brands() if not a.brand or slug == a.brand]
        print("\n".join("```\n" + to_text(c) + "```" if a.save else to_text(c) for c in cards))
        if a.save and cards:
            d = f.settings.output_dir / "scorecards" / f"week-{cards[0]['monday']}"
            d.mkdir(parents=True, exist_ok=True)
            for c in cards:
                (d / f"{c['brand']}.md").write_text(f"# Scorecard: {c['brand']}\n\n```\n{to_text(c)}```\n")
            print(d)
        if any(fl.severity == "stop" and fl.status == "flag" for c in cards for fl in c["flags"]):
            raise SystemExit(2)
    s.set_defaults(func=cmd)
