"""Print-on-demand starter set: 10 challenge posters made from the Etsy printables' own chart pages.

Each poster reuses one page of an existing printable (`source`, `page` is 1-based), re-laid out at poster proportions
and rendered at 300 DPI. Listing copy follows the same Etsy rules as launch/etsy/seo.py: title under 15 words, 13 tags
of 20 characters or less, no income promises, and the production partner and AI-tools disclosure in every description.
"""
from __future__ import annotations

# Masters, chosen to cover Printify's common poster sizes at 300 DPI (check each product's print area in Printify).
RATIOS = {
    "3x4": dict(w_in=9, h_in=12, px=(5400, 7200), sizes="9x12, 12x16, 18x24 in (300 DPI at 18x24)"),
    "2x3": dict(w_in=8, h_in=12, px=(4800, 7200), sizes="8x12, 12x18, 16x24 in (300 DPI); 24x36 in (200 DPI)"),
    "4x5": dict(w_in=9, h_in=11.25, px=(4800, 6000), sizes="8x10, 11x14 (crops slightly), 16x20 in (300 DPI)"),
}

PRICE_NOTE = ("Suggested starting prices: 12x16 or 12x18 about $22, 18x24 about $32. Before publishing, check that each "
              "size leaves at least $6 after Printify's base price, shipping and Etsy fees; base prices change by provider.")

