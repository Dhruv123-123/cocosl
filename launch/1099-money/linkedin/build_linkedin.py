"""Builds the 30-day LinkedIn plan for freelancers and solo consultants: posts.json and POSTS.md.

    python3 launch/1099-money/linkedin/build_linkedin.py

Posted by hand from Dhruv's personal profile, one a day, Nov 16 to Dec 15, 2026. No links in the post
body (LinkedIn shows link posts to fewer people): where a post points to a free page, the link goes in
`first_comment`, posted right after. Every figure uses 2026 federal numbers from apps/freelance-tax/lib.
"""
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = date(2026, 11, 16)
SITE = "1099money.netlify.app"
RATE = f"Free rate calculator (no sign-up, numbers stay in your browser): {SITE}/rate-calculator/"
QUARTERLY = f"Free quarterly tax calculator: {SITE}"
NOT_ADVICE = "Educational, not tax advice. 2026 federal figures, single filer, no state tax."
TAGS = {
    "rates": "#freelancing #consulting #pricing",
    "clients": "#freelancing #consulting #clientwork",
    "contracts": "#freelancing #consulting #contracts",
    "invoicing": "#freelancing #invoicing #smallbusiness",
    "tax": "#freelancing #selfemployed #taxes",
    "pipeline": "#freelancing #consulting #businessdevelopment",
}

