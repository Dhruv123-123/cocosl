"""Scam Decoded printables: the Family Scam-Safety Kit, the Fridge Card Set and the Caller ID Script Card.

Facts used (all US, checked Nov 2026; recheck once a year):
- Report fraud to the FTC at ReportFraud.ftc.gov; internet crime to the FBI at ic3.gov; identity theft at IdentityTheft.gov.
- DOJ National Elder Fraud Hotline: 1-833-FRAUD-11 (1-833-372-8311). AARP Fraud Watch Network Helpline: 877-908-3360.
- National Do Not Call Registry: donotcall.gov or 1-888-382-1222.
- Credit freezes are free at Equifax, Experian and TransUnion. Caller ID can be faked ("spoofed"), per the FCC.
- The FTC: no real business or government agency will insist you pay with a gift card.
No real company is named as a scammer, and no real victim's details are used (brands/scam-decoded.yaml avoid_topics).
"""
from __future__ import annotations

from shop import Brand

BRAND = Brand("Scam Decoded", "scamdecoded", ink="#0d1b2a", cream="#f4f1ea", accent="#2ec4b6", accent_d="#13867b",
              warm="#ff9f1c", tint="#eaf7f5", muted="#56606b", line="#c6cbd0")
P = BRAND.page

REPORT = [
    ("Fraud and scams", "ReportFraud.ftc.gov"),
    ("Internet crime", "ic3.gov (FBI)"),
    ("Identity theft", "IdentityTheft.gov"),
    ("Scams against people 60+", "1-833-FRAUD-11 (1-833-372-8311), DOJ Elder Fraud Hotline"),
    ("Free help line", "877-908-3360, AARP Fraud Watch Network (open to all)"),
    ("Stop sales calls", "donotcall.gov or 1-888-382-1222"),
]

RED_FLAGS = [
    ("They contacted you first", "A call, text, email, pop-up or message you didn't expect, often from someone \"official\"."),
    ("There's a rush", "Act now, today, in the next hour, or something bad happens: arrest, a frozen account, a missed prize."),
    ("They want it kept secret", "\"Don't tell your bank.\" \"Don't tell your family.\" Real problems don't need secrets."),
    ("They pick an odd way to pay", "Gift cards, crypto, a wire, a payment app, cash in the mail, or a courier at the door."),
    ("They ask for a code or a login", "A one-time code, a password, remote access to your computer, or your full card number."),
]

SCAMS = [
    ("Family emergency (\"grandparent\") call", "A grandchild or relative in trouble: jail, a crash, a hospital. The voice can even sound like theirs.",
     "Urgent, secret, and they need money now", "Hang up. Call the relative or their parent on a number you know. Ask for the family safe word."),
    ("Fake bank or fraud department", "\"Suspicious charge on your account. Read me the code we just sent.\"",
     "They want the code, or want you to move money to a \"safe\" account", "Hang up. Call the number on the back of your card."),
    ("Toll, parcel or delivery text", "Unpaid toll, a parcel on hold, a small fee to pay through a link.",
     "A link in a text you didn't expect, asking for card details", "Don't tap. Go to the official site or app yourself."),
    ("Tech support pop-up", "A loud warning on screen with a number to call, or a call saying your computer is infected.",
     "They want remote access or payment for a \"fix\"", "Close the browser (restart if you must). Never call the number on a pop-up."),
    ("Government impostor", "The IRS, Social Security, Medicare or the police, with a fine or a warrant.",
     "Threats plus gift cards, crypto or a wire", "Hang up. Look up the agency's real number and call it."),
    ("Romance or new online friend", "A warm match or follower who can't meet and soon has an emergency.",
     "Money, gift cards or crypto for someone you haven't met in person", "Talk to someone you trust before sending anything."),
    ("Investment or crypto \"opportunity\"", "A friendly contact shows big returns on an app or site and invites you in.",
     "Promised high returns, pressure to add more, trouble withdrawing", "Don't add money. Check the platform with your state securities regulator."),
    ("Job or task offer", "Easy pay for liking posts or \"rating\" products, found by text or social media.",
     "You have to pay or deposit money to unlock your earnings", "A real job never asks you to pay to get paid. Stop and report it."),
    ("Prize or lottery win", "You've won, but there's a fee, a tax or shipping to pay first.",
     "Paying to collect a prize", "Real prizes don't charge a fee to collect. Don't pay."),
]


