// The Money Toolkit: the free tools as one download that works with no internet, opened straight from a folder.
// This file is the list of what goes in. tools/build-toolkit.mjs turns it into the zip (it needs esbuild to
// bundle each page's modules into one plain script, because browsers won't load modules from a file:// page).
// shared/test/toolkit.test.js checks every source page exists, every output name is unique, and the index is complete.

export const SECTIONS = [
  { id: 'calculators', en: 'Money calculators', items: [
    ['money-calculators/debt-payoff/', 'debt-payoff', 'Debt payoff: avalanche vs snowball', 'Your debt-free date and total interest, both ways.'],
    ['money-calculators/take-home-pay/', 'paycheck-by-state', 'Paycheck calculator by state', 'Take-home pay in all 50 states and DC, 2026 brackets.'],
    ['money-calculators/tax-refund/', 'tax-refund', 'Tax refund estimator', 'Your federal refund or what you owe, from your W-2.'],
    ['money-calculators/emergency-fund/', 'emergency-fund', 'Emergency fund', 'Your target and a month-by-month timeline.'],
    ['money-calculators/compound-interest/', 'compound-interest', 'Compound interest', 'Growth with monthly contributions.'],
    ['money-calculators/savings-interest/', 'savings-interest', 'High-yield savings', 'What your savings earn at today\'s rates.'],
    ['money-calculators/credit-card-minimum/', 'credit-card-minimum', 'Credit card minimum payment', 'How long minimums take and what they cost.'],
    ['money-calculators/roth-vs-traditional/', 'roth-vs-traditional', 'Roth vs Traditional', 'Which leaves you more after tax.'],
    ['money-calculators/student-loans/', 'student-loans', 'Student loan plans', 'Standard, IBR and RAP under the 2026 rules.'],
    ['money-calculators/rent-vs-buy/', 'rent-vs-buy', 'Rent vs buy', 'The true cost of owning, and your break-even year.'],
    ['money-calculators/401k-fees/', '401k-fees', '401(k) fee checker', 'What fund fees cost you over time.'],
    ['money-calculators/remittance-cost/', 'sending-money-abroad', 'Sending money abroad', 'Fees, exchange-rate markup and what really arrives.'],
  ] },
  { id: 'budget', en: 'Budget and bills', items: [
    ['budget/paycheck-plan.html', 'paycheck-planner', 'Paycheck to budget planner', '50/30/20 and zero-based plans from your take-home pay.'],
    ['budget/sinking-funds.html', 'sinking-funds', 'Sinking funds planner', 'Save monthly for the big bills you know are coming.'],
    ['budget/bill-calendar/', 'bill-calendar', 'Bill due date calendar', 'Every bill on a calendar, with phone reminders.'],
    ['budget/money-dashboard.html', 'money-dashboard', 'Money dashboard maker', 'Turn your bank CSV into a spreadsheet dashboard.'],
    ['budget/subscriptions.html', 'subscription-finder', 'Subscription finder', 'Every recurring charge in your bank statement.'],
    ['budget/savings-challenge.html', 'savings-challenge', '52-week savings challenge', 'Tick off weeks and print the chart.'],
    ['budget/afford.html', 'can-i-afford-this', 'Can I afford this?', 'Cash vs loan vs buy now, pay later.'],
    ['budget/holiday.html', 'holiday-planner', 'Holiday spending planner', 'A gift list with a budget per person.'],
    ['budget/networth.html', 'net-worth', 'Net worth snapshot', 'What you own minus what you owe, month by month.'],
    ['budget/couples.html', 'couples-budget', 'Couples budget', 'Split shared bills fairly, 50/50 or by income.'],
    ['budget/checkup.html', 'money-checkup', 'Annual money checkup', '20 questions and the fixes that matter most.'],
  ] },
  { id: 'scams', en: 'Scam safety', items: [
    ['scam-checker/', 'scam-checker', 'Is this a scam?', 'Paste a text or email and see its red flags.'],
    ['scam-checker/link/', 'link-checker', 'Suspicious link checker', 'Look-alike domains and other tricks.'],
    ['scam-checker/vendor/', 'vendor-payment-check', 'Vendor payment check', 'For businesses: verify new bank details before paying.'],
    ['scam-checker/family/', 'family-scam-proofing', 'Family scam-proofing checklist', 'Credit freezes, a safe word and 2-step verification.'],
  ] },
  { id: 'freelance', en: 'Freelancers and side hustles', items: [
    ['freelance-invoices/rate.html', 'freelance-rate', 'What to charge', 'Your hourly, day and weekly freelance rate.'],
    ['freelance-invoices/side-hustle.html', 'side-hustle-profit', 'Side hustle profit', 'Real hourly pay after fees, mileage and tax.'],
    ['freelance-invoices/', 'invoice-tracker', 'Invoice tracker', 'What\'s due, what\'s late and the late fee.'],
    ['freelance-invoices/set-aside/', 'tax-set-aside', 'Quarterly tax set-aside', 'How much of each payment to save for taxes.'],
  ] },
  { id: 'letters', en: 'Letters', items: [
    ['medical-bills/', 'medical-bill-letters', 'Medical bill letters', 'Itemized bill, disputes, financial assistance.'],
    ['medical-bills/debt.html', 'debt-collector-letters', 'Debt collector letters', 'Ask a collector to prove a debt, or stop contact.'],
  ] },
  { id: 'es', en: 'En español', lang: 'es', items: [
    ['money-calculators/es/debt-payoff/', 'es-pagar-deudas', 'Pagar deudas', 'Avalancha o bola de nieve.'],
    ['money-calculators/es/take-home-pay/', 'es-sueldo-neto', 'Sueldo neto por estado', 'Lo que te llega en cada cheque.'],
    ['money-calculators/es/tax-refund/', 'es-reembolso', 'Reembolso de impuestos', 'Tu reembolso federal con tu W-2.'],
    ['money-calculators/es/emergency-fund/', 'es-fondo-emergencia', 'Fondo de emergencia', 'Cuánto y en cuánto tiempo.'],
    ['money-calculators/es/remittance-cost/', 'es-envios-de-dinero', 'Envíos de dinero', 'Cuánto llega de verdad.'],
    ['budget/plan-quincena.html', 'es-plan-de-tu-cheque', 'Presupuesto 50/30/20', 'De tu cheque a tu presupuesto.'],
    ['budget/fondos-ahorro.html', 'es-fondos-de-ahorro', 'Fondos de ahorro', 'Para los gastos que sabes que vienen.'],
    ['budget/bill-calendar/es.html', 'es-calendario-de-pagos', 'Calendario de pagos', 'Todos tus recibos en un calendario.'],
    ['budget/tablero-dinero.html', 'es-tablero-de-dinero', 'Tablero de dinero', 'Tu CSV del banco en una hoja de cálculo.'],
    ['budget/reto-ahorro.html', 'es-reto-de-ahorro', 'Reto de 52 semanas', 'Ahorra $1,378 en un año.'],
    ['scam-checker/es/', 'es-es-una-estafa', '¿Es una estafa?', 'Revisa un mensaje sospechoso.'],
    ['scam-checker/es/enlace/', 'es-revisar-enlace', 'Revisor de enlaces', 'Revisa un enlace antes de abrirlo.'],
  ] },
];

