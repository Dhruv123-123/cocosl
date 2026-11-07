// All words the calculators show, in English and Spanish. Numbers come from lib/calc.js.
// Spanish uses tú and neutral Latin American vocabulary to match the Dinero Simple voice
// (carro, celular, cuenta de cheques; US product names like 401(k), Roth IRA, APY kept in English).
// It needs a native speaker's read before promotion (see apps/README.md).
import { money, duration } from './format.js';

const pct1 = (x) => `${Math.round(x * 1000) / 10}%`;
// The state paragraph under the take-home table (only when a state was picked from the list).
function stateLine(r) {
  const s = r.stateInfo;
  if (!s) return '';
  if (s.none) return `<p><b>${s.name}</b> doesn't tax wages, so nothing comes out for state income tax.${s.note ? ` ${s.note}` : ''}</p>`;
  return `<p>In <b>${s.name}</b> your top state rate is <b>${s.marginal}%</b>, about ${pct1(r.effectiveState)} of your salary overall.${s.note ? ` ${s.note}` : s.local ? ' Some cities or counties here add a local income tax, which is not included.' : ''}</p>`;
}
function stateLineEs(r) {
  const s = r.stateInfo;
  if (!s) return '';
  if (s.none) return `<p><b>${s.name}</b> no cobra impuesto sobre el salario.</p>`;
  return `<p>En <b>${s.name}</b> tu tasa estatal más alta es <b>${s.marginal}%</b>, cerca del ${pct1(r.effectiveState)} de tu salario en total.${s.local ? ' Algunas ciudades o condados agregan un impuesto local que no está incluido.' : ''}</p>`;
}

