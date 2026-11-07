"""Builds the 30-day Threads/X plan for freelancers: posts.json and POSTS.md.

    python3 launch/1099-money/threads-x/build_threads_x.py

One post (or short thread) a day, Nov 16 to Dec 15, 2026, posted by hand on both X and Threads from the
1099 Money accounts. Every part fits X's 280 characters, so the same text works on Threads (500). No links in
the posts: where one helps, it goes in `link_reply`, posted as the first reply. 2026 federal figures from
apps/freelance-tax/lib.
"""
import json
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
START = date(2026, 11, 16)
SITE = "1099money.netlify.app"
RATE = f"Free rate calculator, no sign-up: {SITE}/rate-calculator/"
CALC = f"Free quarterly tax calculator: {SITE}"
Q4 = f"Free Jan 15 calculator: {SITE}/q4/"
INVOICE = f"Free invoice template (fill in, save as PDF): {SITE}/invoice-template/"
NA = "Not tax advice. 2026 federal figures."

# (format, topic, [posts], link_reply or None). A list of more than one post is a thread.
POSTS = [
("numbers", "rates", ["$55K salary ≈ $26/hour.\n\nSame take-home as a freelancer ≈ $75/hour.\n\nNot greed. Health insurance, retirement, both halves of payroll tax, business costs, and ~1,200 billable hours instead of 2,080.\n\n" + NA], RATE),
("hot-take", "rates", ["Your freelance rate isn't too high.\n\nYou're comparing it to a salary that came with health insurance, a 401(k) match, paid vacation and someone else paying half your Social Security."], None),
("thread", "tax", [
  "How to work out what to set aside for taxes from every client payment, in 4 steps 🧵",
  "1. Estimate this year's profit: what clients pay you minus business costs.",
  "2. Look up the federal tax on that profit. At $60K of profit (single, no other income) it's about $12,000. That's ~20%.",
  "3. Add your state's rate. Round up.",
  "4. Every time a client pays, move that % to a separate account the same day. Pay the IRS from it each quarter.\n\n" + NA], CALC),
("question", "rates", ["Freelancers: how many hours a week do you actually bill?\n\nNot work. Bill."], None),
("myth-fact", "tax", ["Myth: no 1099, no tax.\n\nFact: all freelance income is taxable, with or without a form. The 1099 just tells the IRS what the client paid you."], None),
("one-liner", "invoicing", ["Write the due date as a date.\n\n\"Due June 30\" gets paid. \"Net 30\" gets counted wrong."], INVOICE),
("checklist", "invoicing", ["An invoice that gets paid has:\n\n- your name + email\n- client name\n- invoice number\n- invoice date\n- due date (a real date)\n- itemized work\n- total\n- how to pay you\n\nMissing one = a reply asking about it = a week lost."], INVOICE),
("numbers", "rates", ["20% discount math:\n\n$10,000 → $8,000\nTo get back to $10,000 you need $2,000 more work.\n$2,000 is 25% of $8,000.\n\n20% off = 25% more work.\n30% off = 43% more.\n\nCut scope, not your rate."], None),
("thread", "invoicing", [
  "3 messages for a late invoice, copy-paste ready 🧵",
  "Day 1 overdue:\n\"Hi [name], quick reminder that invoice #[x] for $[amount] was due yesterday. Here's the link again: [link]. Let me know if anything's needed on your side.\"",
  "Day 7:\n\"Hi [name], following up on invoice #[x], now a week overdue. Could you tell me the date it'll be paid? Happy to contact whoever processes it.\"",
  "Day 21:\n\"Hi [name], invoice #[x] is 3 weeks overdue. Per our agreement, a late fee of [x] applies from [date] and new work is paused until it's settled. What's the best way to sort this quickly?\"\n\nThe third only works if your contract says it."], None),
("hot-take", "clients", ["A client who won't pay a 50% deposit is telling you something before the project starts.\n\nListen the first time."], None),
("question", "clients", ["Happy Thanksgiving to everyone who works for themselves.\n\nWhat's one client habit you're grateful for this year?"], None),
("myth-fact", "tax", ["Myth: spending before Dec 31 is smart because it's a write-off.\n\nFact: a $1,000 purchase saves roughly $230 of federal tax at $60K profit. You're still out $770.\n\nBuy what the business needs. Not what the deduction needs.\n\n" + NA], None),
("one-liner", "tax", ["The quarterly tax \"quarters\" are 3, 2, 3 and 4 months long.\n\nThe Jan 15 payment covers Sep–Dec. Check your savings against your fall income now."], Q4),
("question", "tax", ["Freelancers: what % of each payment do you set aside for taxes?\n\n15? 20? 25? 30+?"], None),
("numbers", "rates", ["Raise your rate from $75 to $85 (+13%).\n\nLose 10% of your hours.\n\nBefore: 1,200 h × $75 = $90,000\nAfter: 1,080 h × $85 = $91,800\n\nMore money. 120 hours back."], None),
("checklist", "contracts", ["One-page freelance contract:\n\n- who\n- deliverables + what's NOT included\n- revision rounds\n- timeline\n- price, deposit, due dates\n- late fee + right to pause work\n- when ownership transfers\n- kill fee\n\nNot legal advice. Better than nothing."], None),
("thread", "rates", [
  "How to turn your hourly rate into a day rate (without giving away 2 hours a day) 🧵",
  "A day of client work isn't 8 billable hours. Email, calls, admin and switching tasks eat the edges. ~6 is realistic.",
  "$75/hour × 6 = $450/day.\n\nCheck: $450 × 4 days × 48 weeks ≈ $86,400. Same target as the hourly rate. That's the point.",
  "Quote the day rate. Keep the hourly floor to yourself as a check."], RATE),
("hot-take", "tax", ["The most expensive freelance tax mistake isn't a missed deduction.\n\nIt's spending the tax money."], None),
("myth-fact", "tax", ["Myth: an LLC lowers your taxes.\n\nFact: a single-member LLC is taxed exactly like a sole proprietor by default. Same Schedule C, same 15.3% self-employment tax.\n\nIt can help with liability. Not with tax."], None),
("one-liner", "pipeline", ["The best time to look for your next client is while you're too busy to."], None),
("question", "invoicing", ["How do you get paid by most clients?\n\nBank transfer, card, PayPal, check, something else?"], None),
("numbers", "clients", ["$90K revenue. One client = $54K (60%).\n\nThey leave → $36K.\n\nSame revenue, biggest client at 30% → lose them → $63K.\n\nOne is a crisis. The other is a slow quarter."], None),
("thread", "tax", [
  "What self-employment tax actually is, in 4 posts 🧵",
  "As an employee you paid 7.65% for Social Security and Medicare. Your employer quietly paid another 7.65%.",
  "Freelance, you pay both: 15.3%, on 92.35% of your profit. On $60K that's about $8,500, before any income tax.",
  "Two offsets: you deduct half of it, and it builds your Social Security record.\n\nSet aside for it from the first dollar.\n\n" + NA], CALC),
("checklist", "tax", ["Before Dec 31, freelancers:\n\n- check this year's profit\n- tax savings vs what you'll owe\n- make or plan the Jan 15 payment\n- total your 2026 business expenses\n- count your 2026 business miles\n- chase unpaid invoices\n\n" + NA], Q4),
("hot-take", "rates", ["\"Exposure\" is a payment term your landlord doesn't accept."], None),
("myth-fact", "invoicing", ["Myth: an unpaid invoice is a tax write-off.\n\nFact: most freelancers use the cash method. Money you never received was never counted as income, so there's nothing to deduct.\n\nThe protection is a deposit, not a deduction."], None),
("question", "rates", ["What was your first freelance rate, and what is it now?\n\nNo judgment. It helps people just starting."], None),
("one-liner", "invoicing", ["Invoice the day you deliver.\n\nEvery day you wait is a day added to the payment clock."], None),
("numbers", "tax", ["Federal tax set-aside by freelance profit (single, no state):\n\n$40K → ~19%\n$60K → ~20%\n$80K → ~21%\n$100K → ~22%\n\nAdd your state. Round up.\n\n" + NA], CALC),
("thread", "rates", [
  "Setting 2027 rates? 6 numbers to pull first 🧵",
  "1. Take-home you want\n2. Health insurance\n3. Retirement savings",
  "4. Business costs\n5. Weeks you'll really work\n6. Billable hours a week (honestly)",
  "Add 1–3. Gross up for tax. Add 4. Divide by 5 × 6.\n\nThat's your floor. Charge that or the market rate, whichever's higher. Tell clients 30–60 days ahead."], RATE),
]


