"""If Something Happens to Me Planner: a fill-in organiser for Money Made Simple's Etsy shop.

Scouting's product-ideas-round2.md (PR #2): "end of life planner" gets 6,600 searches a month, up 50% in a year,
median price about $13. It's a fill-in organiser, not a will: the listing and every page say so. Labels and blank
space only, no explanatory text, so it isn't a "functional guide" under Etsy's 22 Oct 2026 AI rule. No passwords
are written in it: the digital page asks where they're kept. Undated, Letter + A4, kept out of the undated bundles.
"""
from __future__ import annotations

from printables import how_to, page
from printables_more import box, boxes, lined

LEGAL = ('<p class="note" style="margin-top:6px">Not a legal document. Talk to an estate lawyer about a will, '
         "trusts and powers of attorney.</p>")
KICK = "If something happens to me"


def _t(headers: list[tuple[str, str]], n: int, labels: list[str] | None = None, cls: str = "t30") -> str:
    head = "".join(f'<th style="width:{w}">{h}</th>' if w else f"<th>{h}</th>" for h, w in headers)
    labels = (labels or []) + [""] * max(0, n - len(labels or []))
    body = "".join(f"<tr><td>{x}</td>" + "<td></td>" * (len(headers) - 1) + "</tr>" for x in labels)
    return f'<table class="{cls}"><tr>{head}</tr>{body}</table>'


def p(title: str, meta: str, body: str) -> str:
    if 'class="lines"' not in body and "margin-top:auto" not in body:
        body += lined("Notes")      # fills the rest of the page
    return page(title, meta, body + LEGAL, kicker=KICK)


def about_me() -> str:
    return p("About <em>me</em>", "Last updated: __________", f'''
      <div class="g2">{box("Full legal name", 22)}{box("Other names used", 22)}</div>
      <div class="g3" style="margin-top:8px">{box("Date of birth", 18)}{box("Place of birth", 18)}{box("Citizenship", 18)}</div>
      <div class="g2" style="margin-top:8px">{box("Address", 30)}{box("Phone and email", 30)}</div>
      <h3>Where my ID documents are</h3>
      {_t([("Document", "34%"), ("Where it's kept", ""), ("Last 4 digits", "18%")], 8,
          ["Driver's license / state ID", "Passport", "Social Security card", "Birth certificate", "Marriage / divorce papers",
           "Military records", "Medicare / insurance cards"])}
      {lined("Anything else to know about me", 0.6)}''')


def contacts() -> str:
    return p("Key <em>contacts</em>", "Who to call first", _t(
        [("Who", "26%"), ("Name", "24%"), ("Phone", "18%"), ("Email", "")], 16,
        ["Call first", "Call second", "Executor / trusted person", "Lawyer", "Accountant / tax preparer", "Financial advisor",
         "Insurance agent", "Doctor", "Employer / HR", "Landlord / property manager", "Religious or community contact",
         "Neighbour with a key"], "t34"))


def where_things_are() -> str:
    return p("Where to <em>find things</em>", "Papers, keys and safes", _t(
        [("Item", "34%"), ("Where it's kept", ""), ("Who else knows", "22%")], 18,
        ["Will", "Trust documents", "Power of attorney", "Health care proxy / living will", "Life insurance policies",
         "Deeds and mortgage papers", "Vehicle titles", "Tax returns (last 3 years)", "Safe-deposit box and key",
         "Home safe and combination location", "Spare house and car keys", "Pre-paid funeral or burial papers"], "t30"))


def accounts() -> str:
    return p("Bank and investment <em>accounts</em>", "No full account numbers", _t(
        [("Institution", "24%"), ("Type", "16%"), ("Last 4", "10%"), ("Joint with / beneficiary", "24%"), ("Contact", "")], 18,
        ["", "", "", "", ""], "t30"))


def retirement_insurance() -> str:
    return p("Retirement and <em>insurance</em>", "Policies and plans", f'''
      <h3 style="margin-top:0">Retirement plans and pensions</h3>
      {_t([("Provider", "26%"), ("Type (401k, IRA, pension)", "24%"), ("Last 4", "10%"), ("Beneficiary", "20%"), ("Contact", "")], 7)}
      <h3>Insurance</h3>
      {_t([("Type", "22%"), ("Company", "24%"), ("Policy last 4", "12%"), ("Beneficiary", "20%"), ("Agent / phone", "")], 8,
          ["Life", "Life (work)", "Health", "Home / renters", "Car", "Disability", "Long-term care"])}''')


def debts() -> str:
    return p("Debts and <em>loans</em>", "What I owe", _t(
        [("Lender", "24%"), ("Type", "18%"), ("Last 4", "10%"), ("Autopay from", "18%"), ("Contact", "")], 16,
        ["", "", "", "", ""], "t34"))


