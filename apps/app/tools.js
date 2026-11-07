// The ten tools in the Money Made Simple app (app/index.html), in home-screen order.
// en / es: the page for each language, relative to app/. A tool with no Spanish page uses the English one.
// tools/build-app-shell.mjs reads this list to work out every file to save for offline (app/precache.json).
export const TOOLS = [
  { id: 'budget', icon: '💵', en: '../budget/', es: null, name: { en: 'Budget', es: 'Presupuesto' }, blurb: { en: 'The 20-minute monthly budget', es: 'Presupuesto mensual (en inglés)' } },
  { id: 'paycheck', icon: '🧾', en: '../money-calculators/take-home-pay/', es: '../money-calculators/es/take-home-pay/', name: { en: 'Paycheck', es: 'Salario neto' }, blurb: { en: 'Take-home pay by state', es: 'Lo que te llega por estado' } },
  { id: 'plan', icon: '🗂️', en: '../budget/paycheck-plan.html', es: '../budget/plan-quincena.html', name: { en: '50/30/20', es: '50/30/20' }, blurb: { en: 'Paycheck to budget plan', es: 'De tu cheque a tu plan' } },
  { id: 'bills', icon: '📅', en: '../budget/bill-calendar/', es: '../budget/bill-calendar/es.html', name: { en: 'Bill calendar', es: 'Pagos' }, blurb: { en: 'Every due date this month', es: 'Todas tus fechas de pago' } },
  { id: 'debt', icon: '📉', en: '../money-calculators/debt-payoff/', es: '../money-calculators/es/debt-payoff/', name: { en: 'Debt payoff', es: 'Pagar deudas' }, blurb: { en: 'Your debt-free date', es: 'Tu fecha sin deudas' } },
  { id: 'emergency', icon: '🛟', en: '../money-calculators/emergency-fund/', es: '../money-calculators/es/emergency-fund/', name: { en: 'Emergency fund', es: 'Emergencias' }, blurb: { en: 'How much and how fast', es: 'Cuánto y en cuánto tiempo' } },
  { id: 'sinking', icon: '🪣', en: '../budget/sinking-funds.html', es: '../budget/fondos-ahorro.html', name: { en: 'Sinking funds', es: 'Fondos' }, blurb: { en: 'Save for bills you know are coming', es: 'Para gastos que ya sabes' } },
  { id: 'split', icon: '🤝', en: '../budget/split-bills.html', es: '../budget/dividir-gastos.html', name: { en: 'Split bills', es: 'Dividir gastos' }, blurb: { en: 'Roommates and couples', es: 'Roomies y parejas' } },
  { id: 'challenge', icon: '🐷', en: '../budget/savings-challenge.html', es: '../budget/reto-ahorro.html', name: { en: 'Savings challenge', es: 'Reto de ahorro' }, blurb: { en: '52 weeks, $1,378', es: '52 semanas, $1,378' } },
  { id: 'scam', icon: '🛡️', en: '../scam-checker/', es: '../scam-checker/es/', name: { en: 'Scam check', es: '¿Es estafa?' }, blurb: { en: 'Paste a suspicious message', es: 'Pega un mensaje sospechoso' } },
];

export const urlFor = (t, lang) => (lang === 'es' && t.es) || t.en;
