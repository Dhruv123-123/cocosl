// Money calendar: one .ics file with the money dates of the next year, as a free download for each brand
// (money-calendar.html, calendario-dinero.html; ready-made files from tools/build-money-calendars.mjs).
// Pure functions, no DOM. Dates checked against:
//   IRS estimated tax due dates for 2026 and 2027 (Form 1040-ES; weekend and holiday rule applied), shared
//     with freelance-invoices/lib/setaside.js QUARTERS.
//   Filing deadline April 15, 2027 for 2026 returns; IRA contributions for 2026 are allowed until then.
//   W-2 and 1099-NEC go out by January 31; in 2027 that is a Sunday, so the deadline moves to Monday, Feb 1.
//   HealthCare.gov open enrollment for 2027 plans: Nov 1, 2026 to Jan 15, 2027; enroll by Dec 15 for Jan 1 coverage.
//   Black Friday: the day after the fourth Thursday of November (Nov 27, 2026; Nov 26, 2027).
// Check each year's dates when the IRS publishes them, and move the window forward each November.
import { buildIcs } from './ics.js';

export const GROUPS = ['taxes', 'freelance', 'shopping', 'reset', 'challenge', 'scams', 'health'];
export const BRANDS = {
  mms: { name: 'Money Made Simple', lang: 'en', groups: ['taxes', 'shopping', 'reset', 'challenge', 'health'] },
  1099: { name: '1099 Money', lang: 'en', groups: ['taxes', 'freelance', 'shopping', 'reset'] },
  scam: { name: 'Scam Shield', lang: 'en', groups: ['scams', 'shopping', 'taxes', 'health'] },
  es: { name: 'Dinero Simple', lang: 'es', groups: ['taxes', 'shopping', 'reset', 'challenge', 'health'] },
};

const ESTIMATED = [
  ['2026-09-15', '2026 Q3'], ['2027-01-15', '2026 Q4'], ['2027-04-15', '2027 Q1'], ['2027-06-15', '2027 Q2'], ['2027-09-15', '2027 Q3'], ['2028-01-18', '2027 Q4'],
];

