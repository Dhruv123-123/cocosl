// Debt collector letters, built in the browser for the person to read, edit, print and mail:
//   validation  dispute the debt and ask the collector to verify it (Fair Debt Collection
//               Practices Act and the CFPB's Regulation F). Best sent within the 30-day window
//               in the collector's validation notice.
//   cease       tell the collector to stop contacting you about the debt.
// General information, not legal advice. Neither letter admits the debt is owed.

export const LETTERS = {
  validation: 'Dispute it and ask them to prove it',
  cease: 'Tell them to stop contacting me',
};

export const LIMITS = {
  mailOnly: 'Contact me only by mail, not by phone, text or email.',
  noWork: 'Do not contact me at my workplace.',
  noThirdParty: 'Do not discuss this debt with my family, friends or employer.',
};

const REQUIRED = { name: 'your name', collector: 'the collector\'s name', reference: 'the account or reference number from their letter' };

export function normalize(v = {}) {
  const s = (k, max = 200) => String(v[k] ?? '').replace(/\s+/g, ' ').trim().slice(0, max);
  const out = {
    name: s('name', 80), address: s('address'), collector: s('collector', 100), collectorAddress: s('collectorAddress'),
    reference: s('reference', 60), creditor: s('creditor', 100), amount: s('amount', 20), noticeDate: s('noticeDate', 40),
    limits: (Array.isArray(v.limits) ? v.limits : []).filter((k) => LIMITS[k]),
    date: s('date', 40) || new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
  };
  for (const [k, label] of Object.entries(REQUIRED)) if (!out[k]) throw new Error(`Add ${label}.`);
  return out;
}

const money = (a) => (a && !/^\$/.test(a) ? `$${a}` : a);

function header(v, subject) {
  const lines = [v.name];
  if (v.address) lines.push(v.address);
  lines.push('', v.date, '', v.collector);
  if (v.collectorAddress) lines.push(v.collectorAddress);
  lines.push('', `Re: ${subject}`, `Your reference number: ${v.reference}`);
  if (v.creditor) lines.push(`Original creditor (as you stated): ${v.creditor}`);
  if (v.amount) lines.push(`Amount you say is owed: ${money(v.amount)}`);
  if (v.noticeDate) lines.push(`Date of your letter to me: ${v.noticeDate}`);
  lines.push('', 'To whom it may concern:', '');
  return lines;
}

const NOT_ADMITTED = 'This letter is not an acknowledgment that I owe this debt, and it is not a promise to pay.';
const close = (v) => ['', 'Sincerely,', '', '', v.name];

export function validationLetter(v) {
  return [...header(v, 'I dispute this debt and request validation'),
    'I am writing in response to your attempt to collect the debt referenced above. I dispute this debt. Under the Fair Debt Collection Practices Act and Regulation F, I request that you verify it and stop collection until you have sent me the verification.',
    '',
    'Please send me:',
    '- the name and address of the original creditor, and the account number with that creditor',
    '- an itemization of the amount: what was owed on the itemization date, and every interest charge, fee, payment and credit since then',
    '- a copy of the agreement or other document showing that I owe this debt, and that you own it or are allowed to collect it',
    '- the date of the last payment on the account',
    '',
    NOT_ADMITTED,
    'If you report this debt to a credit bureau, please report it as disputed.',
    ...(v.limits.length ? ['', ...v.limits.map((k) => LIMITS[k])] : []),
    ...close(v)].join('\n');
}

export function ceaseLetter(v) {
  return [...header(v, 'Stop contacting me about this debt'),
    'Under the Fair Debt Collection Practices Act, I am asking you to stop communicating with me about the debt referenced above.',
    '',
    'Do not call, text, email or write to me about this debt, except to tell me that you are ending your collection efforts or that you or the creditor intend to take a specific action that the law allows.',
    '',
    NOT_ADMITTED,
    ...close(v)].join('\n');
}

export function buildDebtLetter(kind, values) {
  const v = normalize(values);
  if (kind === 'validation') return validationLetter(v);
  if (kind === 'cease') return ceaseLetter(v);
  throw new Error('Pick a letter.');
}
