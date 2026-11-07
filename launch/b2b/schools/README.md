# Money Made Simple for Schools (weekly mini-lessons, white label)

A **10-minute financial literacy lesson every week** for high school teachers and college advisors: a class
slide, a student handout, a lesson page with an activity and exit ticket, teacher notes and sources, with
the school's name on every page. Lessons are aligned to the **2021 National Standards for Personal
Financial Education** (Council for Economic Education with the Jump$tart Coalition). **Nothing has been
sent.** Dhruv sends every email by hand. Payment links are placeholders, and nothing was bought.

| File | What it is |
|---|---|
| `product.json` | Labels, call to action ("Money questions? Talk to …") and formats: lesson page (email HTML/text), class slide, student handout PDF, LMS image. |
| `issues.json` | 4 sample lessons, Jan 11 to Feb 1 2027 (class weeks), delivered 2 weeks early. Each has a `standard` field naming its area. |
| `brands/example.json` | A **fictional** school, "Sample Valley High School" (555 number). |
| `brands/cu-sponsored.json` | The same school, sponsored by a fictional credit union: the credit line prints on every format. |
| `brands/placeholders.json` | Every brand slot as a token, for the school's review. |
| `sales-sheet.html` | One-page sales sheet → `out/sales-sheet.pdf`. |
| `PROSPECTS.csv` | 40 prospects: 13 Montana districts, 15 Idaho districts, 8 Montana two-year colleges, 4 Idaho community colleges, each with a 1–5 `fit_score`. |
| `FOLLOW_UP_SEQUENCE.md` | 3 emails for schools that got the sample and went quiet. |
| `onboarding/` | Services agreement and invoice templates (lawyer review needed). |

Build from `launch/b2b/`: `python3 build.py schools`. Deliver a month to a signed school:
`python3 deliver.py schools --month 2027-01 --name "..." --logo ... --set HELP_CONTACT="..."`.

## The 4 sample lessons and the standards

| Week | Lesson | National Standards area |
|---|---|---|
| Jan 11 | Your first paycheck: gross vs net, Social Security 6.2%, Medicare 1.45%, the W-4 | Earning Income |
| Jan 18 | Needs, wants and a 10-minute budget (50/30/20 as a starting point) | Spending; Saving |
| Jan 25 | Credit scores: FICO's five ingredients, free reports | Managing Credit |
| Feb 1 | Fake job offers and the overpayment check | Managing Risk |

The next topics follow the sixth area, **Investing** (compound interest, the Rule of 72), then rotate:
FAFSA and scholarship scams, renting a first apartment, car loans, banking basics, insurance. Alignment is
by area and benchmark theme. The standards are published by the CEE and Jump$tart, and we don't claim
an official endorsement, so never say "certified" or "approved".

## Pricing, and why

| Plan | Includes | Per school year |
|---|---|---|
| Teacher | One teacher or advisor | **$79** |
| School | Every teacher and advisor in one building | **$299** |
| District | Up to 5 high schools; larger by quote | **$899** |
| College | One campus (advising, TRIO, financial aid, first-year seminar) | **$399** |
| Sponsored | A local credit union pays the school or district price; the school pays nothing | same as above |

Founding pilot: the first 3 schools get spring semester 2027 free.

**What the prices are based on (all public, checked 7 Nov 2026):**

