// Medical bill letters. A guided form fills in four letters people can send to a hospital or
// provider billing office:
//   itemized   ask for an itemized bill (the first step before paying anything large)
//   dispute    point out specific billing errors and ask for a corrected bill
//   assistance ask for the financial assistance (charity care) policy and an application
//   surprise   say a bill looks like it's covered by the No Surprises Act
// Nothing is sent anywhere: the letters are built in the browser for the person to read, edit,
// print and mail themselves. This is general information, not legal or medical advice.

export const LETTERS = {
  itemized: 'Ask for an itemized bill',
  dispute: 'Dispute billing errors',
  assistance: 'Ask for financial assistance',
  surprise: 'Surprise bill (No Surprises Act)',
};

export const ERRORS = {
  duplicate: 'The same charge appears more than once',
  notReceived: 'Charges for care, tests or supplies I did not receive',
  cancelled: 'Charges for a test or procedure that was cancelled',
  dates: 'Charges on dates I was not there',
  roomDays: 'More room or bed days than nights I stayed (the discharge day is usually not billed)',
  quantity: 'Quantities that look wrong (for example, medication doses)',
  insurance: 'The bill was not sent to my insurance, or was sent to the wrong plan',
  paid: 'A payment I already made is not shown',
  codes: 'Charges without a clear description or billing code',
};

export const SURPRISE = {
  emergency: 'Emergency care billed at out-of-network rates',
  facility: 'An out-of-network doctor at an in-network hospital or surgery center (for example, anesthesia, radiology, pathology or an assistant surgeon)',
  estimate: 'I\'m uninsured or paid myself, and the bill is at least $400 more than my Good Faith Estimate',
};

const REQUIRED = { patient: 'your name', provider: 'the hospital or provider\'s name', account: 'the account number from the bill' };

/** Clean the form values. Throws an Error naming the first missing field. */
export function normalize(v = {}) {
  const s = (k, max = 200) => String(v[k] ?? '').replace(/\s+/g, ' ').trim().slice(0, max);
  const out = {
    patient: s('patient', 80), address: s('address'), phone: s('phone', 40), email: s('email', 80),
    provider: s('provider', 100), providerAddress: s('providerAddress'), account: s('account', 60),
    serviceDates: s('serviceDates', 80), amount: s('amount', 20), insurer: s('insurer', 80), claim: s('claim', 60),
    details: String(v.details ?? '').trim().slice(0, 1500), household: s('household', 3), income: s('income', 20),
    estimate: s('estimate', 20), billDate: s('billDate', 40),
    errors: (Array.isArray(v.errors) ? v.errors : []).filter((e) => ERRORS[e]),
    surprise: SURPRISE[v.surprise] ? v.surprise : 'emergency',
    date: s('date', 40) || new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
  };
  for (const [k, label] of Object.entries(REQUIRED)) if (!out[k]) throw new Error(`Add ${label}.`);
  return out;
}

const money = (a) => (a && !/^\$/.test(a) ? `$${a}` : a);

function header(v, subject) {
  const from = [v.patient, v.address, v.phone, v.email].filter(Boolean);
  const to = ['Billing Department', v.provider, v.providerAddress].filter(Boolean);
  const ref = [`Patient: ${v.patient}`, `Account number: ${v.account}`];
  if (v.serviceDates) ref.push(`Date(s) of service: ${v.serviceDates}`);
  if (v.amount) ref.push(`Amount billed: ${money(v.amount)}`);
  if (v.insurer) ref.push(`Insurance: ${v.insurer}${v.claim ? `, claim number ${v.claim}` : ''}`);
  return [...from, '', v.date, '', ...to, '', `Re: ${subject}`, ...ref, '', 'Dear Billing Department,', ''];
}

function footer(v, extra = []) {
  return ['', ...extra,
    'Please send your reply to the address above' + (v.email ? ` or to ${v.email}` : '') + '. Thank you for your help.', '',
    'Sincerely,', '', '', v.patient];
}

const HOLD = 'While this is being reviewed, please place my account on hold so it is not sent to collections or reported to the credit bureaus, and let me know in writing that you have done so.';

export function itemizedLetter(v) {
  return [...header(v, 'Request for an itemized bill'),
    'I am writing to ask for a complete itemized bill for the account above before I pay it.',
    '',
    'Please include, for every charge:',
    '- the date of service',
    '- a plain description of the service, supply or medication',
    '- the billing code (CPT, HCPCS or revenue code) and quantity',
    '- the charge for each line',
    '- any insurance payments, adjustments and payments I have already made',
    '',
    'Please also send a copy of the explanation of benefits or claim details you received from my insurance, if any, and tell me whether you offer financial assistance or payment plans.',
    '',
    HOLD,
    ...footer(v)].join('\n');
}

