// Short-form video ad script generator for small product brands. No AI call, no server: it fills
// proven formats (the same ones in the studio's sample ads) with the brand's own facts, so it's free to
// run and never invents a claim. The lint flags wording that breaks the studio's house rules.

const clean = (s) => String(s ?? '').replace(/\s+/g, ' ').trim();
const cap = (s) => (s ? s[0].toUpperCase() + s.slice(1) : s);
const sentence = (s) => { const t = cap(clean(s)); return t && !/[.!?]$/.test(t) ? `${t}.` : t; };
// On-screen text has to be readable in a second: keep it to a few words.
export const overlay = (s, max = 28) => {
  const t = cap(clean(s).replace(/[.!?]+$/, ''));
  if (t.length <= max) return t;
  const cut = t.slice(0, max + 1).replace(/\s+\S*$/, '');
  return (cut || t.slice(0, max)).replace(/[,;:\s]+$/, '') + '…';
};

export const NICHES = {
  candles: { label: 'Candles & home scent', setting: 'on a side table in low evening light', action: 'a match lights the wick' },
  coffee: { label: 'Coffee, tea & food', setting: 'on a kitchen counter in morning light', action: 'coffee pours into a cup' },
  jewelry: { label: 'Jewelry & accessories', setting: 'on linen beside a gift box', action: 'a hand holds the piece up to the light' },
  'body-care': { label: 'Soap & body care', setting: 'on a bathroom shelf beside a folded towel', action: 'hands work up a lather' },
  home: { label: 'Home & kitchen', setting: 'in a tidy kitchen or living room', action: 'hands set it in place' },
  kids: { label: 'Toys & kids', setting: 'on a playroom rug', action: 'hands stack and arrange the pieces' },
  outdoor: { label: 'Outdoor, travel & bags', setting: 'packed by the front door', action: 'hands pack it and zip it shut' },
  fitness: { label: 'Fitness & sport', setting: 'on a gym bag in a bright room', action: 'it gets used, mid-workout' },
  pets: { label: 'Pets', setting: 'next to a dog or cat bed', action: 'a hand offers it to the pet' },
  other: { label: 'Something else', setting: 'in the place it gets used', action: 'hands use it' },
};

export const FORMATS = {
  'three-things': { label: '"3 things" explainer', best: 'Products with a story on the label: coffee, food, skincare ingredients' },
  sensory: { label: 'Sensory close-up', best: 'Candles, food, textures: anything that looks or sounds good up close' },
  'problem-solution': { label: 'Problem → solution', best: 'Products that fix an everyday annoyance' },
  'before-after': { label: 'Before / after', best: 'Organisers, cleaning, decor, plants, anything with a visible change' },
  demo: { label: '"Watch this" speed demo', best: 'Gadgets and tools that work fast on camera' },
  comparison: { label: 'Side-by-side comparison', best: 'Reusable or upgraded versions of something people already buy' },
  gift: { label: 'Gift angle', best: 'Jewelry, candles, anything bought as a present' },
  founder: { label: 'Founder story (your own voice)', best: 'Small makers. Must be the real founder speaking, never an AI presenter' },
};

export const LENGTHS = [15, 20, 30];
const PRESENTERS = { 'ai-presenter': 'AI presenter', 'ai-voice': 'AI voice', founder: 'Founder (real person)' };
// Shown top-left for the whole ad, so viewers know what's AI.
const LABELS = { 'ai-presenter': 'AI-generated presenter · Ad', 'ai-voice': 'AI-generated voice · Ad', founder: 'Ad' };

