# Follow-up sequence: from first email to a member perk

Every message here is sent **by you, by hand, from your own inbox**, in the same thread as the first
email. Each lead's pitch file in `pitches/` already has a filled-in Email 1, Follow-up 1 and
Follow-up 2. This file covers when to send them and what to send when someone replies.

The cold part is three emails, maximum. Anyone who says no or asks you to stop gets `do_not_contact`
in `TRACKER.csv` and never hears from you again. Every cold email keeps the footer (your name, a postal
address and the opt-out line). CAN-SPAM requires it.

---

## The map

```
Day 0   Email 1 (offer the free 2027 tax calendar)       ── pitches/<lead>.md, "Email 1"
Day 4   Follow-up 1 (short bump)                         ── same thread, "Follow-up 1"
Day 9   Follow-up 2 (3 tax habits + member code /        ── same thread, "Follow-up 2"
        group license for the $49 bundle)
        No reply after Follow-up 2 → status "no_reply", stop.

Any reply → jump to the matching branch below and stop the cold sequence.
```

Days are working days. Weekends, Thanksgiving (Thu 26 and Fri 27 Nov) and Christmas Eve and Day are
skipped, and the dates in `TRACKER.csv` already account for that.

**Pacing:** 8 new first emails a weekday, from Wed 11 Nov to Tue 24 Nov. The last follow-ups go out
Wed 9 Dec, well before the Jan 15 payment the whole pitch is built around. On a busy day that's 8 first
emails, 8 follow-up 1s and 8 follow-up 2s. If you're also running the Scam Decoded kit (8 a day from
Tue 10 Nov), that's up to about 48 hand-sent emails a day in the week of 16 Nov. Halve both kits'
pace if that's too much: the dates matter less than not rushing.

**Best send times:** Tuesday to Thursday, 9 to 11am their time. Associations are run by volunteers, so
replies can take a week or two. That's normal; don't chase beyond Follow-up 2.

---

## Branch A: "Yes, send the calendar" (the goal)

**A1. Same day: send it**

Attach `freelancer-tax-calendar-2027.pdf` (`apps/freelance-tax/downloads/`), or link the free page on
the site once it's live (`{Calendar link}`, the `/free/` page).

```
Hi {name},

Here you go: the 2027 Freelancer Tax Calendar is attached. Feel free to forward it, print it for the
space, or post it wherever members will see it.

If it helps, here's a short blurb you can paste into a newsletter, Slack or member email as-is:

  ---
  Free for members: the 2027 Freelancer Tax Calendar
  Every federal tax date a US freelancer needs next year, what to do on each one, and a 15-minute
  routine to run before each quarterly payment. The next one is Fri Jan 15, 2027 (the 4th payment for
  your 2026 income). Printable PDF, no sign-up: {Calendar link}
  Educational, not tax advice.
  ---

Thanks for sharing it. If members have questions about the calendar, they can reply to me directly.

{Your Name}

--
{Your Name} · 1099 Money
{Street address or PO box / registered mailbox}, {City, Postcode}, {Country}
```

Write today's date in `calendar_sent` in the tracker. **Don't mention the bundle in this email.**

**A2. About 3 weeks later, only if they shared it** (`blurb_shared` = yes)

```
Hi {name},

Thanks again for passing the calendar on to members. With the Jan 15 payment coming up, I wanted to
mention one thing, and then I'll leave you alone.

Some groups give members a perk on the paid version, the Freelancer Money Bundle ($49: quarterly tax
tracker, rate calculator, proposal/contract/invoice templates and 14 client email scripts). Two ways
that could work for {group}:

  - a member code, so members get it for $39 (you'd just share the code), or
  - a group license, so you give it to members for free: $199 for up to 25 people, $499 for up to 100.

Happy to send a sample page first if you'd like to see it. Either way, thanks for sharing the calendar.

{Your Name}
```

---

## Branch B: "Tell me more about the member perk / group license"

Send `GROUP_LICENSE.md`'s summary (paste it, don't attach it), plus the bundle link, and offer a
15-minute call. Then:

- **Member code:** create a discount code in the store (`MEMBERS-{GROUP}`, $10 off, no expiry or a
  date they pick) and send it with the blurb below. Track sales of that code in the store.
- **Group license:** send a payment link for the tier (Stripe or Gumroad), and once it's paid, send a
  private download link they can share with members (a separate Gumroad product, or a Netlify page
  that isn't linked anywhere). Put the license terms from `GROUP_LICENSE.md` in the download's README.

Member-code blurb for their newsletter:

```
Member perk: the Freelancer Money Bundle from 1099 Money, $39 with code {CODE} (usually $49).
A quarterly tax tracker, a tax-aware rate calculator, proposal, contract and invoice templates, and
14 client email scripts. {Bundle link}
Educational tools, not tax or legal advice.
```

---

## Branch C: "Is this tax advice? Can members rely on it?"

```
Good question. No: it's educational material, not tax, legal or financial advice, and it says so on
every page. The dates come from IRS rules as of November 2026 and the figures are 2026 federal ones.
For anything specific to their situation, members should check with a CPA or enrolled agent. The
calendar's job is just to make sure nobody misses a date.
```

Never claim the calendar or bundle makes anyone compliant, avoids penalties for sure, or replaces an
accountant. "Generally avoids the underpayment penalty" is as far as the wording goes, and only about
the safe harbor rule.

---

## Branch D: "Are you selling something / is this an affiliate thing?"

```
Fair question. The calendar is free and stays free. I also sell a $49 bundle of spreadsheets and
templates for freelancers, which I mentioned in my last note, but there's no obligation and the
calendar is yours to share either way. There are no affiliate links in anything I've sent you.
```

(True as written: the calendar and these emails have no affiliate links. Keep it that way.)

---

## Branch E: "Not for us" / "No thanks" / "Remove me"

```
Understood, thanks for letting me know. I won't email again.
```

Set `status` = `do_not_contact`. Never email again, including from another kit.

---

## Branch F: "We don't share outside offers with members" / "We have a vendor policy"

```
Totally understand, thanks for explaining. If it's ever useful, the calendar is free to share
without any mention of me. Good luck with the new year.
```

Status `closed_policy`. Don't follow up.

---

## Branch G: "Send it to {other person}"

Thank them, then send Email 1 to the new person with "{name} suggested I get in touch" as the first
line. Start a new row in the tracker for that person. Only use an address they gave you in the reply.

---

## Branch H: auto-replies and out-of-office

Ignore them. If it says the inbox isn't monitored, mark `status` = `dead_inbox` and stop. If it gives a
return date, carry on with the planned follow-ups after that date.

---

## Status values for TRACKER.csv

`not sent` · `sent` · `replied` · `calendar_sent` · `perk_discussing` · `code_live` · `license_sold` ·
`no_reply` · `closed_policy` · `do_not_contact` · `dead_inbox`
