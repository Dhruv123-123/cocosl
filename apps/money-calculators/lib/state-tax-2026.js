// State income tax on wages, tax year 2026 (rates in effect January 1, 2026). Update every January.
// No API calls: these are published tables, copied in by hand.
//
// Source for every rate, bracket, standard deduction and personal exemption below:
//   Tax Foundation, "State Individual Income Tax Rates and Brackets, 2026"
//   https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/
// Extra sources for the rules the table can't show:
//   Connecticut personal exemption phase-out: CT DRS, Form CT-1040 instructions (Table A)
//     https://portal.ct.gov/drs/individuals/individual-tax-page/personal-income-tax
//   Pennsylvania taxes employee 401(k) contributions: PA DOR, "Compensation" (PA-40 instructions)
//     https://www.revenue.pa.gov/FormsandPublications/PAPersonalIncomeTaxGuide/Pages/Compensation.aspx
//   Local (city or county) income taxes exist in these states, per the Tax Foundation table's footnote (a).
//
// Model (an estimate, not a tax return):
//   state taxable income = wages - pre-tax 401(k) (except PA) - pre-tax health - standard deduction - personal exemptions
//   tax = brackets applied to that, minus any exemption credits, never below zero.
// Left out on purpose: dependents, itemizing, local taxes, credits that depend on things we don't ask
// (Utah's taxpayer credit phases out with income, so it isn't applied; that slightly overstates Utah).