function normalize(input) {
  const facts = (input.facts || []).map(clean).filter(Boolean).slice(0, 3);
  const v = {
    brand: clean(input.brand), product: clean(input.product), niche: NICHES[input.niche] ? input.niche : 'other',
    price: clean(input.price), audience: clean(input.audience), problem: clean(input.problem), alternative: clean(input.alternative),
    cta: clean(input.cta) || 'Link below', format: FORMATS[input.format] ? input.format : 'three-things',
    length: LENGTHS.includes(Number(input.length)) ? Number(input.length) : 20,
    presenter: PRESENTERS[input.presenter] ? input.presenter : 'ai-voice', facts,
  };
  if (!v.brand) throw new RangeError('Add your brand name');
  if (!v.product) throw new RangeError('Add the product name');
  if (facts.length < 2) throw new RangeError('Add at least two true facts about the product (from your label or listing)');
  if (v.format === 'founder') v.presenter = 'founder';
  if (v.price && /^\d/.test(v.price)) v.price = `$${v.price}`;
  return v;
}

// Each format returns { hooks: [A, B, C], beats: [{ visual, voice, text }] } for everything after the hook.
const BUILD = {
  'three-things': (v, n) => ({
    hooks: [`Three things worth knowing about ${v.product}.`, `Before you buy ${v.niche === 'coffee' ? 'your next bag' : 'another one'}, check these three things.`, `${v.brand} in three facts.`],
    hookVisual: `Presenter or hands hold up ${v.product} and tap the label`,
    beats: v.facts.map((f, i) => ({ visual: `Close-up of the detail that shows: ${f}`, voice: `${['One', 'Two', 'Three'][i]}: ${f}.`, text: `${i + 1} · ${overlay(f, 24)}` })),
  }),
  sensory: (v, n) => ({
    hooks: ['Turn your sound on for this one.', `Watch ${v.product} up close.`, `A closer look at ${v.product}.`],
    hookVisual: `Extreme close-up: ${n.action}`,
    beats: [
      { visual: `Slow macro shot of the texture and detail`, voice: sentence(v.facts[0]), text: overlay(v.facts[0]) },
      { visual: `Slow pan across ${v.product}`, voice: sentence(v.facts[1]), text: overlay(v.facts[1]) },
      ...(v.facts[2] ? [{ visual: `${cap(v.product)} ${n.setting}`, voice: sentence(v.facts[2]), text: overlay(v.facts[2]) }] : []),
    ],
  }),
  'problem-solution': (v, n) => {
    const problem = v.problem || `the usual ${v.niche === 'other' ? 'hassle' : 'problem'}`;
    return {
      hooks: [`${cap(problem.replace(/[.?!]+$/, ''))}? Here's a fix.`, `If ${problem.replace(/[.?!]+$/, '')} drives you mad, watch this.`, `The fix for ${problem.replace(/[.?!]+$/, '')}.`],
      hookVisual: `Show the problem: ${problem}`,
      beats: [
        { visual: `Hands bring in ${v.product}`, voice: `This is ${v.product} from ${v.brand}.`, text: overlay(v.product) },
        ...v.facts.slice(0, 2).map((f) => ({ visual: `Show it solving the problem: ${f}`, voice: sentence(f), text: overlay(f) })),
      ],
    };
  },
  'before-after': (v, n) => ({
    hooks: ['Before… and after.', `Same ${v.niche === 'home' ? 'room' : 'spot'}, one change.`, `What ${v.product} does in ten seconds.`],
    hookVisual: `"Before" shot: ${v.problem || 'the space or item without the product'}`,
    beats: [
      { visual: `${cap(n.action)}, using ${v.product}`, voice: `Add ${v.product}.`, text: 'Before → after' },
      { visual: `"After" shot from the same angle`, voice: sentence(v.facts[0]), text: overlay(v.facts[0]) },
      { visual: `Close-up of the product`, voice: sentence(v.facts[1]), text: overlay(v.facts[1]) },
    ],
  }),
  demo: (v, n) => ({
    hooks: ['Watch this.', `${cap(v.product)}, in real time.`, `How fast is ${v.product}? Watch.`],
    hookVisual: `Mid-action, no intro: ${n.action}, using ${v.product}`,
    beats: [
      { visual: `Same action, wider shot, real speed (no speed-up unless labelled)`, voice: sentence(v.facts[0]), text: overlay(v.facts[0]) },
      { visual: `Result close-up`, voice: sentence(v.facts[1]), text: overlay(v.facts[1]) },
      ...(v.facts[2] ? [{ visual: `${cap(v.product)} ${n.setting}`, voice: sentence(v.facts[2]), text: overlay(v.facts[2]) }] : []),
    ],
  }),
  comparison: (v, n) => {
    const alt = v.alternative || 'the usual kind';
    return {
      hooks: [`${cap(alt)} vs ${v.product}.`, `Still using ${alt}? Look at this.`, `One swap: ${alt} for ${v.product}.`],
      hookVisual: `Split screen: ${alt} on the left, ${v.product} on the right`,
      beats: v.facts.map((f) => ({ visual: `Split screen, ${v.product} side highlighted: ${f}`, voice: sentence(f), text: overlay(f) })),
    };
  },
  gift: (v, n) => ({
    hooks: [`Still need a gift${v.audience ? ` for ${v.audience}` : ''}?`, `A gift that doesn't look last-minute.`, `Gift idea, under ${v.price || 'budget'}.`],
    hookVisual: `Hands untie a ribbon on a box`,
    beats: [
      { visual: `Lid lifts to reveal ${v.product}`, voice: `${cap(v.product)} from ${v.brand}.`, text: overlay(v.product) },
      ...v.facts.slice(0, 2).map((f) => ({ visual: `Close-up of the detail: ${f}`, voice: sentence(f), text: overlay(f) })),
    ],
  }),
  founder: (v, n) => ({
    hooks: [`I'm the person who makes ${v.product}.`, `Why I started ${v.brand}.`, `Here's how ${v.product} gets made.`],
    hookVisual: `Founder to camera in the workshop or studio (real person, own voice)`,
    beats: [
      { visual: `Hands making or packing ${v.product}`, voice: sentence(v.facts[0]), text: overlay(v.facts[0]) },
      { visual: `Close-up of the finished product`, voice: sentence(v.facts[1]), text: overlay(v.facts[1]) },
      ...(v.facts[2] ? [{ visual: `${cap(v.product)} ${n.setting}`, voice: sentence(v.facts[2]), text: overlay(v.facts[2]) }] : []),
    ],
  }),
};

