# Sender setup guide: one account, a group per brand, welcome automations, footer, imports

Written 2026-11-07. **Docs only. Nothing was signed up for or sent.** This follows the choice in
`newsletter-tool-decision.md`: **Sender Free Forever, one account**, with a group and a sender identity per
brand. Dhruv does every step in Sender himself. Steps come from Sender's help pages (linked at the end). Where
a page didn't say something, this guide says so instead of guessing.

## TL;DR

- **Groups:** two per brand. `<Brand> - new` is where the signup form drops people. `<Brand>` is the
  confirmed list that gets the newsletter. A double opt-in automation moves people from the first to the
  second.
- **Welcome:** one automation per brand, triggered by "Subscriber joins a group" on the confirmed group.
  Our day offsets 0, 1, 2, 3, 4, 5, 6, 9 become: email, then 1-day delay + email (×6), then a 3-day delay +
  the last email. Every gap is at least 1 day, so our 20-hour minimum gap still holds.
- **Only Money Made Simple has a welcome sequence today** (`brands/sequences/money-made-simple.yaml`).
  Scam Decoded, 1099 Money and Dinero Simple need one written before their automations can be built.
- **Footer:** Sender adds the unsubscribe link and reads the postal address from **Settings > Email
  footer**. Put a real address there before the first send. Our "not financial advice" and AI-disclosure
  lines go in the email body, not the footer.
- **Imports:** one CSV per brand, email in the first column, dates as `YYYY-MM-DD hh:mm:ss`, and pick the
  group on the last screen. **Leave "Trigger active automations upon import" unticked** for anyone who
  already got the factory's welcome emails, or they get them twice.
- **Turn off the factory's own welcome sender** once Sender runs the welcomes: set `SEQUENCES_EVERY=0`.
  The worker treats 0 as "never" (`worker.py`, `_due`). Leave it on while there is no Sender automation.

## 1. Account and brands (once)

1. Create one Sender account with `hello@<main domain>`. Ask support the one-account question first
   (`newsletter-tool-decision.md`, "Before signing up").
2. **Settings > Email footer:** enter the business's postal address (see section 4).
3. Per brand, add a **sender identity** (from name = the brand, from email = `hello@<brand domain>`), and
   authenticate that domain (SPF and DKIM records at the registrar, `domain-plan.md`).
4. For Dinero Simple, set the template language to Spanish so the unsubscribe and browser links are in
   Spanish (`newsletter.md`).

## 2. Groups per brand

| Brand | Signup group | Confirmed group (newsletter + welcome) | Optional |
|---|---|---|---|
| Money Made Simple | `MMS - new` | `Money Made Simple` | `MMS - not confirmed` |
| Scam Decoded | `Scam - new` | `Scam Decoded` | `Scam - not confirmed` |
| 1099 Money | `1099 - new` | `1099 Money` | `1099 - not confirmed` |
| Dinero Simple | `Dinero - new` | `Dinero Simple` | `Dinero - no confirmado` |

**Why two groups:** Sender's double opt-in is built from a form, a group and an automation. The form adds
people to a "new" group. An automation sends a confirmation email with a button, waits, checks whether it
was clicked, and moves clickers to the confirmed group. The welcome then triggers on joining the confirmed
group, so nobody gets the lead magnet before confirming.

**Double opt-in automation (per brand):** Automation > Create New Workflow > trigger "Subscriber is added
to a group" = `<Brand> - new` > Email ("Confirm your subscription", one button) > Delay 1 day > Condition:
link clicked? > Yes: move to `<Brand>` > No: move to `<Brand> - not confirmed`.

Sender's help page doesn't say whether API or imported contacts also go through this. Imports go straight
into the confirmed group (section 5), so they skip it.

## 3. Welcome automation, mapped from `brands/sequences/money-made-simple.yaml`

Automation > Create New Workflow > Create from scratch > name it `MMS welcome` > trigger **"Subscriber joins
a group" = `Money Made Simple`**. Then add these steps in order. Sender's delays count from the step before,
so our absolute day offsets become relative delays.

