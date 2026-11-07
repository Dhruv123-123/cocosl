"""Write ANSWER_BANK.md from answers.py.   python launch/dinero-simple/community/build_answers.py"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from answers import A  # noqa: E402

LINK = re.compile(r"https?://|www\.|\.(com|org|gov|net|app)\b", re.I)


def build() -> str:
    for _, q, a, _ in A:
        if LINK.search(a):
            raise SystemExit(f"answer has a link: {q}")
    topics = sorted({t for t, *_ in A})
    out = [f"""# Dinero Simple: answer bank for Quora and Facebook groups

{len(A)} Spanish answers to questions our audience asks in Quora en español and in Facebook groups (immigrant communities, Latino moms, neighborhood and job groups). They have no links, on purpose: groups ban self-promotion, and a helpful answer with no link builds more trust than a link. People who want more find the profile.

## Rules for posting

- **Native-speaker review first.** These are machine-written. The reviewer reads them with the rest of the copy.
- **Facts under "Verificar" get checked** before posting, especially anything marked ALTO RIESGO.
- **Post as yourself, by hand.** Put "Hago Dinero Simple, contenido de finanzas en español" in your Quora and Facebook profile, so the affiliation is clear. Never pretend to be a customer or a neutral stranger.
- **Adapt every time.** Answer the exact question asked, change the opening to match the person's situation and cut what doesn't apply. Don't paste the same text in several groups: groups and platforms flag repeated text as spam.
- **No links, no product names, no DMs offering help.** If someone asks where to learn more, say the name of the page and let them look it up, only where group rules allow it.
- **Never give individual legal, tax or immigration advice.** The answers already send those questions to a licensed attorney, an accredited representative, VITA or a nonprofit counselor; keep those lines.
- Read each group's rules before the first answer. About 3 answers a week is plenty.

Topics: {", ".join(topics)}.
"""]
    for n, (t, q, a, check) in enumerate(A, 1):
        words = len(re.findall(r"\w+", a))
        block = f"\n## {n}. {q}\n\n*Tema: {t} · {words} palabras*\n\n{a}\n"
        if check:
            block += "\n**Verificar:**\n" + "".join(f"- [ ] {c}\n" for c in check)
        block += "- [ ] Revisión de hablante nativo\n"
        out.append(block)
    return "".join(out)


if __name__ == "__main__":
    (HERE.parent / "ANSWER_BANK.md").write_text(build())
    print(f"Wrote ANSWER_BANK.md with {len(A)} answers")