def start_page() -> str:
    return P("Start <em>here</em>", "Family Scam-Safety Kit", f'''
      <p class="big">Scams work because they're fast and they feel urgent. This kit slows everything down. Fill it in
      together once, put the cards where you'll see them, and you'll know what to do before the phone rings.</p>
      <h3>Do this first (about 30 minutes, together)</h3>
      <ol class="steps big">
        <li>Read the five red flags (page 2) and the scams decoded (page 3) out loud.</li>
        <li>Choose a family safe word and fill in the safety plan (page 4).</li>
        <li>Write your trusted numbers on page 7, copied from your cards and statements, not from a search.</li>
        <li>Work through the account lockdown checklist (page 6), one item a week if that's easier.</li>
        <li>Put page 8, "If it happens", somewhere everyone can find it.</li>
      </ol>
      <h3>Printing</h3>
      <p>Print at 100% (actual size) on US Letter or A4. Mostly white, so it's easy on ink. Reprint the logs as often as you like.</p>
      <div style="margin-top:auto" class="box fineprint">Educational content to help you spot and report scams. It is not
      legal, financial or security advice, and no checklist can stop every scam. If you've lost money, contact your bank
      straight away, then report it (page 7). Phone numbers and websites were checked in November 2026; check them again
      once a year. Made by Scam Decoded with the help of AI tools for drafting and layout.</div>''')


def red_flags_page() -> str:
    items = "".join(f'<div class="flag"><b>{i}. {a}</b>{b}</div>' for i, (a, b) in enumerate(RED_FLAGS, 1))
    return P("The five <em>red flags</em>", "One is enough to stop", f'''
      <p class="big">Almost every scam has at least one of these. You don't need to work out which scam it is. If you
      spot one red flag, stop, and check another way.</p>{items}
      <div class="box" style="margin-top:auto;background:var(--ink);color:var(--cream);border-color:var(--ink)">
        <div class="kick" style="color:var(--gold)">The one rule</div>
        <div style="font-size:20pt;font-weight:900;letter-spacing:-.01em;margin-top:4px">Hang up. Look it up. Call back.</div>
        <div style="margin-top:4px">Use a number you already trust: the back of your card, a statement, or the official website you typed in yourself.</div>
      </div>''', kicker="Scam Decoded")


def scams_page() -> str:
    rows = "".join(f'<tr><td class="wrap"><b>{n}</b></td><td class="wrap">{h}</td><td class="wrap">{t}</td><td class="wrap">{d}</td></tr>'
                   for n, h, t, d in SCAMS)
    return P("Scams <em>decoded</em>", "Nine common ones", f'''
      <table><tr><th style="width:19%">The scam</th><th style="width:29%">What you hear</th><th style="width:24%">The giveaway</th>
      <th>What to do</th></tr>{rows}</table>
      <p class="fineprint" style="margin-top:8px">Scammers copy real names and logos, and caller ID can be faked. A call
      that shows your bank's name can still be a scam, so judge the request, not the caller ID.</p>''')


def plan_page() -> str:
    return P("Our family <em>safety plan</em>", "Fill in together", '''
      <div class="g2">
        <div class="box"><div class="lbl">Our family safe word</div><div class="line" style="height:34px"></div>
          <div class="fineprint" style="margin-top:4px">Something easy to remember and hard to guess. Not a pet's name or
          anything on social media. Never text or post it.</div></div>
        <div class="box"><div class="lbl">Who knows it</div><div class="line"></div><div class="line"></div></div>
      </div>
      <h3>Our rules</h3>
      <table class="t26"><tr><th style="width:6%"></th><th>We agree that...</th></tr>
        <tr><td class="c"><span class="cb"></span></td><td>If anyone calls in trouble asking for money, we hang up and call them back on a number we know.</td></tr>
        <tr><td class="c"><span class="cb"></span></td><td>We ask for the safe word before sending money or sharing anything, even if the voice sounds right.</td></tr>
        <tr><td class="c"><span class="cb"></span></td><td>We never pay anyone with gift cards, crypto or a wire because they called, texted or emailed us.</td></tr>
        <tr><td class="c"><span class="cb"></span></td><td>We never read out a code that was texted or emailed to us.</td></tr>
        <tr><td class="c"><span class="cb"></span></td><td>Anyone can call another family member to check, any time, and nobody gets teased for it.</td></tr>
        <tr><td class="c"><span class="cb"></span></td><td></td></tr>
        <tr><td class="c"><span class="cb"></span></td><td></td></tr>
      </table>
      <h3>Who we check with first</h3>
      <table class="t28"><tr><th>Name</th><th>Relationship</th><th>Phone</th><th>Best time</th></tr>
        <tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td><td></td></tr></table>
      <div class="g2" style="margin-top:auto">
        <div class="box"><div class="lbl">Signed</div><div class="line"></div><div class="line"></div></div>
        <div class="box"><div class="lbl">Date, and the date we'll review it</div><div class="line"></div><div class="line"></div></div>
      </div>''')