| Our step (day_offset) | Sender steps | Subject | Preview text | Button |
|---|---|---|---|---|
| 0 | Email (right after joining) | Your 7-Day Money Reset is here | One 15-minute task a day. Start with Day 1. | Open the checklist → checklist link |
| 1 | Delay 1 day, Email | Day 1: the only number you need to start | from the yaml | checklist link |
| 2 | Delay 1 day, Email | Day 2: the 15-minute subscription sweep | from the yaml | — |
| 3 | Delay 1 day, Email | Day 3: the expenses that aren't really surprises | from the yaml | — |
| 4 | Delay 1 day, Email | Day 4: a small buffer beats a perfect plan | from the yaml | — |
| 5 | Delay 1 day, Email | Day 5: debts on one page (and finishing the reset) | from the yaml | checklist link |
| 6 | Delay 1 day, Email | If you'd rather the spreadsheet did the maths | product line from the yaml | See what's inside → budget page |
| 9 | **Delay 3 days**, Email | Last note on the template (plus a savings tip) | One savings tip, then back to the weekly email. | Look at {product_name} → budget page |

Then **Activate** (workflows stay in draft until you do), and use **Test workflow** on your own address.

**What doesn't carry over, and what to do:**

| Factory feature | In Sender | Do this |
|---|---|---|
| `{link:...}`, `{signoff}`, `{product_name}`, `{price}` placeholders | Not understood | Paste the **rendered** text from `factory sequence-preview money-made-simple`, not the yaml |
| `{if launch}...{/if}` (the day 6 and day 9 launch-price lines) | No date conditional in the pages read | Build the automation with the **no-launch** wording. During a launch week, edit the day 6 and day 9 emails to the launch wording, and change them back the day `launch_ends` passes, so no email claims an expired discount |
| `max_late_days: 3` (skip steps that are 3+ days late) | Not offered | Not needed: Sender sends on schedule |
| `min_gap_hours: 20` | Delays of at least 1 day | Never use a delay shorter than 1 day |
| Our footer (unsubscribe + `BUSINESS_ADDRESS`) | Sender's footer | Remove ours; keep `footer_note` at the end of the body (section 4) |
| One step per run, never the same step twice | Sender tracks each contact in the workflow | Don't re-trigger: don't remove and re-add people to the confirmed group |

Sender's example welcome also adds an "opened?" condition and branches. **Skip that**: every confirmed
subscriber should get the whole reset, whether or not their mail app reports opens.

## 4. The footer: what CAN-SPAM needs and where each part lives

The FTC's CAN-SPAM guide applies to any email whose main purpose is commercial. The day 6 product email
and the weekly issues with affiliate links count. The rules that matter for us:

| Rule (FTC guide) | Where it's handled |
|---|---|
| Header information (from, reply-to) isn't misleading | Sender identity per brand: the brand name and a domain we own |
| Subject lines match the content | Our subjects are plain descriptions; keep them that way |
| Say clearly if the message is an ad | Product and affiliate emails keep their disclosure lines (`affiliates-for-new-creators.md`) |
| **Include a valid physical postal address**: a street address, a USPS-registered PO box, or a private mailbox registered with a commercial mail receiving agency under USPS rules | **Settings > Email footer** in Sender. Use a PO box or virtual mailbox, not a home address |
| **Tell people how to opt out, clearly** | Sender's `{$unsubscribe}` tag, in the default footer of drag-and-drop templates. **Custom HTML templates need it added by hand**, inside a link |
| If you offer an opt-out menu, one choice must stop all marketing email | Sender also has `{$unsubscribe_from_all}`; with one account for four brands, people should be able to leave just one brand (`{$unsubscribe}`) or all |
| Honour opt-outs within 10 business days; the link must work for 30 days after sending; don't charge or ask for more than an email address to unsubscribe | Sender handles the link and the list; don't re-import unsubscribed people (our export never includes them) |
| Penalty: up to $53,088 per violating email (FTC, January 2024 figure) | — |
| You're responsible even if a tool sends it | Check each new template's preview for both the address and the unsubscribe link |

