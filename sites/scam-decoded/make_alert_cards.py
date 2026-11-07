"""'Scam alert of the day' cards from the alerts in content/alerts/ (1080x1350, Instagram's 4:5 feed size).

    python3 make_alert_cards.py   ->  ../../launch/scam-decoded/alert-cards/<date>-<slug>.png + CARDS.md

Each card: the scam's name, the example message with its giveaways circled in red (the alert's `flags`, numbered to
match its 3 tells), the tells, the 3 steps, and the official source with the alert's date. CARDS.md has a caption for
each card and the weekday posting plan (08:30, a slot no other plan uses). Rerun after adding or editing an alert.
Needs Pillow and the Inter font (falls back to DejaVu Sans).
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import build as B

HERE = Path(__file__).resolve().parent
OUT = HERE.parent.parent / "launch" / "scam-decoded" / "alert-cards"
W, H, M = 1080, 1350, 64
NAVY, CREAM, TEAL, AMBER, MUTED, RED, PINK, INK = ("#0d1b2a", "#f4f1ea", "#2ec4b6", "#ff9f1c", "#9fb0c0", "#d7263d",
                                                   "#ffe1e4", "#0d1b2a")
TIME = "08:30"
HASHTAGS = ["scamalert", "scamawareness", "fraudprevention", "staysafeonline", "scamdecoded"]


def font(weight: str, size: int):
    for p in (f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf",
              f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if weight != 'Regular' else ''}.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def wrap(d: ImageDraw.ImageDraw, text: str, f, width: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def flagged_words(example: str, flags: list[str]) -> list[tuple[str, int]]:
    """Each word of the example with the 1-based flag it belongs to (0 = none)."""
    spans = []
    for k, ph in enumerate(flags, 1):
        i = example.find(ph)
        spans.append((i, i + len(ph), k))
    out = []
    for m in re.finditer(r"\S+", example):
        k = next((k for a, b, k in spans if m.start() < b and m.end() > a), 0)
        out.append((m.group(), k))
    return out


def badge(d, x, y, n, r=17, fill=RED):
    d.ellipse((x, y, x + 2 * r, y + 2 * r), fill=fill)
    f = font("Bold", 22)
    d.text((x + r, y + r), str(n), font=f, fill="white", anchor="mm")


def message_block(d, y, words, f, width, x0, lh) -> int:
    """Draw the example word by word; flagged runs get a pink highlight, a red underline and a number badge."""
    x, line = x0, []
    lines = [[]]
    seen = set()
    for w, k in words:
        extra = 40 if k and k not in seen else 0
        wl = d.textlength(w + " ", font=f) + extra
        if x + wl > x0 + width and lines[-1]:
            lines.append([])
            x = x0
        lines[-1].append((w, k, k and k not in seen))
        if k:
            seen.add(k)
        x += wl
    for ln in lines:
        x = x0
        for j, (w, k, first) in enumerate(ln):
            joined = k and j + 1 < len(ln) and ln[j + 1][1] == k  # highlight runs on through the space
            if first:
                badge(d, x, y + 3, k)
                x += 40
            wl = d.textlength(w, font=f)
            sp = d.textlength(" ", font=f)
            if k:
                end = x + wl + (sp if joined else 3)
                d.rectangle((x - 3, y + 2, end, y + lh - 6), fill=PINK)
                d.line((x - 3, y + lh - 6, end, y + lh - 6), fill=RED, width=3)
            d.text((x, y), w, font=f, fill=INK)
            x += wl + sp
        y += lh
    return y


def card(a: dict) -> Image.Image:
    for scale in (1.24, 1.16, 1.08, 1.0, 0.94, 0.88, 0.82, 0.76):  # largest text that fits
        im = Image.new("RGB", (W, H), NAVY)
        d = ImageDraw.Draw(im)
        label, bg, fg = B.SEVERITY[a["severity"]]
        date = dt.date.fromisoformat(str(a["alert_date"]))
        d.rectangle((0, 0, W, 96), fill=bg)
        d.text((M, 48), f"SCAM ALERT OF THE DAY · {date.strftime('%a %b')} {date.day}".upper(), font=font("Bold", 30),
                fill=fg, anchor="lm")
        d.text((W - M, 48), label.upper(), font=font("Bold", 24), fill=fg, anchor="rm")
        y = 128
        tf = font("ExtraBold", int(54 * scale))
        for ln in wrap(d, a["scam"], tf, W - 2 * M):
            d.text((M, y), ln, font=tf, fill=CREAM)
            y += int(64 * scale)
        y += 6
        d.text((M, y), f"Arrives by: {a['channel']} · fictional example", font=font("Regular", int(26 * scale)), fill=MUTED)
        y += int(48 * scale)
        mf, lh = font("Medium", int(32 * scale)), int(46 * scale)
        words = flagged_words(a["example"], a["flag_list"])
        top = y
        probe = ImageDraw.Draw(Image.new("RGB", (W, H)))
        bottom = message_block(probe, top + 26, words, mf, W - 2 * M - 56, M + 28, lh) + 18
        d.rounded_rectangle((M, top, W - M, bottom), radius=26, fill="#eef2f4")
        message_block(d, top + 26, words, mf, W - 2 * M - 56, M + 28, lh)
        y = bottom + int(34 * scale)
        hf, bf, blh = font("Bold", int(30 * scale)), font("Regular", int(27 * scale)), int(36 * scale)
        for head, key, color in (("The giveaways", "tell", RED), ("Do this", "do", TEAL)):
            d.text((M, y), head.upper(), font=hf, fill=AMBER if key == "do" else "#ff8a96")
            y += int(46 * scale)
            for n in (1, 2, 3):
                badge(d, M, y, n, r=16, fill=color)
                for ln in wrap(d, a[f"{key}_{n}"], bf, W - 2 * M - 52):
                    d.text((M + 52, y), ln, font=bf, fill=CREAM)
                    y += blh
                y += int(12 * scale)
            y += int(18 * scale)
        foot = H - 112
        if y <= foot:
            d.line((M, foot, W - M, foot), fill="#24384c", width=2)
            src = f"Source: {a['source_title']}"
            sf = font("Regular", 22)
            src = wrap(d, src, sf, W - 2 * M)[0] + ("…" if len(wrap(d, src, sf, W - 2 * M)) > 1 else "")
            d.text((M, foot + 20), src, font=sf, fill=MUTED)
            d.text((M, foot + 56), "SCAM DECODED · free scam checker, link in bio", font=font("Bold", 24), fill=TEAL)
            return im
    raise SystemExit(f"alert {a['slug']}: too much text for one card; shorten the tells or steps")


def caption(a: dict) -> str:
    tells = " ".join(f"{n}) {a[f'tell_{n}']}" for n in (1, 2, 3))
    return (f"Scam alert: {a['scam']}.\n\nThe giveaways: {tells}\n\nWhat to do: {a['do_1']}\n\n"
            f"Source: {a['source_title']} ({a['source_url']}). The example on the card is made up.\n\n"
            "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends "
            "nothing anywhere.\n\n" + " ".join("#" + h for h in HASHTAGS))


def draft_card(path: Path) -> Path:
    """Card for a draft alert (new_alert.py --text), written to alert-cards/drafts/ for review."""
    if not B.CFG:
        B.CFG = B.load_config()
    a, _ = B.parse_front_matter(path.read_text())
    a["slug"] = re.sub(r"^\d+-", "", path.stem)
    a["flag_list"] = [x.strip() for x in str(a.get("flags", "")).split("|") if x.strip()]
    for n in (1, 2, 3):
        for k in ("tell", "do"):
            a.setdefault(f"{k}_{n}", "")
    a["severity"] = a.get("severity") if a.get("severity") in B.SEVERITY else "warning"
    (OUT / "drafts").mkdir(parents=True, exist_ok=True)
    out = OUT / "drafts" / f"{a['alert_date']}-{a['slug']}.png"
    im = card(a)
    d = ImageDraw.Draw(im)
    d.rectangle((W - 360, 0, W, 96), fill=RED)  # can't be mistaken for a reviewed card
    d.text((W - M, 48), "DRAFT · NOT CHECKED", font=font("Bold", 26), fill="white", anchor="rm")
    im.save(out, optimize=True)
    return out


def main() -> list[Path]:
    B.CFG = B.load_config()
    alerts = [a for a in B.alert_items() if a["flag_list"]]
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()
    rows, caps, paths = [], [], []
    for a in alerts:
        date = dt.date.fromisoformat(str(a["alert_date"]))
        p = OUT / f"{date.isoformat()}-{a['slug']}.png"
        card(a).save(p, optimize=True)
        paths.append(p)
        wk = "" if date.weekday() < 5 else " (weekend: move to the next weekday)"
        rows.append(f"| {date.strftime('%a %b')} {date.day}{wk} | {TIME} | {a['severity']} | {a['scam']} | `{p.name}` |")
        caps.append(f"### {date.isoformat()}: {a['scam']}\n\nImage: `{p.name}`\n\n```\n{caption(a)}\n```\n")
    md = ["# Scam alert of the day: cards", "",
          "One image per weekday, from the alerts in `sites/scam-decoded/content/alerts/`. Post at 08:30 America/New_York "
          "(no other plan uses that slot) as an Instagram feed post and a TikTok photo post. Nothing has been posted; "
          "Dhruv posts each by hand.", "",
          "Rebuild after adding an alert: `python3 new_alert.py \"...\"`, fill it in (including `flags`), then "
          "`python3 make_alert_cards.py` from `sites/scam-decoded/`. Check the source page that morning: if the "
          "official advice changed, edit the alert first.", "",
          "Gaps: the plan has a card only on days with an alert. Write the next alert a few days ahead so the "
          "weekday run doesn't break, and keep each one tied to an official FTC, FBI/IC3 or BBB page.", "",
          "| Date | Time | Severity | Scam | Image |", "|---|---|---|---|---|", *rows, "", "## Captions", "", *caps]
    (OUT / "CARDS.md").write_text("\n".join(md))
    print(f"wrote {len(paths)} cards to {OUT}")
    return paths


if __name__ == "__main__":
    main()