def bills() -> str:
    return p("Bills and <em>autopays</em>", "To stop, move or keep paying", _t(
        [("Bill", "24%"), ("Amount", "12%"), ("Due", "10%"), ("Paid from", "18%"), ("Autopay?", "10%"), ("Stop / move / keep", "")], 18,
        ["Rent / mortgage", "Electric", "Gas", "Water", "Internet", "Phone", "Car payment", "Insurance"], "t30"))


def digital() -> str:
    return p("Digital <em>life</em>", "Never write passwords here", f'''
      <div class="g2">{box("Where my passwords are kept (app or place, not the passwords)", 30)}{box("Who can get into it", 30)}</div>
      {_t([("Account or device", "28%"), ("Username / email", "26%"), ("What to do (close, keep, memorialise)", "")], 15,
          ["Phone", "Computer", "Email", "Photos / cloud storage", "Social media", "Online banking", "Shopping accounts"], "t30")}''')


def subscriptions() -> str:
    return p("Subscriptions and <em>memberships</em>", "To cancel or transfer", _t(
        [("Service", "28%"), ("Cost", "12%"), ("Renews", "14%"), ("Account email", "24%"), ("Cancel?", "")], 20,
        ["Streaming", "Music", "News", "Gym", "Clubs / associations", "Software", "Delivery / shopping"], "t30"))


def home_property() -> str:
    return p("Home and <em>property</em>", "House, cars, storage", f'''
      <div class="g3">{box("Own or rent", 18)}{box("Mortgage lender / landlord", 18)}{box("Home insurance", 18)}</div>
      <h3>Vehicles</h3>
      {_t([("Vehicle", "30%"), ("Title kept", "22%"), ("Loan / lender", "24%"), ("Spare key", "")], 4)}
      <h3>Other property</h3>
      {_t([("Item", "30%"), ("Where", "26%"), ("Who should have it", "")], 7, ["Storage unit", "Jewellery", "Collections", "Tools", "Family keepsakes"])}
      {lined("Home notes (alarm company, where the shut-offs are, who has a key)", 0.6)}''')


def pets_dependents() -> str:
    return p("People and pets in <em>my care</em>", "Who looks after them", f'''
      <h3 style="margin-top:0">People who depend on me</h3>
      {_t([("Name", "24%"), ("Relationship", "18%"), ("Needs", "30%"), ("Who will help", "")], 5)}
      <h3>Pets</h3>
      {_t([("Name", "18%"), ("Type", "14%"), ("Food, meds, routine", "30%"), ("Vet", "18%"), ("Who will take them", "")], 5)}
      {lined("Notes for whoever steps in", 0.7)}''')


def medical() -> str:
    return p("Medical <em>information</em>", "For an emergency", f'''
      <div class="g3">{box("Blood type", 16)}{box("Allergies", 16)}{box("Organ donor?", 16)}</div>
      {_t([("Doctor or specialist", "30%"), ("For", "22%"), ("Phone", "20%"), ("Address", "")], 6)}
      <h3>Medicines</h3>
      {_t([("Medicine", "30%"), ("Dose", "16%"), ("When", "18%"), ("Pharmacy", "")], 8)}
      <div class="g2" style="margin-top:8px">{box("Health care proxy (name, where the form is)", 26)}{box("Living will / advance directive kept", 26)}</div>''')


def wishes() -> str:
    opts = ["Burial", "Cremation", "Green burial", "Donate my body", "Not decided"]
    cb = "".join(f'<span style="margin-right:14px"><span class="cb"></span> {o}</span>' for o in opts)
    return p("My <em>wishes</em>", "In my own words", f'''
      <div class="box"><div class="lbl">I'd like</div><div style="margin-top:6px">{cb}</div></div>
      <div class="g2" style="margin-top:8px">{box("Service: where, what kind", 30)}{box("Music, readings, who speaks", 30)}</div>
      <div class="g2" style="margin-top:8px">{box("Donations in my name to", 26)}{box("Pre-paid plans or plots", 26)}</div>
      {lined("A note to the people I love")}''')


def updates() -> str:
    return p("Review <em>log</em>", "Look it over once a year", _t(
        [("Date reviewed", "18%"), ("What changed", ""), ("Pages updated", "18%"), ("Initials", "12%")], 18, None, "t34") +
        boxes(["Copy given to", "Next review", "Where this planner is kept"]))


HOW = ["Fill in what you can today. Blanks are fine; come back to them.",
       "Write where things are and the last 4 digits only: never full account numbers or passwords.",
       "Tell one or two people where you keep this planner, and review it once a year."]


def pages() -> list[str]:
    return [how_to("If Something Happens to Me <em>Planner</em>", HOW, LEGAL), about_me(), contacts(), where_things_are(),
            accounts(), retirement_insurance(), debts(), bills(), subscriptions(), digital(), home_property(),
            pets_dependents(), medical(), wishes(), updates()]
