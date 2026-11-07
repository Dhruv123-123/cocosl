"""4 YouTube long videos for weeks 31-34, each with an original_element (ORIGINALITY_PASS.md rule 3)."""
from sources import *
from common import P_FAMILY, P_TEXT
from shorts import P_TEENS, P_HOME


def L(**k):
    return k


LONG = [
L(week=31, pillar=P_TEENS,
 title="Teens and summer money: money flips, free game coins and check-first babysitting jobs",
 title_variants=["3 scams aimed at teens this summer", "Before your teen's first paycheck, watch this together"],
 hook="3 scams go after teens every summer, right when they first have money of their own. Here's each one, and the talk that stops all three.",
 thumb="Teen scams: 3 to know",
 hashtags=["teens", "summerjob", "paymentapps", "parenting", "gaming", "scamdecoded"],
 caption="Money flips, free game coins and fake babysitting jobs: three scams that go after teens in summer, and the "
         "ten-minute talk that stops them. Examples are fictional.",
 description_intro="Three scams that target teens in summer, how each one works, and a ten-minute talk to have before "
                   "the first paycheck.",
 original_element="Dhruv screen-records the security settings in a payment app and a game account on his own phone "
                  "(2-step verification, private payments, parent PIN), with face cam intro and outro.",
 sources=[CASH_FLIP, FTC_FREE_MONEY, ROBLOX_GEN, ROBLOX_SCAMS, FTC_NANNY, FTC_CHILDCARE_CHECK, FTC_CHECKS],
 claims=["Cash flipping offers are scams (Cash App)", "Free Robux generators are scams (Roblox)",
         "Scammers posing as families send fake checks to nannies and caregivers (FTC)"],
 segs=[
  ("Why summer", "Summer is when a lot of teens get their first real money: a job, babysitting, birthday cash in a "
   "payment app. Scammers know it. The three scams in this video all show up in a teen's feed or messages, and all "
   "three rely on the same thing, a teen who hasn't seen the trick before. So let's show them the trick."),
  ("Money flips", "Scam one is the money flip. A post says send fifty dollars and get five hundred back, with fake "
   "screenshots of happy customers. Nobody can multiply money you send them. Once the fifty is sent, it's gone, and "
   "then comes a release fee, then a verification fee, then a tax. Cash App itself warns about this. The rule is simple: "
   "payment apps are for people you know in real life."),
  ("Free game coins", "Scam two is free game currency. A video or a site promises unlimited free coins, just log in. "
   "There's no generator. The site keeps the username and password, and the scammer takes the account, the items and "
   "anything bought with real money. Roblox says it plainly: free Robux generators are scams. The rule: the password "
   "goes into the game, and nowhere else."),
  ("Check-first jobs", "Scam three is the job that pays before it starts. A family hires your teen to babysit by text, "
   "mails a check for more than the pay, and asks them to send the extra to a supplier. The bank shows the money, then "
   "the check bounces days later, and your teen owes the bank everything they sent. The FTC has warned about this one "
   "again this year. The rule: no real job pays you first and asks for money back."),
  ("Settings", "Now the settings. On screen, I'm going through my own payment app and game account. Turn on two-step "
   "verification on both. Set payments to private so strangers can't see who your teen pays. Turn on payment "
   "notifications. And on game accounts for younger kids, set a parent PIN so purchases and settings need you."),
  ("The talk", "Then the talk, and keep it short. Three rules: pay only people you know, passwords stay in the app, and "
   "no job pays you first. And one promise: if something feels off, they can tell you, and nobody's in trouble. That "
   "promise matters most, because shame is what stops kids from telling anyone until it's too late."),
  ("If it happened", "If it already happened, act the same day. Report the account inside the app. Change any password "
   "that was typed into a fake site. Call the bank about any check that was deposited. And report it at report fraud dot "
   "f t c dot gov. Then thank your teen for telling you."),
 ]),
L(week=32, pillar=P_HOME,
 title="Before Father's Day: car warranty calls, Google listing threats and the overpaying car buyer",
 title_variants=["3 scams that go after Dad", "Car, business, and the buyer who overpays"],
 hook="3 scams go after dads who own a car or a small business. Here's each one, before Father's Day.",
 thumb="3 scams aimed at Dad",
 hashtags=["fathersday", "carwarranty", "smallbusiness", "carsales", "robocall", "scamdecoded"],
 caption="Car warranty 'final notices', robocalls threatening your Google listing, and the buyer who overpays for "
         "Dad's truck. Three scams to send Dad before Father's Day. Examples are fictional.",
 description_intro="Three scams aimed at car owners and small business owners, and what to do about each.",
 original_element="Dhruv shows his own phone's call log of warranty robocalls (numbers blurred) and walks through "
                  "blocking and reporting them, with face cam intro and outro.",
 sources=[FTC_WARRANTY, FTC_WARRANTY_CALLS, FTC_SERVICE, FTC_GOOGLE_RC, FTC_SMB, FTC_DIRECTORY, FTC_CAR_SELLERS, FBI_CAR],
 claims=["Auto warranty robocalls and mailers often aren't from the manufacturer or dealer (FTC)",
         "The FTC took action against robocallers falsely threatening removal from Google (FTC)",
         "Scammers send fake checks to online car sellers (FTC)"],
 segs=[
  ("Why Dad", "This one's for the dads, and everyone who has to explain things to one. If your dad owns a car or runs a "
   "small business, his phone probably rings with at least one of these every week. Three scams, what each one "
   "wants, and one simple answer for each."),
  ("Warranty calls", "Scam one is the car warranty final notice. A robocall or an official-looking postcard says your "
   "warranty is about to expire. It's not from the carmaker or the dealer. Usually it's a seller of service contracts, "
   "which are not the same as a warranty, and some take a down payment and disappear. The FTC's advice is to hang up. "
   "Your dealer or the owner's manual tells you what you already have."),
  ("If he wants coverage", "If Dad does want extra coverage, that's fine, but it's a decision for the kitchen table, "
   "not a cold call. Get the contract in writing. Read what's not covered, who does the repairs, and how to cancel. And "
   "compare it with simply saving the money for repairs."),
  ("Google listing calls", "Scam two hits small business owners. A robocall says your business will be removed from "
   "Google today unless you press one. Then someone offers to fix it, or get you to the first page, for a fee. The FTC "
   "has taken action against robocallers using exactly this threat. A basic Google Business Profile is free, and you "
   "manage it yourself. Its cousin is the directory invoice, a bill for a listing nobody ordered. The FTC says don't pay "
   "invoices you can't match to an order."),
  ("The overpaying buyer", "Scam three is for anyone selling a car, boat or trailer online. A buyer offers full price, "
   "doesn't need to see it, and sends a check for more than the price. Send the difference to my shipper, they say. "
   "The check bounces days later. The FTC warned car sellers about this one. The rule: never send back an overpayment, "
   "and get paid in a way you can confirm, like at your bank together."),
  ("Blocking calls", "Now on screen, my own call log. Here's how to block a number, how to turn on your carrier's spam "
   "filter, and how to report a robocall at the FTC's site. It won't stop every call, but each report helps the FTC "
   "find the people behind them."),
  ("For Father's Day", "So for Father's Day, send him this, or better, sit down for ten minutes and set up his call "
   "filter together. One rule covers all three: hang up, and check it yourself with someone you already know, your "
   "dealer, your own business profile, your own bank."),
 ]),
L(week=33, pillar=P_FAMILY,
 title="Official-looking scams: jury duty warrants, deed letters and 'storage full' emails",
 title_variants=["Looks official, isn't: 3 scams", "Seals, badges and deadlines: how fake official messages work"],
 hook="3 scams borrow the look of something official: a court, a county office and your phone's own storage warning.",
 thumb="Looks official. Isn't.",
 hashtags=["juryduty", "governmentimposter", "homeowner", "phishing", "seniors", "scamdecoded"],
 caption="A jury duty warrant call, a deed letter with a seal, and an email saying your photos will be deleted. "
         "How each one borrows authority, and how to check. Examples are fictional.",
 description_intro="Three scams that look official, how each one borrows authority, and the one check that works on all three.",
 original_element="Dhruv lays three fictional mock-ups on his desk (a call script, a deed letter, a storage email) "
                  "and marks the tells on each with a pen, filmed from above; then his own phone's real storage screen.",
 sources=[COURTS_JUROR, FTC_DEED, FTC_CLOUD, FTC_PHISH],
 claims=["Federal courts don't ask for payment or sensitive information by phone for jury service (US Courts)",
         "Deed copy mailers often come from private companies (FTC)",
         "Scammers send fake 'cloud storage full' messages (FTC)"],
 segs=[
  ("Borrowed authority", "Some scams don't try to be your friend. They try to look official: a badge number, a seal, a "
   "case number, a deadline. That look does the work, because most of us don't argue with a court or a county office. "
   "Here are three of them, with the tells marked in pen."),
  ("Jury duty", "One, the jury duty warrant call. You missed jury duty, there's a warrant, pay the fine now to cancel "
   "it, with a payment app or gift cards. The federal courts have a page warning about this call. Courts send jury "
   "notices by mail, and they don't ask for your Social Security number or card by phone. Hang up and call the court "
   "yourself, using the number on its own website."),
  ("The deed letter", "Two, the deed letter. Official seal, your parcel number, response due in ten days, get a "
   "certified copy of your deed for eighty-nine dollars. It's a private company, and the small print usually says so. "
   "The FTC says your county recorder can usually give you a copy for a few dollars, or free online. The same trick is "
   "used for homestead exemptions and property tax appeals, which you can usually file yourself."),
  ("Storage full", "Three, the storage email. Your cloud storage is full, your photos will be deleted, upgrade now with "
   "a discount. The link goes to a lookalike page for your card details. Now my own phone: Settings, my name, storage. "
   "That's the real number, and it's one tap from the home screen."),
  ("The pattern", "Put the three side by side and the pattern is the same. Authority, a deadline, and a way to pay or "
   "click right now. Real courts, counties and phone companies give you time, and they let you check through their own "
   "website."),
  ("One check", "So here's the one check that works on all three. Don't use the phone number, the link, or the "
   "address in the message. Find the court, the county or the company yourself, and ask. If it's real, they'll tell "
   "you. If it isn't, you've lost nothing but five minutes."),
  ("If you paid", "If you already paid, call your bank or the gift card company the same day, and report it at report "
   "fraud dot f t c dot gov. And look through an older parent's mail pile with them every so often. These letters "
   "are aimed at them."),
 ]),
L(week=34, pillar=P_TEXT,
 title="4th of July weekend scams: lost pet texts, money 'sent by mistake' and fake celebrity ads",
 title_variants=["3 scams for the long weekend", "Fireworks, payment apps and fake ads"],
 hook="3 scams pick up around the 4th of July. One goes after people whose pets ran from the fireworks.",
 thumb="4th of July: 3 scams",
 hashtags=["fourthofjuly", "lostpet", "paymentapps", "deepfake", "longweekend", "scamdecoded"],
 caption="Lost pet texts after the fireworks, strangers who send money 'by mistake', and fake celebrity ads for holiday "
         "deals. Three scams for the long weekend. Examples are fictional.",
 description_intro="Three scams that pick up around the 4th of July weekend, and what to do about each.",
 original_element="Dhruv screen-records two real settings on his own phone: setting a payment app to private, and the "
                  "'report ad' menu in a social app, with face cam intro and outro.",
 sources=[BBB_LOST_PET, FTC_GVOICE, VENMO_SCAMS, CASH_SCAMS, FTC_CELEB, FTC_IMPOSTER_ADS],
 claims=["Scammers target lost pet posts asking for codes or money (BBB)",
         "Payment apps warn about strangers who send money 'by mistake' (Venmo)",
         "Scammers use fake celebrity endorsements in ads (FTC)"],
 segs=[
  ("The weekend", "Long weekends are busy for scammers too. People are distracted, shopping, traveling, and on the 4th, "
   "a lot of pets bolt when the fireworks start. Here are three scams that pick up around the holiday, and a simple "
   "answer for each."),
  ("Lost pets", "One, the lost pet text. You post a flyer with your number, and a text arrives: I think I found your "
   "dog, send me the code I'm about to text so I know you're the owner. The code is a sign-up code for an account in "
   "your name. The other version asks for gas money to bring the pet back. The Better Business Bureau has warned about "
   "both. A real finder sends a photo and meets you. No codes, and no money before you see your pet."),
  ("Before the 4th", "Before the fireworks, check your pet's microchip details are current and the tag has your number. "
   "When you post a flyer, hold back one detail only you know, and ask callers to describe it. And call local shelters "
   "every day."),
  ("Sent by mistake", "Two, the accidental payment. Three hundred dollars arrives in your payment app from a stranger, "
   "then a polite message: so sorry, can you send it back? Their payment came from a stolen card or account, and it "
   "gets reversed. The three hundred you sent back from your own money doesn't. Venmo and Cash App both warn about this. "
   "Don't send it back. Contact support inside the app and let them reverse it."),
  ("Settings", "On screen, my own payment app. Here's how to set payments to private, and turn on notifications, so a "
   "surprise payment never goes unnoticed."),
  ("Fake celebrity ads", "Three, the fake endorsement. A famous face in an ad, promoting a holiday deal, a gadget, or an "
   "investment. The FTC says many of these endorsements are fake, and some videos are made with AI. Search the "
   "celebrity's name and the product. If it's real, it's on their own pages. If it isn't, scroll past and report the "
   "ad. Here's that menu, two taps. The FTC is asking people to report these ads to them as well."),
  ("Have a good weekend", "So, three habits for the long weekend: no codes to strangers, no sending back money you "
   "didn't ask for, and no buying from a famous face without checking. Enjoy the fireworks, and keep the dog inside."),
 ]),
]
