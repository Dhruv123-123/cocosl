// Scam Shield app (scam-checker/app/): the "Is this a scam?" checklist, the red-flag quiz and the
// report-it directory. Pure data and functions, no DOM, no network. Works offline.

// ---------- Checklist ----------
// Yes/no questions about what happened. Weights: 3 = a sign on its own, 2 = strong, 1 = worth noticing.
export const QUESTIONS = [
  { id: 'pay', w: 3, q: 'Did they ask you to pay with gift cards, crypto, a wire transfer, Zelle, Cash App or a payment app?', why: 'Real companies and agencies don\'t ask for gift cards or crypto, and money sent through these is very hard to get back.' },
  { id: 'code', w: 3, q: 'Did they ask for a code sent to your phone, a password or your PIN?', why: 'A one-time code is the key to your account. Nobody real ever needs you to read it out.' },
  { id: 'remote', w: 3, q: 'Did they ask you to install an app or let them control your computer or phone?', why: 'Remote access lets them see your bank logins and move money while you watch.' },
  { id: 'move', w: 3, q: 'Did they tell you to move your money to keep it "safe"?', why: 'Banks and the government never ask you to move money to a "safe account". That account is theirs.' },
  { id: 'secret', w: 2, q: 'Did they tell you to keep it secret, or not to tell your bank or family?', why: 'Secrecy is how scammers stop someone from warning you.' },
  { id: 'urgent', w: 2, q: 'Is there a deadline, a threat or a countdown (arrest, account closed, fine, "today only")?', why: 'Pressure is designed to stop you from checking.' },
  { id: 'firstContact', w: 1, q: 'Did they contact you first, out of the blue?', why: 'Most scams start with a message or call you didn\'t ask for.' },
  { id: 'link', w: 2, q: 'Does it want you to tap a link to log in, pay or "verify" something?', why: 'Fake login pages look exactly like the real ones. Go to the app or type the address yourself.' },
  { id: 'tooGood', w: 2, q: 'Is it a prize, refund, job, investment or deal that seems too good to be true?', why: 'Big wins you never entered and easy money are the oldest bait there is.' },
  { id: 'feeFirst', w: 2, q: 'Do you have to pay a fee, tax or deposit first to get money, a prize or a job?', why: 'Paying to get paid is the shape of an advance-fee scam.' },
  { id: 'identity', w: 1, q: 'Do they claim to be from the government, your bank, a delivery company, tech support or a family member?', why: 'Scammers pretend to be someone you trust. Hang up and call them back on a number you look up yourself.' },
  { id: 'romance', w: 2, q: 'Is it someone you met online, never in person, who now needs money or wants to talk about investing?', why: 'Romance and "pig butchering" scams build trust for weeks before asking for money.' },
];

export function verdict(answers) {
  const yes = QUESTIONS.filter((x) => answers[x.id] === true);
  const answered = QUESTIONS.filter((x) => answers[x.id] === true || answers[x.id] === false).length;
  const score = yes.reduce((t, x) => t + x.w, 0);
  const hard = yes.some((x) => x.w === 3);
  const level = hard || score >= 4 ? 'high' : score >= 2 ? 'medium' : answered ? 'low' : 'none';
  return { level, score, flags: yes, answered };
}

export const VERDICT_TEXT = {
  high: { title: 'Very likely a scam. Stop here.', steps: ['Don\'t pay, don\'t send codes and don\'t tap the link.', 'Hang up or stop replying. You don\'t owe them an explanation.', 'If you already paid or shared anything, call your bank\'s fraud line now, using the number on the back of your card.', 'Report it (see Report it) so it can be stopped.'] },
  medium: { title: 'Some red flags. Check before you do anything.', steps: ['Don\'t use any link or phone number they gave you.', 'Look up the company or agency yourself and contact them directly.', 'Talk it over with someone you trust before paying or sharing anything.'] },
  low: { title: 'No big red flags from your answers.', steps: ['Scams change fast, so still contact the company through its own app or website if money or logins are involved.', 'If anything changes, like a new request to pay, run the checklist again.'] },
  none: { title: 'Answer the questions above.', steps: [] },
};

