"""`factory launch-mode`: launch two brands first (scouting's two-brand plan, research/scouting/two-brand-launch-plan.md).

    factory launch-mode                 # show the current mode
    factory launch-mode two-brand       # only Money Made Simple and Scam Decoded in today, reslot and scorecard
    factory launch-mode two-brand --brands money-made-simple,scam-decoded
    factory launch-mode all             # every brand again (turn it off)

Stored in data/launch-mode.yaml. While it's on, `factory today`, `factory reslot` (without --brand) and
`factory scorecard` leave the other brands out, so a paused brand never eats Dhruv's 15 minutes. Nothing is
deleted or unscheduled: the other brands' posts stay where they are. `factory scorecard --gate` checks the
plan's five gates for adding brand 3.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

TWO_BRAND = ["money-made-simple", "scam-decoded"]


def path(factory) -> Path:
    return Path(factory.settings.home) / "data" / "launch-mode.yaml"


def load(factory) -> dict:
    p = path(factory)
    if not p.is_file():
        return {"mode": "all", "brands": []}
    data = yaml.safe_load(p.read_text()) or {}
    return {"mode": data.get("mode", "all"), "brands": list(data.get("brands") or []), "since": data.get("since", "")}


def active_brands(factory) -> list[str] | None:
    """The brands in play, or None when every brand is (mode all)."""
    m = load(factory)
    if m["mode"] == "all" or not m["brands"]:
        return None
    return [b for b in m["brands"]]


def in_play(factory, slug: str) -> bool:
    act = active_brands(factory)
    return act is None or slug in act


def set_mode(factory, mode: str, brands: list[str] | None = None) -> dict:
    p = path(factory)
    p.parent.mkdir(parents=True, exist_ok=True)
    if mode == "all":
        data = {"mode": "all", "brands": [], "since": date.today().isoformat()}
    else:
        chosen = brands or TWO_BRAND
        known = factory.brands()
        missing = [b for b in chosen if b not in known]
        data = {"mode": mode, "brands": chosen, "since": date.today().isoformat()}
        if missing:
            data["note"] = f"not in brands/ yet: {', '.join(missing)} (they show up once their brand file is merged)"
    p.write_text("# factory launch-mode: which brands today / reslot / scorecard show\n" + yaml.safe_dump(data, sort_keys=False))
    factory.db.log("launch_mode.set", "", None, data)
    return data


def register(sub, factory_fn) -> None:
    s = sub.add_parser("launch-mode", help="two-brand launch: show only MMS + Scam Decoded in today/reslot/scorecard")
    s.add_argument("mode", nargs="?", choices=["show", "two-brand", "all"], default="show")
    s.add_argument("--brands", default="", help="comma-separated brands for two-brand (default MMS, Scam Decoded)")

    def cmd(a):
        f = factory_fn(a)
        if a.mode != "show":
            data = set_mode(f, a.mode, [b.strip() for b in a.brands.split(",") if b.strip()] or None)
            if data.get("note"):
                print(f"Note: {data['note']}")
        m = load(f)
        if m["mode"] == "all":
            print("Launch mode: all brands")
        else:
            print(f"Launch mode: {m['mode']} since {m.get('since') or '?'} · {', '.join(m['brands'])}")
            others = [b for b in f.brands() if b not in m["brands"]]
            if others:
                print(f"Left out of today / reslot / scorecard: {', '.join(others)} (their queued posts stay as they are)")
    s.set_defaults(func=cmd)
