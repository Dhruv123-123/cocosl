"""Moving Planner: a printable moving budget, checklist and utilities tracker for Money Made Simple's Etsy shop.

Scouting's product-ideas-round2.md (PR #2): "moving checklist" gets 14,800 searches a month, up 50%, with few
listings. The budget page uses the same 11 categories, in the same order, as the apps thread's moving cost
calculator and the Moving Budget Sheet (launch/templates/moving_sheet.py). Task lists are short labels to tick,
not instructions. Undated, Letter + A4, kept out of the undated bundles.
"""
from __future__ import annotations

from printables import how_to, page
from printables_more import box, boxes, lined

# Same labels and order as launch/templates/moving_sheet.py and the apps thread's moving cost calculator (tested).
CATEGORIES = ["Movers or truck rental", "Fuel and mileage", "Packing supplies", "Storage", "Travel and lodging",
              "Deposits (new place)", "Overlap rent", "Utility setup", "Cleaning", "Time off work", "Buffer"]
UTILITIES = ["Electric", "Gas", "Water and sewer", "Trash and recycling", "Internet", "Phone", "Renter's or home insurance",
             "Streaming and subscriptions", "Mail forwarding (USPS)", "Other"]

KICK = "Moving planner"


def _check(items: list[str], blanks: int = 2) -> str:
    rows = "".join(f'<tr><td class="c" style="width:7%"><span class="cb"></span></td><td>{x}</td></tr>' for x in items + [""] * blanks)
    return f'<table class="t26"><tr><th></th><th>To do</th></tr>{rows}</table>'


def overview() -> str:
    return page("Moving <em>day plan</em>", "", f'''
      <div class="g3">{box("Moving date", 20)}{box("Moving from", 20)}{box("Moving to", 20)}</div>
      <div class="g3" style="margin-top:8px">{box("Movers / truck", 20)}{box("Pick-up time", 20)}{box("Keys handed over / collected", 20)}</div>
      <h3>Important contacts</h3>
      <table class="t30"><tr><th style="width:28%">Who</th><th>Name</th><th>Phone</th><th>Confirmation #</th></tr>
      {"".join(f"<tr><td>{w}</td><td></td><td></td><td></td></tr>" for w in ["Movers / truck rental", "Old landlord / agent", "New landlord / agent", "Storage", "Cleaner", "Helpers", ""])}</table>
      {lined("Notes")}''', kicker=KICK)


def budget() -> str:
    body = "".join(f"<tr><td>{c}</td><td></td><td></td><td></td></tr>" for c in CATEGORIES)
    return page("Moving <em>budget</em>", "Total budget: $__________", f'''
      <table class="t34"><tr><th style="width:36%">Cost</th><th class="r">Estimate</th><th class="r">Actual</th><th class="r">Paid</th></tr>{body}
      <tr class="tot"><td>Total</td><td></td><td></td><td></td></tr></table>
      {lined("Notes")}{boxes(["Budget", "Total actual", "Left over / over by"])}''', kicker=KICK)


def quotes() -> str:
    lines = ["Company", "Type (full service, labour only, truck)", "Date available", "Base price", "Packing and materials",
             "Mileage or fuel", "Stairs, long carry, heavy items", "Insurance or valuation", "Deposit", "USDOT number (interstate)",
             "Reviews checked", "Total"]
    rows = "".join(f'<tr{" class=tot" if x == "Total" else ""}><td>{x}</td><td></td><td></td><td></td></tr>' for x in lines)
    return page("Mover <em>quotes</em>", "Compare three", f'''
      <table class="t34"><tr><th style="width:34%"></th><th>Quote 1</th><th>Quote 2</th><th>Quote 3</th></tr>{rows}</table>
      {lined("Notes")}{boxes(["Chosen", "Booked on", "Deposit paid"])}''', kicker=KICK)


