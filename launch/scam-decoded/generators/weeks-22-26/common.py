STYLE = "Clean flat vector illustration, deep navy and cream with teal and amber warning accents, simple shapes."
END = "No text, no logos, no real people."
MASCOT = "the small round teal shield mascot with big curious eyes"

CTA = "Follow, and send this to someone who'd fall for it."
CTA_TIKTOK = "Follow for one scam decoded every day, and send this to someone who'd fall for it."

P_TEXT = "text and email scams, decoded"
P_INVEST = "investment and crypto scams on social media"
P_ID = "identity theft and credit freezes"
P_FAMILY = "protecting older parents and family"
P_SECURITY = "account security basics (passwords, 2FA, SIM swap)"

KIT = ("Free family plan template and the printable Family Scam-Proofing Kit are in our bio. The kit is our own "
       "product ($9).")
AURA = ("The identity-protection service in our bio (Aura) is an affiliate link: we may earn a commission if you "
        "sign up, at no extra cost to you. You don't need a paid service to freeze your credit; that part is free.")
ONEPASS = ("The password manager in our bio (1Password) is an affiliate link: we may earn a commission if you sign "
           "up, at no extra cost to you. Any reputable password manager works.")
NORD = ("The VPN in our bio (NordVPN) is an affiliate link: we may earn a commission if you sign up, at no extra "
        "cost to you.")

FTC_SCAM = "https://consumer.ftc.gov/articles/how-avoid-scam"
FTC_REPORT = "https://reportfraud.ftc.gov/"
IC3 = "https://www.ic3.gov/"
IDTHEFT = "https://www.identitytheft.gov/"


def v(x: str) -> str:
    return f"{STYLE} {x} {END}"


def seg(h, n, o, vis):
    return {"heading": h, "narration": n, "on_screen_text": o, "visual_prompt": v(vis)}