// ---------- Red-flag quiz ----------
// Each item is a short message. answer: true = scam. flags: what gives it away (or why it's fine).
export const QUIZ = [
  { m: 'USPS: Your package is on hold due to an incomplete address. Update within 24 hours: usps-redelivery-help.com', a: true, flags: 'USPS doesn\'t text links to update an address, and the real site is usps.com. The 24-hour deadline is pressure.' },
  { m: 'Your Chase card ending 4417 was used for $49.99 at Target. Reply STOP if this wasn\'t you. To review, open the Chase app.', a: false, flags: 'No link, no request for a code, and it sends you to the app you already have. Still, check in the app, not by replying.' },
  { m: 'Hi Mom, I dropped my phone in the toilet. This is my new number. Can you help me pay a bill today? I\'ll pay you back.', a: true, flags: 'A "new number" plus an urgent money request is the family impersonation scam. Call your child on their old number.' },
  { m: 'This is the IRS. A warrant has been issued for your arrest for unpaid taxes. Call 1-888-555-0193 within 2 hours to settle with gift cards.', a: true, flags: 'The IRS contacts you by mail first and never takes gift cards or threatens arrest by phone.' },
  { m: 'Your Netflix payment failed. Update your billing details to avoid suspension: netf1ix-billing.com/login', a: true, flags: 'The "1" in place of an "l" is a look-alike address. Open the Netflix app to check your billing.' },
  { m: 'Your verification code is 482913. Don\'t share this code with anyone. Amazon will never ask you for it.', a: false, flags: 'An automatic code you asked for is normal. The scam is when someone then calls and asks you to read it out.' },
  { m: 'Congratulations! You were selected for a remote job paying $45/hour. No interview needed. Text our hiring manager on WhatsApp to start today.', a: true, flags: 'No interview, high pay and a move to WhatsApp are classic job-scam signs. They usually ask for a "starter kit" payment next.' },
  { m: 'Microsoft Security Alert: Your computer is infected. Do not turn it off. Call support at 1-877-555-0144 immediately.', a: true, flags: 'Microsoft doesn\'t put phone numbers in pop-ups. Close the browser; a real problem doesn\'t need a stranger on the phone.' },
  { m: 'Reminder from Dr. Patel\'s office: your appointment is Tue Nov 18 at 2:30 PM. Reply C to confirm or call the office to reschedule.', a: false, flags: 'An expected reminder with no link, payment or code. If in doubt, call the number you already have for the office.' },
  { m: 'Toll Services: You have an unpaid toll balance of $6.99. Pay now to avoid a $50 late fee: ezpass-tollpay.info', a: true, flags: 'Unpaid toll texts are one of the most common scams. Toll agencies use their own .gov or .com sites, which you can look up yourself.' },
];

export function quizScore(picks) {
  let right = 0;
  QUIZ.forEach((x, i) => { if (picks[i] === x.a) right += 1; });
  return { right, total: QUIZ.length, done: QUIZ.every((_, i) => typeof picks[i] === 'boolean') };
}

// ---------- Report it ----------
// Federal and national places to report, by what happened. Checked 2026-11-07; re-check each year.
export const PLACES = {
  ftc: { name: 'FTC: ReportFraud.ftc.gov', url: 'https://reportfraud.ftc.gov/', what: 'Most scams, fraud and bad business practices. Your report helps law enforcement spot patterns.' },
  idtheft: { name: 'IdentityTheft.gov', url: 'https://www.identitytheft.gov/', what: 'Someone used your name, SSN or accounts. Gets you a personal recovery plan.' },
  ic3: { name: 'FBI Internet Crime Complaint Center (IC3)', url: 'https://www.ic3.gov/', what: 'Online and crypto scams, romance and investment scams, ransomware and business email scams.' },
  spam: { name: 'Forward scam texts to 7726 (SPAM)', url: 'sms:7726', what: 'Free on all major US carriers. Helps your carrier block the sender.' },
  fcc: { name: 'FCC consumer complaints', url: 'https://consumercomplaints.fcc.gov/', what: 'Robocalls, spoofed caller ID and unwanted calls or texts.' },
  dnc: { name: 'National Do Not Call Registry', url: 'https://www.donotcall.gov/', what: 'Register your number and report unwanted sales calls.' },
  uspis: { name: 'U.S. Postal Inspection Service', url: 'https://www.uspis.gov/report', what: 'Fake USPS texts and emails, and mail fraud.' },
  tigta: { name: 'TIGTA (IRS impersonation)', url: 'https://www.tigta.gov/reportcrime-misconduct', what: 'Calls, texts or letters pretending to be the IRS.' },
  ssa: { name: 'Social Security Office of the Inspector General', url: 'https://oig.ssa.gov/report/', what: 'Calls pretending to be Social Security, or misuse of your SSN.' },
  cfpb: { name: 'CFPB complaint', url: 'https://www.consumerfinance.gov/complaint/', what: 'Problems with a bank, card, lender or money transfer company, including a refused fraud claim.' },
  apwg: { name: 'Forward phishing emails to reportphishing@apwg.org', url: 'mailto:reportphishing@apwg.org', what: 'Helps get fake websites taken down.' },
  elder: { name: 'National Elder Fraud Hotline: 1-833-372-8311', url: 'tel:+18333728311', what: 'Free help for people 60 and over, from the U.S. Department of Justice.' },
};