WEEKS = [("8 weeks before", ["Set the moving date", "Set the moving budget", "Get three mover or truck quotes",
                             "Give notice to the landlord (check your lease)", "Start sorting: keep, sell, donate"]),
         ("4 weeks before", ["Book movers or the truck", "Buy or collect boxes and tape", "Book time off work",
                             "Book cleaning", "Start packing rooms you use least"]),
         ("2 weeks before", ["Set up stop and start dates for utilities", "Change address with USPS",
                             "Update bank, employer and subscriptions", "Confirm movers and parking", "Use up the freezer"]),
         ("1 week before", ["Pack everything but the essentials", "Pack the first-night box", "Label every box by room",
                            "Charge devices and pack chargers", "Confirm keys handover"]),
         ("Moving day", ["Photograph the empty old place", "Read the meters", "Check every cupboard", "Lock up and hand over keys"]),
         ("First week", ["Photograph the new place", "Read the meters", "Test smoke alarms", "Unpack the kitchen and beds",
                         "Update the address on your ID"])]


def countdown(part: int) -> str:
    half = WEEKS[:3] if part == 1 else WEEKS[3:]
    body = "".join(f"<h3{' style=margin-top:0' if i == 0 else ''}>{w}</h3>{_check(items, 1)}" for i, (w, items) in enumerate(half))
    return page("Moving <em>checklist</em>", f"Part {part} of 2", body + lined("Notes"), kicker=KICK)


def utilities() -> str:
    rows = "".join(f"<tr><td>{u}</td>" + "<td></td>" * 5 + '<td class="c"><span class="cb"></span></td></tr>' for u in UTILITIES + ["", ""])
    return page("Utilities <em>tracker</em>", "Stop, start or transfer", f'''
      <table class="t34"><tr><th style="width:22%">Service</th><th>Old provider</th><th style="width:11%">Stop on</th>
      <th>New provider</th><th style="width:11%">Start on</th><th style="width:15%">Confirmation #</th><th class="c" style="width:7%">Done</th></tr>{rows}</table>
      {lined("Notes")}{boxes(["Deposits paid", "Final bills paid", "Meter readings taken"])}''', kicker=KICK)


def address_change() -> str:
    who = ["USPS mail forwarding", "Bank and credit cards", "Employer / payroll", "Driver's license and car registration",
           "Voter registration", "Health insurance", "Doctor and dentist", "Pharmacy", "Car and home insurance", "Phone",
           "Subscriptions and deliveries", "School", "Friends and family"]
    rows = "".join(f'<tr><td class="c" style="width:7%"><span class="cb"></span></td><td>{w}</td><td></td><td></td></tr>' for w in who + ["", "", ""])
    return page("Change of <em>address</em>", "Who to tell", f'''
      <table class="t30"><tr><th></th><th style="width:44%">Who</th><th>Date done</th><th>How (online, phone, form)</th></tr>{rows}</table>
      {lined("Notes")}''',
                kicker=KICK)


def boxes_log() -> str:
    rows = "".join(f"<tr><td>{i}</td><td></td><td></td><td class='c'><span class='cb'></span></td><td class='c'><span class='cb'></span></td></tr>" for i in range(1, 31))
    return page("Box <em>inventory</em>", "Number every box", f'''
      <table class="t26"><tr><th style="width:8%">#</th><th style="width:20%">Room</th><th>What's inside</th>
      <th class="c" style="width:9%">Fragile</th><th class="c" style="width:10%">Unpacked</th></tr>{rows}</table>
      {lined("Notes")}''', kicker=KICK)


def first_night() -> str:
    items = ["Phone chargers", "Medicines", "Toiletries", "Toilet paper", "Change of clothes", "Bedding and pillows", "Towels",
             "Snacks and water", "Kettle or coffee", "Mugs, plates, cutlery", "Basic tools", "Light bulbs",
             "Important papers", "Pet food and bowls", "Kids' favourite things"]
    return page("First night <em>box</em>", "Pack it last, open it first", f'''
      <div class="g2"><div>{_check(items[:8], 1)}</div><div>{_check(items[8:], 2)}</div></div>
      {lined("New home notes (Wi-Fi, bin day, where the shut-offs are)")}''', kicker=KICK)


HOW = ["Fill in the moving day plan and the budget first.", "Get quotes and tick the checklist off week by week.",
       "Track each utility and every address change as you go."]


def pages() -> list[str]:
    return [how_to("Moving <em>Planner</em>", HOW), overview(), budget(), quotes(), countdown(1), countdown(2), utilities(),
            address_change(), boxes_log(), first_night()]
