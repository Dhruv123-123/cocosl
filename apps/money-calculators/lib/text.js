// All words the calculators show, in English and Spanish. Numbers come from lib/calc.js.
// Spanish uses tú and neutral Latin American vocabulary to match the Dinero Simple voice
// (carro, celular, cuenta de cheques; US product names like 401(k), Roth IRA, APY kept in English).
// It needs a native speaker's read before promotion (see apps/README.md).
import { money, duration } from './format.js';

const en = {
  fields: {
    initial: 'Starting amount ($)', monthly: 'Added each month ($)', annualRate: 'Yearly return (%)', years: 'Years',
    monthlyExpenses: 'Essential monthly costs ($)', monthsTarget: 'Months to cover', currentSaved: 'Already saved ($)', monthlySave: 'You can save each month ($)', apy: 'Savings APY (%)',
    balance: 'Balance ($)', monthlyDeposit: 'Added each month ($)', hyApy: 'High-yield APY (%)', compareApy: 'Your current APY (%)', months: 'Months',
    cardBalance: 'Card balance ($)', apr: 'APR (%)', minPercent: 'Minimum: % of balance + interest', minFloor: 'Minimum payment floor ($)', fixedPayment: 'What if you paid each month ($)',
    annualContribution: 'Yearly contribution, before tax ($)', currentRate: 'Your tax bracket now (%)', retirementRate: 'Expected tax rate in retirement (%)', yearsToWithdraw: 'Years until you withdraw', annualReturn: 'Yearly return (%)',
    salary: 'Yearly salary ($)', pretax401k: 'Pre-tax 401(k) per year ($)', pretaxHealth: 'Pre-tax health premiums per year ($)', stateRate: 'State income tax, effective (%)', payPeriods: 'Paychecks per year', filing: 'Filing status', single: 'Single', married: 'Married filing jointly',
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
  ef: (v, r) => `<p class="big">${duration(r.months)}</p><p>That's how long until you have <b>${money(r.target)}</b> (${v.monthsTarget} months of costs). You need ${money(r.gap)} more.</p>`,
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
      <tr><td>State income tax</td><td>${money(r.state)}</td></tr>
      <tr><td>Pre-tax 401(k) and health</td><td>${money(r.pretax401k + r.pretaxHealth)}</td></tr>
    </tbody></table>
    <p>Your top federal bracket is <b>${Math.round(r.marginal * 100)}%</b>, but you pay about ${Math.round(r.effectiveFederal * 1000) / 10}% of your salary in federal income tax overall.</p>
    <p class="note">Estimate for tax year 2026 using the standard deduction. It doesn't include credits (like the child tax credit), local taxes, or your exact W-4. States without a wage tax: Alaska, Florida, Nevada, New Hampshire, South Dakota, Tennessee, Texas, Washington, Wyoming.</p>`,
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
  nextStep: 'Next step', affiliateNote: 'Affiliate link: we may earn a commission at no cost to you.', getIt: 'Get it',
  copied: 'Link copied', copyPrompt: 'Copy this link', sending: 'Sending…', notConnected: 'Email signup is not connected yet: set email.action in config.js.',
};

const es = {
  fields: {
    initial: 'Monto inicial ($)', monthly: 'Aporte mensual ($)', annualRate: 'Rendimiento anual (%)', years: 'Años',
    monthlyExpenses: 'Gastos esenciales al mes ($)', monthsTarget: 'Meses a cubrir', currentSaved: 'Ya ahorrado ($)', monthlySave: 'Puedes ahorrar al mes ($)', apy: 'APY de ahorro (%)',
    balance: 'Saldo ($)', monthlyDeposit: 'Depósito mensual ($)', hyApy: 'APY de alto rendimiento (%)', compareApy: 'Tu APY actual (%)', months: 'Meses',
    cardBalance: 'Saldo de la tarjeta ($)', apr: 'Tasa anual APR (%)', minPercent: 'Mínimo: % del saldo + intereses', minFloor: 'Pago mínimo base ($)', fixedPayment: '¿Y si pagaras cada mes? ($)',
    annualContribution: 'Aporte anual, antes de impuestos ($)', currentRate: 'Tu tasa de impuestos hoy (%)', retirementRate: 'Tasa esperada al jubilarte (%)', yearsToWithdraw: 'Años hasta retirar', annualReturn: 'Rendimiento anual (%)',
    salary: 'Salario anual ($)', pretax401k: '401(k) antes de impuestos al año ($)', pretaxHealth: 'Seguro médico antes de impuestos al año ($)', stateRate: 'Impuesto estatal efectivo (%)', payPeriods: 'Cheques de pago al año', filing: 'Estado civil para impuestos', single: 'Soltero/a', married: 'Casados, declaración conjunta',
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
  ef: (v, r) => `<p class="big">${duration(r.months, 'es')}</p><p>Es el tiempo hasta tener <b>${money(r.target)}</b> (${v.monthsTarget} meses de gastos). Te faltan ${money(r.gap)}.</p>`,
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
      <tr><td>Impuesto estatal</td><td>${money(r.state)}</td></tr>
      <tr><td>401(k) y seguro médico antes de impuestos</td><td>${money(r.pretax401k + r.pretaxHealth)}</td></tr>
    </tbody></table>
    <p>Tu tramo federal más alto es <b>${Math.round(r.marginal * 100)}%</b>, pero en total pagas cerca del ${Math.round(r.effectiveFederal * 1000) / 10}% de tu salario en impuesto federal.</p>
    <p class="note">Estimación para el año fiscal 2026 con la deducción estándar. No incluye créditos (como el crédito por hijos), impuestos locales ni tu W-4 exacto. Estados sin impuesto al salario: Alaska, Florida, Nevada, New Hampshire, Dakota del Sur, Tennessee, Texas, Washington y Wyoming.</p>`,
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
  nextStep: 'Siguiente paso', affiliateNote: 'Enlace de afiliado: podemos ganar una comisión sin costo para ti.', getIt: 'Obtenerlo',
  copied: 'Enlace copiado', copyPrompt: 'Copia este enlace', sending: 'Enviando…', notConnected: 'El registro por correo aún no está conectado: configura email.action en config.js.',
};

export const TEXT = { en, es };
