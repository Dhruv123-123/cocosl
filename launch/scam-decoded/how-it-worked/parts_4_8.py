"""Parts 4-8 of 'How the scam actually worked'. Same shape as parts 1-3 in series.py."""
from series import VOICE

PARTS_4_8 = [
dict(part=4, slug="removed-from-google-robocalls",
 title="How the scam actually worked: the robocalls that said Google would close your business",
 title_variants=["'Press 1 to speak to a Google specialist': an FTC robocall case, step by step",
                 "$300 to $700 for a free listing: how the Google robocall scheme worked"],
 hook="4,467 small business owners got FTC refund checks after robocalls said Google would mark them 'permanently closed'.",
 thumb="'Google' didn't call",
 hashtags=["smallbusiness", "robocall", "howitworked", "google", "scamalert", "scamdecoded"],
 caption="A robocall says Google will label your business 'permanently closed' unless you talk to a 'Google "
         "specialist'. Then a $300 to $700 fee to 'claim and verify' a listing that's free. How the FTC's case "
         "against Pointbreak Media worked, and the three checks for any small business.",
 description_intro="Part 4 of How the scam actually worked: the FTC's case against Pointbreak Media and related "
                   "companies, from the 2018 action to the refund checks mailed in 2020, told from the FTC's public record.",
 original_element="Case board c4 (how-it-worked/out/removed-from-google-robocalls.png) drawn by us from the FTC "
                  "releases. Dhruv screen-records the free sign-up page for a Google Business Profile (no account "
                  "details) to show there's nothing to pay for. " + VOICE,
 sources=["https://www.ftc.gov/news-events/news/press-releases/2020/08/ftc-sends-refund-checks-totaling-more-700000-small-business-owners-defrauded-deceptive-robocalls",
          "https://www.ftc.gov/business-guidance/blog/2018/05/ftc-challenges-robocallers-false-threat-small-businesses-will-be-removed-google",
          "https://www.ftc.gov/business-guidance/resources/scams-your-small-business-guide-business-0"],
 claims=["Robocalls claimed to act for Google and threatened to label businesses 'permanently closed' (FTC)",
         "Telemarketers charged a one-time fee of $300 to $700 to 'claim and verify' listings; the court found the claims false (FTC)",
         "In August 2020 the FTC mailed more than $700,000 in refunds to 4,467 small business owners, averaging $158.32 (FTC)",
         "The FTC never requires payment or information to cash a refund check (FTC)"],
 board=dict(kicker="Case file · FTC v. Pointbreak Media · 2018–2020", headline="'Google will close your business'",
  facts=[("$300–700", "fee per business"), ("4,467", "refund checks"), ("$700K+", "refunded")],
  steps=["A robocall 'on Google's behalf'",
         "Threat: listed as 'permanently closed'",
         "'Press 1 for a Google specialist'",
         "A fee to 'claim and verify' a free listing",
         "Promises of top search placement"],
  source="Source: Federal Trade Commission, May 2018 and Aug 18 2020."),
 segs=[
  ("Cold open", "If you've ever run a small business, you've probably had this call. A recorded voice says it's calling "
   "about your Google listing. Your business is about to be marked permanently closed. Press one to speak to a Google "
   "specialist. In 2018, the Federal Trade Commission went to court to stop one set of companies making these calls, "
   "Pointbreak Media and three related companies. Two years later, the FTC mailed refund checks to four thousand four "
   "hundred sixty-seven small business owners. Here's how the scheme worked, from the FTC's public record."),
  ("Step 1: borrow Google", "Step one is borrowing a name every business owner cares about. The callers claimed to be "
   "acting on Google's behalf. For a restaurant, a plumber or a hair salon, Google is where customers find you. So a "
   "call about your Google listing doesn't sound like a sales call. It sounds like an emergency."),
  ("Step 2: the threat", "Step two is the threat. Google will label your business permanently closed unless you speak to "
   "a specialist. Think about what that means to an owner. Closed means customers drive past. It's the kind of threat "
   "that makes you press one before you think."),
  ("Step 3: the fee", "Step three is the fee. Telemarketers said they could claim and verify the business's Google "
   "listing and make it show up prominently in search results, for a one-time fee of three hundred to seven hundred "
   "dollars. The court found those claims were false. Claiming a basic Google Business Profile is free, and no one can "
   "sell you a promised spot at the top of search results."),
  ("Why it worked", "Why did owners pay? Because each piece was close to something true. Listings really can be "
   "claimed. Search placement really does matter. Google really does mark some businesses as closed. The scam stitched "
   "true pieces into a false story, then added a deadline."),
  ("How it ended", "The FTC's 2018 action halted the calls, and in August 2020 the agency mailed more than seven hundred "
   "thousand dollars in refunds, an average of about one hundred fifty-eight dollars per business. One detail from that "
   "refund notice is worth remembering: the FTC never requires payment or information to cash a refund check. If "
   "someone says otherwise, that's a second scam."),
  ("The office version", "These calls still happen, under new names. The FTC's guide for small businesses lists the "
   "same pattern for fake directory listings, fake invoices for ads you never ordered, and fake domain renewals. Same "
   "shape every time: a name you trust, a threat, a fee."),
  ("Three checks", "Three checks for any small business. One: Google doesn't robocall you about your listing. Sign in "
   "to your own Business Profile and look. On screen, that's the free sign-up page. Two: one person approves payments, "
   "and only for invoices that match something you ordered. Three: if you already paid, call your card company and "
   "dispute the charge, and report the call to the FTC. Every report helps them find the next Pointbreak."),
 ]),
dict(part=5, slug="irs-call-centers",
 title="How the scam actually worked: inside the IRS impersonation call centers",
 title_variants=["'You owe the IRS, pay today or be arrested': the call centers behind it",
                 "From a call center in India to a gift card in Texas: one IRS scam, step by step"],
 hook="24 people sentenced, sentences up to 20 years, thousands of victims. This is how the 'you owe the IRS' calls really worked.",
 thumb="Inside the fake IRS calls",
 hashtags=["irs", "howitworked", "governmentimposter", "truecrime", "scamalert", "scamdecoded"],
 caption="Call centers in Ahmedabad, callers posing as the IRS and immigration officers, threats of arrest and "
         "deportation, then a network of runners in the US turning payments into cash. How the case the Justice "
         "Department prosecuted in Houston worked, from the guilty pleas.",
 description_intro="Part 5 of How the scam actually worked: the India-based IRS and USCIS impersonation call center "
                   "case prosecuted in the Southern District of Texas, with 24 defendants sentenced by July 2018, told "
                   "from the Justice Department's public record.",
 original_element="Case board c5 (how-it-worked/out/irs-call-centers.png) drawn by us: the path from a call center "
                  "to a US runner, from the DOJ release. Dhruv on camera holding a gift card from a store rack and "
                  "reading the scam warning printed on its packaging. " + VOICE,
 sources=["https://justice.gov/opa/pr/24-defendants-sentenced-multimillion-dollar-india-based-call-center-scam-targeting-us-victims",
          "https://www.justice.gov/usao-sdtx/pr/dozens-individuals-indicted-multimillion-dollar-indian-call-center-scam-targeting-us",
          "https://www.irs.gov/help/how-to-know-its-the-irs"],
 claims=["24 defendants were sentenced by July 20 2018, with sentences up to 240 months (DOJ)",
         "From 2012 to 2016, call centers in Ahmedabad, India impersonated the IRS and USCIS and threatened arrest, fines or deportation (DOJ)",
         "US-based runners laundered payments using reloadable cards registered with stolen identities, money orders and wire pickups under fake names (DOJ)",
         "The scheme defrauded thousands of US residents of hundreds of millions of dollars, per the release (DOJ)"],
 board=dict(kicker="Case file · S.D. Tex. call center case · 2016–2018", headline="The fake IRS calls, end to end",
  facts=[("24", "people sentenced"), ("20 yrs", "longest sentence"), ("2012–16", "years it ran")],
  steps=["Call centers in Ahmedabad dial US numbers from data lists",
         "'IRS' or 'immigration': you owe, pay or be arrested",
         "Pay by stored value card or wire, today",
         "US runners turn cards and wires into cash",
         "Reloadable cards registered with stolen identities"],
  source="Source: US Department of Justice, Jul 20 2018 (guilty-plea admissions)."),
 segs=[
  ("Cold open", "This is the Internal Revenue Service. There's a warrant for your arrest for unpaid taxes. Pay today, or "
   "officers will come to your home. Millions of Americans got a call like that. In 2016, the Justice Department charged "
   "dozens of people over one network behind them, and by July 2018, twenty-four had been sentenced in Houston, one to "
   "twenty years. The guilty pleas describe, step by step, how the calls turned into cash."),
  ("Step 1: the call centers", "Step one was the call centers, in Ahmedabad, India. According to the pleas, operators "
   "used data brokers and other sources to find people in the US to call. That's why the calls sometimes knew your "
   "name or your address. It wasn't the IRS's records. It was a purchased list."),
  ("Step 2: the threat", "Step two was the threat. Callers posed as officials from the IRS or from US Citizenship and "
   "Immigration Services, and told people they faced arrest, prison, fines or deportation unless they paid a "
   "government debt immediately. Notice who that targets. Immigrants who fear deportation are less likely to call the "
   "police, and that was the point."),
  ("Step 3: the payment", "Step three was payment, by stored value cards or wire transfers. Not a check to the US "
   "Treasury, not a payment on IRS dot gov. A card number read over the phone, or a wire to a name you don't know. "
   "That payment method is the giveaway, every time."),
  ("Step 4: the runners", "Step four is the part most people never hear about. A network of runners inside the US "
   "turned that money into cash, fast. The pleas describe runners buying reloadable cards and sending the card numbers "
   "to India, where they were registered using stolen identities of real Americans and loaded with victims' money. "
   "Runners then bought money orders, deposited them, picked up wires under fake names with false IDs, and took a cut."),
  ("How it ended", "The investigation was led by Homeland Security Investigations, the Department of Homeland Security's "
   "inspector general, and the Treasury Inspector General for Tax Administration. Sentences ranged from probation to "
   "two hundred forty months. Twenty-two defendants were held liable for nearly nine million dollars in restitution to "
   "identified victims. Thirty-two people and five call centers in India were also charged; they're presumed innocent "
   "unless proven guilty."),
  ("Why gift cards", "On camera, here's a gift card from a store rack. Read the packaging. Many now print a warning: "
   "if someone asks you to pay with this card, it's a scam. That warning is there because of cases like this one."),
  ("Three checks", "Three checks. One: the IRS generally contacts you by mail first, and doesn't threaten arrest or "
   "demand immediate payment by phone. Two: no government agency takes gift cards, prepaid cards or wire transfers to a "
   "person. Three: check what you owe yourself, in your IRS Online Account. If you've already paid, call the card "
   "company or wire service right away, and report it to the Treasury Inspector General for Tax Administration and the "
   "FTC."),
 ]),
dict(part=6, slug="scam-compound",
 title="How the scam actually worked: inside a 'pig butchering' scam compound",
 title_variants=["Where the 'wrong number' texts come from: the scam compound case",
                 "127,271 bitcoin: the forced-labor scam compound case, explained"],
 hook="127,271 bitcoin, worth about $15 billion: the largest forfeiture action the Justice Department says it has ever brought.",
 thumb="Inside a scam compound",
 hashtags=["pigbutchering", "cryptoscam", "howitworked", "humantrafficking", "scamalert", "scamdecoded"],
 caption="The 'wrong number' text, the friendship, the investment app. Federal prosecutors say one source of those "
         "messages was compounds in Cambodia where trafficked workers were forced to run them. The case against the "
         "Prince Group's chairman, from the indictment. Allegations only; the defendant is presumed innocent.",
 description_intro="Part 6 of How the scam actually worked: the October 2025 indictment of Prince Group chairman Chen "
                   "Zhi in the Eastern District of New York, and the related bitcoin forfeiture complaint, told from "
                   "the Justice Department's public record. These are allegations; the defendant is presumed innocent.",
 original_element="Case board c6 (how-it-worked/out/scam-compound.png) drawn by us from the DOJ release. Dhruv on "
                  "camera reads a fictional 'wrong number' text thread (clearly marked) and maps each message to the "
                  "stage the indictment describes. " + VOICE,
 sources=["https://www.justice.gov/opa/pr/chairman-prince-group-indicted-operating-cambodian-forced-labor-scam-compounds-engaged",
          "https://www.ic3.gov/",
          "https://consumer.ftc.gov/articles/what-know-about-cryptocurrency-scams"],
 claims=["Chen Zhi, chairman of Prince Group, was indicted for wire fraud conspiracy and money laundering conspiracy (DOJ EDNY, Oct 14 2025)",
         "Prosecutors allege workers were trafficked into walled compounds in Cambodia and forced to run scams under threat of violence (DOJ)",
         "A civil forfeiture complaint targets about 127,271 bitcoin, about $15 billion at announcement, the largest forfeiture action in DOJ history (DOJ)",
         "The FBI's 2024 Internet Crime Report cites more than $5.8 billion in reported crypto investment fraud losses in 2024 (DOJ, citing FBI)"],
 board=dict(kicker="Case file · US v. Chen Zhi · E.D.N.Y. · 2025", headline="Inside a scam compound",
  facts=[("127,271", "bitcoin targeted"), ("~$15B", "value at announcement"), ("$5.8B+", "US crypto investment losses, 2024")],
  steps=["Workers trafficked into walled compounds",
         "Phone farms: thousands of phones, millions of numbers",
         "Build trust over weeks by message or social media",
         "Persuade the victim to 'invest' in crypto",
         "Funds stolen and laundered: 'spraying' and 'funneling'"],
  source="Source: US Department of Justice, Oct 14 2025. Allegations only; the defendant is presumed innocent."),
 segs=[
  ("Cold open", "Hi, is this Jenny? Sorry, wrong number. But you seem nice. That message, and the weeks of friendly "
   "chat that follow, ends with an investment app and a balance that can't be withdrawn. In October 2025, federal "
   "prosecutors in Brooklyn indicted the chairman of a Cambodian conglomerate called Prince Group, alleging his company "
   "ran compounds where trafficked workers were forced to send messages like that one. They also moved to seize about "
   "one hundred twenty-seven thousand bitcoin, worth about fifteen billion dollars at the time. These are allegations, "
   "and the defendant is presumed innocent. Here's what the public record describes."),
  ("Step 1: the workers", "Step one, prosecutors allege, is the workforce. Hundreds of people trafficked into compounds "
   "in Cambodia, surrounded by high walls and barbed wire, and forced to run scams, often under threat of violence. "
   "That changes how to think about the person texting you. Sometimes they're a prisoner too."),
  ("Step 2: phone farms", "Step two is scale. Documents described in the release refer to automated call centers using "
   "thousands of phones and millions of mobile numbers. That's why the wrong-number texts never stop. It's not one "
   "person. It's industrial."),
  ("Step 3: trust", "Step three is time. Scammers build trust over weeks through messaging apps or social media: daily "
   "check-ins, photos, life stories. Nothing is asked for. That patience is what the industry nickname, pig butchering, "
   "refers to, and it's why victims don't feel scammed until the very end."),
  ("Step 4: the investment", "Step four is the ask. Not a request for money, an opportunity: a crypto platform where "
   "the new friend says they've made money. Small deposits show big gains on a website the scammers control. Then "
   "bigger deposits. Then a fee, or a tax, to withdraw, and the money is gone."),
  ("Step 5: the laundering", "Step five is laundering. The release describes 'spraying' and 'funneling' funds through "
   "many accounts, exchanges, online gambling and crypto mining, and alleges luxury purchases including a Picasso. A "
   "network in Brooklyn allegedly laundered money from more than two hundred fifty victims in the US."),
  ("The scale", "For scale: the release cites the FBI's figure of more than five point eight billion dollars in "
   "reported crypto investment fraud losses in the US in 2024 alone. The US Treasury also designated Prince Group a "
   "transnational criminal organization, and the UK announced its own sanctions."),
  ("Three checks", "Three checks. One: a wrong-number text that turns into a friendship is a pattern, not luck. Don't "
   "keep chatting. Two: never invest on a platform someone you met online introduces you to, however long you've "
   "talked. Three: any platform that wants a fee or tax before you can withdraw is a scam, and paying it won't release "
   "the money. If it happened to you, report it to the FBI's IC3 right away, and beware anyone who offers to recover "
   "the money for a fee. That's the next scam."),
 ]),
dict(part=7, slug="money-transfer-586-million",
 title="How the scam actually worked: the money transfer company that paid $586 million",
 title_variants=["Why scammers loved one money transfer company, and how victims got refunds",
                 "$586 million: the Western Union fraud case, step by step"],
 hook="$586 million. That's what Western Union agreed to forfeit in 2017 after scammers used its system for years.",
 thumb="The $586M case",
 hashtags=["westernunion", "wirefraud", "howitworked", "refunds", "scamalert", "scamdecoded"],
 caption="Not a scammer this time: the pipe the money went through. How the FTC and the Justice Department say "
         "Western Union's system was used for scam payments for years, what the company admitted, and how victims "
         "later got money back.",
 description_intro="Part 7 of How the scam actually worked: the January 2017 FTC and Justice Department settlement "
                   "with Western Union, and the refund program that followed, told from the public record.",
 original_element="Case board c7 (how-it-worked/out/money-transfer-586-million.png) drawn by us from the FTC release. "
                  "Dhruv on camera with a blank money transfer form, pointing to the fraud warning the order requires "
                  "on transfer forms. " + VOICE,
 sources=["https://www.ftc.gov/news-events/news/press-releases/2017/01/western-union-admits-anti-money-laundering-violations-settles-consumer-fraud-charges-forfeits-586",
          "https://www.ftc.gov/enforcement/refunds/western-union-refunds",
          "https://www.justice.gov/opa/pr/department-justice-announces-phase-three-compensation-process-western-union-fraud-victims"],
 claims=["Western Union agreed to a $586 million monetary judgment with the FTC and to forfeit $586 million under a DOJ deferred prosecution agreement (FTC, Jan 19 2017)",
         "Western Union admitted willfully failing to maintain an effective anti-money laundering program and aiding and abetting wire fraud (FTC/DOJ)",
         "A 2004 internal proposal to suspend agents with 15 fraud reports in 120 days would have led to action against more than 2,000 agents from 2004 to 2012, per the FTC (FTC)",
         "The order requires fraud warnings on transfer forms and refunds when the company didn't follow its anti-fraud procedures (FTC)"],
 board=dict(kicker="Case file · FTC & DOJ v. Western Union · 2017", headline="The pipe the scam money used",
  facts=[("$586M", "forfeited"), ("2,000+", "agents a 2004 rule would have flagged"), ("2004", "fraud reports logged since")],
  steps=["A scammer tells the victim: send it by money transfer",
         "The victim pays at an agent counter",
         "Some agents were complicit, the FTC alleged",
         "Fraud reports logged, problem agents kept",
         "2017: admissions, $586M, and a refund program"],
  source="Source: Federal Trade Commission, Jan 19 2017."),
 segs=[
  ("Cold open", "Every part of this series so far has had a scammer at the center. This one doesn't. It's about the "
   "pipe the money flowed through. In January 2017, Western Union agreed to a five hundred eighty-six million dollar "
   "judgment with the Federal Trade Commission, and to forfeit the same amount under an agreement with the Justice "
   "Department. It admitted to willfully failing to keep an effective anti-money laundering program, and to aiding and "
   "abetting wire fraud. Here's what the public record says happened."),
  ("Why money transfers", "First, why scammers love money transfers. Lottery scams, grandparent scams, romance scams, "
   "fake IRS calls: for years, the instructions were the same. Go to a store, send the money by transfer, read me the "
   "reference number. It's fast, it reaches almost any country, and once it's picked up, it's very hard to reverse."),
  ("Step 1: the agents", "Step one in the FTC's account is the agents, the stores and counters that handle transfers. "
   "The FTC alleged that fraudsters worldwide used the system for years, that some agents were complicit, and that the "
   "company profited by not promptly suspending or terminating the problem ones."),
  ("Step 2: the reports", "Step two is the paper trail. Starting in at least 2004, the FTC says, the company logged "
   "customer complaints about fraud-induced payments. That same year, its own security department proposed "
   "automatically suspending any agent who paid out fifteen fraud reports within one hundred twenty days. The FTC says "
   "that rule would have led to action against more than two thousand agents worldwide between 2004 and 2012."),
  ("Step 3: the fixes", "Step three is the order. It requires a comprehensive anti-fraud program, blocking transfers to "
   "anyone who's the subject of a fraud report, refunds when the company fails to follow its anti-fraud procedures, "
   "and clear fraud warnings on transfer forms. On camera, that's the kind of warning you'll now see on a form. Read it "
   "before you send money to anyone you haven't met."),
  ("The refunds", "Then the part most people missed: victims could get money back. The Justice Department ran a "
   "compensation program for people who sent money to scammers through Western Union, and paid it out in rounds, "
   "including about one hundred fifty-three million dollars in March 2020 and one hundred forty-seven million in "
   "September 2020. Legitimate refund programs like this never charge you a fee to claim."),
  ("The lesson", "The lesson isn't that one company is bad and the others are safe. It's that the way you pay decides "
   "whether you can get money back. A credit card has dispute rights. A transfer picked up in cash usually doesn't."),
  ("Three checks", "Three checks. One: anyone who tells you to pay by money transfer, gift card or crypto, and hurry, "
   "is the scam. Two: never send a transfer to someone you haven't met in person. Three: if you already sent one, call "
   "the transfer company immediately and ask them to stop it, because until it's picked up, it may still be "
   "stoppable. Then report it to the FTC, and watch for official refund programs, which you'll find on ftc.gov, not "
   "in a text."),
 ]),
dict(part=8, slug="romance-ring",
 title="How the scam actually worked: the 'chairmen' of a romance scam ring",
 title_variants=["Fake love, real millions: a romance scam ring, step by step",
                 "Two 'chairmen' plead guilty: how a romance scam ring ran"],
 hook="More than $100 million, dozens of victims, and 2 'chairmen' who have now pleaded guilty. This is how the romance scam ring ran.",
 thumb="The romance scam 'chairmen'",
 hashtags=["romancescam", "howitworked", "datingapps", "truecrime", "scamalert", "scamdecoded"],
 caption="Fake profiles, months of trust, then money: to the 'partner', or to help 'move' money stolen from other "
         "victims. How a Ghana-based ring ran, according to federal prosecutors in Manhattan, and the three checks "
         "that protect a parent.",
 description_intro="Part 8 of How the scam actually worked: the romance scam and business email compromise conspiracy "
                   "whose two 'chairmen' pleaded guilty in the Southern District of New York in October 2026, told "
                   "from the public record. Sentencing is up to the judge.",
 original_element="Case board c8 (how-it-worked/out/romance-ring.png) drawn by us from the DOJ release. Dhruv "
                  "screen-records a reverse image search of his own photo to show how a stolen profile picture "
                  "turns up under other names. " + VOICE,
 sources=["https://www.justice.gov/usao-sdny/pr/two-chairmen-ghana-romance-scam-conspiracy-plead-guilty",
          "https://consumer.ftc.gov/articles/what-know-about-romance-scams",
          "https://www.ic3.gov/"],
 claims=["Two Ghanaian nationals described as 'chairmen' pleaded guilty to conspiracy to commit wire fraud in October 2026 (DOJ SDNY)",
         "The conspiracy stole and laundered more than $100 million from dozens of victims, per prosecutors (DOJ)",
         "Members posed as romantic partners online, often targeting vulnerable older adults, and some victims were persuaded to help launder other victims' money (DOJ)",
         "The two face up to 20 years in prison; they were extradited on August 7 2025 (DOJ)"],
 board=dict(kicker="Case file · SDNY romance scam conspiracy · 2026", headline="The romance scam ring",
  facts=[("$100M+", "stolen and laundered"), ("2", "'chairmen' plead guilty"), ("20 yrs", "maximum each")],
  steps=["Fake identities pose as romantic partners online",
         "Weeks or months building trust, often with older adults",
         "Ask for money, or ask the victim to 'move' funds",
         "Businesses tricked into wiring funds too",
         "Proceeds laundered to West Africa"],
  source="Source: US Attorney's Office, Southern District of New York, Oct 29 2026."),
 segs=[
  ("Cold open", "She's a doctor working overseas. He's an engineer on an oil rig. They message every day, for months, "
   "and they can never quite video call. In October 2026, two men from Ghana, described by prosecutors as chairmen of "
   "a criminal organization, pleaded guilty in Manhattan to conspiracy to commit wire fraud. Prosecutors say the group "
   "stole and laundered more than one hundred million dollars from dozens of victims. Here's how they say it ran."),
  ("Step 1: the profile", "Step one is the identity. Members assumed fake identities to pose as romantic partners "
   "online. The photos are usually stolen from real people. On screen, I'm running a reverse image search on a photo "
   "of myself, so you can see how quickly a picture shows up under other names. Try it on any profile that seems too "
   "perfect."),
  ("Step 2: the trust", "Step two is time. According to the release, many victims were vulnerable older men and women. "
   "The messages come every day. The relationship feels real, because to the victim, it is. That's why we never call "
   "people who fall for this foolish. The whole operation is built to beat good judgment."),
  ("Step 3: the money", "Step three is money, and it comes in two forms. The first is familiar: send money to the "
   "partner, for a ticket, a medical bill, a customs fee. The second is less known. Prosecutors say victims were also "
   "persuaded to help launder money taken from other victims: receive this transfer, then send it on. That can pull an "
   "innocent person into a criminal investigation."),
  ("Step 4: the businesses", "Step four shows how these groups diversify. The same organization, prosecutors say, also "
   "tricked businesses into wiring money, the business email compromise scam from part three of this series. Then the "
   "proceeds were laundered back to West Africa."),
  ("How it's ending", "The two men were extradited to the US in August 2025. One was held responsible for about twelve "
   "and a half million dollars in losses, the other for about twenty-eight and a half million. Each faces up to twenty "
   "years, though the judge decides the actual sentence. Another member was previously sentenced to eighty-five months, "
   "and one remains at large."),
  ("For families", "If you're worried about a parent, start with kindness. Ask about the person they're talking to, and "
   "listen. Shame is what makes people hide transfers, and hiding is what keeps the money flowing."),
  ("Three checks", "Three checks. One: never send money, gift cards or crypto to someone you haven't met in person, "
   "however long you've talked. Two: never receive and pass on money for someone, which can make you part of a crime. "
   "Three: reverse image search their photos, and if they can't do a live video call, assume they're not who they say. "
   "If it already happened, report it to the FBI's IC3 and the FTC, and tell your bank about any transfers."),
 ]),
]