// Split the ad's length into whole-second slots: 3s hook, the beats, then a closing card.
function timings(length, beatCount) {
  const hook = 3;
  const close = length >= 30 ? 5 : 4;
  const middle = length - hook - close;
  const each = Math.floor(middle / beatCount);
  const extra = middle - each * beatCount;
  const out = [[0, hook]];
  let t = hook;
  for (let i = 0; i < beatCount; i++) { const d = each + (i < extra ? 1 : 0); out.push([t, t + d]); t += d; }
  out.push([t, length]);
  return out;
}

/** Build a full script. Returns { title, format, length, presenter, label, rows, hooks, caption, shotList, notes, lint }. */
export function buildScript(input) {
  const v = normalize(input);
  const n = NICHES[v.niche];
  const b = BUILD[v.format](v, n);
  // Short ads can't fit many beats: about one beat per 4 seconds after the hook and close.
  const maxBeats = Math.max(2, Math.floor((v.length - 7) / 4));
  const beats = b.beats.slice(0, maxBeats);
  const close = {
    visual: `${cap(v.product)} ${n.setting}, end card with logo${v.price ? ' and price' : ''}`,
    voice: `${v.brand}. ${sentence(v.cta)}`,
    text: [v.brand, v.price].filter(Boolean).join(' · '),
  };
  const slots = timings(v.length, beats.length);
  const rows = [{ visual: `Hook A: ${b.hookVisual}`, voice: b.hooks[0], text: overlay(b.hooks[0], 30) }, ...beats, close]
    .map((r, i) => ({ time: `${slots[i][0]}–${slots[i][1]}s`, ...r }));
  const label = LABELS[v.presenter];
  const caption = `${cap(v.product)} from ${v.brand}. ${sentence(v.facts[0])}${v.price ? ` ${v.price}.` : ''} ${sentence(v.cta)}`.replace(/\s+/g, ' ').trim();
  const shotList = [b.hookVisual, ...beats.map((r) => r.visual), close.visual].map((s, i) => `${i + 1}. ${s}`);
  const notes = [
    'Every fact on screen must be true and come from your own label, listing or test results.',
    v.presenter === 'founder'
      ? 'Founder format: film the real founder in their own voice. Don\'t use an AI presenter or a cloned voice for this one.'
      : 'Presenter presents the product only. No "I use it / I love it / it changed my life" lines from an AI presenter.',
    'Format: 9:16 vertical, 1080×1920, burned-in captions, music low under the voice.',
    'Test all three hooks: same ad, swap only the first 3 seconds.',
  ];
  const lint = lintText([...v.facts, v.product, v.problem, v.alternative, v.cta, v.audience].join(' \n '));
  return { title: `${v.brand}: ${v.product}`, format: FORMATS[v.format].label, length: v.length, presenter: PRESENTERS[v.presenter], label, rows, hooks: b.hooks, caption, shotList, notes, lint };
}

