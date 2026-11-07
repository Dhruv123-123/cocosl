// Family security setup: a step-by-step checklist for the whole household, with progress saved
// in the browser. Steps are per household (the safe word), per adult (credit freezes, 2-step
// verification, phone PIN) or per child (child credit freezes). It never asks for or stores
// passwords, PINs or the safe word itself: only which steps are done.

export const BUREAUS = {
  equifax: { name: 'Equifax', url: 'https://www.equifax.com/personal/credit-report-services/credit-freeze/', phone: '1-888-298-0045' },
  experian: { name: 'Experian', url: 'https://www.experian.com/freeze/center.html', phone: '1-888-397-3742' },
  transunion: { name: 'TransUnion', url: 'https://www.transunion.com/credit-freeze', phone: '1-888-909-8872' },
};

// [id, scope, minutes, title, why, how[]]
export const STEPS = [
  ['safe-word', 'household', 10, 'Pick a family safe word',
    'Scammers can clone a voice from a short video and call pretending to be a family member in trouble. A word only your family knows settles it in seconds.',
    ['Choose a word or short phrase that isn\'t on social media (not a pet\'s or street name).', 'Tell it to everyone in person or on a call, not by text or email.', 'Agree: if anyone calls asking for money or help urgently, ask for the word. No word, hang up and call them back on their usual number.', 'Don\'t write it in this app. We only save that you\'ve done it.']],
  ['scam-talk', 'household', 15, 'Talk through the 3 rules',
    'Most scams fall apart against three habits. Older relatives are targeted most, so include them.',
    ['Nobody legitimate asks for gift cards, crypto, wire transfers or payment apps to fix a problem.', 'Never share a code you didn\'t ask for: a "verification code" request is how accounts get taken over.', 'Hang up and call back on a number you look up yourself, never one in the message.']],
  ['freeze-equifax', 'adult', 10, 'Freeze credit at Equifax',
    'A freeze stops anyone opening new credit in your name. It\'s free, doesn\'t hurt your score, and you can lift it for a day when you apply for something.',
    ['Create an account or call, and choose "freeze" (also called a security freeze).', 'Save the login or PIN in a password manager or somewhere safe at home.']],
  ['freeze-experian', 'adult', 10, 'Freeze credit at Experian', 'You need all three: lenders may check any one of them.',
    ['Create an account or call, and choose "freeze".', 'Save the login or PIN somewhere safe.']],
  ['freeze-transunion', 'adult', 10, 'Freeze credit at TransUnion', 'The third bureau. After this one, new credit in your name is blocked.',
    ['Create an account or call, and choose "freeze".', 'Save the login or PIN somewhere safe.']],
  ['email-2fa', 'adult', 10, 'Turn on 2-step verification for your main email',
    'Your email resets every other password, so it\'s the account to protect first.',
    ['Open your email\'s security settings and turn on 2-step verification.', 'Use an authenticator app or a passkey if offered. Text-message codes are better than nothing.', 'Save the backup codes somewhere safe.']],
  ['bank-alerts', 'adult', 10, 'Turn on bank alerts and 2-step login',
    'Alerts for every payment or transfer mean you see fraud within minutes, not at the end of the month.',
    ['In your bank\'s app, turn on alerts for transfers, card payments and new payees.', 'Turn on 2-step verification for the login.']],
  ['phone-pin', 'adult', 15, 'Lock your phone number',
    'In a SIM swap or port-out scam, someone moves your number to their phone and receives your login codes.',
    ['In your carrier\'s app or account settings, set an account PIN or passcode.', 'Turn on the number-transfer lock if your carrier has one (names vary: number lock, port-out protection, account lock).', 'Don\'t reuse your bank PIN.']],
  ['child-freeze', 'child', 30, 'Request a credit freeze for your child',
    'Children\'s identities are attractive because nobody checks their credit for years. A parent can request a freeze for a child at each bureau.',
    ['Each bureau has a page for freezing a minor\'s credit. You\'ll usually need copies of the child\'s birth certificate and Social Security card plus your ID and proof of address, sent by mail or upload.', 'Do it at all three bureaus.', 'Keep the confirmation letters with the child\'s documents.']],
];

export const OPTIONAL = [
  ['IRS Identity Protection PIN', 'Stops someone filing a tax return in your name.', 'https://www.irs.gov/identity-theft-fraud-scams/get-an-identity-protection-pin'],
  ['my Social Security account', 'Create it before a scammer does.', 'https://www.ssa.gov/myaccount/'],
  ['Report fraud', 'If something has already happened: identity theft recovery plan.', 'https://www.identitytheft.gov/'],
];

export const emptyFamily = () => ({ members: [], done: {} });

export function loadFamily(raw) {
  try { const d = JSON.parse(raw); if (d && Array.isArray(d.members) && d.done && typeof d.done === 'object') return d; } catch { /* fall through */ }
  return emptyFamily();
}

export function addMember(data, { name, kind = 'adult' }) {
  name = String(name || '').trim().slice(0, 40);
  if (!name) throw new Error('Add a first name or nickname.');
  if (data.members.length >= 12) throw new Error('That\'s the most this checklist handles.');
  const member = { id: Math.random().toString(36).slice(2, 9), name, kind: kind === 'child' ? 'child' : 'adult' };
  data.members.push(member);
  return member;
}

export function removeMember(data, id) {
  data.members = data.members.filter((m) => m.id !== id);
  for (const k of Object.keys(data.done)) if (k.startsWith(`${id}:`)) delete data.done[k];
}

const keyFor = (memberId, stepId) => `${memberId || 'home'}:${stepId}`;

export function toggle(data, memberId, stepId, when = new Date().toISOString().slice(0, 10)) {
  const k = keyFor(memberId, stepId);
  if (data.done[k]) delete data.done[k];
  else data.done[k] = when;
  return Boolean(data.done[k]);
}

/** Every task for this household, in the order to do them, with done state. */
export function tasks(data) {
  const out = [];
  for (const [id, scope, minutes, title, why, how] of STEPS) {
    const who = scope === 'household' ? [null] : data.members.filter((m) => m.kind === scope);
    for (const m of who) {
      const k = keyFor(m?.id, id);
      out.push({ key: k, stepId: id, memberId: m?.id || null, member: m?.name || 'Whole family', scope, minutes, title, why, how, bureau: BUREAUS[id.replace('freeze-', '')] || null, done: data.done[k] || null });
    }
  }
  return out;
}

export function progress(data) {
  const all = tasks(data);
  const done = all.filter((t) => t.done).length;
  const byMember = [{ id: null, name: 'Whole family' }, ...data.members].map((m) => {
    const mine = all.filter((t) => t.memberId === (m.id ?? null));
    return { id: m.id ?? null, name: m.name, done: mine.filter((t) => t.done).length, total: mine.length };
  }).filter((m) => m.total);
  const next = all.find((t) => !t.done) || null;
  return {
    done, total: all.length, pct: all.length ? Math.round((done / all.length) * 100) : 0,
    minutesLeft: all.filter((t) => !t.done).reduce((s, t) => s + t.minutes, 0),
    byMember, next,
  };
}
