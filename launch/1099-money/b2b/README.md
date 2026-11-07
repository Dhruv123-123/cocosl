# 1099 Money B2B outreach: coworking spaces and freelancer groups

Everything you need to offer the free **2027 Freelancer Tax Calendar** to 75 coworking spaces and
freelancer associations, and then the **$49 Freelancer Money Bundle** as a member perk. **Nothing here
has been sent.** You send every email yourself, by hand, from your own inbox.

## What's in here

| File | What it is |
|---|---|
| `leads.csv` | 75 researched coworking spaces and freelancer groups, in the factory's import format (`name,contact_name,email,website,niche,source,notes`). Sorted in send order. |
| `leads_research.csv` | Same leads with the research: where the email is published, what we noticed, flags, narrow-inbox and free-mail markers, the opener and the subject line. |
| `pitches/NNN-name.md` | One file per lead: Email 1, Follow-up 1, Follow-up 2 and planned send dates. Numbered in send order. |
| `ALL_PITCHES.md` | Every pitch in one file, for scrolling. |
| `TRACKER.csv` | Send schedule (8 new a weekday from Wed 11 Nov) with blank columns for sent dates, replies, calendar sent, blurb shared, offer, bundle sold and outcome. |
| `FOLLOW_UP_SEQUENCE.md` | The sequence (day 0 / 4 / 9), plus what to send for every kind of reply, including the member blurb. |
| `GROUP_LICENSE.md` | Draft member-code and group-license terms and proposed prices. |
| `build_b2b.py`, `openers.py`, `leads_source.tsv` | The source. Edit a lead or an opener, then run `python3 launch/1099-money/b2b/build_b2b.py`. |

## The offer

- **Email 1** gives something useful first: the free 2027 Freelancer Tax Calendar PDF
  (`apps/freelance-tax/downloads/freelancer-tax-calendar-2027.pdf`), to share with members, plus a
  ready-to-paste newsletter blurb. No link in the first email, so it stays out of spam folders.
  The hook is real and timely: the 4th estimated payment for 2026 is due Fri Jan 15, 2027.
- **Follow-up 1** is a short bump.
- **Follow-up 2** gives three tax habits for their kind of member for free (the third is written for
  each group: coworking members, translators, editors, journalists, designers, medical writers,
  consultants), then offers the bundle once: a member code ($39 instead of $49) or a group license
  ($199 for up to 25, $499 for up to 100). **These prices are proposals.** Change them in
  `build_b2b.py` (`MEMBER_PRICE`, `GROUP_SMALL`, `GROUP_LARGE`) and rebuild, or find-and-replace.

## How the leads were found

Public web search and local "best coworking in ..." guides were used to find names. Then each
organization's **own website** was opened to check that it's active, serves freelancers or small
businesses, and publishes an email on its own site (the page is in `leads_research.csv` →
`email_source_url`). No scraping tools, no bought lists, no guessed emails, and no personal addresses
from anywhere else. 4 translator-association chapters publish their email only in the American
Translators Association's chapter directory (atanet.org), which is the official parent body; those
are marked in `flags`. Chains (WeWork, Regus, Industrious, Spaces, Expansive) were skipped, and so were
spaces that have closed, sites that now redirect to unrelated pages, and contact-form-only sites.

**Mix:** coworking spaces 45, translator and interpreter associations 20, writers' and journalists' groups 3, editors' groups 2, freelancer and founder communities 2, medical writers' association 1, creative guild 1, independent consultants' association 1.

Many coworking spaces publish only a contact form, so they're under-represented. Translator and
interpreter associations (ATA chapters and affiliates) were the easiest to verify and are a strong fit:
most members are independent contractors who pay quarterly estimated tax.

## Before you send anything (one-time setup)

1. **Put the bundle on sale** and paste the real link in place of `{Bundle link}` everywhere.
   Listing: `launch/1099-money/products/bundle/LISTING.md`.
2. **Decide the member and group prices** (see `GROUP_LICENSE.md`) and set up the member code.
3. **Fill in** `{Your Name}` and the footer postal address (a PO box or virtual mailbox is fine). The
   footer with an address and opt-out line is required by CAN-SPAM.
4. **Have the calendar ready to attach**, and once the site is live, put the free page's URL in place of
   `{Calendar link}` in the blurb (`FOLLOW_UP_SEQUENCE.md`, Branch A).
5. Send from a normal inbox on your own domain if you can. If the domain is new, start at 4 a day.

## Daily routine (about 30 minutes)

1. Open `TRACKER.csv` and filter `email1_planned` = today.
2. For each lead, open its pitch file, spend 60 seconds on their site to check the detail is still true,
   tweak the opener if needed, and send Email 1.
3. Send any Follow-up 1s and 2s due today, **only to people who haven't replied**.
4. Write the sent date in the tracker. Anyone who says no or stop: `do_not_contact`, never again.
5. Reply to yeses the same day using `FOLLOW_UP_SEQUENCE.md` (Branch A).

## Things to know about specific leads

- **Role inboxes:** 8 leads publish only a `president@`, `board@`, `admin@`, `help@` or
  `support@` address. Their Email 1 already asks them to pass it to whoever runs the newsletter.
  Associations are volunteer-run, so all association emails include that line.
- **Free-mail addresses:** 2 groups publish a Gmail address on their own site (or in the ATA
  directory) as their official contact. That's fine to use.
- **Named people:** Switchboard (Emily), Ward4 (Kristen) and FatPipe (Laura) publish a named staff
  address, so the greeting uses the first name. COVE and the VIP Center also show a name, but their
  main address is a shared inbox, so the greeting uses the team.
- **Possibly stale:** 6 leads have a site with no 2026 activity (footer 2024 or 2025, or
  undated posts). They're at the end of the send order. Check the site first, and skip any that look
  closed.
- **Decoded addresses:** The Hivery and IECA hide their email behind spam protection; the address in
  the list is what their link decodes to.
- **Big national groups** (Freelancers Union, EFA, NWU, ASJA, AMWA, Graphic Artists Guild, SEJ, NAJIT,
  IECA) get far more pitches and may have a formal partner process. If they reply, ask whether they
  have a member-benefits program, and quote a bigger-group price (see `GROUP_LICENSE.md`).

## Rules for every message

- The calendar and bundle are educational. Never say they make anyone compliant, guarantee no penalty,
  or replace an accountant (Branch C).
- Every tax figure in these emails is a 2026 federal rule as of November 2026: the Jan 15, 2027 payment,
  the 100% / 110% safe harbor, the $2,000 1099-NEC threshold, and the $20,000 / 200-payment 1099-K
  threshold. Recheck irs.gov if you send any of these after January.
- No fake urgency, no invented testimonials, and no "other spaces already offer it" until one actually does.
- No affiliate links anywhere in this kit.

## What to expect

Honest numbers for hand-written cold email to small organizations: a 5 to 10% reply rate is a good
result, and a free, timely calendar should get more yeses than a sales pitch would. From 75 leads, a
realistic target is 5 to 10 replies, 4 to 8 groups sharing the calendar (each one puts it in front of
dozens or hundreds of freelancers, some of whom join the email list), and 0 to 2 member codes or group
licenses in the first month. The real value is learning which kind of group says yes, so that the next
75 can all come from it.