// Wording that gets ads rejected or breaks the house rules (and often the FTC's rules on endorsements and claims).
const LINT = [
  [/\b(i|we)\s+(love|use|swear by|can'?t live without)\b|\bchanged my life\b|\bmy favou?rite\b/i, 'Sounds like a personal testimonial. An AI presenter can\'t give one; use a factual line instead.'],
  [/\b(\d(\.\d)?\s*stars?|five[- ]star|5\/5|rated #?1|best[- ]selling|bestseller)\b/i, 'Ratings or "best-selling" need proof you can show. Leave out unless you have it.'],
  [/\b(cure[sd]?|heal[sd]?|treat(s|ment)?|clinically|anti-?aging|detox|eczema|acne|anxiety|insomnia|weight loss|lose \d+)\b/i, 'Health or body-result claim. These need real evidence and are restricted on ad platforms.'],
  [/\b(guarantee[sd]?|100% (safe|natural|effective)|risk[- ]free|never (fails|breaks))\b/i, 'Absolute claims like "guaranteed" or "100% safe" need proof and get flagged.'],
  [/\b(best|number one|world'?s (best|first)|only one)\b|#1\b/i, '"Best" or "#1" is a claim you may be asked to back up. A specific fact usually sells better.'],
  [/\b(make|earn) \$?\d|\bpassive income\b|\bget rich\b/i, 'Income claims are restricted on every ad platform.'],
  [/\b(doctor|dermatologist|vet)[- ]?(approved|recommended)\b/i, 'Professional endorsements need a real, documented endorsement.'],
];

/** Flag risky wording. Returns [{ phrase, reason }], one per rule. */
export function lintText(text) {
  const out = [];
  for (const [re, reason] of LINT) {
    const m = re.exec(String(text || ''));
    if (m) out.push({ phrase: m[0], reason });
  }
  return out;
}

/** Plain-text version of a script, for copying into a doc or sending to an editor. */
export function scriptToText(s) {
  return [
    `${s.title}`,
    `${s.format} · ${s.length}s · ${s.presenter} · 9:16`,
    `Label on screen: ${s.label}`,
    '',
    ...s.rows.map((r) => `${r.time}\n  Visual: ${r.visual}\n  Voice: "${r.voice}"\n  On screen: ${r.text}`),
    '',
    'Hooks to test:',
    ...s.hooks.map((h, i) => `  ${'ABC'[i]}: "${h}"`),
    '',
    `Caption: ${s.caption}`,
    '',
    'Shot list:',
    ...s.shotList.map((x) => `  ${x}`),
    '',
    'Notes:',
    ...s.notes.map((x) => `  - ${x}`),
  ].join('\n');
}