export function disputeLetter(v) {
  if (!v.errors.length && !v.details) throw new Error('Tick at least one problem or describe what looks wrong.');
  return [...header(v, 'Billing errors on my account'),
    'I have reviewed my bill and believe it contains errors. I am asking you to review the charges below and send me a corrected bill.',
    '',
    ...v.errors.map((e) => `- ${ERRORS[e]}`),
    ...(v.details ? ['', 'Details:', v.details] : []),
    '',
    'If you believe a charge is correct, please explain it and send the supporting records (for example, the itemized bill with billing codes, and the record showing the service was provided).',
    ...(v.errors.includes('insurance') ? ['', `Please submit the claim to my insurance${v.insurer ? ` (${v.insurer})` : ''} before billing me. I can send my insurance card details if needed.`] : []),
    '',
    HOLD,
    ...footer(v)].join('\n');
}

export function assistanceLetter(v) {
  const facts = [];
  if (v.household) facts.push(`My household has ${v.household} ${v.household === '1' ? 'person' : 'people'}`);
  if (v.income) facts.push(`our total yearly income is about ${money(v.income)}`);
  return [...header(v, 'Request for financial assistance'),
    'I am writing to ask for financial assistance (sometimes called charity care) with the bill for the account above.',
    ...(facts.length ? ['', `${facts.join(', and ')}. Paying this bill in full would be a hardship for us.`] : ['', 'Paying this bill in full would be a hardship for me.']),
    '',
    'Please send me:',
    '- your financial assistance policy and a plain-language summary of it',
    '- the application form and a list of the documents you need',
    '- the discount I may qualify for, and whether it can be applied to past bills on my account',
    '',
    'I understand that nonprofit hospitals are required under federal rules to have a written financial assistance policy and to accept applications for a period after the first bill. Please consider this letter the start of my application.',
    '',
    HOLD,
    ...footer(v, ['If I don\'t qualify, please tell me about any payment plans without interest.', ''])].join('\n');
}

export function surpriseLetter(v) {
  const body = {
    emergency: [
      'I received emergency care, and I have been billed at out-of-network rates. I believe this bill is covered by the federal No Surprises Act, which generally limits what I can be charged for emergency care to my in-network cost-sharing (copay, coinsurance and deductible).',
    ],
    facility: [
      'I had care at an in-network facility, and I have been billed by an out-of-network provider for care I did not choose. I believe this bill is covered by the federal No Surprises Act, which generally limits what I can be charged in this situation to my in-network cost-sharing, unless I gave written consent in advance under the law\'s notice-and-consent rules. I do not believe I gave that consent.',
    ],
    estimate: [
      `I was uninsured or paid for this care myself, and I received a Good Faith Estimate${v.estimate ? ` of ${money(v.estimate)}` : ''} before my care. The bill${v.amount ? ` of ${money(v.amount)}` : ''} is at least $400 more than that estimate.`,
      '',
      `Please review the bill and correct it to match the estimate. If we can't resolve this, I understand I can start the federal patient-provider dispute resolution process within 120 days of the date on the bill${v.billDate ? ` (${v.billDate})` : ''}, and I intend to do so.`,
    ],
  }[v.surprise];
  return [...header(v, 'Bill I believe is protected under the No Surprises Act'),
    ...body,
    '',
    v.surprise === 'estimate'
      ? 'Please send me a corrected bill, or an explanation of each charge that is above the estimate.'
      : `Please re-process this bill so I am charged only my in-network cost-sharing${v.insurer ? `, as determined by my plan (${v.insurer})` : ''}, and send me a corrected bill. If you believe the protections don't apply, please explain why in writing.`,
    '',
    HOLD,
    ...footer(v, ['I may also contact the federal No Surprises Help Desk (1-800-985-3059) about this bill.', ''])].join('\n');
}

const BUILDERS = { itemized: itemizedLetter, dispute: disputeLetter, assistance: assistanceLetter, surprise: surpriseLetter };

export function buildLetter(kind, values) {
  const b = BUILDERS[kind];
  if (!b) throw new Error('Pick a letter.');
  return b(normalize(values));
}

/** Which letters to send, in order, for the answers to the three quick questions. */
export function suggest({ haveItemized = false, cantAfford = false, surprise = false } = {}) {
  const out = [];
  if (!haveItemized) out.push('itemized');
  else out.push('dispute');
  if (surprise) out.push('surprise');
  if (cantAfford) out.push('assistance');
  return out;
}
