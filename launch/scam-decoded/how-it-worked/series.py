"""'How the scam actually worked': one real, documented case per long video, told step by step from public
records (DOJ, FTC, court filings), ending with the three checks that would have stopped it.

From the competitor teardown on PR #2 (idea 4). Each part has an original element: a case board we draw
ourselves from the public record (build.py renders it), plus Dhruv on camera with the source document.
"""

# ------------------------------------------------------------------ the 8-part outline
OUTLINE = [
 dict(part=1, slug="bail-money-calls", status="produced",
  case="Grandparent 'bail money' network run from Montreal call centers (US v. West et al., D. Vt., indictment unsealed Mar 4 2025)",
  angle="How a fake grandchild, a fake lawyer and a 'bail bondsman' at the door allegedly took more than $21 million from older Americans.",
  source="https://www.justice.gov/usao-vt/pr/25-canadian-nationals-charged-vermont-connection-nationwide-multimillion-dollar"),
 dict(part=2, slug="pop-up-that-always-finds-viruses", status="produced",
  case="Restoro and Reimage tech support settlement (FTC, Mar 14 2024, $26 million)",
  angle="A fake Windows pop-up, a 'scan' that found problems on every computer, and a phone call that cost hundreds more.",
  source="https://www.ftc.gov/news-events/news/press-releases/2024/03/tech-support-firms-will-pay-26-million-settle-ftc-charges-they-deceived-consumers-buying-repair"),
 dict(part=3, slug="fake-invoices-120-million", status="produced",
  case="Evaldas Rimasauskas business email compromise (SDNY, sentenced Dec 19 2019)",
  angle="How lookalike emails and a company with a borrowed name took over $120 million from two US tech companies.",
  source="https://www.justice.gov/usao-sdny/pr/lithuanian-man-sentenced-5-years-prison-theft-over-120-million-fraudulent-business"),
 dict(part=4, slug="removed-from-google-robocalls", status="outline",
  case="FTC v. Pointbreak Media (2018): robocalls falsely threatening small businesses with removal from Google",
  angle="The script, the 'press 1', and the refund checks the FTC later sent to small business owners.",
  source="https://www.ftc.gov/news-events/news/press-releases/2020/08/ftc-sends-refund-checks-totaling-more-700000-small-business-owners-defrauded-deceptive-robocalls"),
 dict(part=5, slug="irs-call-centers", status="outline",
  case="India-based IRS and immigration impersonation call centers (DOJ, S.D. Tex., indictments 2016, sentencings 2018)",
  angle="Inside the call centers behind 'you owe the IRS, pay today or be arrested', and the US money runners who bought gift cards.",
  source="https://justice.gov/opa/pr/24-defendants-sentenced-multimillion-dollar-india-based-call-center-scam-targeting-us-victims"),
 dict(part=6, slug="scam-compound", status="outline",
  case="Prince Group chairman indicted over Cambodian forced-labor scam compounds (DOJ, E.D.N.Y., Oct 2025)",
  angle="Where 'wrong number' crypto investment texts come from: workers held in compounds, and the record bitcoin forfeiture.",
  source="https://www.justice.gov/opa/pr/chairman-prince-group-indicted-operating-cambodian-forced-labor-scam-compounds-engaged"),
 dict(part=7, slug="money-transfer-586-million", status="outline",
  case="Western Union forfeits $586 million (FTC and DOJ, Jan 2017)",
  angle="How scammers used one money transfer company for years, and how victims later got money back.",
  source="https://www.ftc.gov/news-events/news/press-releases/2017/01/western-union-admits-anti-money-laundering-violations-settles-consumer-fraud-charges-forfeits-586"),
 dict(part=8, slug="romance-ring", status="outline",
  case="Ghana-based romance scam conspiracy, leaders plead guilty (SDNY)",
  angle="From a dating profile to a money mule's bank account: the roles in a romance scam ring. Verify the filing details before scripting.",
  source="https://www.justice.gov/usao-sdny/pr/two-chairmen-ghana-romance-scam-conspiracy-plead-guilty"),
]

VOICE = "Dhruv on camera and in his own voice throughout; no AI voice."

