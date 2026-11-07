# B2B launch checklist (for Dhruv)

Four offers are ready to sell: **credit unions** (Weekly Scam Alert), **libraries and senior centers**
(Scam Watch), **employers** (Money Made Simple at Work) and **CPA and bookkeeping firms** (Freelancer
Money Notes, for their 1099 clients). Nothing has been sent, posted or deployed;
you do every send by hand. Plan on about 2 hours of setup, then 30 to 45 minutes a day.

## 1. Decide (10 minutes)

- [ ] **The name you sell under.** The sales sheets and emails say "Scam Decoded". Members never see it,
      because their packs carry only the client's brand, so this only matters if you rename the brand.
- [ ] **A business name and mailing address** for invoices and email footers. CAN-SPAM requires a real
      postal address in commercial email; one you already have is fine.
- [ ] **The email you sell from.** It goes in every sales sheet and on the landing page.

## 2. Fill in (30 minutes)

- [ ] `{{YOUR_NAME}}`, `{{YOUR_EMAIL}}`, `{{YOUR_PHONE}}` in these files:
      - `credit-union-alert/sales-sheet.html` and `credit-union-alert/roi.html`
      - `employer-wellness/sales-sheet.html`, `community-scam-watch/sales-sheet.html` and
        `freelancer-client-letter/sales-sheet.html`
      - `credit-union-alert/onboarding/KICKOFF_EMAIL.md`
      Find any you missed with `grep -rn "{{YOUR_" launch/b2b --include=*.html --include=*.md`.
- [ ] `{{YOUR_BUSINESS_NAME}}` and `{{YOUR_ADDRESS}}` in `credit-union-alert/onboarding/invoice.html`.
- [ ] `salesEmail` in `site/config.js` (now `REPLACE_ME@example.com`).
- [ ] **Leave every `{{PAYMENT_LINK…}}` as it is.** Set up payments only after the first yes; most
      clients want an invoice anyway.
- [ ] Rebuild everything: `cd launch/b2b && python3 build.py && python3 site/build_site.py`.
- [ ] Optional: publish the landing page by dragging `site/dist/` onto Netlify Drop (free). Do this only
      if you want a link to put in follow-ups; email 1 has no link anyway.

## 3. Send first: credit unions, then accounting firms, libraries, employers

| Week | Who | Why this order | Files |
|---|---|---|---|
| **1** | **Credit unions, rows 1 to 30** (Montana first) | Biggest recurring price, weekly cadence, and the ROI page makes the case. | `credit-union-alert/COLD_EMAILS.md`, `PROSPECTS.csv` |
| **1 to 2** | **CPA and bookkeeping firms** (MT and ID, 30) | Send before mid-January: after that they're buried in tax season until late April. Small firms decide fast, and it's the cheapest yes to get. | `freelancer-client-letter/README.md` (emails inside), `PROSPECTS.csv` |
| **2** | **Libraries and Area Agencies on Aging** | Cheap and quick to say yes; good first logos and testimonials. Call the senior centers (phone script). | `community-scam-watch/COLD_EMAILS.md` |
| **3** | **Employers**, via SHRM chapters and the 2 brokers first | Longer buying cycle. A single broker or chapter can open many doors. | `employer-wellness/COLD_EMAILS.md` |
| 4+ | **Credit unions, rows 31 to 60** (WY, UT, CO) | Use what you learned from batch 1's replies. | same |

Before each prospect's email: fill in their `website` and `contact_route` from their own site (about
3 minutes each), and write one true `{Personal line}`. Send to 5 to 8 new prospects a day, Tuesday to
Thursday mornings, from your own inbox, in plain text with no attachments or links in email 1.
Never guess an address, buy a list or scrape a directory.

## 4. Follow up

| Day | Send | Notes |
|---|---|---|
| 0 | Email 1 | Log `sent` in the CSV. |
| 4 | Follow-up 1 (same thread) | One or two lines. |
| 10 | Follow-up 2: give something useful | The free sample alert, with no strings attached. |
| 21 | Final note | Only if they replied once and then went quiet. Otherwise stop after day 10. |

- **Stop at the first "no" or "unsubscribe"**, and note it in the CSV.
- Replies to common questions ("send pricing", "talk to compliance", "we already do this") are in each
  `COLD_EMAILS.md` under **Replies**.
- **When someone asks for a sample,** send the fictional sample pack zip, the sales sheet and the
  compliance note (plus `roi.pdf` for credit unions). Never brand a pack with their logo until they ask.
- **When someone says yes,** follow `credit-union-alert/onboarding/README.md`. It covers kickoff,
  intake, approval, the first send and the invoice. For the other two products, use the same kit and
  change the product name.

## 5. Check after 2 weeks

- About 40 credit unions emailed with **no replies**? Change the subject line and the first sentence
  before you touch the price.
- Replies, but every one says "no budget"? Lead with the Essentials tier ($49) and the 2 free months.
- **One yes is enough to start.** Before its first send, write weeks 5 and 6 from
  `credit-union-alert/CONTENT_CALENDAR.md`, so you're always 2 issues ahead.

## Not ready yet

- **Spanish edition** (`credit-union-alert/es/`): it needs a native-speaker review before you offer it.
  Until then, sell Plus without promising Spanish, or say it starts once a reviewer is lined up.
- **Broker partner rates** in `employer-wellness/COLD_EMAILS.md` are proposals; confirm them before
  quoting.
- **4 library websites** in `community-scam-watch/PROSPECTS.csv` still need looking up.