const en = {
  fields: {
    initial: 'Starting amount ($)', monthly: 'Added each month ($)', annualRate: 'Yearly return (%)', years: 'Years',
    monthlyExpenses: 'Essential monthly costs ($)', monthsTarget: 'Months to cover (0 = our suggestion)', stability: 'How steady is your income?', stSteady: 'Very steady (two incomes, or a secure salaried job)', stAverage: 'Fairly steady (one salaried income)', stVariable: 'Up and down (commission, gig work, one income with kids)', stUnstable: 'Could stop suddenly (self-employed, seasonal, layoffs in my field)', currentSaved: 'Already saved ($)', monthlySave: 'You can save each month ($)', apy: 'Savings APY (%)',
    balance: 'Balance ($)', monthlyDeposit: 'Added each month ($)', hyApy: 'High-yield APY (%)', compareApy: 'Your current APY (%)', months: 'Months',
    cardBalance: 'Card balance ($)', apr: 'APR (%)', minPercent: 'Minimum: % of balance + interest', minFloor: 'Minimum payment floor ($)', fixedPayment: 'What if you paid each month ($)',
    annualContribution: 'Yearly contribution, before tax ($)', currentRate: 'Your tax bracket now (%)', retirementRate: 'Expected tax rate in retirement (%)', yearsToWithdraw: 'Years until you withdraw', annualReturn: 'Yearly return (%)',
    salary: 'Yearly salary ($)', pretax401k: 'Pre-tax 401(k) per year ($)', pretaxHealth: 'Pre-tax health premiums per year ($)', stateRate: 'Custom state tax rate (%)', state: 'State you live in', stateCustom: 'Enter my own rate', payPeriods: 'Paychecks per year', filing: 'Filing status', single: 'Single', married: 'Married filing jointly',
    debtName: 'Name', debtBalance: 'Balance ($)', debtApr: 'APR (%)', debtMin: 'Minimum ($)', remove: 'Remove', removeAria: 'Remove this debt',
  },
  dur: (m) => duration(m, 'en'),
  growth: (v, r) => `<p class="big">${money(r.finalBalance)}</p>
    <p>After ${v.years} years you would have put in <b>${money(r.totalContributed)}</b> and growth would add
    <b>${money(r.totalGrowth)}</b>. That growth share is ${Math.round((r.totalGrowth / Math.max(r.finalBalance, 1)) * 100)}% of the total.</p>`,
  growthNote: (v) => `Assumes a steady ${v.annualRate}% a year, compounded monthly. Real returns go up and down, and are not guaranteed.`,
  chartLabel: (a, b) => `Balance grows from ${a} to ${b}`, legendTotal: 'Total balance', legendIn: 'What you put in',
  efDone: (r) => `<p class="big">You're there</p><p>Your ${money(r.target)} goal is already covered. Keep it somewhere boring, insured and separate from spending money.</p>`,
  efNoSave: (r) => `<p class="big">Add a monthly amount</p><p>Your goal is ${money(r.target)}. Even $25 a week gets you moving.</p>`,
  efStarter: (r) => `<p>First milestone: <b>${money(r.starterGoal)}</b>. It covers most surprise bills and is the hardest part.</p>`,
  ef: (v, r) => `<p class="big">${duration(r.months)}</p><p>That's how long until you have <b>${money(r.target)}</b> (${r.monthsTarget} months of costs). You need ${money(r.gap)} more.</p>`,
  efSuggest: (r, used) => `<p class="note">For income like yours we suggest about <b>${r.suggested} months</b> of essential costs${used ? '' : `; you picked ${r.monthsTarget}`}.</p>`,
  efTimeline: 'Your timeline', efMarks: { starter: 'Starter fund', oneMonth: 'One month of costs', half: 'Halfway', target: 'Fully funded' }, efNow: 'Done', efNever: 'Not at this rate', efIn: (m) => `in ${duration(m)}`,
  savings: (v, r) => `<p class="big">+${money(r.difference, 2)}</p>
    <p>At ${v.apy}% APY you'd earn <b>${money(r.interest, 2)}</b> in interest over ${duration(v.months)}, versus <b>${money(r.compareInterest, 2)}</b> at ${v.compareApy}%.</p>
    <p class="note">APYs change. Check the current rate and that the bank is FDIC insured (or the credit union NCUA insured).</p>`,
  ccFixed: (v, f, saved) => `<p>Paying a flat <b>${money(v.fixedPayment)}</b> a month clears it in <b>${duration(f.months)}</b> with ${money(f.interest)} interest. You'd keep <b>${money(saved)}</b>.</p>`,
  ccFixedNever: (v) => `<p>${money(v.fixedPayment)} a month doesn't cover the interest, so the balance would never shrink.</p>`,
  cc: (m, fixed) => `<p class="big">${duration(m.months)}</p>
    <p>That's how long the minimum payment takes. You'd pay <b>${money(m.interest)}</b> in interest, ${money(m.paid)} in total.</p>${fixed}
    <p class="note">Card issuers calculate minimums differently. Your statement's "minimum payment warning" box shows your card's real numbers.</p>`,
  takeHome: (v, r) => `<p class="big">${money(r.perPaycheck)} <small class="per">per paycheck</small></p>
    <p>About <b>${money(r.perMonth)}</b> a month and <b>${money(r.takeHome)}</b> a year from a ${money(r.salary)} salary.</p>
    <table class="split-table"><tbody>
      <tr><td>Federal income tax</td><td>${money(r.federal)}</td></tr>
      <tr><td>Social Security</td><td>${money(r.socialSecurity)}</td></tr>
      <tr><td>Medicare</td><td>${money(r.medicare)}</td></tr>
      <tr><td>${r.stateInfo ? `${r.stateInfo.name} income tax` : 'State income tax'}</td><td>${money(r.state)}</td></tr>
      <tr><td>Pre-tax 401(k) and health</td><td>${money(r.pretax401k + r.pretaxHealth)}</td></tr>
    </tbody></table>
    <p>Your top federal bracket is <b>${Math.round(r.marginal * 100)}%</b>, but you pay about ${Math.round(r.effectiveFederal * 1000) / 10}% of your salary in federal income tax overall.</p>
    ${stateLine(r)}
    <p class="note">Estimate for tax year 2026 using the standard deduction. It doesn't include credits (like the child tax credit), local taxes, or your exact W-4. State figures come from the <a href="https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/" target="_blank" rel="noopener">Tax Foundation's 2026 state tables</a>; federal figures from the IRS. States without a wage tax: Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming.</p>`,
  roth: (r) => {
    const head = r.winner === 'tie' ? "It's a tie" : r.winner === 'roth' ? 'Roth comes out ahead' : 'Traditional comes out ahead';
    return `<p class="big">${head}</p>
      <p>After tax: Roth <b>${money(r.roth)}</b>, Traditional <b>${money(r.traditional)}</b>${r.winner === 'tie' ? '' : `, a difference of <b>${money(r.difference)}</b>`}.</p>
      <p>The one question that decides it: <b>is your tax rate higher now, or later?</b> Higher now favours Traditional. Higher later favours Roth. Unsure? Many people split contributions.</p>
      <p class="note">Simplified: same pre-tax dollars, flat tax rates, no employer match or income limits. Check IRS contribution and income limits for the current year.</p>`;
  },
  debtInfeasible: '<p class="big">Not paid off at this budget</p><p>The payments don\'t outrun the interest. Raise the extra amount, or look at a lower-rate option.</p>',
  debtPaidIn: (name, m) => `${name}: paid off in ${duration(m)}`,
  debtVerdict: (c) => (c.interestSaved > 0
    ? `Avalanche saves <b>${money(c.interestSaved)}</b> in interest${c.monthsSaved > 0 ? ` and ${duration(c.monthsSaved)}` : ''}. Snowball gives you quicker wins. Pick the one you'll stick with.`
    : 'Both orders cost about the same here, so go with snowball for the quick wins.'),
  debt: (a, s, verdict, listA, listS) => `<p class="big">Debt-free in ${duration(a.months)}</p>
    <p>Paying <b>${money(a.budget)}</b> a month in total. ${verdict}</p>
    <div class="two"><div><h3>Avalanche (highest APR first)</h3><p>${money(a.totalInterest)} interest, ${duration(a.months)}</p>${listA}</div>
    <div><h3>Snowball (smallest balance first)</h3><p>${money(s.totalInterest)} interest, ${duration(s.months)}</p>${listS}</div></div>`,
  defaultDebts: ['Credit card', 'Store card', 'Car loan'],
  printAva: 'Print my avalanche plan', printSnow: 'Print my snowball plan',
  planTitle: (strategy) => `My debt-free plan (${strategy === 'avalanche' ? 'avalanche: highest APR first' : 'snowball: smallest balance first'})`,
  planIntro: (a) => `Pay ${money(a.budget)} a month in total. Debt-free in ${duration(a.months)}, with ${money(a.totalInterest)} of interest. Tick each month when it's paid.`,
  planMonth: 'Month', planPaid: 'Paid', planLeft: 'left', planFooter: 'Made with the free debt payoff calculator. Estimates assume your APRs and minimums stay the same.',
  fees: {
    name: 'Fund name', category: 'Type', er: 'Expense ratio (%)', balance: 'Your balance ($)',
    categories: { 'us-stock': 'US stock', 'intl-stock': 'International stock', bond: 'Bond', 'target-date': 'Target date', stable: 'Stable value or cash', other: 'Other' },
    defaults: [['S&P 500 Index', 'us-stock', 0.04, 18000], ['Large Cap Growth (active)', 'us-stock', 0.82, 12000], ['International Index', 'intl-stock', 0.08, 6000], ['Target Date 2055', 'target-date', 0.65, 9000]],
    result: (r) => `<p class="big">${money(r.yearlyFees)} a year in fund fees</p>
      <p>Your average expense ratio is <b>${r.avgExpenseRatio}%</b> on ${money(r.total)}.</p>
      <p>Over ${r.years} years, fees could take about <b>${money(r.feeDrag)}</b> out of your balance: ${money(r.endWithFees)} instead of ${money(r.endNoFees)}.</p>`,
    table: (rows) => `<table class="fees"><thead><tr><th>Fund</th><th>Fee</th><th>A year</th></tr></thead><tbody>${rows}</tbody></table>`,
    cheaper: (name, er) => `Lower-cost option of the same type in your plan: ${name} (${er}%)`,
    gap: (r) => (r.lowestCostGap > 1
      ? `<p>If each fund cost the same as the lowest-cost fund of its type in your plan, you'd have about <b>${money(r.lowestCostGap)}</b> more after ${r.years} years. That isn't a reason to switch on its own: compare what the funds hold first.</p>`
      : '<p>You already hold the lowest-cost fund of each type you entered.</p>'),
    note: 'Estimate: same return every year, contributions split like your balances, fund expense ratios only (not plan admin fees). Education, not investment advice.',
  },
  nextStep: 'Next step', affiliateNote: 'Affiliate link: we may earn a commission at no cost to you.', getIt: 'Get it',
  copied: 'Link copied', copyPrompt: 'Copy this link', sending: 'Sending…', notConnected: 'Email signup is not connected yet: set email.action in config.js.',
};

