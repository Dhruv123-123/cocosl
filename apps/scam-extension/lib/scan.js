// GENERATED from scam-checker/ by scam-extension/build.mjs. Edit the original, then rebuild.
// Scam Shield message checker: rule-based red-flag detection for texts, emails and DMs.
// Runs entirely in the browser (nothing is uploaded) and under node for tests.
// It flags common scam patterns. It cannot prove a message is safe, and the UI says so.

// Official domains for brands scammers impersonate most. A link that names the brand
// but isn't on one of these domains is a strong red flag.
export const OFFICIAL_DOMAINS = {
  usps: ['usps.com', 'usps.gov'],
  ups: ['ups.com'],
  fedex: ['fedex.com'],
  dhl: ['dhl.com'],
  amazon: ['amazon.com', 'amazon.co.uk', 'amazon.ca', 'amazon.de', 'amazon.in', 'amazon.es', 'amazon.com.mx', 'amzn.to', 'a.co'],
  paypal: ['paypal.com', 'paypal.me'],
  apple: ['apple.com', 'icloud.com'],
  microsoft: ['microsoft.com', 'live.com', 'outlook.com', 'office.com'],
  netflix: ['netflix.com'],
  irs: ['irs.gov'],
  ssa: ['ssa.gov'],
  chase: ['chase.com'],
  wellsfargo: ['wellsfargo.com'],
  bankofamerica: ['bankofamerica.com'],
  coinbase: ['coinbase.com'],
  venmo: ['venmo.com'],
  zelle: ['zellepay.com'],
  cashapp: ['cash.app', 'cash.me', 'squareup.com'],
  ezpass: ['e-zpassny.com', 'ezpassnj.com', 'e-zpassiag.com', 'ezpassva.com', 'ezpassmd.com', 'paturnpike.com'],
  facebook: ['facebook.com', 'fb.com', 'meta.com'],
  instagram: ['instagram.com'],
  google: ['google.com', 'goo.gl', 'youtube.com', 'g.co'],
  walmart: ['walmart.com'],
  costco: ['costco.com'],
  dmv: ['.gov'],
};

const SHORTENERS = ['bit.ly', 'tinyurl.com', 't.co', 'ow.ly', 'is.gd', 'buff.ly', 'rebrand.ly', 'cutt.ly', 'shorturl.at', 'rb.gy', 't.ly', 'tiny.cc', 's.id', 'qrco.de', 'lnkd.in'];
const RISKY_TLDS = ['top', 'xyz', 'click', 'icu', 'live', 'shop', 'buzz', 'cyou', 'rest', 'sbs', 'cfd', 'monster', 'quest', 'bond', 'lol', 'vip', 'win', 'loan', 'work', 'support', 'help', 'info', 'online', 'site', 'store', 'fun', 'cc', 'tk', 'ml', 'ga', 'cf', 'gq', 'ru', 'cn'];

// Undo common look-alike swaps so "paypa1" and "amaz0n" match the real names.
const HOMOGLYPHS = { 0: 'o', 1: 'l', 3: 'e', 4: 'a', 5: 's', 7: 't', 8: 'b', '$': 's', '@': 'a', '|': 'l' };
export const deLeet = (s) => s.toLowerCase().replace(/rn/g, 'm').replace(/vv/g, 'w').replace(/[01345789$@|]/g, (c) => HOMOGLYPHS[c] || c);

