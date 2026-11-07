# Pinterest pins: 10 designs for the highest-value pages

Rendered PNGs: `site/pins/` (made by `python3 site/tools/make_pins.py`, with `pins.csv` for upload). `--all` adds two
designs for every shop product, comparison and article plus a 60-day posting schedule (`pins/schedule.csv`).

Written Nov 7, 2026. Every number below comes from the page it links to (2026 tax figures, single filer, no
state income tax, unless the pin says otherwise). If a page's numbers change, change the pin.

## Shared spec (all 10)

- **Canvas:** 1000 × 1500 px (2:3), PNG. Safe area: 60 px on every side; keep text out of the bottom 120 px,
  where Pinterest overlays its buttons on mobile.
- **Brand tokens** (same as the site): ink `#0b1d13`, paper `#f4f1e8`, green `#2fbf71`, dark green `#1a7a45`,
  gold `#f2b134`, gold tint `#fdf3dd`, muted `#4b5a51`.
- **Type:** Inter (or system sans). Headline 800 weight, 88–104 px, tight leading (1.05). Subhead 600, 40–44 px.
  Body 500, 34 px. Never below 30 px: most pins are seen at about a third of this size.
- **Contrast:** paper or gold text on ink, ink text on paper or gold. Don't put green text on paper (it fails
  WCAG AA at body size); green is for shapes, bars and highlights.
- **Brand mark:** "MS" gold circle (48 px) + "Money Made Simple" at 30 px, top-left, every pin.
- **Footer line** (bottom safe area, 28 px, muted or paper at 70%): `moneymadesimple.co` once the domain is live.
- **Link:** the page URL + `?utm_source=pinterest&utm_medium=social&utm_campaign=pin-<page>-<n>` (docs/UTM.md).
- **Honesty rules:** no income promises, no "get rich", numbers labelled as estimates or examples. Affiliate pins
  (Compare pages) don't need a disclosure on the image because the page carries it, but don't name a "winner"
  the page doesn't name.
- **Alt text:** paste the "Alt text" line into Pinterest's alt text field.

Boards to create: **Budgeting for beginners**, **Saving money tips**, **Debt payoff**, **Money apps and tools**,
**Budget printables**.

---

## 1. Quiz: "What's your money personality?"

- **Links to:** `/quiz/` · campaign `pin-quiz-1` · board: Budgeting for beginners
- **Pin title:** What's your money personality? Take the 1-minute quiz
- **Image text:** headline "What's your money personality?" · four labels "The Avoider · The Spender · The Juggler ·
  The Saver" · button shape "Take the 1-minute quiz →"
