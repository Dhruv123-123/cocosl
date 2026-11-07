# "Actual Budget + our plan": 6 screen-recording scripts

Written 2026-11-07 for **Money Made Simple**. **Docs only.** Dhruv records these himself, in his own voice,
on his own screen. Nothing has been recorded, uploaded or published. This is recommendation #1 from
`oss-landscape.md`: teach a free, open-source app on screen, and offer The 20-Minute Budget ($12, PR #6) as
the plan that sits on top of it.

Facts about the app come from Actual's own docs, read today (linked in each episode). **Before recording,
open the current version and check every menu name in these scripts.** Actual ships often, and a renamed
button is the most likely error.

## 1. Can we show it and name it? (licence and trademark check)

| Question | Answer | Basis |
|---|---|---|
| Can we show the app on screen and in thumbnails? | **Yes.** Screen recordings of software you're using to teach it are ordinary commentary and teaching use. The code is MIT, which lets anyone use, copy and modify it. Nothing in the licence restricts showing it | `LICENSE.txt` in actualbudget/actual: MIT text, "Copyright James Long" |
| Can we say "Actual Budget" in titles, descriptions and voiceover? | **Yes, to say what the video is about.** That's nominative use: naming a product to talk about it. No trademark policy or brand guidelines are published on actualbudget.org or the repo (searched today), so we follow the general rules below | No published policy found; MIT grants no trademark rights either way |
| Can we use the Actual logo? | **Only as it appears inside the app on screen.** Don't put the logo in our thumbnails, channel art or product covers, and don't make it look like their badge or seal | Avoids implying endorsement |
| Can we sell a "starter file" for it? | **Yes, but give it free with the $12 product, don't sell it alone.** It's our own data (categories, notes, rules) loaded into their free app. Call it "a starter budget for Actual", never "the official Actual template" | MIT lets anyone build on it; naming stays nominative |
| Do we need permission? | **No.** We're not copying their code or docs. If we quote a sentence of their docs on screen, link it | — |

**Rules for every episode:**
1. Name it accurately: "Actual Budget" or "Actual", "a free, open-source budgeting app". Never "our app".
2. Say on screen and in each description: *"Money Made Simple isn't affiliated with or endorsed by Actual
   Budget. Actual is free and open source (MIT licence)."*
3. Link actualbudget.org in every description. No affiliate links for Actual (there aren't any; it's free).
4. Don't say it's "the best", "safest" or "bank-level secure". Say what it does: runs on your computer, your
   data stays local unless you set up a sync server.
5. If a paid host is mentioned (PikaPods, Fly.io), say it costs money and that we get nothing from it.
6. Use **fictional numbers only**: the "Maya" example from The 20-Minute Budget ($3,500 take-home), clearly
   labelled "Example (fictional)". Never a real bank login, account number or statement on screen.
7. YouTube: this is real screen footage with Dhruv's own voice, so it's the original element, and no
   altered-content label is needed. If any part uses the Kokoro voice instead, tick YouTube's
   altered-or-synthetic box per `platform-rules.md`.

## 2. How the plan maps onto Actual

The 20-Minute Budget puts every dollar into four lines. Actual is an envelope (zero-sum) budget: money you
haven't assigned shows in **To Budget**, and the docs' rule is that "all your money should have a job"
([envelope budgeting](https://actualbudget.org/docs/getting-started/envelope-budgeting)). They fit together
like this:

| 20-Minute Budget | In Actual | How it behaves |
|---|---|---|
| Line 1: **Bills** | Category group "Bills" with one category per bill (Rent, Insurance, Utilities, Internet, Phone, Subscriptions, each debt minimum) | Linked to **Schedules**, so each bill is expected and auto-matched |
| Line 2: **Funds** (sinking funds) | Group "Funds": Car maintenance, Gifts & holidays, Travel, Clothing, Medical, Annual renewals | Leftover balances roll into next month by default, which is exactly a sinking fund |
| Line 3: **Goals** | Group "Goals": Emergency fund, Extra debt payment | Assigned first each month |
| Line 4: **Weekly** | One category "Weekly spending" (groceries, gas, fun all in one), budgeted at the monthly pool ($800 for Maya) | Weekly check: spent so far vs. $184 × weeks elapsed. Optional: a separate "Weekly spending" checking account, so its balance *is* the number |
| Monthly reset | Next month's column, To Budget → 0 | Goal templates can fill it in one click (experimental) |

**Goal templates** are an experimental feature (turn on under Settings → Experimental features, check the
exact path in the app). A line in a category's notes sets its monthly amount
([goal templates](https://actualbudget.org/docs/experimental/goal-templates)):
- `#template 1250` for a fixed bill, or `#template schedule Rent` to follow the Rent schedule.
- `#template 600 by 2027-12` for a dated sinking fund (it spreads what's left over the months).
- `#template 50 up to 300` for a fund with a cap.
- Then **Apply budget template** in the month menu. It fills only categories still at 0.

Because it's experimental, Episode 6 shows it as optional, and every episode works without it.

### The starter file (free bonus in the $12 product)

A demo budget built in Actual and exported as a zip (Settings → Export data), which buyers import as a new
file. It contains:
- The four groups and Maya's categories and amounts, with a note on each explaining it.
- `#template` lines in the notes (harmless if templates are off).
- 3 rules: payee renames and auto-categorising, for common names like "NETFLIX.COM" → Subscriptions.
- Schedules for Maya's bills, and one month of clearly fictional transactions.

**To check before shipping:** export from the current version, re-import it into a fresh install on another
computer, and confirm categories, notes, rules and schedules all survive. Write a one-page "import and clear
the example" guide in the product folder. This is product-thread work (PR #6), not done here.

## 3. The series at a glance

| # | Title (YouTube) | Length | What the viewer can do after |
|---|---|---|---|
| 1 | Free budgeting app that works offline: Actual Budget setup (no account needed) | 6-8 min | Installed, first budget file open |
| 2 | Set up your accounts in Actual Budget (on-budget vs off-budget, explained) | 7-9 min | Accounts with starting balances |
| 3 | The 4-line budget in Actual: give every dollar a job in 10 minutes | 9-11 min | Categories made and money assigned |
| 4 | Import your bank transactions into Actual (CSV/OFX) + rules that categorise for you | 8-10 min | A month imported, 3 rules working |
| 5 | Never miss a bill: schedules and credit cards in Actual Budget | 8-10 min | Bills scheduled, card handled |
| 6 | The 20-minute weekly budget check (Actual Budget routine) | 8-10 min | Can run the weekly and monthly routine |

**Cadence:** one a week on MMS's Sunday long-video slot after the YouTube series in `mms-youtube-series.md`,
or swap them in for weaker slots. Each gets **2-3 Shorts** cut from it (vertical crop of the app, one tip per
Short). Spanish versions for Dinero Simple later: Actual's interface language setting needs checking first.

**Recording setup for all six:**
- A fresh install with **only the fictional Maya data**. Hide the desktop, browser tabs and notifications.
- 1920×1080, app window at 1600×900 or full screen, system zoom 125% so text reads on phones.
- Record voice separately or with the screen, then trim silences with auto-editor (`oss-landscape.md` #4).
- Cursor highlight on. Zoom in (post-production) on every button you click.
- Chapters in each description, using the section times below.

---

## Episode 1: Install Actual Budget (desktop, local, no account)

**Sources:** [Install](https://actualbudget.org/docs/install/)

**Hook (0:00-0:20), on camera or over the finished budget screen:**
"Most budgeting apps cost $100 a year and want your bank password. This one is free, open source, and
runs on your own computer. In 7 minutes you'll have it installed and ready, and by the end of this series
you'll have a budget you run in 20 minutes a week."

| Time | Shot | Voiceover (say it in your own words) | On-screen text |
|---|---|---|---|
| 0:20 | actualbudget.org home page | "This is Actual Budget. It's an envelope budgeting app, which means every dollar gets a job, and it's free and open source." | "Actual Budget · free · open source (MIT)" + not-affiliated line |
| 0:45 | Install docs page, the options listed | "There are a few ways to run it. The desktop app for Windows, Mac and Linux works offline, with your data on your computer. There's a browser version you can run locally, but the docs themselves say it's not recommended for long-term use. And if you want sync between devices or the phone, you run a small server, either yourself or a paid host." | "Desktop = simplest" |
| 1:45 | Simple diagram (made in Canva or the factory's chart style): Desktop app → your computer. Server → phone + laptop | "For this series we're using the desktop app. No server, no account, no bank login. You can add sync later." | "Start local. Add sync later." |
| 2:15 | Downloads page → download for your OS → install | Narrate the install. Mention the OS warning dialogs if they appear | — |
| 3:30 | First launch, create a new file | "Create a new budget file. Call it something like 'Home budget'." | — |
| 4:15 | The empty budget screen. Point at To Budget, the month columns, the sidebar | "Three things to know. This number is To Budget: money you have that doesn't have a job yet. These are months. And over here are your accounts, which we'll add next video." | Labels on each area |
| 5:15 | Settings → Export data | "One habit now: back it up. Settings, Export. Do it once a month, or before you change anything big." | "Back up monthly" |
| 5:45 | Close | CTA (below) | — |

**CTA (last 30 s):** "Next video we add your accounts. If you want the plan we're building, with the
spreadsheet and a starter file you can import straight into Actual, it's The 20-Minute Budget, linked
below. The app is free either way."

**Description:** chapters, actualbudget.org link, not-affiliated line, "Educational content, not financial
advice", product link with UTM `?utm_source=youtube&utm_campaign=actual-1`.

**Shorts to cut:** (a) "The free budgeting app that doesn't want your bank password" (0:00-0:45 + install
montage). (b) "What 'To Budget' means" (4:15-5:15).

---

## Episode 2: Accounts, on-budget vs off-budget, starting balances

**Sources:** [Accounts](https://actualbudget.org/docs/accounts/)

**Hook:** "Before you budget anything, the app needs to know what money you actually have. Get this
part right and everything after it is easy."

| Time | Shot | Voiceover | On-screen text |
|---|---|---|---|
| 0:20 | Sidebar → Add account | "Add account. You'll see two choices: create a local account, or set up bank sync. We're doing local. You type or import transactions yourself, and nothing connects to your bank." | "Local = no bank connection" |
| 1:00 | Add "Bills checking", $1,500 (fictional) | "Use today's real balance from your bank app. For Maya, our example, bills checking has $1,500." | "Example (fictional)" |
| 1:45 | Add "Savings" and "Weekly spending" | "Maya uses three accounts: bills checking where pay lands, savings for her funds and emergency fund, and a weekly spending account that only ever holds this week's number." | Diagram from the guide's chapter 5 |
| 3:00 | Add "Credit card" with a negative balance | "Credit cards go in as a negative balance: what you owe." | — |
| 3:45 | Add a 401(k) or car loan, tick **off budget** | "Off-budget is for things you track but don't spend from: retirement accounts, investments, a mortgage or car loan balance. They count toward net worth but don't put money in To Budget." | "On-budget = spendable. Off-budget = tracked only" |
| 5:00 | Budget screen: To Budget now shows the total | "Look at To Budget: that's all your on-budget money, waiting for jobs. Next video we hand them out." | — |
| 5:30 | Quick note on bank sync | "Bank sync exists, but it needs the server plus a provider like SimpleFIN in North America. That's its own video. Importing a file works fine and is what we'll do." | — |
| 6:15 | CTA | Same as Episode 1, pointing to Episode 3 | — |

**Shorts:** (a) "On-budget vs off-budget in 30 seconds". (b) "The 3-account setup that makes budgeting
automatic" (using the guide's payday diagram, a natural product tease).

---

## Episode 3: The 4-line budget: categories and giving every dollar a job

**Sources:** [Envelope budgeting](https://actualbudget.org/docs/getting-started/envelope-budgeting)

This is the episode that sells the product. Teach it fully. The product adds the spreadsheet, the starter
file, and the debt and irregular-income chapters.

**Hook:** "Budgets fail because they ask for 30 decisions a day. This one asks for one number a week. Here's
how to build it in a free app in ten minutes."

| Time | Shot | Voiceover | On-screen text |
|---|---|---|---|
| 0:20 | Slide: the 4 lines (Bills, Funds, Goals, Weekly) | Explain the four lines in one sentence each | The 4 lines |
| 1:15 | Delete or hide Actual's default categories | "Actual starts with some example categories. We'll replace them with four groups." | — |
| 1:45 | Add group "Bills" + Maya's 10 bills | Type them fast; cut the typing down in the edit | Maya's bills table, $2,150 total |
| 3:15 | Group "Funds" + 6 funds | "Sinking funds: predictable costs that aren't monthly. Yearly cost divided by 12. Car maintenance, $480 a year, so $40 a month." | "Yearly ÷ 12" |
| 4:30 | Group "Goals": Emergency fund $200, Extra debt $150 | "Goals get paid first, not with whatever's left." | — |
| 5:15 | Group "Weekly": one category, "Weekly spending" | "One category for groceries, gas, eating out and fun. No policing which is which." | — |
| 5:45 | Assign amounts in this month's column; To Budget goes to 0 | "Now give every dollar a job. Bills, funds, goals... and whatever's left is the weekly pool. For Maya that's $800." | To Budget → $0 |
| 7:00 | Calculator overlay: 800 × 12 ÷ 52 = 184.62 → $184 | "Here's the trick most people miss. Don't divide by four. A month is 4.33 weeks. Multiply by 12, divide by 52, round down. Maya's weekly number is $184." | "× 12 ÷ 52, not ÷ 4" |
| 8:00 | Category notes: type "Weekly number: $184" | "Put the number in the category note so you see it every time." | — |
| 8:30 | Why Funds roll over: show a fund with a balance next month | "Unspent money in a category carries into next month. That's what makes sinking funds work here." | — |
| 9:15 | CTA | "The guide has the full setup, including irregular income, couples and a debt payoff planner, plus the starter file so you can skip the typing. Link below." | — |

**Shorts:** (a) "Why your budget breaks in 5-week months (×12 ÷ 52)". This one stands alone and is the
strongest Short in the series. (b) "Sinking funds in 40 seconds".

---

## Episode 4: Import transactions and set up rules

**Sources:** [Importing](https://actualbudget.org/docs/transactions/importing),
[Rules](https://actualbudget.org/docs/budgeting/rules/)

**Hook:** "Typing every purchase is why people quit. Here's how to pull a month of transactions in at once,
and have the app sort most of them for you."

| Time | Shot | Voiceover | On-screen text |
|---|---|---|---|
| 0:20 | Bank website (a **mock-up**, never a real bank page): "Download transactions" | "Every bank lets you download transactions. Pick OFX or QFX if it's offered; Actual's docs recommend those. CSV works too." | "OFX/QFX > CSV" |
| 1:15 | Account → Import → choose the fictional file | Show the import screen | — |
| 2:00 | CSV field mapping screen | "With CSV you tell it which column is the date, payee and amount. It remembers for next time." | — |
| 3:00 | Duplicate detection | "Import the same week twice by accident? It spots duplicates." | — |
| 3:45 | Rename a payee: "AMZN MKTP US*2K4" → "Amazon" | "When you rename a payee or pick a category, Actual offers to make a rule from it." | — |
| 4:45 | More → Rules → Create new rule: payee contains "NETFLIX" → category Subscriptions | Walk through conditions and actions | "If payee contains... then category = ..." |
| 6:15 | Rule 2: groceries store names → Weekly spending | "For our plan, every grocery store, gas station and restaurant goes to one category: Weekly spending. That's three rules, not thirty." | — |
| 7:15 | Re-import or "apply rules" to show auto-categorised rows | — | — |
| 8:00 | CTA | Starter file includes these rules | — |

**Safety line to say on camera:** "Download the file from your bank's own site or app. Never give a
budgeting video, or anyone, your bank login."

**Shorts:** (a) "Stop typing your budget: import your bank file". (b) "One rule that categorises half your
spending".

---

## Episode 5: Schedules for bills, and credit cards

**Sources:** [Schedules](https://actualbudget.org/docs/schedules),
[Credit cards](https://actualbudget.org/docs/budgeting/credit-cards/)

**Hook:** "If you've ever paid a late fee on a bill you forgot, this is the feature that stops it."

| Time | Shot | Voiceover | On-screen text |
|---|---|---|---|
| 0:20 | Schedules → Add new schedule: Rent, $1,250, repeats monthly on the 1st | "A schedule is a bill the app expects." | — |
| 1:30 | Power bill with an **approximate** amount | "For bills that wobble, mark the amount as approximate. Actual allows a range of about 7.5% either way when it matches." | "Approx. = ±7.5%" |
| 2:30 | Auto-add on vs off | "Turn on auto-add and it creates the transaction on the due date. Or leave it off and it just matches when the real one arrives, within a couple of days." | — |
| 3:30 | Find schedules (it suggests recurring payees from imports) | "Already imported a few months? Find schedules spots repeats for you." | — |
| 4:30 | Upcoming list | "This list is next week's bills. You'll check it in the weekly routine." | — |
| 5:15 | Credit card account: a purchase categorised as Weekly spending | "The safe way to use a card here: every purchase is categorised like cash, and you pay it off in full each week." | — |
| 6:30 | Carried card debt: a "Credit card debt" category in Bills (minimum) and Goals (extra) | "If you're carrying a balance, the minimum goes in Bills and any extra goes in Goals. Actual's docs cover a few ways to handle this; this is the simple one." | — |
| 7:45 | CTA | "The guide's debt chapter compares avalanche and snowball, with a payoff planner." | — |

**Shorts:** (a) "Stop late fees with one setting". (b) "The rule for using a credit card on a budget".

---

## Episode 6: The weekly 20-minute check and the monthly reset

**Sources:** [Envelope budgeting](https://actualbudget.org/docs/getting-started/envelope-budgeting),
[Reports](https://actualbudget.org/docs/reports/),
[Goal templates](https://actualbudget.org/docs/experimental/goal-templates) (optional part)

**Hook:** "Here's the whole routine, with a timer running. 20 minutes, once a week."

| Time | Shot | Voiceover | On-screen text |
|---|---|---|---|
| 0:20 | A 20:00 countdown in the corner for the whole segment (edited down to about 6 minutes of real time) | "Same day every week. Sunday evening works." | Timer |
| 0:40 | **0-5 Look:** import this week's file (or open the synced account) | — | "0-5 Look" |
| 1:40 | **5-10 Log:** Weekly spending category: spent vs $184 × weeks so far | "Week 2: Maya has spent $301 of $368. She's fine." | "5-10 Log" |
| 2:40 | **10-15 Check:** Schedules (did each bill go out?), uncategorised transactions, anything odd | "Anything you don't recognise, dispute it now." | "10-15 Check" |
| 3:40 | **15-20 Decide:** one move. Show the "over" case: move $30 from Weekly next month... or plan a make-up week | "Overspent? Next week is smaller by that much. One move, then close the app." | "15-20 Decide" |
| 4:40 | Overspending in Actual: a red category, and how it carries into next month | "If a category goes red, Actual takes it out of next month's To Budget. Cover it from another category now, or let it carry, but decide." | — |
| 5:40 | **Monthly reset:** next month's column. Assign everything, To Budget → 0. Show Hold for next month on the To Budget menu for early pay | "Paid before the month starts? Hold for next month keeps it for next month's plan." | — |
| 7:00 | Optional: goal templates on, notes with `#template`, Apply budget template | "If you turn on goal templates, which is still experimental, one click fills the month from your notes. Totally optional." | "Experimental" |
| 8:00 | Reports: spending by category for the month | "Once a month, one look at reports. That's it." | — |
| 8:45 | Series wrap + CTA | "That's the system. The free app plus a plan. The guide and starter file are linked if you want to skip the setup." | — |

**Shorts:** (a) "My entire weekly budget routine in 60 seconds" (timer montage). (b) "What to do when you
overspend (don't quit the budget)".

---

## 4. Checklist before recording

- [ ] Latest Actual desktop version installed fresh. Every menu name above checked against it.
- [ ] Only the fictional Maya data in the file. No real names, banks or account numbers anywhere on screen.
- [ ] Mock bank download page made (no real bank's branding).
- [ ] Not-affiliated line in the video and the description of all six.
- [ ] "Educational content, not financial advice" in each description.
- [ ] The 20-Minute Budget product is live, with the starter file tested (export → import on a clean install).
- [ ] Each video run through `factory review` like any other long video: fact-check flags, thumbnail, UTM
      links.

## 5. Open questions for Dhruv

1. **Will you record these yourself?** They only work as real screen footage with your voice. About 90
   minutes per episode including setup and retakes.
2. **Add the starter file to the $12 product?** It's a product-thread change (PR #6) and needs testing.
3. **Spanish versions for Dinero Simple?** Only after checking that Actual's interface can be shown in
   Spanish, so the screen matches the voice.