**What goes at the end of each email body** (above Sender's footer), per brand: the brand's `footer_note`.
For Money Made Simple that is: "Educational content, not financial advice. For decisions about your own
situation, talk to a qualified professional. Written with help from AI tools and reviewed by a human."

Sender's free plan also puts a Sender logo on emails (`newsletter-tool-decision.md`). That's allowed and
needs nothing from us.

## 5. Import format (moving existing subscribers in)

Sender takes **.csv, .txt or .xlsx up to 64MB**, matches on email address, skips invalid addresses, and
wants **dates as `YYYY-MM-DD` or `YYYY-MM-DD hh:mm:ss`**. Field names go in the first row so Sender can
suggest the mapping. Every selected column must be mapped or deselected before you can continue.
**Every contact in a file goes into every group you pick**, so use **one file per brand**.

Target file per brand (UTF-8):

```csv
email,source,subscribed_at,confirmed_at
reader@example.com,site-footer,2026-11-03 14:22:05,2026-11-03 14:25:40
```

`email` maps to Email. `source`, `subscribed_at` and `confirmed_at` map to custom fields (create them with
"+ Create new field" the first time). Don't import `status` or `tags`: everyone exported is confirmed, and
the group replaces the tag.

**Steps:** Subscribers > Add subscribers > Import from a file > Map fields > Organize & import: pick the
brand's **confirmed** group, then decide the automation box:

| Who's in the file | "Trigger active automations upon import" |
|---|---|
| People who already got the factory's welcome emails (or most of them) | **Unticked.** No active automation runs for them, even if they match a group trigger |
| People who signed up but never got a welcome (for example, before the factory sent live) | Ticked, after checking which workflows are active |

Sender asks you to confirm that everyone on the list opted in. Our export only includes confirmed
subscribers, so that's true. **Never import a list from anywhere else.**

**What `factory subscribers-export` gives today** (`funnel/newsletter.py`): columns `email, status, source,
subscribed_at, confirmed_at, tags`, with ISO timestamps (`2026-11-03T14:22:05...`). Sender may not read
those dates, so see change 1 below.

## 6. Factory changes this needs (sent to the main pipeline thread)

1. **`factory subscribers-export --for sender`:** write the four columns above, with dates as
   `YYYY-MM-DD hh:mm:ss` (UTC). Split the output into `...-welcomed.csv` (has any live welcome send in the
   sequence history) and `...-not-welcomed.csv`, so Dhruv knows which file gets the automation box ticked.
2. **`factory sequence-export <brand> --for sender`:** one folder per step with `subject.txt` (subject and
   preview text), `body.html` (our footer removed, `footer_note` kept, placeholders and links rendered),
   `email.txt`, and the **delay from the previous step** in days. Render the launch steps twice
   (`launch/` and `no-launch/`), and write a `CHECKLIST.md` that matches section 3. `sequence-preview`
   already renders most of this, and `newsletter_export.FOOTER_RE` already strips our footer.
3. **A per-brand switch instead of the global `SEQUENCES_EVERY=0`:** for example `welcome_via: sender` in
   the brand yaml, so the worker skips only the brands whose welcomes run in Sender. Until then,
   `SEQUENCES_EVERY=0` turns off all brands' factory welcomes at once.
4. **`factory newsletter --for sender`:** its `CHECKLIST.md` should add one line: "Custom HTML templates
   don't add the unsubscribe link: paste `{$unsubscribe}` in a link, or use the HTML block of a
   drag-and-drop template." Optionally add `--unsub-tag` support so `email.html` can carry
   `<a href="{$unsubscribe}">` for Custom HTML pastes (the `NEWSLETTER_UNSUB_TAG` variable already allows
   this).
5. **Welcome sequences for the other three brands:** `brands/sequences/` has only Money Made Simple.
   Each brand thread should write its own yaml (same shape, its own lead magnet and day-6 product).

## Sources

Read 2026-11-07:
[Sender: importing subscribers](https://www.sender.net/help/subscribers-and-segmentation/importing-subscribers/),
[Sender: create a welcome series](https://www.sender.net/help/automation/create-welcome-series/),
[Sender: double opt-in](https://www.sender.net/help/automation/double-opt-in/),
[Sender Free Forever limits](https://www.sender.net/help/account-settings-and-billing/free-forever-plan-limits),
[FTC: CAN-SPAM Act compliance guide for business](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business).
The `{$unsubscribe}` tag and the Settings > Email footer path come from a secondary guide
([smtpedia](https://smtpedia.com/sender-net-unsubscribe-link/)). Check both in Sender's editor before the
first send. Factory behaviour is from `src/contentfactory/funnel/` and `worker.py` on this branch.
