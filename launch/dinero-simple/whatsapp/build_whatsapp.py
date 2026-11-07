"""Write WHATSAPP_CHANNEL.md (channel setup, how to grow it by hand, and 30 days of messages) from messages.py.
Refuses a bare link (links are [ENLACE: ...] placeholders), a message over 700 characters, or a poll WhatsApp
can't run (2-12 options).

    python launch/dinero-simple/whatsapp/build_whatsapp.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from messages import CHANNEL_NAME, DESCRIPTION, M  # noqa: E402

PLACEHOLDER = re.compile(r"\[ENLACE:[^\]]*\]")
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(com|org|gov|net|app|io|co)\b", re.I)
KINDS = {"bienvenida": "Bienvenida", "consejo": "Consejo del lunes", "alerta": "Alerta de estafa", "numero": "El número de la semana",
         "encuesta": "Encuesta", "hazlo": "Haz esto hoy", "nuevo": "Lo nuevo en Dinero Simple", "pregunta": "Pregunta del domingo"}


def check(day, kind, text, poll) -> None:
    if LINK.search(PLACEHOLDER.sub("", text)):
        raise SystemExit(f"day {day}: bare link")
    if len(text) > 700:
        raise SystemExit(f"day {day}: {len(text)} characters (keep under 700)")
    if poll and not 2 <= len(poll[1]) <= 12:
        raise SystemExit(f"day {day}: a WhatsApp poll needs 2-12 options")
    if kind not in KINDS:
        raise SystemExit(f"day {day}: unknown kind {kind}")


def build() -> str:
    assert [d for d, *_ in M] == list(range(1, 31)), "days 1-30, in order"
    for day, kind, text, poll, _ in M:
        check(day, kind, text, poll)
    out = [f"""# Dinero Simple: WhatsApp Channel kit

A WhatsApp Channel is a one-way broadcast: you post, followers read, react and vote in polls. Followers can't see each other or your number, and you can't see theirs. For this audience, WhatsApp is where family news, prices and warnings already travel, so a channel with one useful message a day can grow by forwarding alone. Nothing in this kit is posted automatically: Dhruv (or whoever runs the channel) posts every message by hand.

## Set up the channel (15 minutes)

1. In WhatsApp, open **Updates** (Novedades) → **+** → **Create channel**. Use the brand phone or a dedicated number, not a personal one, if you can.
2. **Name:** {CHANNEL_NAME}
3. **Description** (paste as is; a fluent speaker checks it first):

   > {DESCRIPTION}

4. **Picture:** the round brand logo from `brand-kit/` (the piggy-bank mascot on coral).
5. **Settings:** allow emoji reactions (they're the main signal you'll get). Turn on the setting that keeps the channel in the public directory once you have a few weeks of posts.
6. Copy the **channel link** (Share → Copy link). Add it to `sites/dinero-simple/site.json` → `"socials"` as `"WhatsApp": "<link>"`, so it shows in the site footer, and rebuild the site. Put it on the Instagram and TikTok bios through the link page, and in the newsletter footer in place of `[ENLACE: canal de WhatsApp]`.

## Posting rules

- **One message a day**, at the same time. 7:30 pm Eastern works for workers after their shift. More than one a day and people mute the channel.
- **Weekly rhythm:**
  - Monday: a tip
  - Tuesday: a scam alert
  - Wednesday: the number of the week
  - Thursday: a poll
  - Friday: "haz esto hoy"
  - Saturday: what's new from Dinero Simple
  - Sunday: a question to think about
- **Short.** Every message fits on one phone screen (under 700 characters). Bold with `*asteriscos*`, italics with `_guiones bajos_`. At most one or two emoji.
- **Links:** the messages use `[ENLACE: ...]` placeholders. Swap each for the real link with `utm_source=whatsapp&utm_medium=channel&utm_campaign=dia-NN`, or delete the line. No more than one message in three should carry a link: the channel earns trust by being useful in the message itself.
- **Polls:** post them as WhatsApp polls (the 📊 attach option), not as text. Next week's Monday tip should follow the winning answer.
- **Same rules as all Spanish copy:** a fluent speaker reviews every message before it goes out, check the facts listed under "Verificar", and anything about immigration sends people to a licensed attorney or DOJ-accredited representative, never a notario.
- Never post anything that names a real person who wrote to you, and never post "testimonials".

## Grow it by hand (no ads, no bought followers, no adding people)

WhatsApp Channels grow by people choosing to follow. Never add anyone to a group or list without asking, and never post the link in groups that don't allow promotion.

1. **Your own circle first (week 1):** send the link one by one to 20 people you know who would find it useful, with a personal line: _"Empecé un canal con consejos de dinero en español, uno al día. Si te sirve, síguelo."_ Post it on your own WhatsApp Status (Estado) twice in the first week.
2. **Everywhere the brand already is (week 1):**
   - The `/links/` page and the bios.
   - The newsletter footer.
   - The end of every long YouTube description.
   - A pinned comment on the best-performing TikTok each week.
   - One line at the end of the welcome email.
3. **Make the messages forwardable (always):** the scam alerts get forwarded the most. End some of them with "Reenvíaselo a quien...". Every forward shows the channel name.
4. **Partners and workshops (month 2 on):** print the channel's QR code (Share → QR) on the workshop worksheets and the B2B partner one-pager (`partners-b2b/`). Ask partner organizations if they'd share the link with their members, by hand, with their permission.
5. **Answer, don't spam:** in Facebook groups and Quora (`ANSWER_BANK.md`), answer the question fully, with no link. Put the channel link in your profile only.
6. **Measure weekly:** followers, reactions per message and poll votes, in a simple table. Keep the message types that get reactions; drop the ones that don't.

## The first 30 days
"""]
    for day, kind, text, poll, check_ in M:
        block = f"\n### Día {day} · {KINDS[kind]}\n\n```\n{text}\n```\n"
        if poll:
            block += f"\n**Encuesta de WhatsApp:** {poll[0]}\n" + "".join(f"- {o}\n" for o in poll[1])
        block += f"\n*{len(text)} caracteres*\n"
        block += "".join(f"- [ ] Verificar: {c}\n" for c in check_) + "- [ ] Revisión de hablante nativo\n"
        out.append(block)
    return "\n".join(out)


def main() -> None:
    (HERE.parent / "WHATSAPP_CHANNEL.md").write_text(build())
    print(f"Wrote WHATSAPP_CHANNEL.md ({len(M)} messages)")


if __name__ == "__main__":
    main()
