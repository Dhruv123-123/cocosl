"""Write NEWSLETTER.md (all six issues, with subjects, send timing and review boxes) and issues/NN-slug.md
(paste-ready bodies with the footer) from issues.py. Refuses any link in a body: links are [ENLACE: ...]
placeholders that get the real URL in the email tool.

    python launch/dinero-simple/newsletter/build_newsletter.py
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from issues import FOOTER, ISSUES  # noqa: E402

PLACEHOLDER = re.compile(r"\[(ENLACE|NOMBRE|DIRECCIÓN)[^\]]*\]")
LINK = re.compile(r"https?://|www\.|\b[\w-]+\.(com|org|gov|net|app|io|co)\b", re.I)
ATTORNEY = ("ATTORNEY REVIEW: a licensed immigration attorney or DOJ-accredited representative has read this issue "
            "before it is sent (it mentions the ITIN)")


def check(issue: dict) -> None:
    bare = PLACEHOLDER.sub("", issue["body"] + issue["asunto"] + issue["asunto_b"] + issue["preview"])
    if LINK.search(bare):
        raise SystemExit(f"issue {issue['n']} has a link outside a placeholder: {LINK.search(bare).group(0)}")
    if "itin" in issue["body"].lower() and "abogado de inmigración con licencia" not in issue["body"]:
        raise SystemExit(f"issue {issue['n']} mentions the ITIN without sending legal questions to a licensed attorney")
    if "Es nuestro producto" not in issue["body"] and "El Presupuesto de 20 Minutos" in issue["body"]:
        raise SystemExit(f"issue {issue['n']} names a kit without saying it is ours")


def paste(issue: dict) -> str:
    return f"Asunto: {issue['asunto']}\nVista previa: {issue['preview']}\n\n{issue['body']}\n\n{FOOTER}\n"


def placeholders(issue: dict) -> list[str]:
    return sorted({m.group(0) for m in PLACEHOLDER.finditer(issue["body"]) if m.group(1) == "ENLACE"})


def build() -> str:
    for i in ISSUES:
        check(i)
    out = [f"""# Dinero Simple: the weekly newsletter (first {len(ISSUES)} issues)

Spanish issues for subscribers who have finished the 10-email welcome sequence. Issues 1–6 are evergreen; issue 7 is the 2026 holiday issue (send it Nov 30 – Dec 3, ahead of the evergreen ones if the list is live by then). One a week, same day and time (Thursday morning works for this audience). Each has one idea, "el número de la semana", one thing to do this week and one scam to watch for. Paste-ready copies with the footer are in `issues/`.

## Rules before sending

- **Native-speaker review first.** Machine-written; the reviewer reads each issue in full.
- **Issues that mention the ITIN (3 and 5) also need a licensed immigration attorney's read** before they go out. Keep the attorney line in them.
- **No links in the body.** Every link is a placeholder like `[ENLACE: comparación de envíos de dinero]`. Swap each one for the real URL in the email tool, with UTM tags (`utm_source=newsletter&utm_medium=email&utm_campaign=carta-NN`). Official pages (IRS, FTC) get no UTM. A placeholder you can't fill: delete the sentence.
- `[NOMBRE]` is the subscriber's first-name merge tag (fallback: "Hola:"). Fill `[DIRECCIÓN POSTAL DEL REMITENTE]` once: US law (CAN-SPAM) requires a postal address and a working unsubscribe link in every email.
- Check the facts under "Verificar" the week you send, especially in issue 5 (tax season).
- Subjects: send A to everyone, or test A against B on 20% of the list and send the winner.

| # | Asunto | Cuándo |
|---|---|---|
""" + "\n".join(f"| {i['n']} | {i['asunto']} | {i['cuando']} |" for i in ISSUES) + "\n"]
    for i in ISSUES:
        words = len(re.findall(r"\w+", PLACEHOLDER.sub("", i["body"])))
        checks = ([ATTORNEY] if "itin" in i["body"].lower() else []) + i["check"]
        out.append(f"""
## Carta {i['n']}: {i['asunto']}

- **Asunto A:** {i['asunto']}
- **Asunto B:** {i['asunto_b']}
- **Vista previa:** {i['preview']}
- **Cuándo:** {i['cuando']} · {words} palabras
- **Enlaces que llenar:** {", ".join(placeholders(i)) or "ninguno"}

{i['body']}

**Verificar:**
""" + "".join(f"- [ ] {c}\n" for c in checks) + "- [ ] Revisión de hablante nativo\n")
    return "\n".join(out)


def main() -> None:
    (HERE / "issues").mkdir(exist_ok=True)
    for i in ISSUES:
        check(i)
        (HERE / "issues" / f"{i['n']:02d}-{i['slug']}.md").write_text(paste(i))
    (HERE.parent / "NEWSLETTER.md").write_text(build())
    print(f"Wrote NEWSLETTER.md and {len(ISSUES)} issues")


if __name__ == "__main__":
    main()