# ------------------------------------------------------------------ parts 1-3, full scripts
PARTS = [
dict(part=1, slug="bail-money-calls",
 title="How the scam actually worked: the 'bail money' calls from Montreal",
 title_variants=["Inside a grandparent scam network: fake grandkids, fake lawyers, real cash",
                 "$21 million in 'bail money': how prosecutors say a grandparent scam ran"],
 hook="25 people charged, more than 40 states, more than $21 million. This is how prosecutors say one grandparent scam network ran.",
 thumb="The 'bail money' calls",
 hashtags=["grandparentscam", "howitworked", "elderfraud", "truecrime", "scamalert", "scamdecoded"],
 caption="A call from a 'grandchild' in jail, a 'lawyer', a gag order and a 'bail bondsman' at the door. How federal "
         "prosecutors say a Montreal-based network ran, step by step, and the three checks that stop it. The people "
         "charged are presumed innocent unless proven guilty.",
 description_intro="Part 1 of How the scam actually worked: the grandparent 'bail money' case announced by the US "
                   "Attorney's Office in Vermont in March 2025, told from the public record. The charges are "
                   "allegations, and the defendants are presumed innocent unless proven guilty.",
 original_element="Case board c1 (how-it-worked/out/bail-money-calls.png), drawn by us from the DOJ release: the five "
                  "steps of the call, timed to the narration. Dhruv on camera holding a printout of the press release, "
                  "highlighting each line as he reads it. " + VOICE,
 sources=["https://www.justice.gov/usao-vt/pr/25-canadian-nationals-charged-vermont-connection-nationwide-multimillion-dollar",
          "https://www.justice.gov/usao-vt/case/united-states-v-gareth-west-et-al",
          "https://consumer.ftc.gov/articles/scammers-use-fake-emergencies-steal-your-money"],
 claims=["25 Canadian nationals were charged in an indictment unsealed March 4 2025 (DOJ, D. Vt.)",
         "Prosecutors allege the scheme took more than $21 million from older Americans in Vermont and more than 40 other states (DOJ)",
         "The scheme allegedly ran from summer 2021 to June 4 2024 from call centers in and around Montreal (DOJ)",
         "Victims were allegedly told a 'gag order' barred them from telling anyone (DOJ)"],
 board=dict(kicker="Case file · US v. West et al. · D. Vt. · 2025", headline="The 'bail money' calls",
  facts=[("25", "people charged"), ("40+", "states with victims"), ("$21M+", "alleged losses")],
  steps=["A 'grandchild' calls: arrested after a car crash, needs bail",
         "A 'lawyer' takes over and names the amount",
         "A 'gag order': don't tell anyone",
         "A 'bail bondsman' comes to the house for the cash",
         "Money moves to Canada in cash and crypto"],
  source="Source: US Attorney's Office, District of Vermont, Mar 4 2025. Charges are allegations; defendants are presumed innocent."),
 segs=[
  ("Cold open", "Imagine the phone rings at your grandmother's house. Grandma, it's me. I was in a car accident, and I've "
   "been arrested. Please don't tell Mom. A few minutes later a lawyer calls with the amount for bail. A few hours later "
   "someone knocks on the door to collect it in cash. According to federal prosecutors, a version of that call was "
   "made again and again, for about three years, from call centers in and around Montreal. In March 2025, twenty-five "
   "Canadian nationals were charged. Prosecutors say the scheme took more than twenty-one million dollars from older "
   "Americans in Vermont and more than forty other states. These are charges, not convictions, so everyone named is "
   "presumed innocent. But the method is laid out in the public record, and it's worth knowing in detail."),
  ("Step 1: the grandchild", "Step one is the call. The caller claims to be a relative, usually a grandchild, who has "
   "been arrested after a car crash and needs bail. The details are vague on purpose. Scammers don't need to know your "
   "grandchild's name if the grandparent says it first: is that you, Michael? Yes, it's me. The panic does the rest."),
  ("Step 2: the lawyer", "Step two, the indictment alleges, is a second person posing as the grandchild's attorney. "
   "This matters. A second voice, with a calm professional tone and a specific dollar amount, makes the story feel "
   "checked. It's also what moves the conversation from feelings to logistics: how much, and how fast."),
  ("Step 3: the gag order", "Step three is secrecy. According to prosecutors, victims were often told there was a gag "
   "order, so they couldn't tell anyone about the arrest. That one line does two jobs. It stops the grandparent calling "
   "the parents, who would know in ten seconds that the grandchild is fine. And it explains away anything odd, because "
   "the courts said so."),
  ("Step 4: the courier", "Step four is the knock at the door. Victims allegedly handed cash to someone posing as a "
   "bail bondsman who came to their home. Notice why that's clever. A bank teller might ask questions about a large "
   "wire. Nobody asks questions about an envelope handed over at your own front door."),
  ("Step 5: the money", "Step five is moving the money. The indictment alleges the cash was sent to Canada through cash "
   "deliveries and financial transactions, sometimes involving cryptocurrency, to hide where it came from and who had "
   "it. By the time a family finds out, the money has usually crossed a border."),
  ("How it came apart", "So how did it come apart? On June 4, 2024, Canadian police executed search warrants at several "
   "call centers and, according to the release, found many of the defendants in the middle of placing calls to older "
   "victims in Virginia. The case was investigated by Homeland Security Investigations, IRS Criminal Investigation, "
   "and Canadian police, with help from many other agencies. Nine other people had already been charged in Vermont in "
   "connection with the same scheme."),
  ("Three checks", "Here are the three checks that break every step. One: hang up and call the grandchild, or their "
   "parent, on a number you already have. That alone ends almost every version of this call. Two: a family safe word, "
   "agreed in person, that anyone calling in a panic has to say. Three: no court, lawyer or bail bondsman sends a "
   "stranger to your house to collect cash. If someone is coming to the door, call the police. And if it already "
   "happened, report it to the police and to the FBI's IC3, and tell the family. Shame keeps people quiet, and quiet "
   "is how the next call works."),
 ]),
dict(part=2, slug="pop-up-that-always-finds-viruses",
 title="How the scam actually worked: the pop-up that found viruses on every computer",
 title_variants=["The $26 million 'free scan': a tech support case, step by step",
                 "Why the scan always found something: inside an FTC tech support case"],
 hook="1 pop-up, 1 'free scan', and the scan found problems no matter what. The FTC case behind it ended in a $26 million settlement.",
 thumb="The scan always found something",
 hashtags=["techsupportscam", "howitworked", "popup", "ftc", "scamalert", "scamdecoded"],
 caption="A fake Windows pop-up, a scan that flagged problems regardless of the computer's real condition, cheap "
         "software, then a call to 'activate' it and a technician for hundreds more. How the FTC's Restoro and "
         "Reimage case worked, and the three checks that stop it.",
 description_intro="Part 2 of How the scam actually worked: the FTC's March 2024 case against Restoro and Reimage, "
                   "two Cyprus-based companies that agreed to pay $26 million, told from the FTC's public record.",
 original_element="Case board c2 (how-it-worked/out/pop-up-that-always-finds-viruses.png) drawn by us from the FTC "
                  "release. Dhruv screen-records our own harmless, clearly labelled mock pop-up on a test laptop and "
                  "shows how to close a frozen browser tab, then the FTC refund page for this case. " + VOICE,
 sources=["https://www.ftc.gov/news-events/news/press-releases/2024/03/tech-support-firms-will-pay-26-million-settle-ftc-charges-they-deceived-consumers-buying-repair",
          "https://www.ftc.gov/enforcement/refunds/restoro-reimage-refunds",
          "https://consumer.ftc.gov/consumer-alerts/2024/03/what-know-you-click-free-computer-security-scan"],
 claims=["Restoro and Reimage agreed to pay $26 million to settle FTC charges (FTC, Mar 14 2024)",
         "The FTC alleged fake Windows pop-ups led to scans that flagged problems regardless of the computer's actual condition (FTC)",
         "The software typically cost $27 to $58, and telemarketers then pitched technician services costing hundreds more (FTC)",
         "The FTC later sent refunds to affected consumers (FTC, Mar 2025)"],
 board=dict(kicker="Case file · FTC v. Restoro & Reimage · 2024", headline="The scan that always found something",
  facts=[("$26M", "settlement"), ("$27–58", "for the software"), ("$100s", "more for a 'technician'")],
  steps=["A fake Windows pop-up: 'scan to avoid more damage'",
         "The 'scan' flags problems, whatever the computer's real state",
         "Buy the software to fix it",
         "Call a number to 'activate' it",
         "A telemarketer gets remote access and sells a technician"],
  source="Source: Federal Trade Commission, Mar 14 2024. The companies settled without a trial."),
 segs=[
  ("Cold open", "You're reading a news site, and a window pops up that looks like Windows itself. Your computer may be "
   "infected. Scan now to avoid more damage. You click, a scan runs, and it finds problems. Lots of them. According to "
   "the Federal Trade Commission, scans like this one found problems regardless of the actual condition of the "
   "computer. In March 2024, the two companies behind them, Restoro and Reimage, both based in Cyprus, agreed to pay "
   "twenty-six million dollars to settle the FTC's charges. Here's how the FTC says it worked, step by step."),
  ("Step 1: the pop-up", "Step one is the pop-up. The FTC says the companies used pop-ups that imitated Windows "
   "security warnings and urged people to run a scan to avoid more damage. The trick is borrowing trust. You already "
   "believe Windows warnings, so the fake one inherits that belief."),
  ("Step 2: the scan", "Step two is the scan. It looks technical, with progress bars and long lists of files, and it "
   "always finds something. The FTC alleged the scans flagged serious problems no matter what state the computer was "
   "really in. A test that can't come back clean isn't a test. It's a sales pitch with a progress bar."),
  ("Step 3: cheap software", "Step three is a small purchase. The software typically cost between twenty-seven and "
   "fifty-eight dollars, according to the FTC. That's low enough that people buy it just to make the warnings stop. "
   "But the low price is the hook, not the business."),
  ("Step 4: the phone call", "Step four is the call. After buying, people were told to call a number to activate the "
   "software. On the call, telemarketers accessed the computer and, the FTC says, pointed to routine errors, the "
   "ordinary messages every computer logs, as signs of viruses or malware. Then the pitch: the software alone can't "
   "fix this, you need a technician, and that costs hundreds of dollars more."),
  ("Why it works", "Look at the shape of it. A scary warning, a test that always fails, a cheap first step, then a "
   "person on the phone with access to your screen. Each step is small. Nobody decides to pay hundreds for a fake "
   "repair. They decide to click a scan, then to spend thirty dollars, then to make one phone call."),
  ("What happened next", "The settlement requires the companies to pay twenty-six million dollars for refunds and bars "
   "them from misrepresenting security or performance problems and from deceptive telemarketing. In March 2025, the "
   "FTC announced it was sending more than twenty-five and a half million dollars to people affected. On screen is the "
   "FTC's refund page for this case."),
  ("Three checks", "Three checks stop every version of this. One: real security warnings don't ask you to call a "
   "number or buy something from a pop-up. Close the browser tab, and if it won't close, restart the computer. Two: "
   "never give remote access to someone you reached through a pop-up or an ad. Three: if you think something's wrong, "
   "use the security tools already built into your computer, or take it to a repair shop you chose yourself. Already "
   "paid? Call your card company and dispute the charge, and if someone had remote access, change your passwords from "
   "a different device."),
 ]),
dict(part=3, slug="fake-invoices-120-million",
 title="How the scam actually worked: the fake invoices that took over $120 million from two tech giants",
 title_variants=["$120 million by email: the business email compromise case, step by step",
                 "Two of the biggest tech companies paid a fake supplier. Here's how."],
 hook="2 of the biggest tech companies in the world, 1 fake supplier, and over $120 million wired away by email.",
 thumb="$120M by fake invoice",
 hashtags=["businessemailcompromise", "howitworked", "phishing", "smallbusiness", "truecrime", "scamdecoded"],
 caption="A company registered with a real supplier's name, lookalike emails, and invoices that sent payments to the "
         "wrong bank. How a Lithuanian man took over $120 million from two US tech companies, according to federal "
         "prosecutors, and the three checks that stop it at any size of business.",
 description_intro="Part 3 of How the scam actually worked: the business email compromise case against Evaldas "
                   "Rimasauskas, sentenced in the Southern District of New York in December 2019, told from the "
                   "public record.",
 original_element="Case board c3 (how-it-worked/out/fake-invoices-120-million.png) drawn by us: the money's path from "
                  "the victims' payments through banks in six countries, from the DOJ release. Dhruv on camera with a "
                  "printed fake invoice he made (clearly marked SAMPLE) and circles the one line that changed. " + VOICE,
 sources=["https://www.justice.gov/usao-sdny/pr/lithuanian-man-sentenced-5-years-prison-theft-over-120-million-fraudulent-business",
          "https://www.justice.gov/usao-sdny/pr/lithuanian-man-pleads-guilty-wire-fraud-theft-over-100-million-fraudulent-business",
          "https://www.ic3.gov/"],
 claims=["Evaldas Rimasauskas was sentenced to 5 years in prison for a scheme that took over $120 million from two US-based internet companies (DOJ SDNY, Dec 19 2019)",
         "He registered a Latvian company with the same name as an Asian computer hardware maker and sent emails posing as its staff (DOJ)",
         "The funds were moved through accounts in Latvia, Cyprus, Slovakia, Lithuania, Hungary and Hong Kong (DOJ)",
         "He was ordered to forfeit $49,738,559.41 and pay $26,479,079.24 in restitution (DOJ)",
         "The FBI's IC3 reports business email compromise losses in the billions of dollars each year (check the latest IC3 annual report)"],
 board=dict(kicker="Case file · US v. Rimasauskas · SDNY · 2019", headline="Over $120 million by fake invoice",
  facts=[("$120M+", "taken"), ("2", "US tech companies"), ("5 years", "prison sentence")],
  steps=["Register a company with a real supplier's name",
         "Open bank accounts in Latvia and Cyprus in that name",
         "Email the victims' staff, posing as the supplier",
         "'Please pay our new account': payments redirected",
         "Move the money on fast: 6 countries"],
  source="Source: US Attorney's Office, Southern District of New York, Dec 19 2019."),
 segs=[
  ("Cold open", "Two of the biggest technology companies in the world. Prosecutors described them only as a "
   "multinational technology company and a multinational online social media company. Both were sending millions of "
   "dollars to a hardware supplier they'd worked with for years. Between 2013 and 2015, more than one hundred twenty "
   "million dollars of those payments went somewhere else. The man behind it, Evaldas Rimasauskas, pleaded guilty to "
   "wire fraud and in December 2019 was sentenced to five years in federal prison. Here's how the Justice Department "
   "says he did it."),
  ("Step 1: borrow a name", "Step one was a name. He registered a company in Latvia with the same name as a real "
   "computer hardware maker based in Asia, one the victims really did business with. Then he opened bank accounts in "
   "Latvia and Cyprus in that name. So when a payment arrived, the name on the account matched the name on the "
   "invoice."),
  ("Step 2: the emails", "Step two was email. He sent messages to employees and agents at the two companies, made to "
   "look like they came from the real supplier's staff, from accounts designed to look genuine. The real supplier "
   "never sent them."),
  ("Step 3: the new account", "Step three was the ask, and it's always the same ask: please send what you owe to these "
   "accounts. Nothing else on the invoice had to change. Same supplier name, same kind of amounts, same kind of "
   "request the finance teams handled every week. One line changed: where the money goes. And according to "
   "prosecutors, the companies paid."),
  ("Step 4: move it fast", "Step four was speed. Once money landed, he quickly moved it on to accounts in Latvia, "
   "Cyprus, Slovakia, Lithuania, Hungary and Hong Kong. When banks asked questions, prosecutors say he gave them "
   "forged invoices, contracts and letters that looked signed by executives at the victim companies, with fake "
   "corporate stamps."),
  ("How it ended", "Lithuanian authorities arrested him in March 2017, and he was extradited to New York that August. "
   "Along with the prison sentence, he was ordered to forfeit about forty-nine point seven million dollars and pay "
   "about twenty-six point five million in restitution."),
  ("Why it matters to you", "You might think this only happens to giant companies. It's the opposite. This is the same "
   "scam that hits a landlord, a small contractor, or someone buying a house, when an email that looks like the title "
   "company says the wiring instructions have changed. The FBI calls it business email compromise, and it reports "
   "billions in losses every year. If it worked on two tech giants with whole finance departments, it can work on "
   "anyone."),
  ("Three checks", "Three checks stop it at any size. One: any change to where money goes gets confirmed by a phone "
   "call, to a number you already had, never the one in the email. Two: two people sign off on new or changed bank "
   "details. Three: slow down on urgency. A real supplier can wait a day for a call back. And if money already went "
   "out, call your bank right away and ask them to recall the wire, then report it at the FBI's IC3. Speed matters "
   "more than anything else in getting it back."),
 ]),
]