def _checks(items: list[str], h: int = 26) -> str:
    rows = "".join(f'<tr><td class="c"><span class="cb"></span></td><td>{x}</td><td></td></tr>' for x in items)
    return f'<table class="t{h}"><tr><th style="width:6%"></th><th>Step</th><th style="width:18%">Done on</th></tr>{rows}</table>'


def before_you_pay_page() -> str:
    return P("Before you <em>pay or click</em>", "Run through it every time", '''
      <p class="big">Ask these before you send money, buy gift cards, tap a link or let anyone into your computer.
      A single "yes" in the first column means stop.</p>
      <table class="t30"><tr><th>Question</th><th class="c" style="width:12%">Yes = stop</th></tr>
        <tr><td>Did they contact me first, out of the blue?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Are they rushing me, or threatening something bad if I wait?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Did they tell me to keep it secret, even from my bank or family?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Do they want gift cards, crypto, a wire, a payment app, or cash picked up?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Do they want a code, a password, my card number or remote access?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Is the deal, the prize or the return much better than normal?</td><td class="c"><span class="cb"></span></td></tr>
        <tr><td>Would I be embarrassed to tell someone I trust about this?</td><td class="c"><span class="cb"></span></td></tr>
      </table>
      <h3>Then check it another way</h3>
      <ol class="steps">
        <li>Hang up or close the message. You can always call back.</li>
        <li>Find the real number yourself: the back of your card, a statement, or the official website you typed in.</li>
        <li>Call a trusted person from your safety plan and talk it through.</li>
        <li>Wait a day. Real problems still exist tomorrow; most scams don't.</li>
      </ol>
      <div class="lines" style="max-height:1.4in;margin-top:6px"></div><div class="note">Notes</div>''')


def lockdown_page() -> str:
    return P("Account <em>lockdown</em>", "One item a week is fine", _checks([
        "Freeze your credit at Equifax, Experian and TransUnion (free; lift it when you apply for credit)",
        "Turn on two-step verification for email, bank and phone-carrier accounts",
        "Use a password manager, or at least a different password for email and banking",
        "Ask your phone carrier for a number lock or port-out PIN (stops SIM-swap theft)",
        "Turn on bank and card alerts for every purchase over a small amount",
        "Sign up for paperless statements, and read them once a month",
        "Register your numbers at donotcall.gov (cuts real sales calls, so odd calls stand out)",
        "Set your phone to silence unknown callers, or send them to voicemail",
        "Update your phone, computer and browser; turn on automatic updates",
        "Check privacy settings on social media: hide your birthday, address and family names",
        "Add a trusted contact to your bank account, if your bank offers it",
        "Shred old statements, and anything with your full Social Security number",
    ], 28) + '<p class="fineprint" style="margin-top:8px">A credit freeze doesn\'t affect your credit score, and you can lift it '
      'for a set time when you need to apply for something. Keep each bureau\'s login or PIN somewhere safe.</p>')


def numbers_page() -> str:
    mine = "".join(f"<tr><td>{x}</td><td></td></tr>" for x in (
        "Bank fraud line (back of card)", "Credit card 1 (back of card)", "Credit card 2 (back of card)", "Phone carrier",
        "Doctor or pharmacy", "Family member 1", "Family member 2", "Trusted neighbour or friend", "Local police (non-emergency)"))
    rep = "".join(f'<tr><td><b>{a}</b></td><td>{b}</td></tr>' for a, b in REPORT)
    return P("Trusted <em>numbers</em>", "Copy from your cards, not a search", f'''
      <p>Scammers buy ads and post fake numbers online. Copy these from the back of your cards, a paper statement or a
      website you typed in yourself.</p>
      <table class="t28"><tr><th style="width:42%">Who</th><th>Number</th></tr>{mine}</table>
      <h3>Where to report a scam (US)</h3>
      <table class="t26"><tr><th style="width:30%">What happened</th><th>Where</th></tr>{rep}</table>
      <p class="fineprint" style="margin-top:6px">Checked November 2026. Emergency or someone in danger: call 911.</p>''')