def xlen(text):
    """Length as X counts it: most Latin text is 1 per character, other symbols and emoji count 2 (twitter-text)."""
    one = ((0, 4351), (8192, 8205), (8208, 8223), (8242, 8247))
    return sum(1 if any(a <= ord(c) <= b for a, b in one) else 2 for c in text)


def build():
    posts = []
    for i, (fmt, topic, parts, link) in enumerate(POSTS):
        d = START + timedelta(days=i)
        posts.append({"n": i + 1, "date": d.isoformat(), "weekday": d.strftime("%a"), "format": fmt, "topic": topic,
                      "posts": parts, "link_reply": link, "longest": max(xlen(p) for p in parts)})
    (HERE / "posts.json").write_text(json.dumps(posts, indent=1, ensure_ascii=False) + "\n")
    out = ["# 30 days of Threads/X posts for freelancers", "",
           "Generated by `build_threads_x.py`. Edit the script, not this file. Post each day's text on **both** X and "
           "Threads, by hand, from the 1099 Money accounts, Nov 16 to Dec 15, 2026. A thread is several posts in a row "
           "(reply to yourself on X; use \"add to thread\" on Threads).", "",
           "Where there's a **link reply**, post it as the first reply to your own post. See README.md for the routine.", ""]
    for p in posts:
        out += [f"## {p['n']}. {p['weekday']} {p['date']} · {p['format']} · {p['topic']}", ""]
        for k, t in enumerate(p["posts"], 1):
            label = f"**{k}/{len(p['posts'])}**" if len(p["posts"]) > 1 else ""
            out += ([label, ""] if label else []) + ["```", t, "```", ""]
        if p["link_reply"]:
            out += [f"**Link reply:** {p['link_reply']}", ""]
    (HERE / "POSTS.md").write_text("\n".join(out))
    print(f"wrote {len(posts)} days, longest part {max(p['longest'] for p in posts)} chars")


if __name__ == "__main__":
    build()