export const SITUATIONS = [
  { id: 'paid', label: 'I already paid or sent money', first: 'Call your bank or payment app\'s fraud line now. The faster you call, the better the chance of stopping the payment.', places: ['ftc', 'ic3', 'cfpb'] },
  { id: 'identity', label: 'I shared my SSN, password or a code', first: 'Change the password and turn on two-step login. Freeze your credit at Equifax, Experian and TransUnion; it\'s free.', places: ['idtheft', 'ftc'] },
  { id: 'text', label: 'A scam text', first: 'Don\'t reply or tap the link. Forward it to 7726, then delete it.', places: ['spam', 'ftc', 'fcc'] },
  { id: 'call', label: 'A scam call or robocall', first: 'Hang up. Call back only on a number you look up yourself.', places: ['ftc', 'fcc', 'dnc'] },
  { id: 'email', label: 'A phishing email', first: 'Don\'t open attachments or links. Use your email\'s "Report phishing" button.', places: ['apwg', 'ftc'] },
  { id: 'online', label: 'An online, crypto, romance or investment scam', first: 'Stop sending money, even to "unlock" a withdrawal. Save the chats and wallet addresses.', places: ['ic3', 'ftc'] },
  { id: 'govt', label: 'Someone pretending to be the IRS or Social Security', first: 'The IRS and Social Security don\'t threaten arrest or take gift cards. Hang up.', places: ['tigta', 'ssa', 'ftc'] },
  { id: 'mail', label: 'A fake USPS or delivery message', first: 'Track packages only at usps.com or the carrier\'s app.', places: ['uspis', 'spam', 'ftc'] },
  { id: 'older', label: 'It happened to someone 60 or older', first: 'Call the National Elder Fraud Hotline for free, one-on-one help.', places: ['elder', 'ftc', 'ic3'] },
];