# (format, topic, body, first_comment or None). The first line is the hook LinkedIn shows before "see more".
POSTS = [
("numbers", "rates", """A $55,000 salary is about $26 an hour. The same take-home as a freelancer needs about $75.

Here's where the gap comes from:

Take-home you want: $55,000
+ health insurance an employer used to cover: $6,000
+ retirement savings you now fund alone: $5,000
= $66,000 you need after tax

To keep $66,000, you need about $84,000 of profit. Federal tax on that is about $17,600, because you now pay both halves of Social Security and Medicare.

+ business costs (software, equipment, insurance): $6,000
= $90,000 of revenue

Now divide by the hours clients actually pay for. 25 billable hours a week for 48 weeks is 1,200 hours, not 2,080.

$90,000 / 1,200 = $75 an hour.

That's a floor, not a ceiling. If your market pays more, charge more.

""" + NOT_ADVICE, RATE),

("myth-fact", "rates", """Myth: you'll bill 40 hours a week as a freelancer.

Fact: a big share of your week goes to work nobody pays for. Finding clients, proposals, invoicing, email, bookkeeping, learning.

That one assumption changes your rate more than almost anything else. Same target ($55,000 take-home, $6,000 health, $5,000 retirement, $6,000 costs), different billable hours:

35 hours a week: $54 an hour
25 hours a week: $75 an hour
20 hours a week: $94 an hour

If you priced yourself assuming a full week and you're billing 22 hours, you're not underperforming. Your rate is.

20 to 30 billable hours a week over 46 to 48 weeks is a common planning range. If you're new, plan on the low end.

""" + NOT_ADVICE, RATE),

("checklist", "clients", """7 questions to ask on a discovery call before you quote a price:

1. What does a good result look like six months from now?
2. What's the deadline, and what happens if it slips?
3. Who approves the work, and who signs off on payment?
4. What have you already tried?
5. Is there a budget range for this?
6. Who else on your side will be involved, and how much of their time can you count on?
7. How do you usually pay vendors? (Net 30? A purchase order? A portal?)

The last one gets skipped most. It's also the one that decides whether you get paid in 2 weeks or 10.

A quote built on these answers is easier to defend, because it's tied to what the client told you they need.

Which question would you add?""", None),

("script", "rates", """How to raise your rate with an existing client, word for word:

"Hi [name], a quick heads-up. Starting [date, 30 to 60 days out], my rate for new work will be $[new rate]. Anything already scheduled before then stays at the current rate. Happy to talk it through if useful."

Why it works:
- It gives notice, so nobody is surprised mid-project.
- It protects work already agreed, which feels fair.
- It doesn't apologize or list your costs. You're informing, not asking.
- It's short. A long explanation reads like an invitation to negotiate.

Most clients reply with "noted" or nothing at all. If one pushes back, you can offer a smaller scope at the new rate rather than the old rate for the same scope.

Save this for January.""", None),

("numbers", "rates", """Raise your rate 13% and you can lose 10% of your billable hours and still earn more.

Today: 1,200 hours at $75 = $90,000
After: 1,080 hours at $85 = $91,800

That's $1,800 more revenue and 120 hours back. Three working weeks.

The fear with a rate increase is losing clients. But you don't need every client to stay. You need the math to work, and it usually works with a few hours lost.

Run your own numbers before you decide:
1. Your current rate and billable hours this year
2. Your new rate
3. How many hours you could lose and still match this year's revenue

At $75 to $85, the break-even is about 1,059 hours. You can lose about 1 hour in 8 before you're worse off.""", None),

("question", "contracts", """Freelancers and consultants: what's one line you add to every contract now that you didn't add when you started?

(Payment terms, revisions, a kill fee, who owns what, something else?)""", None),

("compare", "rates", """Hourly vs project pricing, one line each:

Hourly: the client carries the risk that the work takes longer. You get paid for every hour, but you're capped by hours, and getting faster earns you less.

Project: you carry the risk. Estimate well and get faster over time, and your effective hourly rate goes up.

The middle ground many consultants use: price the project, but build it from your hourly floor.

Estimated hours x hourly floor x 1.2 (buffer for revisions and surprises) = project price.

Then the hourly rate stays private, and the client compares outcomes, not hours.""", None),

("mistake", "invoicing", """3 invoice mistakes that slow down payment:

1. "Net 30" instead of a date.
"Due December 31, 2026" is harder to lose track of than a term someone has to count from.

2. Sending it to the person you work with, not the person who pays.
Ask on day one: who processes invoices, and do you need a PO number on them?

3. Waiting until the end of the month.
Invoice the day the work is delivered, while it's fresh. Every day you wait is a day added to the payment clock.

Bonus: put the payment link and your payment terms on the invoice itself, not just in the contract.

What's the longest you've waited on an invoice?""", None),

("numbers", "rates", """A 20% discount costs you more than 20%.

$10,000 project, 20% off: $8,000.

To get back to $10,000 of revenue, you need another $2,000 of work. That's 25% more work on top of the $8,000 you already sold.

At 30% off, you need 43% more work to break even. At 50% off, double.

If a client needs a lower price, change the scope, not the rate:
- fewer deliverables
- fewer revision rounds
- a longer timeline
- they do part of the work

"I can do it for $8,000 if we drop [X]" keeps your rate intact for the next project, and the next client.""", None),

("script", "invoicing", """Three follow-ups for a late invoice, word for word:

1 day overdue:
"Hi [name], a quick reminder that invoice #[number] for $[amount] was due yesterday. Here's the link again: [link]. Let me know if anything's needed on your side."

7 days overdue:
"Hi [name], following up on invoice #[number], now a week past due. Could you let me know the date it'll be paid? If it's stuck with someone else, I'm happy to contact them directly."

21 days overdue:
"Hi [name], invoice #[number] is three weeks overdue. As in our agreement, a late fee of [X] applies from [date], and I'll need to pause new work until it's settled. I'd rather sort it out quickly; what's the best way forward?"

Each one is polite, specific and asks for one thing. The third only works if your contract says it, so put late fees and the right to pause in writing before you start.""", None),

("question", "clients", """Thanksgiving question for freelancers and consultants:

What's one thing a client did this year that made the work easier?

(Paying on time counts. So does a clear brief.)""", None),

("checklist", "rates", """5 numbers every solo consultant should know about their business:

1. Effective hourly rate: revenue divided by all hours worked, billable or not. Usually much lower than your quoted rate.

2. Utilization: billable hours divided by total hours worked. Tells you how much of your week clients pay for.

3. Revenue by client: what share your biggest client is. If one client is most of your income, losing them is a crisis rather than a slow month.

4. Days to get paid: the average time from invoice to money in the bank.

5. Tax set-aside: the share of each payment you move to savings for tax. At $60,000 of profit, federal tax works out to about 20%.

You don't need software for this. A spreadsheet updated once a month is enough.

Which one have you never calculated?

""" + NOT_ADVICE, None),

("myth-fact", "tax", """Myth: freelancers only deal with taxes in April.

Fact: if you expect to owe $1,000 or more, the IRS expects estimated payments four times a year.

The next one is January 15, 2027, for income earned September through December 2026.

""" + NOT_ADVICE, QUARTERLY),

("question", "invoicing", """How many months of expenses do you keep as a buffer as a freelancer?

Curious where people land: 1, 3, 6, more?""", None),

("numbers", "clients", """What happens when one client is 60% of your revenue:

Revenue: $90,000
Biggest client: $54,000
Everyone else: $36,000

If that client leaves, your revenue drops to $36,000 overnight. At the $75 floor from earlier this month, that covers about 40% of what you need.

Now the same $90,000 spread out:
Biggest client: $27,000 (30%)
Next three: $63,000

Lose the biggest and you're at $63,000. A hard quarter, not a crisis.

A rule of thumb many consultants use: try to keep any one client under about a third of revenue.

You can't always choose. A big anchor client is often how a practice starts. But knowing the number tells you how much time to put into finding the next one.""", None),

("compare", "invoicing", """Three ways to get paid, compared:

Net 30 after delivery
You do all the work, then wait 30 days or more. You're financing the client.

50% deposit, 50% on delivery
Common for projects. You start with cash in hand, and the client has a reason to keep the project moving.

Monthly retainer, paid in advance
Best for ongoing work. You're paid before the month starts, and your income is predictable.

For a new client, a deposit also answers a question early: if they won't pay 50% upfront, they may not pay 100% later either.

Which do you use?""", None),

("mistake", "tax", """4 tax mistakes new freelancers make in year one:

1. Not setting money aside. On $60,000 of profit, federal tax is about $12,000. If none of it was saved, April is a problem.

2. Forgetting self-employment tax. As an employee, your employer paid half of Social Security and Medicare. Now you pay both: 15.3% on 92.35% of profit. On $60,000 that's about $8,500, before income tax.

3. Skipping estimated payments. If you'll owe $1,000 or more, the IRS expects payments in April, June, September and January. Missing them means an underpayment penalty.

4. One bank account for everything. A separate account for the business, and one for tax savings, makes all of the above easier.

None of these need an accountant to fix. They need a percentage and a calendar reminder.

""" + NOT_ADVICE, QUARTERLY),

("script", "contracts", """How to say no to scope creep without sounding difficult:

"Happy to add that. It's outside what we agreed, so I'll send over a quick change estimate: about [X] hours, $[amount], and it moves delivery by [Y] days. Want me to go ahead?"

What this does:
- Starts with yes, so you're not the obstacle.
- Names it as new work, calmly.
- Puts a price and a date on it, so the client can decide.
- Ends with a question, so the next step is theirs.

Most of the time, the client either approves it or decides they don't need it after all. Both are fine. What's not fine is absorbing it silently, because the next request will be bigger.""", None),

("checklist", "contracts", """What a one-page freelance agreement should cover:

1. Who: both parties' names and business names.
2. What: deliverables, in plain words. What's not included.
3. Revisions: how many rounds, and the rate for extra ones.
4. Timeline: dates, and what you need from the client to hit them.
5. Price and payment: amounts, due dates (as dates), deposit.
6. Late payment: a late fee, and the right to pause work.
7. Ownership: when rights transfer (often on full payment) and what you keep, like your own templates and tools.
8. Ending early: notice period, and payment for work done so far (a kill fee).

One page is fine. What matters is that it exists before the work starts.

Not legal advice. For a big engagement, have a lawyer look it over.""", None),

("myth-fact", "tax", """Myth: you can deduct your whole phone bill as a freelancer.

Fact: you can deduct the business-use share. If about 40% of your phone use is for work, 40% of the bill is the business expense.

Same idea for internet and a car used for both. Keep a note of how you worked out the percentage.

""" + NOT_ADVICE, None),

("question", "rates", """Freelancers and consultants: how do you price most of your work?

Hourly, day rate, by project, or a monthly retainer?

And has that changed since you started?""", None),

("numbers", "rates", """Why a day rate isn't your hourly rate x 8:

Hourly floor: $75
Billable hours in a real working day: about 6
Day rate: $75 x 6 = $450

A day of client work still has email, calls, context switching and admin around it. Pricing a day as 8 billable hours means you're giving away 2 every time.

If $450 a day feels like a lot, check it against the year:
$450 x 4 days a week x 48 weeks = $86,400

Close to the $90,000 that $75 an hour was built to reach. The numbers line up because they come from the same target.

""" + NOT_ADVICE, RATE),

("compare", "rates", """Hourly, project or retainer: who carries the risk?

Hourly
Risk on the client: if it takes longer, they pay more.
Good for: unclear scope, ongoing support.

Fixed project
Risk on you: if it takes longer, you earn less per hour.
Good for: well-defined work you've done before.

Retainer
Shared: the client pays for access, you commit capacity.
Good for: ongoing advice or a set number of hours a month.

A useful test: if you can't describe the deliverable in two sentences, don't fix the price yet. Do a short paid discovery first, then quote the project.""", None),

("script", "rates", """When a prospect asks "What's your rate?" on the first call:

"It depends on the scope. Projects like this usually land between $[A] and $[B]. If you can share [the deadline, the number of X, who's involved], I'll send a fixed price by [day]."

Why a range:
- It answers the question, so you don't sound evasive.
- It tells them early if the budget is way off, which saves both of you time.
- It keeps the final number tied to the scope, not to a rate they'll compare with someone else's.

Make sure the low end of the range is something you'd actually take.""", None),

("mistake", "clients", """3 mistakes when you land your first big client:

1. No deposit. A big project with nothing paid upfront means weeks of work before any cash. Ask for one, even on good terms.

2. No end date. "Ongoing" without a review date can turn into months at a rate you set when you knew less. Put a check-in at 90 days.

3. Stopping everything else. It's tempting to go all-in. But if this client is now most of your income, keep a little time each week for finding the next one.

A big client is great news. These three keep it that way.""", None),

("checklist", "pipeline", """A 30-minute weekly routine to keep work coming in:

1. Comment on 5 posts from people in your niche. Add a point, not "great post".
2. Follow up with 2 past clients. "How did [project] turn out?" is enough.
3. Write down one result from recent work. That's next month's case study.
4. Ask one happy client if they know someone who needs the same help.
5. Note every new lead somewhere you'll see it again.

Thirty minutes a week, every week, beats a panicked month of outreach when a project ends.

What would you add?""", None),

("myth-fact", "tax", """Myth: if a client sends you a 1099, they've already handled the tax.

Fact: nothing is withheld on 1099 income. The form just reports what they paid you. The tax is yours to pay, through estimated payments during the year and your return in April.

For 2026, clients send a 1099-NEC if they paid you $2,000 or more. Below that, the income is still taxable.

""" + NOT_ADVICE, None),

("question", "rates", """What did you charge for your first freelance project, and what do you charge now?

No judgment on either number. It helps people starting out to see the range.""", None),

("numbers", "tax", """How much of each payment to set aside for federal tax, by profit:

$40,000 of profit: about 19%
$60,000: about 20%
$80,000: about 21%
$100,000: about 22%

Why it's that high even at modest income: self-employment tax (15.3% on 92.35% of profit) applies from the first dollar. Income tax comes on top.

Add your state's rate on top, and round up. Having too much saved in April is a much better problem than too little.

The simple version: every time a client pays, move the percentage to a separate account the same day.

""" + NOT_ADVICE, QUARTERLY),

("checklist", "rates", """Before you set your 2027 rates, pull these 6 numbers:

1. Take-home pay you want for the year
2. Health insurance cost, if you pay your own
3. What you'll put into retirement
4. Business costs: software, equipment, insurance, fees
5. Weeks you'll actually work (52 minus holidays, vacation and sick days)
6. Billable hours a week, honestly

Then work backwards: add 1 to 3, work out the tax on the profit you'd need, add 4, and divide by 5 x 6.

That's your hourly floor. Compare it with what people in your niche charge, and set your rate at or above both.

A month from now is a good time to tell clients. Start with the math this week.

""" + NOT_ADVICE, RATE),
]


