// Labels and result text for the student loan chooser, rent vs buy, tax refund estimator and debt chart, in English and Spanish.
import { money } from './format.js';

const yrs = (m, es) => {
  const y = Math.floor(m / 12);
  const mo = m % 12;
  if (es) return [y ? `${y} año${y === 1 ? '' : 's'}` : '', mo ? `${mo} mes${mo === 1 ? '' : 'es'}` : ''].filter(Boolean).join(' y ') || '0 meses';
  return [y ? `${y} year${y === 1 ? '' : 's'}` : '', mo ? `${mo} month${mo === 1 ? '' : 's'}` : ''].filter(Boolean).join(' ') || '0 months';
};

const SL_SOURCES = '<a href="https://studentaid.gov/articles/save/" target="_blank" rel="noopener">StudentAid.gov</a>, <a href="https://edfinancial.studentaid.gov/income-driven-repaymentinformation-center/repayment-plan-comparison" target="_blank" rel="noopener">FSA plan comparison</a>';

const TR_SOURCES = (es) => `${es ? 'Fuentes' : 'Sources'}: <a href="https://www.irs.gov/pub/irs-drop/rp-25-32.pdf" target="_blank" rel="noopener">IRS Rev. Proc. 2025-32</a> (${es ? 'tramos, deducción estándar, crédito por hijos' : 'brackets, standard deduction, child tax credit'}), <a href="https://www.irs.gov/credits-deductions/individuals/child-tax-credit" target="_blank" rel="noopener">IRS: Child Tax Credit</a>, <a href="https://www.irs.gov/newsroom/working-families-tax-cuts-tax-deductions-for-working-americans-and-seniors" target="_blank" rel="noopener">IRS: ${es ? 'deducciones por propinas, horas extra y mayores de 65' : 'tips, overtime and senior deductions'}</a>.`;
const EITC_URL = 'https://www.irs.gov/credits-deductions/individuals/earned-income-tax-credit/use-the-eitc-assistant';
const W4_URL = 'https://www.irs.gov/individuals/tax-withholding-estimator';
const pct = (x) => `${Math.round(x * 1000) / 10}%`;
const trRow = (label, v, neg) => (v ? `<tr><td>${label}</td><td>${neg ? '−' : ''}${money(v, 2)}</td></tr>` : '');