POSTERS = [
    dict(slug="100-envelope-challenge-poster", source="100-envelope-challenge", page=2, name="100 Envelope Challenge Poster",
         title="100 Envelope Challenge Poster, $5050 Savings Challenge Wall Chart to Color In",
         tags=["100 envelope", "envelope challenge", "savings poster", "savings challenge", "5050 challenge",
               "money challenge", "savings chart", "color in poster", "cash stuffing", "savings wall art",
               "new year savings", "savings goal", "money saving gift"],
         hook="The 100 Envelope Challenge as a wall chart. Colour in each envelope as you save it; all 100 add up to $5,050."),
    dict(slug="52-week-savings-poster", source="52-week-savings-challenge", page=2, zoom=0.95, name="52 Week Savings Challenge Poster",
         title="52 Week Savings Challenge Poster, $1378 Money Challenge Wall Chart",
         tags=["52 week challenge", "52 week savings", "savings poster", "savings challenge", "1378 challenge",
               "money challenge", "weekly savings", "savings chart", "new year savings", "savings wall art",
               "family savings", "savings goal", "money saving gift"],
         hook="Save $1 in week one, $2 in week two, up to $52. Tick each week on the wall; the full year adds up to $1,378."),
    dict(slug="savings-bingo-poster", source="savings-bingo", page=2, zoom=1.0, name="$1,000 Savings Bingo Poster",
         title="Savings Bingo Poster, $1000 Money Challenge Bingo Board for Your Wall",
         tags=["savings bingo", "money bingo", "bingo challenge", "savings poster", "savings challenge",
               "money challenge", "savings game", "1000 savings", "couples challenge", "savings wall art",
               "fun savings", "savings goal", "money saving gift"],
         hook="A savings challenge you play like bingo. Every square is an amount; cover them all and you've saved $1,000."),
    dict(slug="debt-mountain-poster", source="debt-mountain-coloring-chart", page=2, name="Debt Free Mountain Poster",
         title="Debt Free Chart Poster, Debt Mountain Payoff Tracker to Color In",
         tags=["debt free chart", "debt tracker", "debt payoff tracker", "debt snowball", "debt poster",
               "debt free", "debt coloring page", "pay off debt", "debt free journey", "payoff wall chart",
               "color in poster", "debt mountain", "debt free gift"],
         hook="Climb the debt mountain one block at a time. Each of the 100 blocks is 1% of your debt; colour them as you pay it down."),
    dict(slug="savings-jar-poster", source="spare-change-jar-tracker", page=2, name="Savings Jar Poster",
         title="Savings Jar Poster, Spare Change Goal Tracker Wall Chart to Color In",
         tags=["savings jar", "money jar", "savings poster", "spare change", "jar tracker", "color in poster",
               "savings goal", "kids savings", "savings chart", "coin savings", "savings challenge",
               "savings wall art", "piggy bank"],
         hook="Fill the jar on your wall as you fill the real one. Write your goal on the label and colour in each step."),
    dict(slug="travel-fund-poster", source="travel-fund-tracker", page=2, name="Travel Fund Poster",
         title="Travel Fund Poster, Vacation Savings Tracker Wall Chart to Color In",
         tags=["travel fund", "vacation savings", "travel savings", "savings poster", "trip savings",
               "vacation fund", "savings goal", "travel wall art", "color in poster", "honeymoon fund",
               "savings chart", "travel gift", "savings challenge"],
         hook="Save for the trip on the wall: a passport-style tracker where every stamp is part of your vacation fund."),
    dict(slug="emergency-fund-poster", source="emergency-fund-tracker", page=2, name="Emergency Fund Poster",
         title="Emergency Fund Poster, Rainy Day Savings Goal Tracker to Color In",
         tags=["emergency fund", "rainy day fund", "savings poster", "savings goal", "savings tracker",
               "color in poster", "savings chart", "emergency savings", "savings challenge", "savings wall art",
               "financial goals", "money tracker", "6 month savings"],
         hook="Build your safety net where you can see it. Set your target, split it into steps and colour each one in."),
    dict(slug="house-fund-poster", source="home-fund-tracker", page=2, name="House Fund Poster",
         title="House Fund Poster, Down Payment Savings Tracker, Build the House Wall Chart",
         tags=["house fund", "down payment", "home savings", "savings poster", "first home", "house savings",
               "savings goal", "color in poster", "home buying", "savings chart", "new home fund",
               "savings wall art", "couples savings"],
         hook="Build the house brick by brick: each brick is part of your down payment. Colour them in as you save."),
    dict(slug="no-spend-challenge-poster", source="no-spend-challenge", page=2, name="30 Day No Spend Challenge Poster",
         title="No Spend Challenge Poster, 30 Day No Spend Tracker for Your Wall",
         tags=["no spend challenge", "no spend tracker", "no spend month", "frugal living", "spending challenge",
               "money challenge", "savings poster", "no buy challenge", "budget challenge", "savings wall art",
               "low buy year", "save money", "budget poster"],
         hook="Thirty days, one box each. Colour a box for every day you spend nothing beyond the essentials."),
    dict(slug="save-1000-poster", source="savings-challenge-tracker", page=3, zoom=0.94, name="Save $1,000 Challenge Poster",
         title="Save 1000 Dollars Poster, Savings Challenge Tracker Wall Chart to Color In",
         tags=["save 1000", "1000 savings", "savings challenge", "savings poster", "savings tracker",
               "money challenge", "color in poster", "savings goal", "savings chart", "cash stuffing",
               "new year savings", "savings wall art", "money saving gift"],
         hook="A $1,000 savings chart for the wall. Each circle is an amount; colour it in when you save it."),
]

DISCLOSURE = ("Designed by Money Made Simple with digital design tools (layouts drawn in code; some design and copy "
              "work done with AI assistance). Printed and shipped by our production partner.")


def description(p: dict) -> str:
    return f"""{p['hook']}

WHAT YOU GET
- A printed poster on matte paper (frame not included unless you choose a framed size)
- Plain black line art with green accents, made to be filled in with a pencil or permanent marker
- Matte poster paper is not dry-erase. To reuse it, frame it under glass and use a dry-erase marker on the glass

HOW IT WORKS
1. Pick a size. The poster is printed to order and shipped by our production partner.
2. Hang it where you'll see it every day.
3. Colour in or tick off each step as you save or pay down debt.

GOOD TO KNOW
- An organising tool, not financial advice. Totals shown are simply what the numbers on the chart add up to.
- Colours can vary slightly between screens and print.
- Want the printable version to print at home instead? Search for it in our shop.

{DISCLOSURE}"""