// Text rules: [id, weight, label, advice, regexes...]. Weights are points toward a 0-100 score.
const RULES = [
  ['gift-card', 35, 'Asks for payment in gift cards', 'No real company, government agency or utility takes gift cards as payment. This is a scam.',
    /\b(gift ?cards?|itunes card|google play card|steam card|apple card code|tarjetas? de regalo)\b/i],
  ['crypto-payment', 25, 'Asks you to pay or "invest" with crypto', 'Requests to pay by crypto or crypto ATM are a top scam pattern. Legit agencies never ask for it.',
    /\b(bitcoin|btc|usdt|tether|crypto ?(atm|wallet|currency)?|ethereum|wallet address)\b/i],
  ['p2p-payment', 15, 'Wants payment through Zelle, Cash App, Venmo or a wire', 'These payments are like cash: once sent, they are very hard to get back. Only pay people you know in person.',
    /\b(zelle|cash ?app|venmo|wire transfer|western union|moneygram|money order)\b/i],
  ['code-request', 60, 'Asks you to share a verification code', 'Never read or forward a one-time code to anyone. It is how scammers take over your accounts.',
    /(?<!\b(not|n't|never|nunca|no)\s)\b(send|share|give|read|tell|forward|provide|confirm)\b[^.!?\n]{0,25}\b(code|otp|pin|passcode|c[oó]digo)\b/i,
    /\b(code|otp|c[oó]digo)\b[^.!?\n]{0,30}\b(sent|texted) (to )?you\b[^.!?\n]{0,40}\b(send|share|tell|read)\b/i],
  ['credentials', 25, 'Asks for a password, PIN, SSN or card number', 'Real companies never ask for your full password, PIN or Social Security number by text or email.',
    /\b(social security( number)?|ssn|full card number|card number|cvv|pin number|password|login details|bank details|routing number|n[uú]mero de seguro social)\b/i],
  ['urgency', 15, 'Pressure to act right now', 'Scammers rush you so you don\'t stop and check. A real problem will still be there after you call the official number.',
    /\b(urgent|immediately|right away|within (24|48|12) ?(hours|hrs)|final (notice|warning)|last chance|act now|pay now|act fast|expires? today|today only|asap|urgente|inmediatamente)\b/i, /\bpay\b[^.!?\n]{0,15}\b(now|today)\b/i],
  ['threat', 20, 'Threatens arrest, legal action, or a locked account', 'Government agencies don\'t threaten arrest by text, and banks don\'t close accounts over a single missed tap.',
    /\b(arrest|warrant|lawsuit|legal action|police|suspend(ed)?|locked|deactivat(ed|ion)|frozen|terminated|penalt(y|ies)|late fee|cuenta (suspendida|bloqueada))\b/i],
  ['prize', 25, 'You "won" something you never entered', 'You can\'t win a lottery or sweepstakes you didn\'t enter, and real prizes never require a fee.',
    /\b(you('ve| have)? won|winner|congratulations|claim your (prize|reward|gift)|lottery|sweepstakes|selected to receive|free (iphone|gift)|ganaste|premio)\b/i],
  ['delivery', 15, 'Package delivery problem with a fee or link', 'USPS, UPS and FedEx don\'t text you asking for a redelivery fee. Track packages in the carrier\'s own app or website.',
    /\b(package|parcel|shipment|delivery)\b[^.!?\n]{0,100}\b(on hold|held|failed|unable|pending|incomplete address|redeliver|fee|customs|cannot be delivered|could not be delivered|undeliverable)\b/i],
  ['toll', 25, 'Unpaid toll text', 'Unpaid-toll texts are one of the most common scams right now. Check your account only in your toll agency\'s official app or site.',
    /\b(unpaid|outstanding|overdue)\b[^.!?\n]{0,30}\b(toll|tolls|e-?z ?pass|sunpass|fastrak|toll ?bill)\b/i, /\b(e-?z ?pass|sunpass|fastrak|txtag|peach pass)\b/i],
  ['refund', 20, 'Unexpected refund or overpayment', 'Fake refunds and "overpayments" end with you sending money back. Check your account directly, not through the message.',
    /\b(refund|overpa(id|yment)|reimburse(ment)?|tax rebate|stimulus)\b/i],
  ['job', 30, 'Too-good-to-be-true job or task offer', 'Jobs that pay for "likes", reviews or simple tasks, or that ask you to pay first, are scams.',
    /\b(earn|make)\s*\$?\d{2,4}\s*(-|to)?\s*\$?\d*\s*(\/|per|a)\s*(day|hour|hr)\b/i,
    /\b(work from home|remote (job|position|opportunity)|part[- ]time (job|position)|hiring now|recruiter|task(s)? (job|online)|like (videos|posts)|reshipping|mystery shopper|data entry)\b/i],
  ['investment', 30, 'Guaranteed returns or an "investment opportunity"', 'Nobody can guarantee investment returns. "Mentors" who move you to a trading app are running a scam.',
    /\b(guaranteed (return|profit|income)|risk[- ]free (investment|profit)|double your (money|investment)|\d{2,3}% (return|profit)|trading (platform|signals|mentor)|investment opportunity|forex)\b/i],
  ['remote-access', 35, 'Asks you to install remote-access software', 'Scammers use AnyDesk, TeamViewer and similar apps to take over your computer and bank accounts.',
    /\b(anydesk|teamviewer|ultraviewer|remote ?desktop|screen ?share|logmein|quick ?assist)\b/i],
  ['tech-support', 20, 'Fake tech support or virus warning', 'Microsoft, Apple and antivirus companies don\'t call or text about viruses. Close the message and don\'t call the number.',
    /\b(virus|infected|malware|hacked|security alert|subscription (renewal|renewed)|auto-?renew(al|ed)?|geek squad|norton|mcafee)\b/i],
  ['wrong-number', 15, 'Friendly "wrong number" or stranger opener', 'A chatty wrong-number text that turns into friendship, then crypto investing, is a long con. Don\'t reply.',
    /^\s*(hi|hello|hey)[^.!?\n]{0,30}(is this|are you)\s+\w+\??/i, /\b(wrong number|we met at|my assistant (gave|saved)|sorry to bother)\b/i],
  ['reply-to-activate', 20, 'Tells you to reply so the link becomes clickable', 'Replying "Y" or "1" tells the scammer your number is live and unlocks their link. Don\'t reply.',
    /\breply\s+["']?(y|yes|1)["']?\b[^.!?\n]{0,80}\b(link|activate|reopen|click)\b/i, /\b(reopen|re-open) (this|the) (message|sms|text)\b/i],
  ['move-chat', 15, 'Wants to move the chat to WhatsApp, Telegram or Signal', 'Scammers move you off the platform so its fraud protection and reports can\'t reach them.',
    /\b(whats ?app|telegram|signal app|wechat|kik)\b/i],
  ['fraud-alert-callback', 20, 'A "fraud alert" that says an agent will call you', 'Fake fraud alerts set up a call from a "fraud agent" who talks you into moving money. Hang up and call the number on your card.',
    /\b(agent|specialist|representative|department|team) will (call|contact|reach out to) you\b/i, /\b(fraud (alert|department)|did you (attempt|authorize|authorise|make) (a|this))\b[^.!?\n]{0,80}\b(zelle|wire|transfer|payment)\b/i],
  ['ssn-suspended', 30, 'Says your Social Security number is suspended', 'Social Security numbers are never suspended. This line is used only by scammers.',
    /\b(social security number|ssn|n[uú]mero( de seguro social)?)\b[^.!?\n]{0,30}\b(suspended|suspendido|blocked|bloqueado|compromised|comprometido)\b/i],
  ['generic-greeting', 8, 'Generic greeting instead of your name', 'Companies you have an account with usually use your name.',
    /\b(dear (customer|user|client|member|account holder|valued)|estimado cliente)\b/i],
  ['verify-account', 15, 'Asks you to "verify" or "confirm" your account through a link', 'Go to the company\'s app or type its website yourself instead of using the link.',
    /\b(verify|confirm|update|validate|unlock|restore)\b[^.!?\n]{0,25}\b(your )?(account|identity|information|details|payment|billing|card)\b/i],
  ['secrecy', 20, 'Tells you to keep it secret or not tell your bank', 'Being told not to tell anyone, including your bank, is a classic sign of a scam.',
    /\b(don'?t|do not) (tell|inform|contact|mention|share (this|it))\b[^.!?\n]{0,30}\b(anyone|bank|family|police|teller)\b/i, /\b(keep (this|it) (confidential|secret|between us))\b/i],
  ['romance-money', 20, 'Someone you met online needs money', 'Never send money or crypto to someone you have only met online, however long you\'ve talked.',
    /\b(stuck|stranded|customs|hospital|emergency|plane ticket|visa)\b[^.!?\n]{0,60}\b(send|need|borrow|wire|help)\b[^.!?\n]{0,30}\b(money|\$\d+|funds|cash)\b/i],
  ['government', 15, 'Claims to be the IRS, Social Security, Medicare or another agency', 'The IRS and SSA contact you by mail first. They never demand payment by text, gift card or crypto.',
    /\b(irs|internal revenue|social security administration|ssa|medicare|dmv|department of motor vehicles|immigration|uscis|treasury department|hacienda)\b/i],
  ['money-amount', 5, 'Mentions a specific amount owed or offered', 'Check any balance by logging in yourself, not through the message.',
    /[$€£]\s?\d[\d,]*(\.\d{2})?|\b\d+(\.\d{2})?\s?(usd|dollars|d[oó]lares)\b/i],
];

// Spanish phrasing for the same rules (Dinero Simple / Scam Shield en español).
// Accents are optional because many scam texts drop them.
const ES_PATTERNS = {
  'gift-card': [/\btarjetas? (de )?regalo\b/i],
  'crypto-payment': [/\b(criptomonedas?|cajero (de )?bitcoin|billetera (digital|cripto))\b/i],
  'p2p-payment': [/\b(transferencia bancaria|giro|env[ií]o de dinero)\b/i],
  'code-request': [/(?<!\bno\s)\b(env[ií]e(me)?|enviar(me)?|comparta|compartir(me)?|d[ií]game|decir(me)?|darme|reenv[ií]e|proporcione|mande(me)?|mandar(me)?)\b[^.!?\n]{0,30}\bc[oó]digo\b/i],
  credentials: [/\b(contrase[nñ]a|n[uú]mero de (tarjeta|cuenta|seguro social)|clave|nip)\b/i],
  urgency: [/\b(urgente|inmediatamente|de inmediato|en (las pr[oó]ximas )?(12|24|48) horas|[uú]ltimo aviso|[uú]ltima oportunidad|hoy mismo|pague ahora|act[uú]e ya)\b/i],
  threat: [/\b(arresto|orden de (arresto|captura)|demanda|acci[oó]n legal|polic[ií]a|suspendid[ao]|bloquead[ao]|desactivad[ao]|multa|recargo|cargo por mora)\b/i],
  prize: [/\b(ganaste|ha ganado|has ganado|felicidades|felicitaciones|premio|sorteo|loter[ií]a|reclame su (premio|regalo))\b/i],
  delivery: [/\b(paquete|env[ií]o|entrega)\b[^.!?\n]{0,100}\b(retenido|pendiente|no (pudo|se pudo) (ser )?entregar|direcci[oó]n (incompleta|incorrecta)|tarifa|aduana|reprogramar)\b/i],
  toll: [/\b(peaje|peajes)\b[^.!?\n]{0,40}\b(pendiente|sin pagar|impago|vencido|saldo)\b/i, /\b(saldo|deuda|cargo) (pendiente )?de peaje\b/i],
  refund: [/\b(reembolso|devoluci[oó]n|pago en exceso)\b/i],
  job: [/\b(gane|ganar?|gana)\s*\$?\d{2,4}[^.!?\n]{0,20}\b(al d[ií]a|por d[ií]a|diarios|por hora)\b/i, /\b(trabajo desde casa|empleo remoto|medio tiempo|reclutador[a]?|tareas en l[ií]nea|dar me gusta)\b/i],
  investment: [/\b(rendimientos? garantizad[oa]s?|ganancias garantizadas|sin riesgo|duplica(r)? (tu|su) dinero|plataforma de (inversi[oó]n|trading)|oportunidad de inversi[oó]n)\b/i],
  'remote-access': [/\b(acceso remoto|escritorio remoto)\b/i],
  'tech-support': [/\b(virus|infectad[oa]|hackead[oa]|alerta de seguridad|renovaci[oó]n autom[aá]tica|suscripci[oó]n renovada)\b/i],
  'wrong-number': [/\b(n[uú]mero equivocado|perd[oó]n por (la )?molestia|mi asistente (guard[oó]|me dio))\b/i],
  'reply-to-activate': [/\bresponda\s+["']?(s|s[ií]|1|y)["']?\b[^.!?\n]{0,80}\b(enlace|activar|abrir)\b/i],
  'generic-greeting': [/\b(estimad[oa] (cliente|usuario|miembro))\b/i],
  'verify-account': [/\b(verifique|confirme|actualice|valide|desbloquee)\b[^.!?\n]{0,25}\b(su )?(cuenta|identidad|informaci[oó]n|datos|pago|tarjeta)\b/i],
  secrecy: [/\bno (le )?(diga|cuente|informe|comparta esto)\b[^.!?\n]{0,30}\b(nadie|banco|familia|polic[ií]a)\b/i],
  government: [/\b(seguro social|administraci[oó]n del seguro social|irs|servicio de impuestos internos|inmigraci[oó]n|uscis|medicare|hacienda|sat)\b/i],
  'move-chat': [/\b(whats ?app|telegram)\b/i],
  'fraud-alert-callback': [/\b(un )?(agente|representante|especialista) (le|te) (llamar[aá]|contactar[aá])\b/i, /\balerta de fraude\b/i],
};
for (const rule of RULES) if (ES_PATTERNS[rule[0]]) rule.push(...ES_PATTERNS[rule[0]]);

const BARE_TLDS = new Set(['com', 'net', 'org', 'gov', 'edu', 'us', 'io', 'co', 'me', 'app', 'biz', 'uk', 'ca', 'de', 'mx', 'es', 'in', 'au', 'ly', 'gl', 'to', 'link', 'page', 'xyz', ...RISKY_TLDS]);

const BRAND_WORDS = Object.keys(OFFICIAL_DOMAINS).concat(['wells fargo', 'bank of america', 'cash app', 'social security', 'e-zpass', 'ezpass']);
const brandKey = (w) => w.replace(/[\s-]/g, '').replace('socialsecurity', 'ssa');

/** Pull URLs and bare domains (usps-redelivery.top/pay) out of text. */
export function extractUrls(text) {
  const found = new Set();
  const re = /\b((?:https?:\/\/|hxxps?:\/\/|www\.)[^\s<>"')\]]+|(?:[a-z0-9-]+\.)+(?:[a-z]{2,24}|xn--[a-z0-9-]+)(?:\/[^\s<>"')\]]*)?)/gi;
  for (const m of text.matchAll(re)) {
    let u = m[1].replace(/[.,;:!?]+$/, '');
    // Skip email addresses (handled separately) and plain numbers like 4.99
    const before = text[m.index - 1];
    if (before === '@') continue;
    if (/^\d+(\.\d+)+$/.test(u)) continue;
    // Common non-domain words like "e.g" or file names
    if (/^(e\.g|i\.e|a\.m|p\.m)$/i.test(u)) continue;
    // Bare words like "now.Pay" only count as links when they end in a real top-level domain.
    if (!/^(https?|hxxps?):\/\/|^www\./i.test(u)) {
      const tld = u.split('/')[0].split('.').pop().toLowerCase();
      if (!BARE_TLDS.has(tld) && !tld.startsWith('xn--')) continue;
    }
    found.add(u);
  }
  return [...found];
}

export function parseHost(raw) {
  let s = raw.trim().replace(/^hxxp/i, 'http');
  if (!/^https?:\/\//i.test(s)) s = 'http://' + s;
  try {
    const u = new URL(s);
    return { host: u.hostname.toLowerCase(), protocol: u.protocol, hasAt: /@/.test(raw.split('/').slice(0, 3).join('/')), path: u.pathname };
  } catch {
    return null;
  }
}

const registrable = (host) => {
  const parts = host.split('.');
  const twoPartTlds = ['co.uk', 'com.mx', 'com.au', 'co.in', 'com.br'];
  const last2 = parts.slice(-2).join('.');
  return twoPartTlds.includes(last2) ? parts.slice(-3).join('.') : last2;
};

const isOfficialFor = (brand, host) =>
  (OFFICIAL_DOMAINS[brand] || []).some((d) => (d.startsWith('.') ? host.endsWith(d) : host === d || host.endsWith('.' + d)));

const isAnyOfficial = (host) => Object.keys(OFFICIAL_DOMAINS).some((b) => b !== 'dmv' && isOfficialFor(b, host));

/** Check one link. Returns the issues found and a points total. */
export function analyzeUrl(raw) {
  const parsed = parseHost(raw);
  if (!parsed) return { url: raw, host: null, issues: [], points: 0 };
  const { host, protocol, hasAt } = parsed;
  const issues = [];
  const add = (points, label, code, param = '') => issues.push({ points, label, code, param });
  const tld = host.split('.').pop();
  const reg = registrable(host);

  if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host)) add(30, 'Link goes to a raw IP address instead of a website name', 'ip');
  if (host.split('.').some((p) => p.startsWith('xn--'))) add(30, 'Link uses look-alike international characters (punycode)', 'punycode');
  if (SHORTENERS.includes(host)) add(15, 'Shortened link hides where it really goes', 'shortener');
  if (RISKY_TLDS.includes(tld)) add(15, `Uses a ".${tld}" address, common in scam links`, 'risky-tld', tld);
  if (hasAt) add(25, 'Link contains "@", which can hide the real destination', 'at-sign');
  if (protocol === 'http:' && /^(http|hxxp):/i.test(raw)) add(5, 'Link is not secure (http, not https)', 'http');
  if ((host.match(/-/g) || []).length >= 2) add(10, 'Web address has several hyphens, a common trick for fake sites', 'hyphens');
  if (host.split('.').length >= 5) add(10, 'Unusually long chain of subdomains', 'subdomains');

  const official = isAnyOfficial(host);
  if (!official) {
    const flat = deLeet(host.replace(reg, '') + reg);
    for (const brand of Object.keys(OFFICIAL_DOMAINS)) {
      if (brand === 'dmv' || brand.length < 3) continue;
      // Short names (ups, irs, dhl, ssa) must stand alone so "startups" or "first" don't match.
      const hit = brand.length <= 4 ? new RegExp(`(^|[^a-z])${brand}([^a-z]|$)`).test(flat) : flat.includes(brand);
      if (hit) {
        const leet = !host.includes(brand);
        add(leet ? 40 : 35, leet
          ? `Look-alike spelling of ${brand.toUpperCase()} in a web address that isn't theirs`
          : `Uses the name ${brand.toUpperCase()} but isn't an official ${brand.toUpperCase()} website`, leet ? 'lookalike' : 'brand-mismatch', brand.toUpperCase());
        break;
      }
    }
  }
  return { url: raw, host, official, issues, points: issues.reduce((s, i) => s + i.points, 0) };
}

function emailSenderIssues(sender) {
  const issues = [];
  const m = /@([a-z0-9.-]+)/i.exec(sender || '');
  if (!m) return issues;
  const domain = m[1].toLowerCase();
  const free = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'aol.com', 'icloud.com', 'proton.me', 'protonmail.com', 'gmx.com', 'mail.com'];
  const name = (sender.split('<')[0] || '').toLowerCase();
  for (const b of BRAND_WORDS) {
    const key = brandKey(b);
    if ((name.includes(b) || deLeet(domain).includes(key)) && OFFICIAL_DOMAINS[key] && !isOfficialFor(key, domain)) {
      issues.push({ points: 40, label: `Sender claims to be ${b.toUpperCase()} but writes from ${domain}`, code: 'sender-brand', param: `${b.toUpperCase()}|${domain}` });
      return issues;
    }
  }
  if (free.includes(domain) && /\b(support|security|billing|service|team|admin|bank|irs)\b/.test(name)) {
    issues.push({ points: 20, label: `A "company" writing from a free ${domain} address`, code: 'sender-free', param: domain });
  }
  return issues;
}

export const STEPS = {
  'dont-engage': "Don't click links, call numbers, or reply in the message.",
  'check-official': "To check, open the company's own app or type its web address yourself.",
  'change-password': 'If you already shared a code or password, change that password now and turn on two-factor login.',
  'call-bank': 'If you already paid, call your bank or card issuer right away, and the gift card company for gift cards.',
  disconnect: 'If someone accessed your computer, disconnect it from the internet and change passwords from a different device.',
  report: 'Report it: forward scam texts to 7726 (SPAM), and report fraud at ReportFraud.ftc.gov.',
  'not-proof': "We didn't find common red flags, but that doesn't prove it's safe. If it asks for money or info, check with the company directly.",
};

export const CATEGORIES = [
  ['toll', 'Unpaid toll scam'], ['delivery', 'Fake delivery notice'], ['government', 'Government impersonation'],
  ['remote-access', 'Tech support scam'], ['tech-support', 'Tech support or fake subscription scam'], ['fraud-alert-callback', 'Fake bank fraud alert'], ['investment', 'Investment / crypto scam'],
  ['job', 'Job or task scam'], ['prize', 'Prize or lottery scam'], ['wrong-number', 'Wrong-number / romance opener'],
  ['romance-money', 'Romance scam'], ['refund', 'Refund or overpayment scam'], ['code-request', 'Account takeover attempt'],
  ['gift-card', 'Gift card payment scam'], ['verify-account', 'Phishing (fake account alert)'],
];

// The scam guide for each category: English pages in scams/, Spanish pages in es/estafas/.
export const GUIDES = {
  toll: ['toll-text-scam', 'mensaje-peaje-sin-pagar'], delivery: ['usps-text-scam', 'mensaje-usps-falso'], government: ['irs-scam', 'estafa-irs'],
  'remote-access': ['geek-squad-renewal-scam', 'correo-falso-de-renovacion'], 'tech-support': ['geek-squad-renewal-scam', 'correo-falso-de-renovacion'],
  'fraud-alert-callback': ['bank-fraud-alert-scam', 'alerta-de-fraude-bancaria-falsa'], job: ['job-text-scam', 'estafa-de-empleo-por-mensaje'],
  prize: ['prize-scam', 'estafa-de-premios'], 'wrong-number': ['wrong-number-text-scam', 'mensaje-numero-equivocado'], 'romance-money': ['wrong-number-text-scam', 'mensaje-numero-equivocado'],
  investment: ['wrong-number-text-scam', 'mensaje-numero-equivocado'], 'code-request': ['verification-code-scam', 'estafa-codigo-de-verificacion'],
  refund: ['paypal-scam', 'estafa-paypal'], 'verify-account': ['paypal-scam', 'estafa-paypal'],
};
export const guideFor = (categoryId, lang = 'en') => {
  const g = GUIDES[categoryId];
  return g ? (lang === 'es' ? `estafas/${g[1]}/` : `scams/${g[0]}/`) : null;
};

/**
 * Analyze a message. Returns { score 0-100, level, signals[], links[], category, steps[] }.
 * options.sender: optional "Name <address>" or phone number of who sent it.
 */
export function analyzeMessage(text, { sender = '' } = {}) {
  const input = String(text || '').slice(0, 20000);
  const signals = [];
  for (const [id, weight, label, advice, ...patterns] of RULES) {
    for (const re of patterns) {
      const m = re.exec(input);
      if (m) { signals.push({ id, weight, label, advice, evidence: m[0].trim().slice(0, 80) }); break; }
    }
  }
  const links = extractUrls(input).slice(0, 20).map(analyzeUrl);
  const senderIssues = emailSenderIssues(sender);
  if (/^\+?\d[\d\s().-]{9,}$/.test(sender.trim()) && /\b(bank|irs|usps|ups|fedex|amazon|paypal|toll)\b/i.test(input) && sender.replace(/\D/g, '').length >= 11 && !sender.trim().startsWith('+1')) {
    senderIssues.push({ points: 15, label: 'A "company" texting from an international number', code: 'sender-intl' });
  }

  // Score: strongest signals count fully, extra ones count for less, so ten weak hints can't
  // outweigh one decisive one, and a single weak hint stays low.
  const parts = [...signals.map((s) => s.weight), ...links.map((l) => Math.min(l.points, 60)), ...senderIssues.map((s) => s.points)].sort((a, b) => b - a);
  let raw = 0;
  parts.forEach((p, i) => { raw += p * (i === 0 ? 1 : i === 1 ? 0.8 : i === 2 ? 0.6 : 0.4); });
  // A link plus pressure/payment is the classic smishing combo.
  const riskyLink = links.some((l) => l.points >= 15);
  if (riskyLink && signals.some((s) => ['urgency', 'threat', 'delivery', 'toll', 'verify-account', 'refund', 'prize'].includes(s.id))) raw += 10;
  // Known scam scripts: these pairs together are much stronger than either alone.
  const has = (id) => signals.some((s) => s.id === id);
  const COMBOS = [['investment', 'crypto-payment'], ['job', 'move-chat'], ['wrong-number', 'investment'], ['government', 'gift-card'], ['government', 'threat'], ['fraud-alert-callback', 'secrecy'], ['fraud-alert-callback', 'p2p-payment'], ['tech-support', 'remote-access'], ['romance-money', 'crypto-payment']];
  for (const [a, b] of COMBOS) if (has(a) && has(b)) raw += 15;
  const score = Math.max(0, Math.min(100, Math.round(raw)));
  const level = score >= 60 ? 'high' : score >= 30 ? 'medium' : 'low';

  const ids = new Set(signals.map((s) => s.id));
  const catHit = CATEGORIES.find(([id]) => ids.has(id)) || (links.some((l) => l.points >= 30) ? ['phishing-link', 'Phishing link'] : [null, null]);
  const [categoryId, category] = catHit;

  const stepIds = [];
  if (level !== 'low') stepIds.push('dont-engage');
  if (links.length) stepIds.push('check-official');
  if (ids.has('code-request') || ids.has('credentials')) stepIds.push('change-password');
  if (ids.has('gift-card') || ids.has('crypto-payment') || ids.has('p2p-payment')) stepIds.push('call-bank');
  if (ids.has('remote-access')) stepIds.push('disconnect');
  if (level !== 'low') stepIds.push('report');
  if (level === 'low') stepIds.push('not-proof');
  const steps = stepIds.map((id) => STEPS[id]);

  return { score, level, category, categoryId, stepIds, signals: signals.sort((a, b) => b.weight - a.weight), links, senderIssues, steps };
}