export const EXTRA = {
  en: {
    f: {
      slBalance: 'Total federal loan balance ($)', slRate: 'Average interest rate (%)', slAgi: 'Yearly income, AGI ($)', slHousehold: 'People in your household', slDependents: 'Dependents you claim', slGrowth: 'Raise you expect each year (%)',
      slCohort: 'When were your loans paid out?', slBefore: 'All before July 1, 2026', slAfter: 'At least one on or after July 1, 2026',
      slNew2014: 'First federal loan on or after July 1, 2014?', yes: 'Yes', no: 'No',
      slRegion: 'Where you live', contiguous: 'Lower 48 states or DC', alaska: 'Alaska', hawaii: 'Hawaii',
      rbPrice: 'Home price ($)', rbDown: 'Down payment (%)', rbRate: 'Mortgage rate (%)', rbTerm: 'Mortgage length (years)', rbTax: 'Property tax (% of value a year)', rbIns: 'Home insurance a year ($)', rbHoa: 'HOA a month ($)', rbUpkeep: 'Upkeep (% of value a year)', rbClosing: 'Closing costs to buy (%)', rbSelling: 'Costs to sell (%)', rbApp: 'Home value growth a year (%)',
      rbRent: 'Rent a month ($)', rbRentGrowth: 'Rent increase a year (%)', rbRentersIns: "Renter's insurance a month ($)", rbReturn: 'Investment return a year (%)', rbYears: 'Years you plan to stay',
      trFiling: 'Filing status', trSingle: 'Single', trMarried: 'Married filing jointly', trHoh: 'Head of household',
      trWages: 'Wages for 2026, box 1 of your W-2 ($)', trWithheld: 'Federal tax withheld, box 2 ($)', trOther: 'Other taxable income, like interest ($)', trEstimated: 'Estimated tax payments you made ($)',
      trKids: 'Children under 17', trOtherDeps: 'Other dependents', trTips: 'Tips you were paid ($)', trOvertime: 'Overtime premium, the extra half ($)', trSeniors: 'People 65 or older on the return',
    },
    plan: { standard: 'Standard (10 years)', graduated: 'Graduated (10 years)', extended: 'Extended (25 years)', ibr: 'Income-Based (IBR)', rap: 'Repayment Assistance Plan (RAP)', tiered: 'Tiered Standard' },
    loans(r) {
      const p = Object.fromEntries(r.plans.map((x) => [x.key, x]));
      const rows = r.plans.map((x) => `<tr><td>${this.plan[x.key]}${x.key === 'tiered' ? ` <small>(${x.years} years)</small>` : ''}${x.key === r.cheapest ? ' <span class="badge-mini">lowest total</span>' : ''}${x.key === r.lowestPayment ? ' <span class="badge-mini">lowest payment</span>' : ''}</td>
        <td>${money(x.first)}${Math.abs(x.last - x.first) > 1 && x.forgiven === 0 ? `<small>to ${money(x.last)}</small>` : ''}</td><td>${yrs(x.months)}</td><td>${money(x.paid)}</td><td>${x.forgiven ? money(x.forgiven) : '—'}</td></tr>`).join('');
      const low = p[r.lowestPayment];
      const cheap = p[r.cheapest];
      return `<p class="big">${this.plan[cheap.key]}</p>
        <p>costs the least overall: <b>${money(cheap.paid)}</b>${cheap.forgiven ? `, with ${money(cheap.forgiven)} forgiven at the end` : ''}. ${low.key !== cheap.key ? `If you need the smallest payment now, <b>${this.plan[low.key]}</b> starts at <b>${money(low.first)}</b> a month but costs ${money(low.paid - cheap.paid)} more in total.` : 'It also has the smallest payment to start.'}</p>
        <div class="table-scroll" tabindex="0" role="region" aria-label="Plan comparison"><table class="split-table plans-table"><thead><tr><th>Plan</th><th>Monthly</th><th>Paid off in</th><th>Total paid</th><th>Forgiven</th></tr></thead><tbody>${rows}</tbody></table></div>
        <p class="note"><b>Verify with your loan servicer before you switch.</b> Your servicer (or the Loan Simulator on StudentAid.gov) uses your exact loans, rates and tax return. ${r.cohort === 'after2026' ? 'With a loan paid out on or after July 1, 2026, Tiered Standard and RAP are your only plans.' : 'SAVE ended in March 2026. PAYE and ICR close by July 1, 2028, so they are not shown. Public Service Loan Forgiveness (10 years of payments) is not modeled.'} Forgiven amounts may be taxed as income. Rules from ${SL_SOURCES}; IBR uses 150% of the 2026 poverty guideline (${money(r.poverty)} for your household size).</p>`;
    },
    rentBuy(r) {
      const head = r.winner === 'tie' ? "It's about even" : r.winner === 'buy' ? 'Buying comes out ahead' : 'Renting comes out ahead';
      return `<p class="big">${head}</p>
        <p>After ${r.years} year${r.years === 1 ? '' : 's'}, buying leaves you with about <b>${money(r.buyer)}</b> and renting (investing the difference) about <b>${money(r.renter)}</b>, a gap of <b>${money(Math.abs(r.diff))}</b>.</p>
        <p>${r.breakEven ? `Buying starts to win after about <b>${r.breakEven} year${r.breakEven === 1 ? '' : 's'}</b>.` : "With these numbers, buying doesn't catch up within 30 years."}</p>
        <table class="split-table"><tbody>
          <tr><td>Cash to buy (down payment and closing)</td><td>${money(r.upfront)}</td></tr>
          <tr><td>Owning, first month (mortgage, tax, insurance, HOA, upkeep)</td><td>${money(r.firstMonth.own)}</td></tr>
          <tr><td>Renting, first month</td><td>${money(r.firstMonth.rent)}</td></tr>
          <tr><td>Interest in your first mortgage payment</td><td>${money(r.firstMonth.interest)} of ${money(r.firstMonth.mortgage)}</td></tr>
        </tbody></table>
        ${r.pmiLikely ? '<p>With less than 20% down, lenders usually add mortgage insurance (PMI), which is not included here, so buying costs a bit more than shown.</p>' : ''}
        <p class="note">Estimate only. It assumes whoever pays less each month invests the difference. It leaves out tax deductions, PMI and taxes on gains. Home prices, rents and returns are your guesses, so try a few.</p>`;
    },
    refund(r) {
      const head = r.refund >= 0 ? `Estimated refund: ${money(r.refund, 2)}` : `You may owe: ${money(-r.refund, 2)}`;
      const rows = [
        trRow('Total income (AGI)', r.agi), trRow('Standard deduction', r.standard, true), trRow('No tax on tips', r.tipsDed, true), trRow('No tax on overtime', r.otDed, true), trRow('Senior deduction (65+)', r.seniorDed, true),
        trRow('Taxable income', r.taxable) || '<tr><td>Taxable income</td><td>$0.00</td></tr>', trRow('Tax before credits', r.tax), trRow('Child and dependent credits used', r.nonrefundable, true),
        `<tr><td><b>Your 2026 federal income tax</b></td><td><b>${money(r.owed, 2)}</b></td></tr>`, trRow('Already paid (withholding and estimates)', r.paid), trRow('Refundable child credit', r.refundableCredit),
      ].join('');
      return `<p class="big">${head}</p>
        <p>Your tax comes to <b>${money(r.owed, 2)}</b>, an effective rate of ${pct(r.effective)}. Your top bracket is ${pct(r.marginal)}.${r.refund >= 0 ? ` You paid in ${money(r.paid, 2)}${r.refundableCredit ? ` and get ${money(r.refundableCredit, 2)} of refundable child credit` : ''}, so the difference comes back to you.` : ' You paid in less than you owe. File by April 15, 2027 and pay the balance to avoid penalties.'}</p>
        <div class="table-scroll" tabindex="0" role="region" aria-label="How we got there"><table class="split-table"><tbody>${rows}</tbody></table></div>
        ${r.bigRefund ? `<p>A refund this size is money you lent the IRS for free. To get it in your paychecks instead, use the <a href="${W4_URL}" target="_blank" rel="noopener">IRS Tax Withholding Estimator</a> and give your employer a new W-4.</p>` : ''}
        ${r.owesMuch ? `<p>To avoid owing next year, raise your withholding with the <a href="${W4_URL}" target="_blank" rel="noopener">IRS Tax Withholding Estimator</a>.</p>` : ''}
        ${r.eitcMaybe ? `<p>You may also qualify for the Earned Income Tax Credit, worth up to $8,231 for 2026, which would add to your refund. It isn't included here. Check with the <a href="${EITC_URL}" target="_blank" rel="noopener">IRS EITC Assistant</a>.</p>` : ''}
        <p class="note">Estimate for the 2026 tax year (the return you file in early 2027), using the standard deduction. It leaves out itemizing, the EITC, education and other credits, self-employment tax and state tax. The tips and overtime deductions shrink above $150,000 of income ($300,000 joint), and the senior deduction above $75,000 ($150,000 joint); their phase-out rates come from the law, so check the final IRS forms. ${TR_SOURCES(false)}</p>`;
    },
    debtChart: (start, months) => `Total debt falls from ${start} to $0 in ${yrs(months)}`, debtLegendA: 'Avalanche', debtLegendS: 'Snowball', debtChartTitle: 'Total balance over time', debtChartNow: 'Now', debtSame: 'Same order here, so the lines overlap.', debtChartEnd: (m) => `${yrs(m)}`,
  },
  es: {
    f: {
      slBalance: 'Saldo total de préstamos federales ($)', slRate: 'Tasa de interés promedio (%)', slAgi: 'Ingreso anual, AGI ($)', slHousehold: 'Personas en tu hogar', slDependents: 'Dependientes que declaras', slGrowth: 'Aumento de sueldo esperado al año (%)',
      slCohort: '¿Cuándo recibiste tus préstamos?', slBefore: 'Todos antes del 1 de julio de 2026', slAfter: 'Al menos uno desde el 1 de julio de 2026',
      slNew2014: '¿Primer préstamo federal desde el 1 de julio de 2014?', yes: 'Sí', no: 'No',
      slRegion: 'Dónde vives', contiguous: 'Los 48 estados contiguos o DC', alaska: 'Alaska', hawaii: 'Hawái',
      rbPrice: 'Precio de la casa ($)', rbDown: 'Enganche (%)', rbRate: 'Tasa de la hipoteca (%)', rbTerm: 'Plazo de la hipoteca (años)', rbTax: 'Impuesto predial (% del valor al año)', rbIns: 'Seguro de la casa al año ($)', rbHoa: 'HOA al mes ($)', rbUpkeep: 'Mantenimiento (% del valor al año)', rbClosing: 'Costos de cierre al comprar (%)', rbSelling: 'Costos al vender (%)', rbApp: 'Aumento del valor de la casa al año (%)',
      rbRent: 'Renta al mes ($)', rbRentGrowth: 'Aumento de la renta al año (%)', rbRentersIns: 'Seguro de inquilino al mes ($)', rbReturn: 'Rendimiento de inversión al año (%)', rbYears: 'Años que piensas quedarte',
      trFiling: 'Estado civil para la declaración', trSingle: 'Soltero', trMarried: 'Casados, declaración conjunta', trHoh: 'Cabeza de familia',
      trWages: 'Salario de 2026, casilla 1 de tu W-2 ($)', trWithheld: 'Impuesto federal retenido, casilla 2 ($)', trOther: 'Otros ingresos gravables, como intereses ($)', trEstimated: 'Pagos de impuesto estimado que hiciste ($)',
      trKids: 'Hijos menores de 17', trOtherDeps: 'Otros dependientes', trTips: 'Propinas que recibiste ($)', trOvertime: 'Pago extra por horas extra, la mitad adicional ($)', trSeniors: 'Personas de 65 años o más en la declaración',
    },
    plan: { standard: 'Estándar (10 años)', graduated: 'Graduado (10 años)', extended: 'Extendido (25 años)', ibr: 'Basado en ingresos (IBR)', rap: 'Plan de Asistencia de Pago (RAP)', tiered: 'Estándar escalonado' },
    loans(r) {
      const p = Object.fromEntries(r.plans.map((x) => [x.key, x]));
      const rows = r.plans.map((x) => `<tr><td>${this.plan[x.key]}${x.key === r.cheapest ? ' <span class="badge-mini">menor total</span>' : ''}${x.key === r.lowestPayment ? ' <span class="badge-mini">menor pago</span>' : ''}</td>
        <td>${money(x.first)}</td><td>${yrs(x.months, true)}</td><td>${money(x.paid)}</td><td>${x.forgiven ? money(x.forgiven) : '—'}</td></tr>`).join('');
      const cheap = p[r.cheapest];
      const low = p[r.lowestPayment];
      return `<p class="big">${this.plan[cheap.key]}</p>
        <p>es el que menos cuesta en total: <b>${money(cheap.paid)}</b>. ${low.key !== cheap.key ? `Si necesitas el pago más bajo ahora, <b>${this.plan[low.key]}</b> empieza en <b>${money(low.first)}</b> al mes, pero cuesta ${money(low.paid - cheap.paid)} más en total.` : 'También tiene el pago inicial más bajo.'}</p>
        <div class="table-scroll" tabindex="0" role="region" aria-label="Comparación de planes"><table class="split-table plans-table"><thead><tr><th>Plan</th><th>Pago mensual</th><th>Se paga en</th><th>Total pagado</th><th>Perdonado</th></tr></thead><tbody>${rows}</tbody></table></div>
        <p class="note"><b>Confírmalo con tu administrador de préstamos (servicer) antes de cambiar de plan.</b> El plan SAVE terminó en marzo de 2026; PAYE e ICR cierran a más tardar el 1 de julio de 2028. No se calcula el perdón por servicio público (PSLF). Lo perdonado puede pagar impuestos. Reglas de ${SL_SOURCES}.</p>`;
    },
    rentBuy(r) {
      const head = r.winner === 'tie' ? 'Sale casi igual' : r.winner === 'buy' ? 'Comprar sale mejor' : 'Rentar sale mejor';
      return `<p class="big">${head}</p>
        <p>Después de ${r.years} año${r.years === 1 ? '' : 's'}, comprando tendrías unos <b>${money(r.buyer)}</b> y rentando (e invirtiendo la diferencia) unos <b>${money(r.renter)}</b>: una diferencia de <b>${money(Math.abs(r.diff))}</b>.</p>
        <p>${r.breakEven ? `Comprar empieza a ganar después de unos <b>${r.breakEven} años</b>.` : 'Con estos números, comprar no alcanza a rentar en 30 años.'}</p>
        <table class="split-table"><tbody>
          <tr><td>Efectivo para comprar (enganche y cierre)</td><td>${money(r.upfront)}</td></tr>
          <tr><td>Ser dueño, primer mes</td><td>${money(r.firstMonth.own)}</td></tr>
          <tr><td>Rentar, primer mes</td><td>${money(r.firstMonth.rent)}</td></tr>
        </tbody></table>
        ${r.pmiLikely ? '<p>Con menos de 20% de enganche, el banco suele cobrar seguro hipotecario (PMI), que no está incluido.</p>' : ''}
        <p class="note">Solo una estimación. Supone que quien paga menos cada mes invierte la diferencia. No incluye deducciones de impuestos, PMI ni impuestos sobre ganancias.</p>`;
    },
    refund(r) {
      const head = r.refund >= 0 ? `Reembolso estimado: ${money(r.refund, 2)}` : `Podrías deber: ${money(-r.refund, 2)}`;
      const rows = [
        trRow('Ingreso total (AGI)', r.agi), trRow('Deducción estándar', r.standard, true), trRow('Sin impuesto sobre propinas', r.tipsDed, true), trRow('Sin impuesto sobre horas extra', r.otDed, true), trRow('Deducción para mayores de 65', r.seniorDed, true),
        trRow('Ingreso gravable', r.taxable) || '<tr><td>Ingreso gravable</td><td>$0.00</td></tr>', trRow('Impuesto antes de créditos', r.tax), trRow('Créditos por hijos y dependientes usados', r.nonrefundable, true),
        `<tr><td><b>Tu impuesto federal de 2026</b></td><td><b>${money(r.owed, 2)}</b></td></tr>`, trRow('Ya pagado (retenciones y estimados)', r.paid), trRow('Crédito reembolsable por hijos', r.refundableCredit),
      ].join('');
      return `<p class="big">${head}</p>
        <p>Tu impuesto es de <b>${money(r.owed, 2)}</b>, una tasa efectiva de ${pct(r.effective)}. Tu tramo más alto es ${pct(r.marginal)}.${r.refund >= 0 ? ` Pagaste ${money(r.paid, 2)}${r.refundableCredit ? ` y recibes ${money(r.refundableCredit, 2)} de crédito reembolsable por hijos` : ''}, así que la diferencia te regresa.` : ' Pagaste menos de lo que debes. Declara antes del 15 de abril de 2027 y paga el saldo para evitar multas.'}</p>
        <div class="table-scroll" tabindex="0" role="region" aria-label="Cómo llegamos al resultado"><table class="split-table"><tbody>${rows}</tbody></table></div>
        ${r.bigRefund ? `<p>Un reembolso así es dinero que le prestaste gratis al IRS. Para recibirlo en tus cheques, usa el <a href="${W4_URL}" target="_blank" rel="noopener">estimador de retenciones del IRS</a> (en inglés) y dale un W-4 nuevo a tu empleador.</p>` : ''}
        ${r.owesMuch ? `<p>Para no deber el próximo año, sube tu retención con el <a href="${W4_URL}" target="_blank" rel="noopener">estimador de retenciones del IRS</a>.</p>` : ''}
        ${r.eitcMaybe ? `<p>También podrías calificar para el Crédito por Ingreso del Trabajo (EITC), de hasta $8,231 en 2026, que aumentaría tu reembolso. No está incluido aquí. Revísalo con el <a href="${EITC_URL}" target="_blank" rel="noopener">asistente del EITC del IRS</a>.</p>` : ''}
        <p class="note">Estimación para el año fiscal 2026 (la declaración que presentas a inicios de 2027), con la deducción estándar. No incluye deducciones detalladas, el EITC, créditos de educación u otros, impuesto de trabajo por cuenta propia ni impuesto estatal. Las deducciones por propinas y horas extra bajan con ingresos de más de $150,000 ($300,000 en conjunta), y la de mayores de 65 con más de $75,000 ($150,000 en conjunta); sus tasas de reducción vienen de la ley, así que revisa los formularios finales del IRS. ${TR_SOURCES(true)}</p>`;
    },
    debtChart: (start, months) => `La deuda total baja de ${start} a $0 en ${yrs(months, true)}`, debtLegendA: 'Avalancha', debtLegendS: 'Bola de nieve', debtChartTitle: 'Saldo total con el tiempo', debtChartNow: 'Hoy', debtSame: 'Aquí el orden es el mismo, así que las líneas se enciman.', debtChartEnd: (m) => `${yrs(m, true)}`,
  },
};
