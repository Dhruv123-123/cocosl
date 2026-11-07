# Rate My Budget: viewer submissions

Every Rate My Budget so far (#1–41) is **fictional**, and each one says so on screen and in the caption. This kit is for when viewers start sending in their own budgets. It covers how to collect a budget, the consent we need, how to anonymise it, and how to label the post. Nothing gets posted from a submission until every box in the review checklist is ticked.

**Main rule:** a real person's budget never appears as it was sent. We change details so nobody can recognise the person, and the post says the budget is based on a viewer's and that details were changed. Anything we invent is labelled fictional. A post must never present an invented budget as a real viewer's.

## 1. Where submissions come from

- **Use the form, not DMs.** Use a form (Tally, Google Forms or similar) with the fields in section 2. Link it from link-in-bio and from the RMB captions. If someone sends numbers by DM or comment, reply with the DM template in section 6 and point them to the form. Don't build a video from a DM thread.
- **We don't accept** screenshots of bank or card apps, statements, pay stubs, or anything showing account numbers, names, addresses or employer names. If one arrives anyway, delete it and say so (section 6).
- **Adults only.** Submitters must confirm they're 18 or older. Teen and student budgets in the series stay fictional.
- **Nothing is paid or offered** in exchange for a submission, so a submission is never an endorsement. We don't mention any product a submitter uses by name.

## 2. Submission form (copy into the form builder)

Make every money field a whole number in US dollars per month. Answers in *italics* are optional.

| # | Field | Type | Notes |
|---|---|---|---|
| 1 | Nickname to use (not your real name) | short text | We'll still change it. |
| 2 | Age range | choice: 18–24, 25–34, 35–44, 45–54, 55–64, 65+ | Ranges only. Never an exact age. |
| 3 | Household | choice: just me, partner, partner + kids, single parent, roommates, other | |
| 4 | Region | choice: Northeast, Midwest, South, West, outside the US | No city or state. |
| 5 | Monthly take-home pay (after tax) | number | If it varies, give a typical month and the range. |
| 6 | Housing (rent or mortgage) | number | |
| 7 | Other fixed bills (utilities, phone, insurance, transport) | number | |
| 8 | Debt payments, with each rate if known | text, e.g. "card $150 at 24%" | |
| 9 | Groceries and eating out | number | |
| 10 | Everything else you spend | number | |
| 11 | Saving each month (and where: savings, 401(k), etc.) | number + short text | |
| 12 | Emergency savings today | choice: $0, under $500, $500–$2,000, $2,000–$10,000, $10,000+ | Ranges only. |
| 13 | The one thing you want help with | long text, 300 characters | We'll paraphrase it. We never quote it word for word. |
| 14 | *Anything we should NOT mention* | long text | We follow it. |
| 15 | Email for questions (never shown or shared) | email | Only used to ask questions and to confirm before posting. |
| 16 | Consent (all three boxes required) | checkboxes | Wording in section 3. |

At the top of the form, show: *"Don't include your name, employer, city, account numbers or screenshots. We change details before anything is posted. Submitting doesn't mean we'll use your budget."*

## 3. Consent wording (form checkboxes, version `rmb-consent-v1`)

All three boxes must be ticked. Store the version and the date with the submission.

1. *"I'm 18 or older, and this is my own budget (or I have permission from everyone in my household whose money is in it)."*
2. *"I agree that Money Made Simple can use these numbers, with details changed so I can't be identified, in a Rate My Budget video, carousel, caption or email. It will be labelled as based on a viewer's budget. I won't be named, quoted word for word or paid, and I'm not endorsing anything."*
3. *"I understand this is general education, not personal financial advice. I can ask for my submission to be deleted, or for a post to be taken down, at any time by emailing [contact email]."*

**Before posting**, email the submitter the changed version (the numbers and the one-line problem and fix) and wait for a "yes". If they don't answer within 14 days, don't post it. Turn it into a fictional example instead (section 5, route B).

## 4. Anonymising: the changes every real submission gets

Make all of these changes, even if the submitter says they don't mind being recognised.

- **Rounding:** round every dollar amount to the nearest $50, or $100 above $2,000. Then nudge the amounts by up to about ±10%, as long as the problem and the fix still work out the same. Make sure the totals still add up on screen.
- **Remove:** names (including the nickname they gave), employer, job title (keep a broad field like "healthcare" only if the budget needs it), city or state, school, exact ages, kids' ages or names, dates, and any unusual detail that could identify someone (a rare job, an unusual pet, a specific medical condition).
- **Generalise:** "Target" becomes "a big-box store", "my Honda" becomes "a car payment" and "Chase card" becomes "a credit card". No brand or provider names at all, so it can't read as an endorsement.
- **Paraphrase:** never quote the submitter's own words on screen, in the caption or in the voiceover. The guardrails also block first-person testimonial lines ("I've tried", "changed my life", "I swear by").
- **Don't stack sensitive details.** If the budget includes medical debt, a divorce, a disability, immigration status or a recent death, either leave it out or turn the budget into a fictional one (route B).
- **No screenshots:** visuals are always our own illustrated slides, never the submitter's materials.

## 5. Labels: two routes, never mixed

**Route A: based on a real submission** (consent and confirmation done).
- On screen, first beat: `Viewer budget · details changed`
- Caption line, verbatim: *"Based on a viewer's budget, shared with permission. Names and details changed so they can't be identified. Educational, not financial advice."*
- In content.json, add `"submission": {"id": "RMB-S-0001", "consent_version": "rmb-consent-v1", "consented_on": "YYYY-MM-DD", "confirmed_on": "YYYY-MM-DD"}`. Don't put any personal data in the repo. The id links to the private intake log.

**Route B: fictional** (every RMB so far, and any submission we only use as inspiration).
- On screen: `Fictional example`
- The caption carries the standard line (`FICT` in the generators): *"Fictional example budget for illustration, not a real person or submission…"*
- A fictional budget must not say or hint that it came from a viewer.

`tests/test_pack.py::test_rate_my_budget_items_are_labelled` enforces this. Every Rate My Budget item must carry the fictional line, or the route-A caption line plus a `submission` block with a consent version and both dates.

## 6. Reply templates

**DM or comment with numbers in it:**
> Thanks for sharing! To keep you anonymous we only take budgets through our form (link in bio). It asks for numbers only, never names or screenshots, and we change details before anything goes up. Submitting doesn't mean we'll use it.

**They sent a screenshot with account details:**
> Thanks! We've deleted the screenshot because it showed account details, and we never use those. If you'd like a rating, please send the numbers through the form in our bio instead.

**Asking to confirm the changed version (route A):**
> Hi! We'd like to feature a budget based on yours in Rate My Budget. Here's exactly how it would appear, with details changed: [numbers / problem / fix]. Reply "yes" to approve. If you'd rather we didn't, just say so and we'll delete it. You can ask us to take the post down at any time.

**Takedown or deletion request:** reply within 2 business days, unpublish the post on every platform, delete the row from the intake log and any copies, and reply to confirm. Don't argue the request or ask why.

## 7. The private intake log

Keep it in a private spreadsheet, **never in this repo or the project files**. Columns:

`id · received_on · consent_version · consent boxes (3) · email · status (new / shortlisted / sent for confirmation / confirmed / declined / used fictionally / deleted) · confirmed_on · post content_id · takedown_on · notes`

- Delete unused submissions and their emails after 90 days.
- Once a submission is used, keep only the id, consent version and dates, and delete the raw numbers and the email after 12 months.

## 8. Review checklist before posting (route A)

- [ ] All 3 consent boxes ticked; version and date are in the log
- [ ] The submitter has confirmed the changed version in writing
- [ ] All the section 4 changes are made; nothing could identify the person to someone who knows them
- [ ] No brand, provider or employer names; no quotes in the submitter's words
- [ ] Route-A label is on screen and the caption line is verbatim; `submission` block is in content.json
- [ ] The score uses the published scorecard (month-2 "Rate My Budget: the 5-question scorecard") and the tone is kind. We rate the plan, not the person.
- [ ] The fix is general education (no "you should buy X") and has no income or results promises
- [ ] AI disclosure and the usual human review are done, as for every post