export const sourceFile = (src) => (src.endsWith('/') ? `${src}index.html` : src);

// Spanish edition for Dinero Simple: "Caja de herramientas de dinero". Every page is Spanish, so the whole
// edition is on the native review list (NATIVE_REVIEW_ES.md) before it's sold.
export const SECTIONS_ES = [
  { id: 'calculadoras', es: 'Calculadoras de dinero', lang: 'es', items: [
    ['money-calculators/es/debt-payoff/', 'pagar-deudas', 'Pagar deudas', 'Avalancha o bola de nieve: tu fecha sin deudas.'],
    ['money-calculators/es/take-home-pay/', 'salario-neto', 'Salario neto por estado', 'Lo que te llega en cada cheque, con los impuestos de 2026.'],
    ['money-calculators/es/tax-refund/', 'reembolso-de-impuestos', 'Reembolso de impuestos', 'Tu reembolso federal o lo que debes, con tu W-2.'],
    ['money-calculators/es/emergency-fund/', 'fondo-de-emergencia', 'Fondo de emergencia', 'Cuánto necesitas y en cuánto tiempo lo juntas.'],
    ['money-calculators/es/remittance-cost/', 'envios-de-dinero', 'Envíos de dinero', 'Comisión, tipo de cambio y cuánto llega de verdad.'],
    ['money-calculators/es/compound-interest/', 'interes-compuesto', 'Interés compuesto', 'Cómo crece tu dinero con aportes cada mes.'],
    ['money-calculators/es/savings-interest/', 'intereses-de-ahorro', 'Intereses de ahorro', 'Lo que gana tu ahorro con las tasas de hoy.'],
    ['money-calculators/es/credit-card-minimum/', 'pago-minimo-de-tarjeta', 'Pago mínimo de tarjeta', 'Cuánto tardas y cuánto pagas con el mínimo.'],
    ['money-calculators/es/roth-vs-traditional/', 'roth-o-tradicional', 'Roth o Tradicional', 'Cuál te deja más después de impuestos.'],
    ['money-calculators/es/student-loans/', 'prestamos-estudiantiles', 'Préstamos estudiantiles', 'Los planes de pago con las reglas de 2026.'],
    ['money-calculators/es/rent-vs-buy/', 'rentar-o-comprar', 'Rentar o comprar', 'El costo real de ser dueño y tu año de equilibrio.'],
    ['money-calculators/es/401k-fees/', 'comisiones-401k', 'Comisiones del 401(k)', 'Lo que te cuestan las comisiones con los años.'],
  ] },
  { id: 'presupuesto', es: 'Presupuesto y pagos', lang: 'es', items: [
    ['budget/plan-quincena.html', 'presupuesto-50-30-20', 'Presupuesto 50/30/20 y base cero', 'De tu cheque a tu presupuesto del mes.'],
    ['budget/fondos-ahorro.html', 'fondos-de-ahorro', 'Fondos de ahorro', 'Guarda cada mes para los gastos que sabes que vienen.'],
    ['budget/bill-calendar/es.html', 'calendario-de-pagos', 'Calendario de pagos', 'Todos tus recibos en un calendario, con recordatorios.'],
    ['budget/tablero-dinero.html', 'tablero-de-dinero', 'Tablero de dinero', 'El CSV de tu banco en una hoja de cálculo.'],
    ['budget/reto-ahorro.html', 'reto-de-ahorro', 'Reto de ahorro de 52 semanas', 'Ahorra $1,378 en un año.'],
    ['budget/calendario-dinero.html', 'calendario-de-dinero', 'Calendario de dinero', 'Fechas de impuestos, Black Friday y más en tu calendario.'],
  ] },
  { id: 'estafas', es: 'Protégete de estafas', lang: 'es', items: [
    ['scam-checker/es/', 'es-una-estafa', '¿Es una estafa?', 'Pega un mensaje sospechoso y ve las señales de alerta.'],
    ['scam-checker/es/enlace/', 'revisar-enlace', 'Revisor de enlaces', 'Revisa un enlace antes de abrirlo.'],
    ['scam-checker/es/estafas/', 'guias-de-estafas', 'Guías de estafas comunes', 'USPS, peajes, IRS, Amazon y más, explicados.'],
    ['scam-checker/es/estafas/mensaje-peaje-sin-pagar/', 'estafa-peaje', 'Mensaje de peaje sin pagar', 'Cómo reconocerlo y qué hacer.'],
    ['scam-checker/es/estafas/mensaje-usps-falso/', 'estafa-usps', 'Mensaje falso de USPS', 'Cómo reconocerlo y qué hacer.'],
    ['scam-checker/es/estafas/estafa-irs/', 'estafa-irs', 'Estafa del IRS', 'Cómo reconocerla y qué hacer.'],
  ] },
];

export const EDITIONS = {
  en: { sections: SECTIONS, folder: 'Money-Toolkit', zip: 'Money-Toolkit.zip', lang: 'en' },
  es: { sections: SECTIONS_ES, folder: 'Caja-de-Herramientas', zip: 'Caja-de-Herramientas-de-Dinero.zip', lang: 'es' },
};
export const itemsOf = (sections) => sections.flatMap((s) => s.items.map(([src, out, title, blurb]) => ({ section: s.id, src, out: `${out}.html`, title, blurb, lang: s.lang || 'en' })));
export const ITEMS = itemsOf(SECTIONS);
export const ITEMS_ES = itemsOf(SECTIONS_ES);