def if_it_happens_page() -> str:
    return P("If it <em>happens</em>", "The first hour", '''
      <p class="big">Anyone can be fooled; scammers do this all day. Acting fast matters more than anything else, and
      there's no shame in calling for help.</p>
      <ol class="steps big">
        <li><b>Stop all contact.</b> Hang up, don't reply, and don't send any more money, even if they promise a refund.</li>
        <li><b>Call your bank or card company</b> on the number on your card. Ask them to stop or reverse the payment and to secure the account.</li>
        <li><b>Paid with a gift card?</b> Call the gift card company on the number on the card or its website and ask about a refund. Keep the card and receipt.</li>
        <li><b>Change passwords</b> on email, bank and any account you logged into, starting with email. Turn on two-step verification.</li>
        <li><b>Let someone into your computer?</b> Disconnect it from the internet and have it checked by someone you trust.</li>
        <li><b>Gave out personal details?</b> Go to IdentityTheft.gov for a recovery plan, and freeze your credit.</li>
        <li><b>Report it</b> at ReportFraud.ftc.gov, and at ic3.gov if it happened online. Age 60+: 1-833-FRAUD-11.</li>
        <li><b>Write it down</b> in the incident log while you remember: dates, numbers, names, amounts.</li>
      </ol>
      <div class="box" style="margin-top:auto"><div class="lbl">Watch out for "recovery" offers</div>Anyone who contacts you
      offering to get your money back for a fee is very likely the next scam. Government agencies don't charge to help.</div>''')


def talk_page() -> str:
    return P("How to <em>talk about it</em>", "With parents, kids or a partner", '''
      <div class="g2">
        <div><h3>Do</h3><ul class="big" style="padding-left:18px">
          <li>Start with a story, not a lecture: "I nearly fell for a text like this."</li>
          <li>Make it about everyone, not their age: "We're all making a plan."</li>
          <li>Agree one simple rule: hang up and call back.</li>
          <li>Practise once: you play the caller, they say the safe-word line.</li>
          <li>Say they can call you about anything, any time, and you'll never be annoyed.</li></ul></div>
        <div><h3>Don't</h3><ul class="big" style="padding-left:18px">
          <li>Say "how could you fall for that?" Shame stops people telling you next time.</li>
          <li>Take over their accounts without asking.</li>
          <li>Overload them. One rule they remember beats ten they don't.</li>
          <li>Wait for a crisis to have the conversation.</li></ul></div>
      </div>
      <h3>Lines that help</h3>
      <div class="say"><div class="q">To open it</div><div class="a">"Scammers are faking family voices now. Can we pick a word only we know?"</div></div>
      <div class="say"><div class="q">If they've been caught out</div><div class="a">"Thank you for telling me. Let's call the bank together right now."</div></div>
      <div class="say"><div class="q">For teens</div><div class="a">"If anyone online asks for money, codes or photos, show me first. You won't be in trouble."</div></div>
      <div class="lines" style="max-height:1.2in"></div><div class="note">What we agreed</div>''')


def incident_log_page() -> str:
    rows = "".join("<tr>" + "<td></td>" * 6 + "</tr>" for _ in range(14))
    return P("Incident <em>log</em>", "Write it down while it's fresh", f'''
      <table class="t34"><tr><th style="width:11%">Date</th><th style="width:16%">Who / from</th><th style="width:12%">How</th>
      <th>What they asked for</th><th style="width:18%">What I did</th><th style="width:12%">Reported</th></tr>{rows}</table>
      <p class="fineprint" style="margin-top:6px">"How" = call, text, email, social media, pop-up or at the door. Keep
      screenshots and phone numbers; your bank and the FTC may ask for them.</p>''')


def monthly_check_page() -> str:
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    head = "".join(f'<th class="c">{m}</th>' for m in months)
    tasks = ["Read every bank and card statement", "Check for accounts or charges I don't recognise",
             "Delete texts and emails asking me to act fast", "Talk to one family member about a new scam",
             "Check that the credit freeze is still on", "Update phone and computer", "Review social media privacy"]
    rows = "".join(f'<tr><td>{t}</td>' + '<td class="c"><span class="cb"></span></td>' * 12 + "</tr>" for t in tasks)
    return P("10-minute <em>monthly check</em>", "Tick a box each month", f'''
      <table class="t34"><tr><th style="width:34%">Each month</th>{head}</tr>{rows}</table>
      <h3>Once a year</h3>{_checks(["Pull your free credit reports from all three bureaus at AnnualCreditReport.com",
        "Update the trusted numbers page", "Re-read the safety plan together; change the safe word if it's been shared"], 26)}''')