// [date, group, en title, en description, es title, es description]
const FIXED = [
  ['2026-11-01', 'health', 'Open enrollment starts', 'HealthCare.gov open enrollment for 2027 plans runs Nov 1 to Jan 15. Compare plans before you renew.', 'Empieza la inscripción abierta', 'La inscripción en HealthCare.gov para planes de 2027 va del 1 de noviembre al 15 de enero. Compara planes antes de renovar.'],
  ['2026-11-20', 'shopping', 'Set your holiday budget', 'One week to Black Friday. Write a total and a list before the deals start.', 'Pon tu presupuesto de fiestas', 'Falta una semana para el Black Friday. Escribe un total y una lista antes de las ofertas.'],
  ['2026-11-20', 'scams', 'Holiday shopping scams season', 'Fake delivery texts and too-good deals peak now. Track packages in the store\'s own app.', 'Temporada de estafas de compras', 'Los mensajes falsos de entregas y las ofertas demasiado buenas aumentan ahora. Rastrea tus paquetes en la app de la tienda.'],
  ['2026-11-27', 'shopping', 'Black Friday: stick to the list', 'Buy what\'s on your list, check the price history, and skip "buy now, pay later" for gifts.', 'Black Friday: sigue tu lista', 'Compra lo que está en tu lista, revisa el historial de precios y evita "compra ahora, paga después" para regalos.'],
  ['2026-11-30', 'shopping', 'Cyber Monday', 'Same rules as Friday. Unsubscribe from the deal emails tomorrow.', 'Cyber Monday', 'Las mismas reglas que el viernes. Mañana date de baja de los correos de ofertas.'],
  ['2026-12-15', 'health', 'Health plan deadline for Jan 1', 'Enroll or switch on HealthCare.gov today for coverage starting January 1.', 'Fecha límite para el 1 de enero', 'Inscríbete o cambia de plan hoy en HealthCare.gov para tener cobertura desde el 1 de enero.'],
  ['2026-12-31', 'freelance', 'Last day for 2026 business expenses', 'Expenses paid by today count for 2026. Save the receipts.', 'Último día de gastos de negocio de 2026', 'Los gastos pagados hasta hoy cuentan para 2026. Guarda los recibos.'],
  ['2027-01-02', 'reset', 'January money reset', 'Total last year\'s spending, cancel unused subscriptions, set this year\'s budget and goals.', 'Reinicio de dinero de enero', 'Suma lo que gastaste el año pasado, cancela suscripciones que no usas y pon tu presupuesto y metas del año.'],
  ['2027-01-04', 'reset', 'Check your three credit reports', 'Free every week at AnnualCreditReport.com. Dispute anything you don\'t recognise.', 'Revisa tus tres reportes de crédito', 'Gratis cada semana en AnnualCreditReport.com. Disputa lo que no reconozcas.'],
  ['2027-01-15', 'health', 'Open enrollment ends', 'Last day to pick a HealthCare.gov plan for 2027 in most states.', 'Termina la inscripción abierta', 'Último día para elegir un plan de HealthCare.gov para 2027 en la mayoría de los estados.'],
  ['2027-01-20', 'scams', 'Tax season scams', 'The IRS doesn\'t text, call or email first about money you owe. Hang up and check at IRS.gov.', 'Estafas de temporada de impuestos', 'El IRS no te manda mensajes, llama ni escribe primero por dinero que debes. Cuelga y revisa en IRS.gov.'],
  ['2027-02-01', 'taxes', 'Your W-2 and 1099 forms are due', 'Employers and clients must send them by today. Chase any that are missing.', 'Llegan tus formularios W-2 y 1099', 'Tu empleador y tus clientes deben mandarlos a más tardar hoy. Pide los que falten.'],
  ['2027-02-01', 'freelance', 'Send 1099-NEC forms to contractors', 'If you paid a contractor $2,000 or more in 2026, their 1099-NEC is due today.', 'Manda los 1099-NEC', 'Si pagaste $2,000 o más a un contratista en 2026, su 1099-NEC vence hoy.'],
  ['2027-04-01', 'taxes', 'Two weeks to Tax Day', 'File now, or file for an extension. An extension gives more time to file, not to pay.', 'Faltan dos semanas para los impuestos', 'Declara ya o pide una prórroga. La prórroga te da más tiempo para declarar, no para pagar.'],
  ['2027-04-15', 'taxes', 'Tax Day: file your 2026 return', 'Also the last day for 2026 IRA contributions.', 'Día de impuestos: declara 2026', 'También es el último día para aportar a tu IRA por 2026.'],
  ['2027-07-01', 'reset', 'Mid-year money check-in', 'Halfway through the year: compare spending with your plan and move one goal forward.', 'Revisión de mitad de año', 'Vas a la mitad del año: compara tus gastos con tu plan y avanza una meta.'],
  ['2027-10-15', 'scams', 'Medicare open enrollment scams', 'Medicare enrollment runs Oct 15 to Dec 7. Medicare never calls to sell plans or ask for your number.', 'Estafas de inscripción a Medicare', 'La inscripción de Medicare va del 15 de octubre al 7 de diciembre. Medicare nunca llama para vender planes ni pedir tu número.'],
  ['2027-11-19', 'shopping', 'Set your holiday budget', 'One week to Black Friday. Write a total and a list before the deals start.', 'Pon tu presupuesto de fiestas', 'Falta una semana para el Black Friday. Escribe un total y una lista antes de las ofertas.'],
  ['2027-11-26', 'shopping', 'Black Friday: stick to the list', 'Buy what\'s on your list, check the price history, and skip "buy now, pay later" for gifts.', 'Black Friday: sigue tu lista', 'Compra lo que está en tu lista, revisa el historial de precios y evita "compra ahora, paga después" para regalos.'],
];