- **Layout:** ink background. Headline top third, paper, 100 px, left-aligned. Middle: a 2 × 2 grid of rounded
  cards (paper, 24 px radius, 400 × 220 px each), one personality per card in ink 44 px with a one-line hint in
  muted 30 px ("puts off opening the app", "the money finds a way out", "too many due dates", "saves, but feels
  stuck"). Bottom: gold pill button (ink text, 40 px).
- **Description:** Six questions, one minute, and you'll know whether you're an avoider, a spender, a juggler or a
  saver, plus the one money move that suits your type. Free, no sign-up needed to see your result.
- **Alt text:** Four cards labelled Avoider, Spender, Juggler and Saver under the question "What's your money
  personality?"

## 2. Quiz, variant: "Why your budget keeps failing"

- **Links to:** `/quiz/` · campaign `pin-quiz-2` · board: Budgeting for beginners
- **Pin title:** Why your budget keeps failing (it might be your money personality)
- **Image text:** headline "Your budget isn't broken. It might just be the wrong type." · subhead "6 questions ·
  1 minute · free" · "Find your money personality →"
- **Layout:** paper background, ink text. A large gold quote-style block (full width, 520 px tall) behind the
  headline. Below it, a row of four small circles (ink, 120 px) with the initials A, S, J, S, and the subhead.
  Ink button at the bottom with paper text.
- **Description:** Some people need fewer decisions, some need guard rails, some need fewer due dates. Take the
  six-question quiz to find your type and the budget style that fits it.
- **Alt text:** Headline "Your budget isn't broken. It might just be the wrong type." above four circles and a
  link to a one-minute quiz.

## 3. Compare: budgeting apps

- **Links to:** `/compare/best-budgeting-apps/` · campaign `pin-compare-budgeting-apps-1` · board: Money apps and tools
- **Pin title:** Budgeting apps compared honestly, including when not to pay for one
- **Image text:** headline "Budgeting apps, compared honestly" · checklist "What it costs · How it budgets ·
  Bank syncing · Who it's NOT for" · footer note "Plus the free options that work just as well"
- **Layout:** ink background, paper headline. Middle: a mock table card (paper, 840 × 560 px) with 4 rows; left
  column the four labels above in ink 34 px, right column short green bars of different lengths (decorative, no
  data). Gold sticker top-right of the card: "Who it's NOT for" at 30 px.
- **Description:** Six budgeting apps compared by price model, budgeting style and bank syncing, and who should
  skip each one. Includes the free and spreadsheet options, so you don't pay for an app you won't open.
- **Alt text:** A comparison card listing cost, budgeting style, bank syncing and who each budgeting app is not for.

## 4. Compare: high-yield savings

- **Links to:** `/compare/best-high-yield-savings-accounts/` · campaign `pin-compare-hysa-1` · board: Saving money tips
- **Pin title:** How to pick a high-yield savings account (and switch in 15 minutes)
- **Image text:** headline "Is your savings account earning almost nothing?" · subhead "What to compare in a
  high-yield account" · four ticks "FDIC insured · No monthly fees · Rate history · Fast transfers" · "Switch in
  15 minutes →"
- **Layout:** paper background. Top half: headline in ink, 96 px, with "almost nothing" underlined by a thick gold
  bar. Bottom half: ink panel with four large green ticks and paper labels. No APY numbers on the image: rates
  change weekly and the page tells readers to check them.
- **Description:** What actually matters when you choose a high-yield savings account: deposit insurance, fees,
  how the rate has moved, and transfer times. Five well-known online options side by side, and the 15-minute switch.
- **Alt text:** "Is your savings account earning almost nothing?" with a checklist: FDIC insured, no monthly fees,
  rate history, fast transfers.

## 5. Compare: Rocket Money vs YNAB vs Monarch

- **Links to:** `/compare/rocket-money-vs-ynab-vs-monarch/` · campaign `pin-compare-rm-ynab-monarch-1` · board: Money apps and tools
- **Pin title:** Rocket Money vs YNAB vs Monarch: which budgeting app fits you?
- **Image text:** three column heads "Rocket Money · YNAB · Monarch" · under each, one line: "Finds subscriptions" /
  "Every dollar a job" / "Big-picture dashboard" · headline at top "Which one fits you?"
- **Layout:** ink background. Three tall paper columns (260 × 760 px, 20 px gaps), each with the app name (ink
  40 px, 700) and its one-liner (34 px). No logos (trademark). Headline above in gold, 92 px.
- **Description:** Three popular budgeting apps head to head: how each one budgets, what's free, what it costs,
  how it handles subscriptions, couples and net worth, and who should skip each one.
- **Alt text:** Three columns comparing Rocket Money, YNAB and Monarch under the question "Which one fits you?"

## 6. Compare: balance transfer cards

- **Links to:** `/compare/best-balance-transfer-cards/` · campaign `pin-compare-balance-transfer-1` · board: Debt payoff
- **Pin title:** 0% balance transfer: do the maths before you apply
- **Image text:** headline "0% balance transfer: worth the fee?" · three checks "Intro period long enough? ·
  Transfer fee vs interest saved · Rate after the intro" · "See the worked example →"
- **Layout:** paper background. A big "0%" in ink, 320 px, top-left, with a gold asterisk; headline beside/below
  it. Three numbered rows (gold circles 1–3, ink text). Ink button.
- **Description:** A balance transfer can save hundreds or cost you more. How to compare the intro period, the
  transfer fee and the rate afterwards, with a worked example and the mistakes that cancel out the savings.
- **Alt text:** A large "0%" with three checks for a balance transfer: intro period, transfer fee, rate after.

## 7. Salary: $50,000

- **Links to:** `/budget/50000-salary/` · campaign `pin-budget-50000-1` · board: Budgeting for beginners
- **Pin title:** How to budget on a $50,000 salary (2026 take-home numbers)
- **Image text:** headline "$50,000 a year" · big number "≈ $3,530 a month" · label "take-home after federal tax
  + FICA*" · four lines "Bills · Funds · Goals · Weekly number" · footnote "*2026, single, no state income tax"
- **Layout:** ink background. "$50,000 a year" paper 72 px; "$3,530" gold, 200 px, the visual anchor. Below, a
  stacked bar (840 px wide, 80 px tall) split 50 / 10 / 15 / 25 in dark green, green, gold, paper with the four
  labels under it. Footnote in muted paper 28 px above the footer.
- **Description:** What a $50,000 salary actually leaves you each month in 2026, a line-by-line budget for it,
  how much rent fits, and how much your state changes the numbers. With the maths shown.
- **Alt text:** "$50,000 a year is about $3,530 a month take-home", above a bar split into bills, funds, goals and
  a weekly spending number.

## 8. Salary hub: rent on your salary

- **Links to:** `/budget/` · campaign `pin-budget-hub-1` · board: Budgeting for beginners
- **Pin title:** How much rent can you afford? Real 2026 numbers by salary
- **Image text:** headline "How much rent fits your salary?" · three rows "$50k → $1,250/mo · $60k → $1,500/mo ·
  $75k → $1,875/mo" · note "30% of gross pay. Take-home, budgets and city rents for your salary →"
- **Layout:** paper background, ink headline 92 px. Three wide rows (ink cards, 840 × 170 px) with the salary in
  paper 56 px on the left and the rent in gold 64 px on the right. Note under the cards in muted 32 px.
- **Description:** The 30% rule in real dollars, plus take-home pay, a monthly plan and the big cities where a
  one-bedroom fits, from $30,000 to $200,000.
- **Alt text:** Rent at 30% of gross pay: $1,250 a month on $50,000, $1,500 on $60,000, $1,875 on $75,000.

## 9. Shop: The Money Made Simple Toolkit

- **Links to:** `/shop/#bundles` · campaign `pin-shop-toolkit-1` · board: Budget printables
- **Pin title:** 5 money kits in one: budget, bills, credit, debt and investing ($39)
- **Image text:** headline "Your money system, sorted in 30 days" · list "Bill Cut Kit · 20-Minute Budget ·
  Credit Report Audit · Debt-Free Date Planner · Start Investing With $100 a Month" · price tag "$39 · $62
  separately"
- **Layout:** use the Toolkit cover (`site/static/img/shop/money-toolkit-bundle.jpg`, scaled to 640 px) centred
  on a paper background, tilted 4°, with a soft shadow. Headline above in ink 84 px. List below in 34 px with
  gold bullets. Gold price tag (rounded rectangle, ink text) overlapping the cover's bottom-right corner.
- **Description:** All five Money Made Simple guide-and-spreadsheet kits in one download, with a Start Here map
  and a 30-day plan that uses all five. Excel, Google Sheets or Numbers. One payment, no subscription.
- **Alt text:** The Money Made Simple Toolkit cover with five kits listed and a $39 price tag.

## 10. Shop: savings challenge pack

- **Links to:** `/shop/#bundles` · campaign `pin-shop-savings-pack-1` · board: Budget printables
- **Pin title:** 12 printable savings challenges in one pack ($8)
- **Image text:** headline "12 savings challenges, one download" · tiles "52-week · 100 envelopes · No-spend ·
  Savings bingo · Roll and save · 30-day" · "Letter + A4 · $8"
- **Layout:** paper background. A 3 × 2 grid of tiles (gold tint fill, 280 × 280 px), each with a simple icon
  drawn in ink line art (calendar, envelope, crossed-out bag, bingo grid, die, jar) and the challenge name in
  ink 32 px. Headline above, ink 88 px. Price in an ink pill at the bottom.
- **Description:** Make saving a habit (and a bit of a game): every savings challenge from the shop in one
  printable pack, from the 52-week challenge to savings bingo. Letter and A4 PDFs.
- **Alt text:** Six tiles showing printable savings challenges, including 52-week, 100 envelopes and savings bingo.

---

**Posting order:** follow `pins/schedule.csv`. It starts Mon Nov 30 2026 (week 3 after launch Day 1, per
`launch/money-made-simple/LAUNCH_WEEK.md` on PR #5) with that file's eight site pins: the quiz, then the freeze,
401(k) match, emergency fund, sinking funds, subscriptions, investing with $100 and expense ratios articles.
The same page never gets two pins within 7 days. Pins 7 and 8 can be
repeated for other salaries (`/budget/<salary>-salary/`) by swapping the numbers from that page; keep the
footnote.