def kit_pages() -> list[str]:
    return [start_page(), red_flags_page(), scams_page(), plan_page(), before_you_pay_page(), lockdown_page(),
            numbers_page(), if_it_happens_page(), talk_page(), incident_log_page(), monthly_check_page()]


# ---------------------------------------------------------------- cards (6 x 4 in, landscape)

CARD_CSS = """
.card{ width:6in; height:4in; background:#fff; position:relative; overflow:hidden; padding:.26in .3in .22in;
  display:flex; flex-direction:column; break-after:page; page-break-after:always; }
.card:last-child{ break-after:auto; }
.card.dark{ background:var(--ink); color:var(--cream); }
.card .ck{ font-size:7.5pt; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--green-d); }
.card.dark .ck{ color:var(--gold); }
.card h2{ font-size:25pt; font-weight:900; letter-spacing:-.02em; line-height:1; margin:4px 0 8px; }
.card h2 em{ font-style:normal; color:var(--green-d); }
.card.dark h2 em{ color:var(--green); }
.card ul{ margin:0; padding-left:17px; font-size:11.5pt; line-height:1.38; }
.card .cf{ margin-top:auto; display:flex; justify-content:space-between; font-size:6.5pt; color:var(--muted); }
.card.dark .cf{ color:#9fb0bf; }
.card .wl{ border-bottom:1.3px solid var(--ink); height:27px; }
.card .fillrow{ display:flex; gap:8px; align-items:flex-end; font-size:10pt; font-weight:700; margin-bottom:6px; }
.card .fillrow span{ white-space:nowrap; } .card .fillrow div{ flex:1; border-bottom:1.3px solid var(--ink); height:22px; }
.sheet{ width:var(--w); height:var(--h); background:#fff; display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:.35in; break-after:page; page-break-after:always; position:relative; overflow:hidden; }
.sheet:last-child{ break-after:auto; }
.sheet .cut{ outline:1px dashed #9aa3ab; outline-offset:0; }
.sheet .sfoot{ position:absolute; bottom:.25in; left:0; right:0; text-align:center; font-size:7pt; color:#9aa3ab; }
"""


def _card(kicker: str, title: str, body: str, dark: bool = False, foot: str = "scamdecoded") -> str:
    return (f'<div class="card{" dark" if dark else ""}"><div class="ck">{kicker}</div><h2>{title}</h2>{body}'
            f'<div class="cf"><span>&copy; Scam Decoded &middot; personal use</span><span>{foot}</span></div></div>')


def fridge_cards() -> list[str]:
    return [
        _card("Before you do anything", "Stop. Is it <em>a scam?</em>", '''<ul>
          <li>They contacted <b>you</b>, out of the blue</li><li>They're <b>rushing</b> you or threatening you</li>
          <li>They want it kept <b>secret</b></li><li>They want <b>gift cards, crypto or a wire</b></li>
          <li>They want a <b>code</b> or a password</li></ul>''', dark=True, foot="One flag is enough. Hang up."),
        _card("Payment rule", "Gift cards are <em>for gifts</em>", '''<ul>
          <li>No real agency or company will insist you pay with a gift card</li>
          <li>Same for crypto, wires, payment apps or cash picked up at the door</li>
          <li>If someone asks you to buy cards and read the numbers: it's a scam</li></ul>'''),
        _card("If anyone calls about money", "Hang up. <em>Look up.</em> Call back.", '''<ul>
          <li>Caller ID can be faked, even your bank's name</li>
          <li>Use the number on the back of your card or a statement</li>
          <li>Never call a number from a pop-up, a text or the caller</li></ul>''', dark=True, foot="You can always call back."),
        _card("Only our family knows it", "Our <em>safe word</em>", '''
          <div class="wl" style="height:40px;margin:6px 0 10px"></div>
          <ul><li>A "family member" in trouble on the phone? Ask for the word.</li>
          <li>No word, no money, no matter how real the voice sounds.</li><li>Never text it or post it.</li></ul>'''),
        _card("Before I send money", "Who I <em>call first</em>", '''
          <div class="fillrow"><span>Name</span><div></div><span>Phone</span><div></div></div>
          <div class="fillrow"><span>Name</span><div></div><span>Phone</span><div></div></div>
          <div class="fillrow"><span>Bank fraud line</span><div></div></div>
          <div class="fillrow" style="font-weight:400;font-size:9pt"><span>Age 60+: DOJ Elder Fraud Hotline 1-833-372-8311</span></div>'''),
        _card("Texts and emails", "Never share <em>a code</em>", '''<ul>
          <li>A one-time code is a key to your account</li>
          <li>Anyone who asks you to read it out is trying to get in</li>
          <li>Unexpected link about a toll, parcel or account? Don't tap it. Go to the official app or site yourself.</li></ul>''',
              dark=True, foot="Report scams: ReportFraud.ftc.gov"),
    ]