const addDays = (s, n) => new Date(Date.parse(`${s}T00:00:00Z`) + n * 86400000).toISOString().slice(0, 10);

/** Every event of every group, with both languages. */
export function allEvents() {
  const out = FIXED.map(([date, group, t, d, te, de], i) => ({ id: `fixed-${date}-${i}`, date, group, en: [t, d], es: [te, de] }));
  for (const [due, q] of ESTIMATED) {
    for (const group of ['taxes', 'freelance']) {
      if (group === 'taxes' && !/Q4/.test(q) && due !== '2027-04-15') continue; // employees: only the dates most people need
      out.push({ id: `est-${group}-${due}`, date: due, group, en: [`Estimated tax due (${q})`, 'Pay at IRS.gov/payments or with IRS Direct Pay. Pay your state too if it has income tax.'], es: [`Vence el pago estimado (${q})`, 'Paga en IRS.gov/payments o con IRS Direct Pay. Paga también a tu estado si cobra impuesto sobre ingresos.'] });
    }
    out.push({ id: `est-soon-${due}`, date: addDays(due, -7), group: 'freelance', en: [`One week to estimated tax (${q})`, 'Add up this quarter\'s profit and move the tax money from your set-aside account.'], es: [`Falta una semana para el pago estimado (${q})`, 'Suma la ganancia del trimestre y pasa el dinero de impuestos de tu cuenta de ahorro.'] });
  }
  // 52-week savings challenge: start Jan 1, 2027, check in on the first Sunday of each month.
  const start = '2027-01-01';
  out.push({ id: 'challenge-start', date: start, group: 'challenge', en: ['Start the 52-week savings challenge', 'Save $1 this week, $2 next week, and so on: $1,378 by the end of the year.'], es: ['Empieza el reto de ahorro de 52 semanas', 'Ahorra $1 esta semana, $2 la próxima y así: $1,378 al final del año.'] });
  for (let m = 1; m < 12; m += 1) {
    const first = new Date(Date.UTC(2027, m, 1));
    const sunday = new Date(first.getTime() + ((7 - first.getUTCDay()) % 7) * 86400000).toISOString().slice(0, 10);
    const weeks = Math.floor((Date.parse(`${sunday}T00:00:00Z`) - Date.parse(`${start}T00:00:00Z`)) / (7 * 86400000)) + 1; // the week you're in
    const total = (weeks * (weeks + 1)) / 2;
    out.push({ id: `challenge-${sunday}`, date: sunday, group: 'challenge', en: ['Savings challenge check-in', `Week ${weeks}: about $${total.toLocaleString('en-US')} saved if you're on track.`], es: ['Revisión del reto de ahorro', `Semana ${weeks}: unos $${total.toLocaleString('en-US')} ahorrados si vas al día.`] });
  }
  return out.sort((a, b) => a.date.localeCompare(b.date) || a.id.localeCompare(b.id));
}

/** Events for a brand's choice of groups, from `from` (inclusive) for a year. */
export function eventsFor({ groups, lang = 'en', from, days = 366 } = {}) {
  const to = addDays(from, days);
  const want = new Set(groups);
  const seen = new Set();
  return allEvents().filter((e) => want.has(e.group) && e.date >= from && e.date < to).filter((e) => {
    const key = `${e.date}|${e.en[0]}`; // the same date and title from two groups shows once
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  }).map((e) => ({ uid: e.id, date: e.date, group: e.group, title: e[lang === 'es' ? 'es' : 'en'][0], description: e[lang === 'es' ? 'es' : 'en'][1] }));
}

export function calendarFile(brandKey, { groups, from, stamp } = {}) {
  const b = BRANDS[brandKey] || BRANDS.mms;
  const events = eventsFor({ groups: groups || b.groups, lang: b.lang, from });
  const name = b.lang === 'es' ? `Calendario de dinero de ${b.name}` : `${b.name} money calendar`;
  return { events, ics: buildIcs(events.map((e) => ({ ...e, description: `${e.description} (${b.name})` })), { name, stamp }) };
}