// Each bracket is [income above which the rate applies, rate %]. A first threshold above 0 means 0% below it.
// sd: standard deduction [single, married]. pe: personal exemption deduction [single, married].
// credit: exemption credit taken off the tax [single, married].
const same = (b) => ({ single: b, married: b });
export const STATES = {
  AL: { name: 'Alabama', single: [[0, 2], [500, 4], [3000, 5]], married: [[0, 2], [1000, 4], [6000, 5]], sd: [3000, 8500], pe: [1500, 3000], local: true },
  AK: { name: 'Alaska', none: true },
  AZ: { name: 'Arizona', ...same([[0, 2.5]]), sd: [8350, 16700] },
  AR: { name: 'Arkansas', ...same([[0, 2], [4600, 3.9]]), sd: [2470, 4940], credit: [29, 58] },
  CA: {
    name: 'California',
    single: [[0, 1], [11079, 2], [26264, 4], [41452, 6], [57542, 8], [72724, 9.3], [371479, 10.3], [445771, 11.3], [742953, 12.3], [1000000, 13.3]],
    married: [[0, 1], [22158, 2], [52528, 4], [82904, 6], [115084, 8], [145448, 9.3], [742958, 10.3], [891542, 11.3], [1000000, 12.3], [1485906, 13.3]],
    sd: [5540, 11080], credit: [153, 306], note: 'Paychecks in California also take out about 1.3% for State Disability Insurance (SDI), which is not included here.',
  },
  CO: { name: 'Colorado', ...same([[0, 4.4]]), sd: [16100, 32200] },
  CT: {
    name: 'Connecticut',
    single: [[0, 2], [10000, 4.5], [50000, 5.5], [100000, 6], [200000, 6.5], [250000, 6.9], [500000, 6.99]],
    married: [[0, 2], [20000, 4.5], [100000, 5.5], [200000, 6], [400000, 6.5], [500000, 6.9], [1000000, 6.99]],
    pe: [15000, 24000], pePhase: [30000, 48000],
    note: 'Connecticut also phases out its lower rates for higher earners, which this estimate does not include.',
  },
  DE: { name: 'Delaware', ...same([[2000, 2.2], [5000, 3.9], [10000, 4.8], [20000, 5.2], [25000, 5.55], [60000, 6.6]]), sd: [3250, 6500], credit: [110, 220] },
  FL: { name: 'Florida', none: true },
  GA: { name: 'Georgia', ...same([[0, 5.19]]), sd: [12000, 24000] },
  HI: {
    name: 'Hawaii',
    single: [[0, 1.4], [9600, 3.2], [14400, 5.5], [19200, 6.4], [24000, 6.8], [36000, 7.2], [48000, 7.6], [125000, 7.9], [175000, 8.25], [225000, 9], [275000, 10], [325000, 11]],
    married: [[0, 1.4], [19200, 3.2], [28800, 5.5], [38400, 6.4], [48000, 6.8], [72000, 7.2], [96000, 7.6], [250000, 7.9], [350000, 8.25], [450000, 9], [550000, 10], [650000, 11]],
    sd: [4400, 8800], pe: [1144, 2288],
  },
  ID: { name: 'Idaho', single: [[4811, 5.3]], married: [[9622, 5.3]], sd: [16100, 32200] },
  IL: { name: 'Illinois', ...same([[0, 4.95]]), pe: [2925, 5850] },
  IN: { name: 'Indiana', ...same([[0, 2.95]]), pe: [1000, 2000], local: true },
  IA: { name: 'Iowa', ...same([[0, 3.8]]), sd: [16100, 32200], credit: [40, 80], local: true },
  KS: { name: 'Kansas', single: [[0, 5.2], [23000, 5.58]], married: [[0, 5.2], [46000, 5.58]], sd: [3605, 8240], pe: [9160, 18320] },
  KY: { name: 'Kentucky', ...same([[0, 3.5]]), sd: [3360, 3360], local: true },
  LA: { name: 'Louisiana', ...same([[0, 3]]), sd: [12875, 25750] },
  ME: { name: 'Maine', single: [[0, 5.8], [27399, 6.75], [64849, 7.15]], married: [[0, 5.8], [54849, 6.75], [129749, 7.15]], sd: [8350, 16700], pe: [5300, 10600] },
  MD: {
    name: 'Maryland',
    single: [[0, 2], [1000, 3], [2000, 4], [3000, 4.75], [100000, 5], [125000, 5.25], [150000, 5.5], [250000, 5.75], [500000, 6.25], [1000000, 6.5]],
    married: [[0, 2], [1000, 3], [2000, 4], [3000, 4.75], [150000, 5], [175000, 5.25], [225000, 5.5], [300000, 5.75], [600000, 6.25], [1200000, 6.5]],
    sd: [3350, 6700], pe: [3200, 6400], local: true, note: 'Every Maryland county adds its own income tax, roughly 2.25% to 3.3%, which is not included here.',
  },
  MA: { name: 'Massachusetts', ...same([[0, 5], [1083150, 9]]), pe: [4400, 8800] },
  MI: { name: 'Michigan', ...same([[0, 4.25]]), pe: [5900, 11800], local: true },
  MN: { name: 'Minnesota', single: [[0, 5.35], [33310, 6.8], [109430, 7.85], [203150, 9.85]], married: [[0, 5.35], [48700, 6.8], [193480, 7.85], [337930, 9.85]], sd: [15300, 30600] },
  MS: { name: 'Mississippi', ...same([[10000, 4]]), sd: [2300, 4600], pe: [6000, 12000] },
  MO: { name: 'Missouri', ...same([[1348, 2], [2696, 2.5], [4044, 3], [5392, 3.5], [6740, 4], [8088, 4.5], [9436, 4.7]]), sd: [16100, 32200], local: true },
  MT: { name: 'Montana', single: [[0, 4.7], [47500, 5.65]], married: [[0, 4.7], [95000, 5.65]], sd: [16100, 32200] },
  NE: { name: 'Nebraska', single: [[0, 2.46], [4130, 3.51], [24760, 4.55]], married: [[0, 2.46], [8250, 3.51], [49530, 4.55]], sd: [8850, 17700], credit: [176, 352] },
  NV: { name: 'Nevada', none: true },
  NH: { name: 'New Hampshire', none: true },
  NJ: {
    name: 'New Jersey',
    single: [[0, 1.4], [20000, 1.75], [35000, 3.5], [40000, 5.53], [75000, 6.37], [500000, 8.97], [1000000, 10.75]],
    married: [[0, 1.4], [20000, 1.75], [50000, 2.45], [70000, 3.5], [80000, 5.53], [150000, 6.37], [500000, 8.97], [1000000, 10.75]],
    pe: [1000, 2000],
  },
  NM: { name: 'New Mexico', single: [[0, 1.5], [5500, 3.2], [16500, 4.3], [33500, 4.7], [66500, 4.9], [210000, 5.9]], married: [[0, 1.5], [8000, 3.2], [25000, 4.3], [50000, 4.7], [100000, 4.9], [315000, 5.9]], sd: [16100, 32200] },
  NY: {
    name: 'New York',
    single: [[0, 3.9], [8500, 4.4], [11700, 5.15], [13900, 5.4], [80650, 5.9], [215400, 6.85], [1077550, 9.65], [5000000, 10.3], [25000000, 10.9]],
    married: [[0, 3.9], [17150, 4.4], [23600, 5.15], [27900, 5.4], [161550, 5.9], [323200, 6.85], [2155350, 9.65], [5000000, 10.3], [25000000, 10.9]],
    sd: [8000, 16050], local: true, note: 'New York City and Yonkers residents pay a city income tax on top, which is not included here.',
  },
  NC: { name: 'North Carolina', ...same([[0, 3.99]]), sd: [12750, 25500] },
  ND: { name: 'North Dakota', single: [[48475, 1.95], [244825, 2.5]], married: [[80975, 1.95], [298075, 2.5]], sd: [16100, 32200] },
  OH: { name: 'Ohio', ...same([[26050, 2.75]]), pe: [2400, 4800], local: true, note: 'Most Ohio cities add a local income tax, often 1% to 2.5%, which is not included here.' },
  OK: { name: 'Oklahoma', single: [[3750, 2.5], [4900, 3.5], [7200, 4.5]], married: [[7500, 2.5], [9800, 3.5], [14400, 4.5]], sd: [6350, 12700], pe: [1000, 2000] },
  OR: { name: 'Oregon', single: [[0, 4.75], [4550, 6.75], [11400, 8.75], [125000, 9.9]], married: [[0, 4.75], [9100, 6.75], [22800, 8.75], [250000, 9.9]], sd: [2910, 5820], credit: [256, 512], local: true },
  PA: { name: 'Pennsylvania', ...same([[0, 3.07]]), taxes401k: true, local: true, note: 'Pennsylvania taxes 401(k) contributions, and most towns add a local wage tax, which is not included here.' },
  RI: { name: 'Rhode Island', ...same([[0, 3.75], [82050, 4.75], [186450, 5.99]]), sd: [11200, 22400], pe: [5250, 10500] },
  SC: { name: 'South Carolina', ...same([[3640, 3], [18230, 6]]), sd: [8350, 16700] },
  SD: { name: 'South Dakota', none: true },
  TN: { name: 'Tennessee', none: true },
  TX: { name: 'Texas', none: true },
  UT: { name: 'Utah', ...same([[0, 4.5]]), note: "Utah's taxpayer credit shrinks as income rises and isn't applied here, so this may run a little high." },
  VT: { name: 'Vermont', single: [[0, 3.35], [49400, 6.6], [119700, 7.6], [249700, 8.75]], married: [[0, 3.35], [82500, 6.6], [199450, 7.6], [304000, 8.75]], sd: [7650, 15300], pe: [5300, 10600] },
  VA: { name: 'Virginia', ...same([[0, 2], [3000, 3], [5000, 5], [17000, 5.75]]), sd: [8750, 17500], pe: [930, 1860] },
  WA: { name: 'Washington', none: true, note: 'Washington taxes only large capital gains, not wages.' },
  WV: { name: 'West Virginia', ...same([[0, 2.22], [10000, 2.96], [25000, 3.33], [40000, 4.44], [60000, 4.82]]), pe: [2000, 4000] },
  WI: { name: 'Wisconsin', single: [[0, 3.5], [15110, 4.4], [51950, 5.3], [332720, 7.65]], married: [[0, 3.5], [20150, 4.4], [69260, 5.3], [443630, 7.65]], sd: [13960, 25840], pe: [700, 1400] },
  WY: { name: 'Wyoming', none: true },
  DC: { name: 'District of Columbia', ...same([[0, 4], [10000, 6], [40000, 6.5], [60000, 8.5], [250000, 9.25], [500000, 9.75], [1000000, 10.75]]), sd: [16100, 32200] },
};

