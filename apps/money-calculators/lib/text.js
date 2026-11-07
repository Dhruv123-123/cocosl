// All words the calculators show, in English and Spanish. Numbers come from lib/calc.js.
// Spanish needs a native speaker's read before promotion (see apps/README.md).
import { money, duration } from './format.js';

const en = {
  fields: {
    initial: 'Starting amount ($)', monthly: 'Added each month ($)', annualRate: 'Yearly return (%)', years: 'Years',
    monthlyExpenses: 'Essential monthly costs ($)', monthsTarget: 'Months to cover', currentSaved: 'Already saved ($)', monthlySave: 'You can save each month ($)', apy: 'Savings APY (%)',
    balance: 'Balance ($)', monthlyDeposit: 'Added each month ($)', hyApy: 'High-yield APY (%)', compareApy: 'Your current APY (%)', months: 'Months',
    cardBalance: 'Card balance ($)', apr: 'APR (%)', minPercent: 'Minimum: % of balance + interest', minFloor: 'Minimum payment floor ($)', fixedPayment: 'What if you paid each month ($)',
    annualContribution: 'Yearly contribution, before tax ($)', currentRate: 'Your tax bracket now (%)', retirementRate: 'Expected tax rate in retirement (%)', yearsToWithdraw: 'Years until you withdraw', annualReturn: 'Yearly return (%)',
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
    monthlyExpenses: 'Gastos esenciales al mes ($)', monthsTarget: 'Meses a cubrir', currentSaved: 'Ya ahorrado ($)', monthlySave: 'Puede ahorrar al mes ($)', apy: 'APY de ahorro (%)',
    balance: 'Saldo ($)', monthlyDeposit: 'Depósito mensual ($)', hyApy: 'APY de alto rendimiento (%)', compareApy: 'Su APY actual (%)', months: 'Meses',
    cardBalance: 'Saldo de la tarjeta ($)', apr: 'Tasa anual APR (%)', minPercent: 'Mínimo: % del saldo + intereses', minFloor: 'Pago mínimo base ($)', fixedPayment: '¿Y si pagara cada mes? ($)',
    annualContribution: 'Aporte anual, antes de impuestos ($)', currentRate: 'Su tasa de impuestos hoy (%)', retirementRate: 'Tasa esperada al jubilarse (%)', yearsToWithdraw: 'Años hasta retirar', annualReturn: 'Rendimiento anual (%)',
    debtName: 'Nombre', debtBalance: 'Saldo ($)', debtApr: 'APR (%)', debtMin: 'Mínimo ($)', remove: 'Quitar', removeAria: 'Quitar esta deuda',
  },
  dur: (m) => duration(m, 'es'),
  growth: (v, r) => `<p class="big">${money(r.finalBalance)}</p>
    <p>Después de ${v.years} años habría aportado <b>${money(r.totalContributed)}</b> y el crecimiento sumaría
    <b>${money(r.totalGrowth)}</b>. El crecimiento es el ${Math.round((r.totalGrowth / Math.max(r.finalBalance, 1)) * 100)}% del total.</p>`,
  growthNote: (v) => `Supone un ${v.annualRate}% anual constante, capitalizado cada mes. Los rendimientos reales suben y bajan, y no están garantizados.`,
  chartLabel: (a, b) => `El saldo crece de ${a} a ${b}`, legendTotal: 'Saldo total', legendIn: 'Lo que usted aportó',
  efDone: (r) => `<p class="big">¡Ya lo tiene!</p><p>Su meta de ${money(r.target)} ya está cubierta. Guárdela en una cuenta aburrida, asegurada y separada del dinero para gastos.</p>`,
  efNoSave: (r) => `<p class="big">Agregue un monto mensual</p><p>Su meta es ${money(r.target)}. Aunque sean $25 por semana, ya avanza.</p>`,
  efStarter: (r) => `<p>Primera meta: <b>${money(r.starterGoal)}</b>. Cubre la mayoría de los gastos inesperados y es la parte más difícil.</p>`,
  ef: (v, r) => `<p class="big">${duration(r.months, 'es')}</p><p>Es el tiempo hasta tener <b>${money(r.target)}</b> (${v.monthsTarget} meses de gastos). Le faltan ${money(r.gap)}.</p>`,
  savings: (v, r) => `<p class="big">+${money(r.difference, 2)}</p>
    <p>Con un APY de ${v.apy}% ganaría <b>${money(r.interest, 2)}</b> de intereses en ${duration(v.months, 'es')}, comparado con <b>${money(r.compareInterest, 2)}</b> al ${v.compareApy}%.</p>
    <p class="note">Los APY cambian. Revise la tasa actual y que el banco esté asegurado por la FDIC (o la cooperativa por la NCUA).</p>`,
  ccFixed: (v, f, saved) => `<p>Si paga <b>${money(v.fixedPayment)}</b> fijos al mes, la liquida en <b>${duration(f.months, 'es')}</b> con ${money(f.interest)} de intereses. Se ahorraría <b>${money(saved)}</b>.</p>`,
  ccFixedNever: (v) => `<p>${money(v.fixedPayment)} al mes no cubre los intereses, así que el saldo nunca bajaría.</p>`,
  cc: (m, fixed) => `<p class="big">${duration(m.months, 'es')}</p>
    <p>Eso tarda pagando solo el mínimo. Pagaría <b>${money(m.interest)}</b> de intereses, ${money(m.paid)} en total.</p>${fixed}
    <p class="note">Cada emisor calcula el mínimo distinto. El recuadro de "advertencia de pago mínimo" en su estado de cuenta muestra los números reales de su tarjeta.</p>`,
  roth: (r) => {
    const head = r.winner === 'tie' ? 'Empate' : r.winner === 'roth' ? 'Gana la Roth' : 'Gana la Tradicional';
    return `<p class="big">${head}</p>
      <p>Después de impuestos: Roth <b>${money(r.roth)}</b>, Tradicional <b>${money(r.traditional)}</b>${r.winner === 'tie' ? '' : `, una diferencia de <b>${money(r.difference)}</b>`}.</p>
      <p>La pregunta que lo decide: <b>¿su tasa de impuestos es más alta hoy o después?</b> Más alta hoy favorece la Tradicional. Más alta después favorece la Roth. ¿No está seguro? Mucha gente divide sus aportes.</p>
      <p class="note">Simplificado: mismos dólares antes de impuestos, tasas fijas, sin aporte del empleador ni límites de ingreso. Revise los límites del IRS para el año en curso.</p>`;
  },
  debtInfeasible: '<p class="big">No se liquida con este presupuesto</p><p>Los pagos no superan los intereses. Suba el monto extra o busque una opción con tasa más baja.</p>',
  debtPaidIn: (name, m) => `${name}: liquidada en ${duration(m, 'es')}`,
  debtVerdict: (c) => (c.interestSaved > 0
    ? `Avalancha ahorra <b>${money(c.interestSaved)}</b> en intereses${c.monthsSaved > 0 ? ` y ${duration(c.monthsSaved, 'es')}` : ''}. Bola de nieve le da victorias más rápido. Elija el que va a mantener.`
    : 'Los dos órdenes cuestan casi lo mismo, así que elija bola de nieve por las victorias rápidas.'),
  debt: (a, s, verdict, listA, listS) => `<p class="big">Sin deudas en ${duration(a.months, 'es')}</p>
    <p>Pagando <b>${money(a.budget)}</b> al mes en total. ${verdict}</p>
    <div class="two"><div><h3>Avalancha (APR más alta primero)</h3><p>${money(a.totalInterest)} de intereses, ${duration(a.months, 'es')}</p>${listA}</div>
    <div><h3>Bola de nieve (saldo más chico primero)</h3><p>${money(s.totalInterest)} de intereses, ${duration(s.months, 'es')}</p>${listS}</div></div>`,
  defaultDebts: ['Tarjeta de crédito', 'Tarjeta de tienda', 'Préstamo de auto'],
  printAva: 'Imprimir mi plan avalancha', printSnow: 'Imprimir mi plan bola de nieve',
  planTitle: (strategy) => `Mi plan para salir de deudas (${strategy === 'avalanche' ? 'avalancha: APR más alta primero' : 'bola de nieve: saldo más chico primero'})`,
  planIntro: (a) => `Pague ${money(a.budget)} al mes en total. Sin deudas en ${duration(a.months, 'es')}, con ${money(a.totalInterest)} de intereses. Marque cada mes cuando lo pague.`,
  planMonth: 'Mes', planPaid: 'Pagado', planLeft: 'queda', planFooter: 'Hecho con la calculadora gratis para pagar deudas. Son estimaciones que suponen que sus tasas y mínimos no cambian.',
  nextStep: 'Siguiente paso', affiliateNote: 'Enlace de afiliado: podemos ganar una comisión sin costo para usted.', getIt: 'Obtenerlo',
  copied: 'Enlace copiado', copyPrompt: 'Copie este enlace', sending: 'Enviando…', notConnected: 'El registro por correo aún no está conectado: configure email.action en config.js.',
};

export const TEXT = { en, es };
