# Follow-up sequence: from first email to a $99 sale

Every message here is sent **by you, by hand, from your own inbox**, in the same thread as the first
email. Each lead's pitch file in `pitches/` already has a filled-in Email 1, Follow-up 1 and
Follow-up 2. This file covers when to send them and what to send when someone replies.

The cold part is three emails, maximum. Anyone who says no or asks you to stop gets `do_not_contact`
in `TRACKER.csv` and never hears from you again. Every cold email keeps the footer (your name, a postal
address and the opt-out line). CAN-SPAM requires it.

---

## The map

```
Day 0   Email 1 (offer the free poster)          ── pitches/<lead>.md, "Email 1"
Day 4   Follow-up 1 (short bump)                 ── same thread, "Follow-up 1"
Day 9   Follow-up 2 (3 scam tells + $99 pack)    ── same thread, "Follow-up 2"
        No reply after Follow-up 2 → status "no_reply", stop.

Any reply → jump to the matching branch below and stop the cold sequence.
```

Days are working days. Weekends, Thanksgiving (Thu 26 and Fri 27 Nov) and Christmas Eve and Day are
skipped, and the dates in `TRACKER.csv` already account for that.

**Pacing:** 8 new first emails a weekday, from Tue 10 Nov to Mon 23 Nov. The last follow-ups go out
Tue 8 Dec. On a busy day that's 8 first emails, 8 follow-up 1s and 8 follow-up 2s, so about 24
hand-sent messages, on top of the ad-studio kit if you're running both.

**Best send times:** Tuesday to Thursday, 9 to 11am their time. Montana and southern Idaho (Boise, Twin
Falls, Pocatello, Idaho Falls) are on Mountain time; Spokane, Coeur d'Alene and Bend are on Pacific. Dental and vet front desks are busiest first thing; mid-morning is better for them.

---

## Branch A: "Yes, send the poster" (the goal)

**A1. Same day: send it**

Attach `Poster-Verify-Before-You-Pay.pdf` (from the training pack's `dist/` folder, or the project's
`products/team-training/`).

```
Here you go, {first name}! The poster is attached. It prints fine on plain Letter paper.

The one-line version for the team: if a message asks you to pay, change bank details, buy gift cards
or read out a code, stop and call back on a number you already have.

If it's useful, I also made a full 45-minute session you can run yourself (slides with speaker notes,
three practice scenarios, a quiz, certificates and a one-page verification policy). It's $99 for the
whole office: {Pack link}

No pressure at all. Hope the poster helps.

{Your Name}
```

**A2. One week later, only if they haven't replied to A1**

```
Hi {first name}, just checking the poster came through OK. If anyone on your team had questions about
it, I'm happy to answer them.

{Your Name}
```

That's the last message unless they write back.

---

## Branch B: "How much is the training?" / "Tell me more"

```
Thanks for asking, {first name}!

It's $99, one-time, for your whole office (any number of people). You get:

- 25 editable slides with speaker notes (about 45 minutes)
- 3 practice scenarios with model answers
- a 12-question quiz with answer key
- completion certificates and an attendance log
- a one-page payment and data verification policy you can adopt as-is
- the "Verify before you pay" poster

Nobody needs a security background to run it; the facilitator guide walks through it. Here's the
link: {Pack link}

{Your Name}
```

If the launch code is still running (first 14 days after the pack goes live only), add: "If you get it
this week, the code TEAMLAUNCH takes $30 off." Don't mention it after it ends.

---

## Branch C: "Does this make us compliant?" / "Our insurer asked about training"

Be straight with them. Never say the pack makes anyone compliant with a law, regulation or insurance
requirement.

```
Good question. Honestly, I can't tell you it meets any particular requirement, since that depends on
your insurer or regulator. What I can say is that it gives you a dated attendance log and certificates,
which help you keep a record that training happened. I'd check with your insurer or advisor on exactly
what they need.

{Your Name}
```

---

## Branch D: "We already do training" / "Our IT company handles this"

```
That's great to hear, and you're ahead of most offices. Feel free to keep the poster either way.
Thanks for letting me know!

{Your Name}
```

Status `has_training`. Don't follow up.

---

## Branch E: "Not now" / "Maybe after tax season"

```
Totally understand. I'll leave it with you. The poster offer stands whenever it's useful.

{Your Name}
```

Status `later`. You may email once more after the date they gave you, and then stop.

---

## Branch F: "No thanks" / "Stop" / "Unsubscribe" / no answer

Status `do_not_contact`. Reply only if they asked a question. Never email again from any address.

---

## Branch G: "Is this a scam?"

It's a fair question to get from a scam-awareness email, and a good sign their instincts work.

```
Ha, that's exactly the right instinct! Nothing to click and nothing to pay. I just make plain-English
scam-awareness material for small offices. If you'd rather check me out first, here's the site:
{Brand site URL}. And if you don't want the poster, no problem at all.

{Your Name}
```

---

## After a sale

- Thank them the same day. The store's delivery message already points to the facilitator guide.
- Two weeks later: "How did the session go? Anything I should add for next time?" Their answer is
  your best product feedback.
- If they say something good about it, ask permission before quoting them anywhere, and quote them
  exactly. Never write a testimonial for someone.