export const STATE_SOURCE = 'https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/';

// Alphabetical by name, for a <select>.
export const STATE_OPTIONS = Object.entries(STATES).sort((a, b) => a[1].name.localeCompare(b[1].name)).map(([code, s]) => [code, s.name]);

const r2 = (x) => Math.round(x * 100) / 100;

function bracketTax(income, brackets) {
  let tax = 0;
  let marginal = 0;
  brackets.forEach(([from, rate], i) => {
    const to = i + 1 < brackets.length ? brackets[i + 1][0] : Infinity;
    if (income > from) { tax += (Math.min(income, to) - from) * (rate / 100); marginal = rate; }
  });
  return { tax, marginal };
}

// wages: salary. Returns { tax, taxable, marginal (%), name, none, local, note }.
export function stateIncomeTax(code, { wages, filing = 'single', pretax401k = 0, pretaxHealth = 0 }) {
  const s = STATES[code];
  if (!s) throw new RangeError('Pick a state from the list');
  const i = filing === 'married' ? 1 : 0;
  const base = { name: s.name, none: !!s.none, local: !!s.local, note: s.note || '' };
  if (s.none) return { ...base, tax: 0, taxable: 0, marginal: 0 };
  const agi = Math.max(0, wages - pretaxHealth - (s.taxes401k ? 0 : pretax401k));
  let exemption = s.pe ? s.pe[i] : 0;
  if (s.pePhase) exemption = Math.max(0, exemption - Math.ceil(Math.max(0, agi - s.pePhase[i]) / 1000) * 1000);
  const taxable = Math.max(0, agi - (s.sd ? s.sd[i] : 0) - exemption);
  const { tax, marginal } = bracketTax(taxable, s[filing === 'married' ? 'married' : 'single']);
  return { ...base, tax: r2(Math.max(0, tax - (s.credit ? s.credit[i] : 0))), taxable: r2(taxable), marginal };
}