def caller_id_large() -> str:
    lines = [
        ("When someone calls about my bank, card or money", "\"I don't handle that on calls I didn't make. I'll call the number on my card.\""),
        ("When a \"grandchild\" or relative needs money", "\"What's our family word?\" Then I hang up and call them on their own number."),
        ("When it's \"the IRS\", Social Security, Medicare or the police", "\"Send me a letter. I'll call your office myself.\""),
        ("When they want to get into my computer", "\"I don't let anyone into my computer.\" Then I hang up."),
        ("When they want a code they texted me", "\"I don't read out codes.\" Then I hang up."),
        ("When they say I've won something", "\"I don't pay to collect prizes.\""),
        ("When they keep pushing", "\"I'm hanging up now.\" It's not rude. It's my phone."),
    ]
    says = "".join(f'<div class="say" style="padding:9px 14px"><div class="q" style="font-size:10pt">{q}</div>'
                   f'<div class="a" style="font-size:16pt;line-height:1.25">{a}</div></div>' for q, a in lines)
    return BRAND.page("What I say <em>on the phone</em>", "Keep it by the phone", f'''
      {says}
      <div class="box" style="margin-top:auto;background:var(--ink);color:var(--cream);font-size:14pt;font-weight:800;text-align:center">
        Caller ID can be faked. If in doubt: hang up, look up the number, call back.</div>''', kicker="Large print")


def caller_id_card() -> str:
    return _card("Caller ID script", "What I <em>say</em>", '''<ul style="font-size:10.4pt;line-height:1.32">
      <li><b>Bank or card:</b> "I'll call the number on my card."</li>
      <li><b>Relative in trouble:</b> "What's our family word?"</li>
      <li><b>IRS, Social Security, police:</b> "Send a letter. I'll call you."</li>
      <li><b>Computer problem:</b> "I don't let anyone in." Hang up.</li>
      <li><b>A code they texted:</b> "I don't read out codes."</li>
      <li><b>Anything else odd:</b> "I'm hanging up now."</li></ul>''', foot="Caller ID can be faked")


def wallet_card() -> str:
    return ('<div class="wallet"><div class="ck">Scam Decoded</div><div class="wt">Hang up. Look up.<br>Call back.</div>'
            '<div class="wl2">Family word: <span></span></div><div class="wl2">Call first: <span></span></div></div>')


WALLET_CSS = """
.wallet{ width:3.5in; height:2in; padding:.16in .2in; background:var(--ink); color:var(--cream); overflow:hidden;
  display:flex; flex-direction:column; }
.wallet .ck{ font-size:6.5pt; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--gold); }
.wallet .wt{ font-size:17pt; font-weight:900; line-height:1.02; letter-spacing:-.01em; margin:4px 0 auto; }
.wallet .wl2{ font-size:8pt; font-weight:700; display:flex; gap:6px; margin-top:5px; }
.wallet .wl2 span{ flex:1; border-bottom:1px solid var(--cream); }
.wgrid{ display:grid; grid-template-columns:repeat(2,3.5in); gap:.12in .25in; }
"""


def card_sheets(cards: list[str]) -> list[str]:
    """Two 6 x 4 in cards per Letter/A4 sheet, with dashed cut lines."""
    out = []
    for i in range(0, len(cards), 2):
        pair = "".join(f'<div class="cut">{c}</div>' for c in cards[i:i + 2])
        out.append(f'{pair}<div class="sfoot">Cut on the dashed lines. Print at 100% (actual size). Card stock works best.</div>')
    return out


