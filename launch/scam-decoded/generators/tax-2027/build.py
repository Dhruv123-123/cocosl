"""Tax season scam pack, Sat Jan 16 - Sat Apr 10 2027: IRS impersonation, fake preparers, refund-theft texts, IP PIN.

    python3 build.py   ->  ../../tax-2027.json and ../../POSTING_PLAN_TAX_2027.md

12 posts on Saturdays, the one day the weekly plans leave open (Mar 6 is taken, so it's skipped).
Formats rotate Short -> carousel -> TikTok minute cut, and every video has a different look from the one before.
Angles are new: the existing weekly plans already cover arrest calls, refund trackers, extensions and tax relief.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "weeks-22-26"))
from common import CTA, CTA_TIKTOK, MASCOT, P_ID, P_TEXT, seg  # noqa: E402

DIRTY = "https://www.irs.gov/newsroom/dirty-dozen-tax-scams-for-2026-irs-reminds-taxpayers-to-watch-out-for-dangerous-threats"
SCAMS = "https://www.irs.gov/help/tax-scams/recognize-tax-scams-and-fraud"
PHISHING = "https://www.irs.gov/help/report-fraud/report-fake-irs-treasury-or-tax-related-emails-and-messages"
KNOW = "https://www.irs.gov/help/how-to-know-its-the-irs"
IPPIN = "https://www.irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin"
IPPIN_FAQ = ("https://www.irs.gov/identity-theft-fraud-scams/"
             "frequently-asked-questions-about-the-identity-protection-personal-identification-number-ip-pin")
IDT = "https://www.irs.gov/identity-theft-central/identity-theft-guide-for-individuals"
PREPARER = "https://www.irs.gov/taxtopics/tc254"
FREE_PREP = "https://www.irs.gov/individuals/free-tax-return-preparation-for-qualifying-taxpayers"
FREE_FILE = "https://www.irs.gov/e-file-do-your-taxes-for-free"
W2 = "https://www.irs.gov/newsroom/form-w-2-ssn-data-theft-information-for-businesses-and-payroll-service-providers"
REJECTS = "https://www.irs.gov/faqs/electronic-filing-e-file/age-name-or-ssn-rejects-errors-correction-procedures"
IMPOSTER = ("https://www.ftc.gov/news-events/news/press-releases/2026/06/"
            "ftc-data-show-people-reported-losing-3-point-5-billion-imposter-scams-2025")
SPAM = "https://consumer.ftc.gov/articles/how-recognize-and-report-spam-text-messages"
VOICE = "Dhruv records the narration in his own voice. No AI voice on TikTok cuts."
CHECKER = "Not sure about a message? Paste it into our free scam checker (link in bio). It runs on your phone and sends nothing anywhere."
P_TAX = "tax season scams"
QUIZ = "a full-screen countdown card reading PAUSE"


def slides(cover, items, save, cover_vis):
    out = [("Hook", "", cover, cover_vis)]
    out += [(str(i), n, o, v) for i, (n, o, v) in enumerate(items, 1)]
    out.append(("Save this", save, "Save it. Share it.", f"{MASCOT} giving a thumbs up"))
    return out


POSTS = [
 dict(date="2027-01-16", kind="short", look="illustrated", topic="IRS impersonation", pillar=P_TAX,
  title="'I'll set up your IRS account for you': 1 offer to refuse",
  hook="1 friendly offer to set up your IRS online account is how some tax identity theft starts.",
  thumb="Set it up yourself",
  hashtags=["taxseason", "irs", "identitytheft", "taxscam", "scamdecoded"],
  description="Why you should create your IRS Online Account yourself, not through a 'helper'.",
  caption="An IRS Online Account is useful: it shows what you owe, your payments and your IP PIN. That's why scammers "
          "offer to 'help' you set one up. Create it yourself at IRS.gov.",
  sources=[DIRTY, IDT], claims=["Scammers pose as helpers to collect information during IRS Online Account setup (IRS Dirty Dozen 2026)",
                                "Create your account directly at IRS.gov (IRS)"],
  original_element="Illustrated beats; the closing beat is 5 seconds of Dhruv's screen showing IRS.gov's sign-in page (no login).",
  segments=[
   ("Hook", "One friendly offer. I'll set up your IRS online account for you, just send me your details.",
    "'I'll set it up for you'", f"{MASCOT} looking at a laptop"),
   ("Why they want it", "That account shows your tax records and your IP PIN. Whoever sets it up can get in, and file in "
                        "your name.", "Whoever sets it up can get in", "a padlock with someone else's key"),
   ("The tell", "The IRS says create your account directly at I R S dot gov. Don't rely on a helper who contacted you.",
    "Create it yourself at IRS.gov", "an address bar reading IRS.gov"),
   ("Do this", "Set it up yourself, with your own email and phone. Then turn on an IP PIN while you're in there.",
    "Your email. Your phone. Your account.", f"{MASCOT} with a shield"),
  ]),
 dict(date="2027-01-23", kind="carousel", look="checklist", topic="IP PIN", pillar=P_ID,
  title="The IRS IP PIN: 6 facts before you file",
  hook="6 facts about the IRS IP PIN, the 6-digit number that blocks tax refund theft.",
  thumb="IP PIN: 6 facts",
  hashtags=["ippin", "taxseason", "identitytheft", "irs", "scamdecoded"],
  description="Six facts about the IRS Identity Protection PIN.",
  caption="The IP PIN is a 6-digit number the IRS gives you so nobody else can file a federal return with your Social "
          "Security number. 6 facts before you file.",
  sources=[IPPIN, IPPIN_FAQ], claims=["Anyone with an SSN or ITIN who can verify their identity can get an IP PIN (IRS)",
                                      "A new IP PIN is generated each year (IRS)", "The IP PIN is used on federal returns only, not state returns (IRS)"],
  original_element="Slide 3 is a screenshot of where the IP PIN lives in the IRS Online Account (Dhruv's own, PIN blurred).",
  segments=slides("IP PIN: 6 facts", [
   ("Anyone with an SSN or ITIN who can verify their identity can get one. You don't need to be a victim first.", "1. Anyone can get one", "a 6-digit code on a shield"),
   ("It's 6 digits, and without it nobody can e-file a federal return with your Social Security number.", "2. It blocks fake returns", "a return with a stop sign"),
   ("The fastest way is your IRS Online Account or the IRS app. There's also a paper form if your income is under the limit.", "3. Get it online", "a phone with the IRS app"),
   ("A new one is generated every year. Look up the current one in your account each January.", "4. It changes yearly", "a calendar with January circled"),
   ("Give it only to the preparer filing your return. Don't put it on your state return or an extension.", "5. Federal return only", "a form labelled 1040"),
   ("Lost it? Look it up in your account, or call the number on IRS.gov. It isn't proof of identity on calls.", "6. Lost it? Look it up", "a magnifying glass on a lock"),
  ], "Save this and get yours before you file.", f"{MASCOT} holding a 6-digit card")),
 dict(date="2027-01-30", kind="tiktok", look="walkthrough", topic="refund-theft texts", pillar=P_TAX,
  title="The 'IRS refund' text with a QR code, played out",
  hook="4 red flags in 1 'IRS refund' text with a QR code. Watch them light up one by one.",
  thumb="QR code from the 'IRS'? No.",
  hashtags=["taxrefund", "irs", "qrcode", "taxscam", "scamdecoded"],
  description="The fake IRS refund text with a QR code, walked through.",
  caption="Refund 'pending verification', a QR code and a 48-hour deadline. The IRS doesn't start contact about your "
          "refund by text. Example is fictional.",
  sources=[DIRTY, PHISHING, SPAM], claims=["Scammers send IRS-looking texts with QR codes that lead to fake sites (IRS Dirty Dozen 2026)",
                                           "Report IRS-related phishing to phishing@irs.gov (IRS)"],
  original_element="Walkthrough video w8-irs-refund-text (originality/out/walkthroughs/w8-irs-refund-text). " + VOICE,
  segments=[
   ("Hook", "Four red flags in one IRS refund text, and this one has a QR code. Watch them light up one by one.",
    "4 red flags. Watch.", "walkthrough w8, blank"),
   ("The text", "IRS notice. Your federal refund of two thousand three hundred eighteen dollars is pending verification. "
                "Scan the QR code or visit the link within forty-eight hours to avoid cancellation.",
    "'Pending verification'", "walkthrough w8, first message"),
   ("Pause", "Pause. Count the red flags before I point them out.", "Pause: count them", QUIZ),
   ("Flags 1 and 2", "One: it says IRS, by text, out of the blue. The IRS doesn't start contact about your refund that way. "
                     "Two: forty-eight hours or it's cancelled. Refunds don't expire like that.",
    "1: IRS by text · 2: deadline", "walkthrough w8, flags 1 and 2"),
   ("Flags 3 and 4", "Three: the link and the QR code go to a site that isn't I R S dot gov. Four: it wants your Social "
                     "Security number, birthday and bank routing number. That's enough to file in your name and send the "
                     "refund to them.", "3: not IRS.gov · 4: SSN + bank", "walkthrough w8, flags 3 and 4"),
   ("The fix", "Check your refund only at I R S dot gov slash refunds, typed in yourself. Forward the text to seven seven "
               "two six, and report it to phishing at I R S dot gov.", "IRS.gov/refunds. Report to phishing@irs.gov.",
    f"{MASCOT} pointing at an address bar"),
   ("Already scanned?", "Already scanned it and typed your details? Get an IP PIN now, so nobody can file with your number, "
                        "and follow the steps at identity theft dot gov.", "Typed your SSN? Get an IP PIN now.",
    "a shield with six digits"),
  ]),
 dict(date="2027-02-06", kind="short", look="quiz pause", topic="fake preparers", pillar=P_TAX,
  title="Quiz: which of 3 tax preparers gets your W-2?",
  hook="3 tax preparers, 1 you can trust. Pause and pick before I tell you.",
  thumb="Which preparer?",
  hashtags=["taxpreparer", "taxseason", "ghostpreparer", "irs", "scamdecoded"],
  description="A quick quiz on choosing a tax preparer: PTIN, signatures and fees.",
  caption="A: charges a percentage of your refund. B: won't sign the return. C: has a PTIN, signs the return, and gives "
          "you a copy. Only one is safe.",
  sources=[PREPARER, DIRTY], claims=["Paid preparers must have a PTIN and sign the return (IRS)",
                                            "Avoid preparers who base fees on the size of your refund (IRS)",
                                            "Taxpayers are legally responsible for what's on their return (IRS)"],
  original_element="Quiz format with a real 3-second pause card; Dhruv on camera for the answer.",
  segments=[
   ("Hook", "Three tax preparers, one you can trust. Pause and pick.", "Pause: A, B or C?", "three cards labelled A B C"),
   ("The three", "A charges twenty percent of your refund. B prepares it but won't sign it. C has a P T I N, signs the "
                 "return and gives you a copy.", "A: % cut · B: no signature · C: PTIN",
    "the three cards with labels"),
   ("Answer", "C. A fee based on your refund is a red flag. A preparer who won't sign is what the IRS calls a ghost "
              "preparer.", "C is the only safe one", "card C with a green check"),
   ("Why it matters", "You're legally responsible for what's on your return, even if they wrote it. Never sign a blank one.",
    "You're responsible for your return", f"{MASCOT} holding a pen over a blank form"),
  ]),
 dict(date="2027-02-13", kind="carousel", look="quiz", topic="fake preparers", pillar=P_TAX,
  title="Spot the red flags: the 'biggest refunds in town' preparer ad",
  hook="4 red flags in 1 tax preparer ad. How many can you find before you swipe?",
  thumb="Find 4 red flags",
  hashtags=["taxpreparer", "ghostpreparer", "spotthescam", "taxseason", "scamdecoded"],
  description="A quiz carousel: four red flags in a ghost preparer's ad.",
  caption="Quiz time. Count the red flags in the ad on slide 1 before you swipe. Example is fictional.",
  sources=[PREPARER, DIRTY], claims=["Ghost preparers won't sign returns or omit their PTIN (IRS)",
                                            "Never sign a blank or incomplete return (IRS)"],
  original_element="Rendered quiz carousel q8-ghost-preparer: use the 7 PNG slides as-is (originality/out/quizzes/q8-ghost-preparer).",
  segments=slides("Find 4 red flags", [
   ("'20% of your refund.' A fee based on how big your refund is.", "1. A % of your refund", "quiz slide 3"),
   ("'Just sign here and we'll fill in the rest.' Never sign a blank or incomplete return.", "2. Sign a blank return", "quiz slide 4"),
   ("'Same-day cash advance.' A pitch to get you in the door, not a reason to choose them.", "3. Cash advance pitch", "quiz slide 5"),
   ("'No PTIN needed.' Paid preparers must have a PTIN and sign your return.", "4. No PTIN", "quiz slide 6"),
  ], "Use a preparer with a PTIN who signs, or free IRS-certified help. How many did you get?", f"{MASCOT} holding a score card")),
 dict(date="2027-02-20", kind="tiktok", look="face cam", topic="refund-theft texts", pillar=P_TAX,
  title="The 'boss' who emails HR for every W-2, played out",
  hook="1 email from the 'CEO' to payroll can hand every employee's W-2 to a tax thief.",
  thumb="Your boss didn't ask for the W-2s",
  hashtags=["w2", "smallbusiness", "payroll", "phishing", "scamdecoded"],
  description="The W-2 phishing email aimed at payroll and HR, and the one-call rule that stops it.",
  caption="Work in payroll, HR or a small business office? The 'boss' email asking for every employee's W-2 is a classic "
          "tax season scam. Call the boss first.",
  sources=[W2, SCAMS], claims=["Scammers impersonate executives to request employees' Forms W-2 from payroll staff (IRS)",
                               "Stolen W-2 data is used to file fraudulent returns (IRS)"],
  original_element="Dhruv on camera reading the 'CEO' email from his phone, then the one-call rule. " + VOICE,
  segments=[
   ("Hook", "One email to payroll from the CEO can hand every employee's W-2 to a tax thief. Here's how it reads.",
    "1 email to payroll", "Dhruv on camera holding a phone"),
   ("The email", "Hi, quick favour. I need copies of all employee W-2s for a meeting with the accountant. PDF is fine. "
                 "I'm traveling, so email is best. Thanks.", "'All employee W-2s, by email'", "an email on a phone screen"),
   ("Pause", "Pause. If this landed in your inbox at work, what would you do first?", "Pause: what do you do?", QUIZ),
   ("The tells", "The sender's address is one letter off, or a personal email. The request is urgent and unusual. And "
                 "the boss can't be reached, so you can't check. And it wants PDFs by email, the least safe way to send them.", "Odd address · urgent · unreachable",
    "an email address with one letter circled"),
   ("Why it matters", "W-2s hold names, Social Security numbers and wages. That's everything a thief needs to file fake "
                      "returns for your whole company, before your coworkers file their own.", "W-2s = SSNs + wages",
    "a stack of W-2s blowing away"),
   ("The rule", "One call. Before sending any W-2s, call the person who asked, on a number you already have. Not the "
                "number in the email. Payroll teams can make it a written rule: W-2s never go out by email. If it was already sent, tell your manager and the IRS right away.",
    "Call before you send", f"{MASCOT} holding a phone"),
  ]),
 dict(date="2027-02-27", kind="short", look="data chart", topic="IRS impersonation", pillar=P_TAX,
  title="$920 million to fake agents: 3 things the IRS won't do",
  hook="About $920 million. That's what people reported losing to fake government agents in 2025.",
  thumb="$920M to fake agents",
  hashtags=["irs", "governmentimposter", "taxseason", "ftcdata", "scamdecoded"],
  description="FTC data on government impersonation losses, and three things the real IRS won't do.",
  caption="People told the FTC they lost about $920 million to government impersonators in 2025. Fake IRS agents are a "
          "big part of that. 3 things the real IRS won't do.",
  sources=[IMPOSTER, KNOW, DIRTY], claims=["People reported losing about $920 million to government impersonators in 2025 (FTC, Jun 2026)",
                                           "The IRS generally contacts people by mail first and doesn't demand immediate payment by phone or threaten arrest (IRS)"],
  original_element="An FTC data chart beat drawn like originality/out/charts (bars: imposters $3.5B, business ~$1B, government ~$920M).",
  segments=[
   ("Hook", "About nine hundred twenty million dollars. That's what people told the FTC they lost to fake government "
            "agents in twenty twenty-five.", "~$920M to fake government agents", "an FTC-style bar chart, government bar in amber"),
   ("Won't 1", "The real IRS won't call, text or email out of the blue demanding payment. It usually starts with a letter.",
    "1. No surprise payment demands", "an envelope with the IRS eagle simplified"),
   ("Won't 2", "It won't threaten arrest, and it won't ask for gift cards, crypto or a wire.", "2. No arrest threats, no gift cards",
    "a gift card with a red X"),
   ("Won't 3", "And it won't ask you to read your details over the phone to a caller. Hang up, and check your account at "
               "I R S dot gov.", "3. Check your account yourself", f"{MASCOT} hanging up a phone"),
  ]),
 dict(date="2027-03-13", kind="carousel", look="comparison", topic="fake preparers", pillar=P_TAX,
  title="Free tax help that's real: VITA, TCE and IRS Free File vs the search ad",
  hook="3 free, IRS-backed ways to get your taxes done, and 1 search ad that charges for the same thing.",
  thumb="Free tax help: 3 real options",
  hashtags=["freetaxprep", "vita", "taxseason", "irsfreefile", "scamdecoded"],
  description="Free IRS-backed tax help, compared with paid lookalikes in search ads.",
  caption="Before you pay a stranger to do your taxes, check the free options:\n1. VITA (IRS-certified volunteers)\n"
          "2. TCE (focus on people 60 and over)\n3. IRS Free File\nStart from IRS.gov, not a search ad.",
  sources=[FREE_PREP, FREE_FILE], claims=["VITA and TCE offer free tax return preparation for qualifying taxpayers (IRS)",
                                          "TCE focuses on taxpayers 60 and older (IRS)", "IRS Free File offers free guided tax software for eligible taxpayers (IRS)"],
  original_element="Slide 4 is Dhruv's screen recording still of IRS.gov's free tax prep site locator.",
  segments=slides("Free tax help: 3 real options", [
   ("VITA: IRS-certified volunteers prepare basic returns for free for people who qualify, often by income.", "1. VITA", "a volunteer at a desk"),
   ("TCE: free tax help focused on people 60 and over, with volunteers who know pensions and retirement questions.", "2. TCE", "an older adult with a volunteer"),
   ("IRS Free File: free guided tax software for eligible taxpayers, reached from IRS.gov.", "3. IRS Free File", "a laptop with a free tag"),
   ("The search ad: a lookalike 'free file' site that charges at the end, or a preparer who takes a cut. Start at IRS.gov.", "Skip: the search ad", "a search result with a price tag"),
  ], "Save this, and send it to someone who pays to file every year.", f"{MASCOT} holding a 1040")),
 dict(date="2027-03-20", kind="tiktok", look="illustrated", topic="IP PIN", pillar=P_ID,
  title="'Dependent already claimed': your child's SSN, what now?",
  hook="1 rejection message, 'dependent already claimed', can mean someone used your child's SSN.",
  thumb="Someone claimed your kid?",
  hashtags=["taxseason", "dependents", "identitytheft", "ippin", "scamdecoded"],
  description="What to do when your e-filed return is rejected because a dependent was already claimed, and how an IP PIN helps.",
  caption="Your return bounces: the dependent's SSN was already used. It might be a family mix-up, or identity theft. "
          "Here's what to do, and how a child's IP PIN helps.",
  sources=[REJECTS, IPPIN_FAQ, IDT], claims=["E-filed returns are rejected when a dependent's SSN was already used on another return (IRS)",
                                             "Dependents can have their own IP PIN, entered on the e-filed return (IRS)"],
  original_element="Illustrated explainer with Dhruv's own voice. " + VOICE,
  segments=[
   ("Hook", "One rejection message: dependent already claimed. It can mean someone used your child's Social Security "
            "number. Here's what to do.", "'Dependent already claimed'", f"{MASCOT} holding a rejected form"),
   ("Two causes", "Sometimes it's a mix-up: an ex, a grandparent or another relative claimed the same child. Sometimes it's a "
                  "stranger who bought or stole the number. Either way, the e-filed return won't go through until it's sorted.", "Mix-up or identity theft", "two paths from one form"),
   ("Pause", "Pause. Before you panic, who else could have claimed your child this year? Think about it.",
    "Pause: who else could it be?", QUIZ),
   ("If it's family", "Talk to them first. Only one person can claim a child, and the IRS has tie-breaker rules. If you're "
                      "the one entitled to claim, you can file on paper and the IRS will sort it out by mail.",
    "Family? Talk first. Then paper-file.", "two adults talking with a form"),
   ("If it's a stranger", "If nobody you know claimed them, treat it as identity theft. Follow the IRS identity theft "
                          "steps, and file on paper with your correct information.", "A stranger? Identity theft steps.",
    "a shield with a child icon"),
   ("Next year", "Then lock it. A dependent can have their own IP PIN, and an e-filed return claiming them is rejected "
                 "without it. Get one for each child in January. It's free, and a new one comes every year, just like yours.", "Get your child an IP PIN", "a 6-digit code on a small shield"),
  ]),
 dict(date="2027-03-27", kind="short", look="screen recording", topic="IP PIN", pillar=P_ID,
  title="Getting an IP PIN takes about 10 minutes. Here's the screen.",
  hook="10 minutes on IRS.gov, and nobody can e-file a federal return with your Social Security number.",
  thumb="IP PIN in 10 minutes",
  hashtags=["ippin", "taxseason", "identitytheft", "irs", "scamdecoded"],
  description="A screen walkthrough of where to get an IRS IP PIN.",
  caption="Most of the work is verifying who you are. After that, the IP PIN is on your profile page, and a new one shows "
          "up every January.",
  sources=[IPPIN, IPPIN_FAQ], claims=["You can get an IP PIN through your IRS Online Account or the IRS app (IRS)",
                                      "A new IP PIN is generated each year (IRS)"],
  original_element="Dhruv screen-records signing in to his own IRS Online Account and finding the IP PIN section (personal details blurred).",
  segments=[
   ("Hook", "Ten minutes on I R S dot gov, and nobody can e-file a federal return with your Social Security number.",
    "10 minutes. 1 PIN.", "Dhruv's screen: IRS.gov home page"),
   ("Step 1", "Go to I R S dot gov, typed yourself, and sign in to your online account. If it's your first time, you'll "
              "verify your identity. That's most of the ten minutes.", "Sign in at IRS.gov", "Dhruv's screen: sign-in page"),
   ("Step 2", "Open your profile and find the identity protection PIN section. Choose to get one, and save it somewhere safe.",
    "Profile → IP PIN", "Dhruv's screen: profile page, PIN blurred"),
   ("Step 3", "Give it only to the preparer filing your federal return. A new one shows up every January.",
    "Only your preparer. New each January.", f"{MASCOT} holding a calendar"),
  ]),
 dict(date="2027-04-03", kind="carousel", look="data", topic="refund-theft texts", pillar=P_TAX,
  title="5 ways criminals steal a tax refund, and the 1 lock that blocks most of them",
  hook="5 ways a tax refund gets stolen, and 1 lock that blocks most of them.",
  thumb="Refund theft: 5 ways",
  hashtags=["taxrefund", "identitytheft", "ippin", "taxseason", "scamdecoded"],
  description="Five ways tax refunds get stolen, and why an IP PIN is the lock.",
  caption="Refund thieves need your SSN and enough details to file before you do. Here's how they get them, and the "
          "lock that stops a fake federal return.",
  sources=[DIRTY, W2, IPPIN, IDT], claims=["Scammers use phishing texts, W-2 theft and fake account 'helpers' to get taxpayer data (IRS)",
                                           "An IP PIN prevents others from e-filing a federal return with your SSN (IRS)"],
  original_element="Data-style carousel: the IRS figure of 600+ social media impersonators reported in fiscal year 2025 on slide 1.",
  segments=slides("Refund theft: 5 ways", [
   ("Fake IRS texts and emails with links or QR codes that ask for your SSN and bank details.", "1. Phishing texts", "a phone with a QR code"),
   ("Fake IRS accounts on social media. The IRS says it reported more than 600 impersonators in fiscal year 2025.", "2. Fake IRS social accounts", "a profile with a fake badge"),
   ("A 'helper' who sets up your IRS online account and keeps access.", "3. Account 'helpers'", "a key changing hands"),
   ("Stolen W-2s from a payroll email scam at work.", "4. Stolen W-2s", "a stack of W-2s"),
   ("A preparer who changes the refund's bank account to their own.", "5. A crooked preparer", "a refund arrow bending away"),
  ], "The lock: an IP PIN. Get one at IRS.gov, and check refunds only at IRS.gov/refunds.", f"{MASCOT} with a padlock")),
 dict(date="2027-04-10", kind="tiktok", look="quiz pause", topic="IRS impersonation", pillar=P_TAX,
  title="IRS letter or fake? 3 checks before you call",
  hook="3 checks tell you if an IRS letter is real, 5 days before Tax Day.",
  thumb="Real IRS letter?",
  hashtags=["irs", "irsletter", "taxday", "taxscam", "scamdecoded"],
  description="Three checks for an IRS letter before you call any number on it.",
  caption="The IRS usually contacts you by mail first, so scammers fake letters too. 3 checks before you call.",
  sources=[KNOW, SCAMS, DIRTY], claims=["The IRS generally contacts people by mail first (IRS)",
                                        "You can confirm what you owe and see notices in your IRS Online Account (IRS)"],
  original_element="Quiz pause format with a real-looking (fictional, marked) letter on screen. " + VOICE,
  segments=[
   ("Hook", "Three checks tell you if an IRS letter is real. Tax Day is in five days, so scammers are mailing too.",
    "Real or fake? 3 checks.", "a letter on a kitchen table"),
   ("Pause", "Pause. This letter says you owe four thousand dollars and must call within ten days. What would you check "
             "first?", "Pause: what do you check?", QUIZ),
   ("Check 1", "One: the notice number, usually CP or LTR and a number, in the corner. Look it up on I R S dot gov to see "
               "what that notice is really about. If the number doesn't match a real notice, that's your answer.", "1. Look up the notice number", "a corner of a letter, number circled"),
   ("Check 2", "Two: sign in to your IRS online account. If you really owe, the balance is there. If there's no balance, don't pay the letter.",
    "2. Check your online account", "a laptop with the account page"),
   ("Check 3", "Three: if you need to call, use the number on I R S dot gov, not the one in the letter. Fake letters copy "
               "everything except the phone number.", "3. Call the number on IRS.gov", "two phone numbers, one crossed out"),
   ("The payment", "And the real IRS takes payment through I R S dot gov or a check to the U.S. Treasury. Never gift cards, "
                   "crypto or a payment app to a person. Already paid? Call your bank right away and report it at report fraud dot F T C dot gov.", "Pay only through IRS.gov", f"{MASCOT} with a check"),
  ]),
]


def item(p):
    fmt = "carousel" if p["kind"] == "carousel" else "short"
    platforms = {"short": ["instagram", "youtube"], "tiktok": ["tiktok"], "carousel": ["instagram"]}[p["kind"]]
    time = {"short": "12:00", "tiktok": "18:00", "carousel": "19:30"}[p["kind"]]
    cta = CTA_TIKTOK if p["kind"] == "tiktok" else CTA
    return {"format": fmt, "pillar": p["pillar"], "platforms": platforms, "post_on": f"{p['date']} {time}",
            "topic": p["topic"], "look": p["look"], "original_element": p["original_element"],
            "idea_angle": f"Tax season 2027 pack: {p['topic']}. {p['description']}",
            "script": {"title": p["title"], "hook": p["hook"], "segments": [seg(*r) for r in p["segments"]], "cta": cta,
                       "caption": p["caption"] + "\n\n" + CHECKER + "\n\n" + cta, "hashtags": p["hashtags"],
                       "description": p["description"], "thumbnail_text": p["thumb"], "sources": p["sources"],
                       "claims_to_verify": p["claims"]}}


def plan(items):
    import datetime as dt
    rows = ["# Scam Decoded: tax season scam pack, Sat Jan 16 – Sat Apr 10 2027", "",
            "12 Saturday posts on IRS impersonation, fake preparers, refund-theft texts and the IP PIN. Saturdays are the "
            "one slot the weekly plans leave open (Sat Mar 6 is already taken, so it's skipped). Times America/New_York. "
            "Nothing has been posted.", "",
            "The weekly plans already cover arrest calls, refund trackers, extensions, tax relief and filing for free; this "
            "pack takes new angles (online account 'helpers', QR-code texts, W-2 phishing, dependents, the IP PIN screen).", "",
            "| # | Date | Time | Where | Format | Look | Topic | Title |", "|---|---|---|---|---|---|---|---|"]
    for n, (p, i) in enumerate(zip(POSTS, items)):
        d = dt.date.fromisoformat(p["date"])
        where = {"short": "Reels + Shorts", "tiktok": "TikTok", "carousel": "Instagram"}[p["kind"]]
        fmt = {"short": "Short", "tiktok": "TikTok minute cut", "carousel": "Carousel"}[p["kind"]]
        rows.append(f"| #{n} | {d.strftime('%a %b')} {d.day} | {i['post_on'][11:]} | {where} | {fmt} | {p['look']} | "
                    f"{p['topic']} | {p['title']} |")
    rows += ["", "Original elements Dhruv records: the IRS.gov sign-in page (#0), his IP PIN screen with the PIN blurred "
             "(#1, #9), the free tax prep locator (#7), and his own voice on every TikTok cut. Walkthrough w8 and quiz q8 "
             "are rendered in originality/out/.", "",
             "Before posting: verify each item's `claims_to_verify` against its `sources` that week (IRS pages change "
             "every filing season), and check the IRS Dirty Dozen list for 2027 when it comes out."]
    return "\n".join(rows) + "\n"


def main():
    items = [item(p) for p in POSTS]
    root = HERE.parent.parent
    videos = [i for i in items if i["format"] == "short"]
    assert all(a["look"] != b["look"] for a, b in zip(videos, videos[1:]))
    for i in items:
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        if i["platforms"] == ["tiktok"]:
            assert 165 <= w <= 230 and any(s["heading"] == "Pause" for s in i["script"]["segments"]), (i["script"]["title"], w)
        elif i["format"] == "short":
            assert 60 <= w <= 120, (i["script"]["title"], w)
        for s in i["script"]["segments"]:
            assert len(s["on_screen_text"].split()) <= 12, s["on_screen_text"]
    (root / "tax-2027.json").write_text(json.dumps(items, indent=1, ensure_ascii=False) + "\n")
    (root / "POSTING_PLAN_TAX_2027.md").write_text(plan(items))
    for n, i in enumerate(items):
        w = sum(len(s["narration"].split()) for s in i["script"]["segments"])
        hook = i["script"]["hook"]
        assert any(ch.isdigit() for ch in hook.split(".")[0][:60]), hook
        print(n, i["post_on"], i["format"], i["platforms"][0], i["look"], w, i["script"]["title"][:60])


if __name__ == "__main__":
    main()