def build():
    posts = []
    for i, (fmt, topic, body, comment) in enumerate(POSTS):
        d = START + timedelta(days=i)
        text = body.strip() + "\n\n" + TAGS[topic]
        posts.append({
            "n": i + 1, "date": d.isoformat(), "weekday": d.strftime("%a"), "format": fmt, "topic": topic,
            "hook": body.strip().split("\n")[0], "text": text, "first_comment": comment, "chars": len(text),
        })
    (HERE / "posts.json").write_text(json.dumps(posts, indent=1, ensure_ascii=False) + "\n")
    out = ["# 30 days of LinkedIn posts for freelancers and solo consultants",
           "",
           "Generated by `build_linkedin.py`. Edit the script, not this file. Post one a day, by hand, from Dhruv's "
           "personal profile, Nov 16 to Dec 15, 2026. Then reshare to the 1099 Money page (see README.md).",
           "",
           "Where a post has a **first comment**, post it as a comment straight after the post. It holds the link, "
           "so the post itself has none.",
           ""]
    for p in posts:
        out += [f"## {p['n']}. {p['weekday']} {p['date']} · {p['format']} · {p['topic']}", "", "```", p["text"], "```", ""]
        if p["first_comment"]:
            out += [f"**First comment:** {p['first_comment']}", ""]
    (HERE / "POSTS.md").write_text("\n".join(out))
    print(f"wrote {len(posts)} posts")


if __name__ == "__main__":
    build()