def wallet_sheet() -> str:
    cards = "".join(f'<div class="cut">{wallet_card()}</div>' for _ in range(8))
    return f'<div class="wgrid">{cards}</div><div class="sfoot">Eight wallet cards (3.5 x 2 in). Cut on the dashed lines. Fill in with a pen.</div>'


# ---------------------------------------------------------------- listings

GOOD = ["This is a DIGITAL DOWNLOAD. Nothing is shipped. Your files are in your Etsy account right after payment.",
        "PDFs in US Letter and A4. Print at home or at a print shop, as often as you like, for your own family.",
        "US phone numbers and reporting sites, checked November 2026.",
        "For personal use only. Please don't resell or share the files.",
        "Educational content, not legal, financial or security advice. No checklist can stop every scam."]
DISCLOSURE = ("How it's made: designed by Scam Decoded. AI tools helped draft the text and lay out the pages; every page "
              "was checked against official sources (FTC, FBI, DOJ) before listing.")
CAT = "Paper & Party Supplies > Paper > Stationery (or Home & Living > Office, whichever Etsy suggests)"


def _gumroad(hook: str, get: list[str], price: float) -> str:
    g = "\n".join(f"- {x}" for x in get)
    return (f"{hook}\n\nWhat's inside:\n{g}\n\nInstant download: PDFs in US Letter and A4. ${price:g}, one payment, "
            "files you keep.\n\nEducational content, not legal, financial or security advice. US reporting contacts, "
            "checked November 2026. Made with the help of AI tools for drafting and layout, and checked against official "
            "sources. Questions or a problem with a file? Reply to your receipt email.")


KIT_GET = ["11 pages: the five red flags, nine common scams decoded, a family safety plan with a safe word, a before-you-pay checklist",
           "An account lockdown checklist (credit freeze, two-step verification, SIM-swap lock)",
           "Trusted numbers and where to report scams in the US",
           "\"If it happens\": the first hour, step by step",
           "A guide to talking with parents, teens or a partner, an incident log and a monthly 10-minute check"]
CARDS_GET = ["6 fridge cards, 6 x 4 in: Stop. Is it a scam? / Gift cards are for gifts / Hang up. Look up. Call back. / Our safe word / Who I call first / Never share a code",
             "Two files per paper size: one card per page (for photo or card printing) and two cards per sheet with cut lines"]
CALLER_GET = ["A large-print phone-side page with seven things to say, word for word",
              "The same scripts on a 6 x 4 in card, and a sheet of 8 wallet cards (3.5 x 2 in)"]

LISTINGS = [
    dict(slug="family-scam-safety-kit", name="Family Scam-Safety Kit", price=9.00, kind="kit",
         title="Family Scam Safety Kit Printable, Scam Awareness Checklist and Safe Word Plan",
         tags=["scam awareness", "scam prevention", "fraud prevention", "elderly parents", "family safe word",
               "identity theft", "senior safety", "caregiver printable", "scam checklist", "online safety",
               "grandparent scam", "elder care", "family scam plan"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF",
                     "Primary colour": "Blue", "Secondary colour": "White"},
         hook="Scams work because they're fast. This printable kit slows everything down, so your family knows exactly what to do before the phone rings."),
    dict(slug="scam-fridge-cards", name="Scam Fridge Card Set", price=5.00, kind="cards",
         title="Scam Warning Fridge Cards, Printable Scam Awareness Cards for Seniors and Families",
         tags=["scam awareness", "fridge cards", "senior safety", "elderly parents", "scam prevention",
               "gift card scam", "caregiver gift", "fraud awareness", "printable cards", "family safe word",
               "phone scam", "safety reminder", "elder care"],
         attributes={"Occasion": "None", "Holiday": "None", "File type": "PDF", "Primary colour": "Blue",
                     "Secondary colour": "Orange", "Orientation": "Landscape"},
         hook="Six bold cards for the fridge or the desk, each with one rule that stops a common scam."),
    dict(slug="caller-id-script-card", name="Caller ID Script Card for Seniors", price=4.00, kind="cards",
         title="Phone Scam Script Card for Seniors, Large Print What to Say Card",
         tags=["phone scam", "senior safety", "large print", "elderly parents", "scam awareness",
               "caregiver printable", "scam prevention", "caller id", "grandparent scam", "fraud prevention",
               "wallet card", "elder care", "dementia caregiver"],
         attributes={"Occasion": "None", "Holiday": "None", "File type": "PDF", "Primary colour": "Blue",
                     "Secondary colour": "White"},
         hook="Exactly what to say when a suspicious call comes in, in large print, for the phone table, the fridge and the wallet."),
    dict(slug="scam-safety-bundle", name="Family Scam-Safety Bundle", price=12.00, kind="bundle",
         title="Scam Safety Bundle Printable, Family Kit, Fridge Cards and Senior Phone Script",
         tags=["scam awareness", "scam prevention", "senior safety", "elderly parents", "family safe word",
               "fraud prevention", "caregiver gift", "identity theft", "printable bundle", "phone scam",
               "online safety", "elder care", "large print"],
         attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF",
                     "Primary colour": "Blue", "Secondary colour": "Orange"},
         hook="Everything in one download: the 11-page Family Scam-Safety Kit, the six fridge cards and the caller ID script cards, for less than buying them separately ($18)."),
]