- **Strong free competitors exist.** Next Gen Personal Finance's curriculum is free
  ([NGPF](https://www.ngpf.org/blog/advocacy/how-many-states-require-students-to-take-a-personal-finance-course-for-high-school-graduation)),
  and Banzai offers standards-aligned content "at no cost" to districts ([banzai.org](https://banzai.org/curriculum/mt)).
  So we can't charge for content alone. The price is for **time saved and the school's own branding**: a
  ready 10 minutes a week, current to this year's rules. That keeps it at teacher-card and small-PO levels.
- **Paid curricula quote per school.** Ramsey Education's high school curriculum uses custom quotes based on
  students and use ([ramseysolutions.com](https://www.ramseysolutions.com/education/foundations-personal-finance-hs0)).
  We publish flat prices instead, since a small buyer can approve those without a quote.
- **Demand is real and recent.** Montana requires a half-credit of financial education or economics for
  graduation from the class of 2026 ([Montana Free Press](https://montanafreepress.org/2024/08/09/preparing-montana-students-for-world-finance)).
  Oregon requires a personal finance semester for students graduating after Jan 1, 2027, and 30 states have
  passed requirements ([CEE Survey of the States](https://www.councilforeconed.org/survey-of-the-states-progress-report)).
  NGPF counts 30 states with a standalone course as of Apr 2026.
- **Sponsorship is a common model.** Banzai works with local banks and credit unions, and runs co-branded
  sites under their names (for example austinbank.banzai.org). Our sponsored tier lets a credit union client of `../credit-union-alert/` fund local
  schools, and pairs with the Scam Watch sponsorship.

**These are proposals.** Confirm them before quoting, and check each district's purchasing rules: many need
a W-9, a vendor form and a purchase order before any invoice.

## Rules for school content

- **No student data, ever.** No logins, no tracking, no student names or emails. Teachers post the lesson
  themselves. This keeps FERPA and state student-privacy laws out of the picture; say so plainly when asked.
- **Education only.** No product, bank, card, app or investment recommendations. A sponsor's name appears
  only in the credit line, never in a lesson.
- **Made-up examples only,** so no student is asked to share their own or their family's money.
- **Every fact sourced** (IRS, CFPB, FTC, myFICO for score weights), checked at delivery.
- Footers carry the AI disclosure ("Drafted with AI help and fact-checked by a person").

## Cold emails

Write to **curriculum directors, CTE or social studies coordinators** (districts) and **student success,
TRIO or financial aid directors** (colleges), using only contacts the district or college lists on its own
site. Don't email individual teachers from a staff directory, and never guess an address. Same sending rules as
`../credit-union-alert/COLD_EMAILS.md`: plain text, no attachment or link in email 1, your mailing address
and an opt-out line in every email, stop at the first "no". **Avoid Dec 18 to Jan 4 and the last 2 weeks of
each semester.** The best windows are early December (planning for spring) and late July to August.

**Email 1 (district)**
Subject: A ready 10-minute money lesson each week, for {District}

> Hi {First name},
>
> {Personal line: one true sentence from their site, e.g. their new personal finance course or CTE pathway.}
>
> I write a weekly financial literacy mini-lesson for high schools: a class slide, a student handout, an
> activity and an exit ticket, with your school's name on it, aligned to the 2021 National Standards for
> Personal Financial Education. Each lesson arrives 2 weeks early, uses made-up examples, and needs no
> student data or logins.
>
> {Montana only: With the new half-credit requirement starting with the class of 2026, it can fill
> advisory or support a finance or economics course.}
>
> Would a free 4-lesson sample be useful? It's made for a fictional school, so you can see exactly what
> teachers would get.
>
> {Your name}
> Money Made Simple · {Your mailing address}
> If you'd rather not hear from me again, just reply "no thanks".

**Email 1 (college):** same, but say "first-year seminars, advising and TRIO workshops" instead of high
schools, drop the Montana line, and offer it for "your students".

**Follow-up 1 (day 4, same thread):** "Hi {First name}, just checking this reached you. Happy to send the
sample if it's useful, or I'll leave it there." Same signature.

**Follow-up 2 (day 10): give something useful.** Paste the paycheck lesson's activity and answer key as
plain text: "Feel free to use this with a class as it is." Then stop. Same signature.

**Credit union sponsors:** if you already work with a credit union through `../credit-union-alert/`, offer
the sponsored tier there first. "Sponsor financial literacy at [high school]" is an easy yes for many
credit unions, and the school pays nothing.

**When they say yes to the sample:** send `out/demo-packet.zip` and `out/sales-sheet.pdf`.