const es = {
  fields: {
    initial: 'Monto inicial ($)', monthly: 'Aporte mensual ($)', annualRate: 'Rendimiento anual (%)', years: 'Años',
    monthlyExpenses: 'Gastos esenciales al mes ($)', monthsTarget: 'Meses a cubrir (0 = nuestra sugerencia)', stability: '¿Qué tan estable es tu ingreso?', stSteady: 'Muy estable (dos ingresos, o un empleo fijo seguro)', stAverage: 'Bastante estable (un solo sueldo fijo)', stVariable: 'Sube y baja (comisiones, trabajos por app, un ingreso con hijos)', stUnstable: 'Podría parar de golpe (independiente, temporada, despidos en mi área)', currentSaved: 'Ya ahorrado ($)', monthlySave: 'Puedes ahorrar al mes ($)', apy: 'APY de ahorro (%)',
    balance: 'Saldo ($)', monthlyDeposit: 'Depósito mensual ($)', hyApy: 'APY de alto rendimiento (%)', compareApy: 'Tu APY actual (%)', months: 'Meses',
    cardBalance: 'Saldo de la tarjeta ($)', apr: 'Tasa anual APR (%)', minPercent: 'Mínimo: % del saldo + intereses', minFloor: 'Pago mínimo base ($)', fixedPayment: '¿Y si pagaras cada mes? ($)',
    annualContribution: 'Aporte anual, antes de impuestos ($)', currentRate: 'Tu tasa de impuestos hoy (%)', retirementRate: 'Tasa esperada al jubilarte (%)', yearsToWithdraw: 'Años hasta retirar', annualReturn: 'Rendimiento anual (%)',
    salary: 'Salario anual ($)', pretax401k: '401(k) antes de impuestos al año ($)', pretaxHealth: 'Seguro médico antes de impuestos al año ($)', stateRate: 'Tasa estatal propia (%)', state: 'Estado donde vives', stateCustom: 'Escribir mi propia tasa', payPeriods: 'Cheques de pago al año', filing: 'Estado civil para impuestos', single: 'Soltero/a', married: 'Casados, declaración conjunta',
    debtName: 'Nombre', debtBalance: 'Saldo ($)', debtApr: 'APR (%)', debtMin: 'Mínimo ($)', remove: 'Quitar', removeAria: 'Quitar esta deuda',
  },
  dur: (m) => duration(m, 'es'),
  growth: (v, r) => `<p class="big">${money(r.finalBalance)}</p>
    <p>Después de ${v.years} años habrías aportado <b>${money(r.totalContributed)}</b> y el crecimiento sumaría
    <b>${money(r.totalGrowth)}</b>. El crecimiento es el ${Math.round((r.totalGrowth / Math.max(r.finalBalance, 1)) * 100)}% del total.</p>`,
  growthNote: (v) => `Supone un ${v.annualRate}% anual constante, capitalizado cada mes. Los rendimientos reales suben y bajan, y no están garantizados.`,
  chartLabel: (a, b) => `El saldo crece de ${a} a ${b}`, legendTotal: 'Saldo total', legendIn: 'Lo que tú aportaste',
  efDone: (r) => `<p class="big">¡Ya lo tienes!</p><p>Tu meta de ${money(r.target)} ya está cubierta. Guárdala en una cuenta aburrida, asegurada y separada del dinero para gastos.</p>`,
  efNoSave: (r) => `<p class="big">Agrega un monto mensual</p><p>Tu meta es ${money(r.target)}. Aunque sean $25 por semana, ya avanzas.</p>`,
  efStarter: (r) => `<p>Primera meta: <b>${money(r.starterGoal)}</b>. Cubre la mayoría de los gastos inesperados y es la parte más difícil.</p>`,
  ef: (v, r) => `<p class="big">${duration(r.months, 'es')}</p><p>Es el tiempo hasta tener <b>${money(r.target)}</b> (${r.monthsTarget} meses de gastos). Te faltan ${money(r.gap)}.</p>`,
  efSuggest: (r, used) => `<p class="note">Para un ingreso como el tuyo sugerimos unos <b>${r.suggested} meses</b> de gastos esenciales${used ? '' : `; elegiste ${r.monthsTarget}`}.</p>`,
  efTimeline: 'Tu calendario', efMarks: { starter: 'Fondo inicial', oneMonth: 'Un mes de gastos', half: 'La mitad', target: 'Meta completa' }, efNow: 'Listo', efNever: 'No a este ritmo', efIn: (m) => `en ${duration(m, 'es')}`,
  savings: (v, r) => `<p class="big">+${money(r.difference, 2)}</p>
    <p>Con un APY de ${v.apy}% ganarías <b>${money(r.interest, 2)}</b> de intereses en ${duration(v.months, 'es')}, comparado con <b>${money(r.compareInterest, 2)}</b> al ${v.compareApy}%.</p>
    <p class="note">Los APY cambian. Revisa la tasa actual y que el banco esté asegurado por la FDIC (o la cooperativa por la NCUA).</p>`,
  ccFixed: (v, f, saved) => `<p>Si pagas <b>${money(v.fixedPayment)}</b> fijos al mes, la liquidas en <b>${duration(f.months, 'es')}</b> con ${money(f.interest)} de intereses. Te ahorrarías <b>${money(saved)}</b>.</p>`,
  ccFixedNever: (v) => `<p>${money(v.fixedPayment)} al mes no cubre los intereses, así que el saldo nunca bajaría.</p>`,
  cc: (m, fixed) => `<p class="big">${duration(m.months, 'es')}</p>
    <p>Eso tardas pagando solo el mínimo. Pagarías <b>${money(m.interest)}</b> de intereses, ${money(m.paid)} en total.</p>${fixed}
    <p class="note">Cada emisor calcula el mínimo distinto. El recuadro de "advertencia de pago mínimo" en tu estado de cuenta muestra los números reales de tu tarjeta.</p>`,
  takeHome: (v, r) => `<p class="big">${money(r.perPaycheck)} <small class="per">por cheque</small></p>
    <p>Unos <b>${money(r.perMonth)}</b> al mes y <b>${money(r.takeHome)}</b> al año con un salario de ${money(r.salary)}.</p>
    <table class="split-table"><tbody>
      <tr><td>Impuesto federal sobre la renta</td><td>${money(r.federal)}</td></tr>
      <tr><td>Seguro Social</td><td>${money(r.socialSecurity)}</td></tr>
      <tr><td>Medicare</td><td>${money(r.medicare)}</td></tr>
      <tr><td>${r.stateInfo ? `Impuesto estatal (${r.stateInfo.name})` : 'Impuesto estatal'}</td><td>${money(r.state)}</td></tr>
      <tr><td>401(k) y seguro médico antes de impuestos</td><td>${money(r.pretax401k + r.pretaxHealth)}</td></tr>
    </tbody></table>
    <p>Tu tramo federal más alto es <b>${Math.round(r.marginal * 100)}%</b>, pero en total pagas cerca del ${Math.round(r.effectiveFederal * 1000) / 10}% de tu salario en impuesto federal.</p>
    ${stateLineEs(r)}
    <p class="note">Estimación para el año fiscal 2026 con la deducción estándar. No incluye créditos (como el crédito por hijos), impuestos locales ni tu W-4 exacto. Los datos estatales vienen de las <a href="https://taxfoundation.org/data/all/state/state-income-tax-rates-2026/" target="_blank" rel="noopener">tablas estatales 2026 de Tax Foundation</a>; los federales, del IRS. Estados sin impuesto al salario: Alaska, Florida, Nevada, New Hampshire, Dakota del Sur, Tennessee, Texas, Washington y Wyoming.</p>`,
  roth: (r) => {
    const head = r.winner === 'tie' ? 'Empate' : r.winner === 'roth' ? 'Gana la Roth' : 'Gana la Tradicional';
    return `<p class="big">${head}</p>
      <p>Después de impuestos: Roth <b>${money(r.roth)}</b>, Tradicional <b>${money(r.traditional)}</b>${r.winner === 'tie' ? '' : `, una diferencia de <b>${money(r.difference)}</b>`}.</p>
      <p>La pregunta que lo decide: <b>¿tu tasa de impuestos es más alta hoy o después?</b> Más alta hoy favorece la Tradicional. Más alta después favorece la Roth. ¿No estás seguro? Mucha gente divide sus aportes.</p>
      <p class="note">Simplificado: mismos dólares antes de impuestos, tasas fijas, sin aporte del empleador ni límites de ingreso. Revisa los límites del IRS para el año en curso.</p>`;
  },
  debtInfeasible: '<p class="big">No se liquida con este presupuesto</p><p>Los pagos no superan los intereses. Sube el monto extra o busca una opción con tasa más baja.</p>',
  debtPaidIn: (name, m) => `${name}: liquidada en ${duration(m, 'es')}`,
  debtVerdict: (c) => (c.interestSaved > 0
    ? `Avalancha ahorra <b>${money(c.interestSaved)}</b> en intereses${c.monthsSaved > 0 ? ` y ${duration(c.monthsSaved, 'es')}` : ''}. Bola de nieve te da victorias más rápido. Elige el que vas a mantener.`
    : 'Los dos órdenes cuestan casi lo mismo, así que elige bola de nieve por las victorias rápidas.'),
  debt: (a, s, verdict, listA, listS) => `<p class="big">Sin deudas en ${duration(a.months, 'es')}</p>
    <p>Pagando <b>${money(a.budget)}</b> al mes en total. ${verdict}</p>
    <div class="two"><div><h3>Avalancha (APR más alta primero)</h3><p>${money(a.totalInterest)} de intereses, ${duration(a.months, 'es')}</p>${listA}</div>
    <div><h3>Bola de nieve (saldo más chico primero)</h3><p>${money(s.totalInterest)} de intereses, ${duration(s.months, 'es')}</p>${listS}</div></div>`,
  defaultDebts: ['Tarjeta de crédito', 'Tarjeta de tienda', 'Préstamo del carro'],
  printAva: 'Imprimir mi plan avalancha', printSnow: 'Imprimir mi plan bola de nieve',
  planTitle: (strategy) => `Mi plan para salir de deudas (${strategy === 'avalanche' ? 'avalancha: APR más alta primero' : 'bola de nieve: saldo más chico primero'})`,
  planIntro: (a) => `Paga ${money(a.budget)} al mes en total. Sin deudas en ${duration(a.months, 'es')}, con ${money(a.totalInterest)} de intereses. Marca cada mes cuando lo pagues.`,
  planMonth: 'Mes', planPaid: 'Pagado', planLeft: 'queda', planFooter: 'Hecho con la calculadora gratis para pagar deudas. Son estimaciones que suponen que tus tasas y mínimos no cambian.',
  fees: {
    name: 'Nombre del fondo', category: 'Tipo', er: 'Expense ratio (%)', balance: 'Tu saldo ($)',
    categories: { 'us-stock': 'Acciones de EE. UU.', 'intl-stock': 'Acciones internacionales', bond: 'Bonos', 'target-date': 'Fecha objetivo', stable: 'Valor estable o efectivo', other: 'Otro' },
    defaults: [['Índice S&P 500', 'us-stock', 0.04, 18000], ['Crecimiento grande (activo)', 'us-stock', 0.82, 12000], ['Índice internacional', 'intl-stock', 0.08, 6000], ['Fecha objetivo 2055', 'target-date', 0.65, 9000]],
    result: (r) => `<p class="big">${money(r.yearlyFees)} al año en comisiones de fondos</p>
      <p>Tu expense ratio promedio es <b>${r.avgExpenseRatio}%</b> sobre ${money(r.total)}.</p>
      <p>En ${r.years} años, las comisiones te podrían quitar unos <b>${money(r.feeDrag)}</b>: tendrías ${money(r.endWithFees)} en vez de ${money(r.endNoFees)}.</p>`,
    table: (rows) => `<table class="fees"><thead><tr><th>Fondo</th><th>Comisión</th><th>Al año</th></tr></thead><tbody>${rows}</tbody></table>`,
    cheaper: (name, er) => `Opción más barata del mismo tipo en tu plan: ${name} (${er}%)`,
    gap: (r) => (r.lowestCostGap > 1
      ? `<p>Si cada fondo costara lo mismo que el más barato de su tipo en tu plan, tendrías unos <b>${money(r.lowestCostGap)}</b> más en ${r.years} años. Eso solo no es razón para cambiarte: primero compara qué tiene cada fondo.</p>`
      : '<p>Ya tienes el fondo más barato de cada tipo que ingresaste.</p>'),
    note: 'Estimación: mismo rendimiento cada año, aportes repartidos como tus saldos y solo el expense ratio de los fondos (no los costos de administración del plan). Es educación, no asesoría de inversión.',
  },
  nextStep: 'Siguiente paso', affiliateNote: 'Enlace de afiliado: podemos ganar una comisión sin costo para ti.', getIt: 'Obtenerlo',
  copied: 'Enlace copiado', copyPrompt: 'Copia este enlace', sending: 'Enviando…', notConnected: 'El registro por correo aún no está conectado: configura email.action en config.js.',
};

export const TEXT = { en, es };