# Merged into the card set, Nov 7 2026 (see RETIRED). Reverse by deleting the slug from RETIRED.
CARDSET_GET = ["7 cards, 6 x 4 in: the six fridge cards (Stop. Is it a scam? / Gift cards are for gifts / Hang up. Look up. Call back. / Our safe word / Who I call first / Never share a code) and the caller ID script card",
               "A large-print phone-side page with seven things to say, word for word",
               "A sheet of 8 wallet cards (3.5 x 2 in)",
               "One card per page (for photo or card printing), and Letter and A4 sheets with cut lines"]
LISTINGS.append(dict(
    slug="scam-card-set", name="Scam Decoded Card Set", price=6.00, kind="cards",
    title="Scam Warning Cards Printable, Fridge Cards, Phone Script Card and Wallet Cards for Seniors",
    tags=["scam awareness", "fridge cards", "senior safety", "elderly parents", "phone scam",
          "wallet card", "large print", "caregiver gift", "scam prevention", "printable cards",
          "family safe word", "gift card scam", "elder care"],
    attributes={"Occasion": "None", "Holiday": "None", "Paper size": "US Letter, A4", "File type": "PDF",
                "Primary colour": "Blue", "Secondary colour": "Orange", "Orientation": "Landscape"},
    hook="Cards only, no reading: seven bold cards for the fridge and the phone table, a large-print script for what to say on a suspicious call, and wallet cards. Made to sit next to the Family Scam-Proofing Kit and the large-print seniors guide."))

# Products from this module that overlap with Scam Decoded's existing ladder (PR #9) and are not listed. Each says
# where it went, so the choice can be reversed by removing the slug here.
RETIRED = {
    "family-scam-safety-kit": "Merged into The Family Scam-Proofing Kit ($9, PR #9), which covers the same plan, lockdown, decoder and incident log. Pages only this kit had (before-you-pay check, how to talk about it, monthly check) are worth adding to that kit.",
    "scam-fridge-cards": "Merged into the Scam Decoded Card Set ($6).",
    "caller-id-script-card": "Merged into the Scam Decoded Card Set ($6), which is cards only, so it no longer overlaps the 13-page large-print seniors guide ($7, PR #9).",
    "scam-safety-bundle": "Retired with the kit. The card set is recommended after the kit and the seniors guide instead (see the cross-sell map).",
}

_GET = {"scam-card-set": CARDSET_GET, "family-scam-safety-kit": KIT_GET, "scam-fridge-cards": CARDS_GET, "caller-id-script-card": CALLER_GET,
        "scam-safety-bundle": ["Family Scam-Safety Kit (11 pages)"] + CARDS_GET[:1] + CALLER_GET}
_HOW = {"kit": ["Print the pages you need.", "Fill in the safety plan and trusted numbers together.",
                "Keep \"If it happens\" where everyone can find it, and do the monthly check."],
        "cards": ["Print on card stock at 100%, or send the one-card-per-page file to a photo printer.",
                  "Cut on the dashed lines.", "Put them where the phone and the mail are: the fridge, the desk, the wallet."],
        "bundle": ["Unzip the download.", "Fill in the kit together.", "Print the cards and put them by the phone and on the fridge."]}
for _it in LISTINGS:
    _it["status"] = "retired" if _it["slug"] in RETIRED else "active"
    _it["category"] = CAT
    _it["description"] = __import__("shop").etsy_description(_it["hook"], _GET[_it["slug"]], _HOW[_it["kind"]], GOOD, DISCLOSURE)
    _it["gumroad"] = _gumroad(_it["hook"], _GET[_it["slug"]], _it["price"])
