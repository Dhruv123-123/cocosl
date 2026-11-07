"""Share images for /quiz/score/N/ (1200x630, the size link previews use).

    python3 make_quiz_cards.py   ->  static/img/quiz/score-0.png ... score-12.png

Rerun after changing the tiers or the number of questions in content/quiz.json. Needs Pillow and the Inter font
(falls back to DejaVu Sans).
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "static" / "img" / "quiz"
NAVY, CREAM, TEAL, AMBER, MUTED = "#0d1b2a", "#f4f1ea", "#2ec4b6", "#ff9f1c", "#c9d3dc"


def font(weight: str, size: int):
    for p in (f"/usr/share/fonts/opentype/inter/Inter-{weight}.otf",
              f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if weight != 'Regular' else ''}.ttf"):
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def card(score: int, total: int, tier: str, site: str) -> Image.Image:
    im = Image.new("RGB", (1200, 630), NAVY)
    d = ImageDraw.Draw(im)
    d.polygon([(90, 70), (130, 84), (130, 116), (90, 146), (50, 116), (50, 84)], fill=TEAL)
    d.text((150, 84), "SCAM DECODED · COULD YOU SPOT IT?", font=font("Bold", 34), fill=CREAM)
    d.text((70, 170), f"{score}/{total}", font=font("ExtraBold", 230), fill=AMBER)
    d.text((70, 430), tier, font=font("ExtraBold", 64), fill=CREAM)
    d.text((70, 515), f"12 messages. Scam or legit? Can you beat {score}?", font=font("Regular", 34), fill=MUTED)
    d.text((70, 565), site.replace("https://", "") + "/quiz/", font=font("Bold", 30), fill=TEAL)
    return im


def main():
    q = json.loads((HERE / "content" / "quiz.json").read_text())
    site = json.loads((HERE / "site.json").read_text())["url"].rstrip("/")
    total = len(q["questions"])
    OUT.mkdir(parents=True, exist_ok=True)
    for s in range(total + 1):
        tier = next(t for t in q["tiers"] if s >= t["min"])["name"]
        card(s, total, tier, site).save(OUT / f"score-{s}.png", optimize=True)
    print(f"wrote {total + 1} cards to {OUT}")


if __name__ == "__main__":
    main()