// State and territory attorney general (or consumer protection) complaint pages, copied from the National
// Association of Attorneys General's directory on 2026-11-07. Pages move: the directory link is always shown too.
export const AG_DIRECTORY = 'https://www.naag.org/our-work/center-for-consumer-protection/consumer-file-a-complaint/';
export const STATE_AGS = [
  ['AL', 'Alabama', 'https://www.alabamaag.gov/consumer-complaint/'],
  ['AK', 'Alaska', 'https://www.law.alaska.gov/pdf/consumer/FORM_complaint.pdf'],
  ['AS', 'American Samoa', 'https://www.americansamoa.gov/contactus'],
  ['AZ', 'Arizona', 'https://consumer-complaint.azag.gov/publiccomplaint/begin.aspx'],
  ['AR', 'Arkansas', 'https://arkansasag.gov/file-a-complaint/'],
  ['CA', 'California', 'https://www.dca.ca.gov/consumers/complaints/consumer.shtml'],
  ['CO', 'Colorado', 'https://www.stopfraudcolorado.gov/about-consumer-protection/report-fraud.html'],
  ['CT', 'Connecticut', 'https://www.dir.ct.gov/ag/complaint/'],
  ['DE', 'Delaware', 'https://attorneygeneral.delaware.gov/fraud/cpu/complaint/'],
  ['DC', 'District of Columbia', 'https://dcforms.dc.gov/webform/oag-consumer-complaint-form'],
  ['FL', 'Florida', 'https://www.myfloridalegal.com/pages.nsf/Main/E3EB45228E9229DD85257B05006E32EC'],
  ['GA', 'Georgia', 'https://consumer.georgia.gov/consumer-services/filing-a-complaint'],
  ['GU', 'Guam', 'https://guamattorneygeneral.org/consumer-protection/'],
  ['HI', 'Hawaii', 'https://web2.dcca.hawaii.gov/ocpcomplaint/'],
  ['ID', 'Idaho', 'https://www.ag.idaho.gov/office-resources/online-forms/?form=File%20a%20Complaint&complaint=Consumer%20Complaint'],
  ['IL', 'Illinois', 'https://illinoisattorneygeneral.gov/File-A-Complaint/'],
  ['IN', 'Indiana', 'https://www.in.gov/attorneygeneral/2426.htm'],
  ['IA', 'Iowa', 'https://www.iowaattorneygeneral.gov/for-consumers/file-a-consumer-complaint/'],
  ['KS', 'Kansas', 'https://www.ag.ks.gov/file-a-complaint'],
  ['KY', 'Kentucky', 'https://www.ag.ky.gov/Resources/Consumer-Resources/Consumers/Pages/Consumer-Complaints.aspx'],
  ['LA', 'Louisiana', 'https://www.ag.state.la.us/Page/ConsumerDispute'],
  ['ME', 'Maine', 'https://www.maine.gov/ag/consumer/complaints/complaint_form.shtml'],
  ['MD', 'Maryland', 'https://www.marylandattorneygeneral.gov/pages/cpd/complaint.aspx'],
  ['MA', 'Massachusetts', 'https://www.mass.gov/how-to/file-a-consumer-complaint'],
  ['MI', 'Michigan', 'https://www.michigan.gov/ag/complaints'],
  ['MN', 'Minnesota', 'https://www.ag.state.mn.us/Office/Complaint.asp'],
  ['MS', 'Mississippi', 'https://www.ago.state.ms.us/divisions/consumer-protection/consumer-complaint-form/'],
  ['MO', 'Missouri', 'https://ago.mo.gov/get-help/programs-services-from-a-z/consumer-complaints/'],
  ['MT', 'Montana', 'https://www.dojmt.gov/office-of-consumer-protection/consumer-complaints/'],
  ['NE', 'Nebraska', 'https://protectthegoodlife.nebraska.gov/file-report'],
  ['NV', 'Nevada', 'https://ag.nv.gov/Complaints/CSU_Complaints___FAQ/'],
  ['NH', 'New Hampshire', 'https://www.doj.nh.gov/consumer/complaints/index.htm'],
  ['NJ', 'New Jersey', 'https://www.njconsumeraffairs.gov/Pages/File-a-Complaint-old.aspx'],
  ['NM', 'New Mexico', 'https://www.nmag.gov/file-a-complaint.aspx'],
  ['NY', 'New York', 'https://ag.ny.gov/consumer-frauds/Filing-a-Consumer-Complaint'],
  ['NC', 'North Carolina', 'https://ncdoj.gov/file-a-complaint/consumer-complaint/'],
  ['ND', 'North Dakota', 'https://attorneygeneral.nd.gov/consumer-resources/consumer-complaints'],
  ['MP', 'Northern Mariana Islands', 'https://www.cnmioag.org/contact-us/'],
  ['OH', 'Ohio', 'https://www.ohioattorneygeneral.gov/Individuals-and-Families/Consumers/File-A-Complaint.aspx'],
  ['OK', 'Oklahoma', 'https://www.oag.ok.gov/consumer-protection-unit'],
  ['OR', 'Oregon', 'https://justice.oregon.gov/consumercomplaints/OnlineComplaints/OnlineComplaintForm/en'],
  ['PA', 'Pennsylvania', 'https://www.attorneygeneral.gov/submit-a-complaint/consumer-complaint/'],
  ['PR', 'Puerto Rico', 'https://www.justicia.pr.gov/querellas-2/'],
  ['RI', 'Rhode Island', 'https://riag.ri.gov/forms/consumer-complaint'],
  ['SC', 'South Carolina', 'https://eservice.llr.sc.gov/Complaints/'],
  ['SD', 'South Dakota', 'https://consumer.sd.gov/complaintform.aspx'],
  ['TN', 'Tennessee', 'https://www.tn.gov/attorneygeneral/working-for-tennessee/file-a-consumer-complaint.html'],
  ['TX', 'Texas', 'https://www.texasattorneygeneral.gov/cpd/file-a-consumer-complaint'],
  ['VI', 'U.S. Virgin Islands', 'https://usvidoj.com/contact-us/'],
  ['UT', 'Utah', 'https://attorneygeneral.utah.gov/contact-us/'],
  ['VT', 'Vermont', 'https://ago.vermont.gov/consumer-assistance-program-complaint-form'],
  ['VA', 'Virginia', 'https://www.oag.state.va.us/consumer-protection/index.php/file-a-complaint'],
  ['WA', 'Washington', 'https://www.atg.wa.gov/file-complaint'],
  ['WV', 'West Virginia', 'https://ago.wv.gov/about/Divisions/Pages/Consumer-Protection-and-Anti-Trust-Division-.aspx'],
  ['WI', 'Wisconsin', 'https://www.doj.state.wi.us/dls/consumer-protection/how-file-consumer-complaint'],
  ['WY', 'Wyoming', 'https://sites.google.com/a/wyo.gov/wy-ag/law-office-division/consumer-protection-and-antitrust-unit/consumer-complaints'],
];
export const agFor = (code) => STATE_AGS.find((s) => s[0] === code) || null;
