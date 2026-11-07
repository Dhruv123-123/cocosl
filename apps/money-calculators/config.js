// Everything you need to edit lives here. Links that still contain REPLACE_ME are hidden
// automatically, so the site is safe to deploy before your affiliate accounts are approved.
export default {
  brand: 'Money Made Simple',
  siteUrl: 'https://moneymadesimple.netlify.app',       // the main brand site (site/ in the repo)
  calculatorsUrl: 'https://moneymadesimple.netlify.app/calculators',

  // Email capture. provider: 'netlify' (works with zero setup on Netlify), 'buttondown', 'kit',
  // 'mailerlite', 'formspree' or 'none'. For anything except netlify, paste the form action URL.
  email: {
    provider: 'netlify',
    formName: 'calculator-signup',
    action: '',
    emailField: 'email',
    thanksUrl: 'https://moneymadesimple.netlify.app/free/thanks/',
    leadMagnet: 'The 7-Day Money Reset',
    pitch: 'Get the free 7-Day Money Reset: seven 15-minute tasks that sort out your money this week.',
    // Spanish pages: until Dinero Simple has its own lead magnet, signups go to a simple thank-you page.
    es: {
      formName: 'calculadoras-registro',
      thanksUrl: 'es/gracias/', // relative to the calculators' root
      title: 'Un paso de dinero por semana, gratis',
      pitch: 'Reciba cada semana un paso sencillo para ordenar su dinero, en español.',
    },
  },

  // The paid product each calculator can point to (Gumroad, Stripe Payment Link, Lemon Squeezy...).
  product: {
    name: 'The 20-Minute Budget',
    price: '$12',
    url: 'https://REPLACE_ME.gumroad.com/l/the-20-minute-budget',
    pitch: 'The spreadsheet and guide behind our budgeting videos. Set it up once, check it in 20 minutes a month.',
    es: null, // set { name, price, url, pitch } once a Spanish edition exists; English product is hidden on /es/
  },

  // Affiliate offers. Keep `disclosure` true for anything that pays you.
  // complianceReview: brokerage / adviser offers need a FINRA 2210 / SEC Marketing Rule check before going live.
  affiliates: {
    hysa: {
      es: { label: 'Comparar cuentas de ahorro de alto rendimiento', blurb: 'Los bancos en línea han pagado mucho más que el ahorro de los bancos grandes. Revise el APY actual y el seguro de la FDIC antes de abrir una.' },
      label: 'Compare high-yield savings accounts',
      blurb: 'Online banks have been paying far more than big-bank savings. Check the current APY and FDIC insurance before you open one.',
      url: 'https://REPLACE_ME/hysa',
    },
    brokerage: {
      es: { label: 'Abrir una cuenta de fondos indexados de bajo costo', blurb: 'Busque cuentas sin comisiones de mantenimiento, sin mínimos y con fondos indexados amplios de bajo costo.' },
      label: 'Open a low-cost index fund account',
      blurb: 'Look for no account fees, no minimums and broad index funds with low expense ratios.',
      url: 'https://REPLACE_ME/brokerage',
      complianceReview: true,
    },
    debt: {
      es: { label: 'Revisar tasas de préstamos personales y transferencias de saldo', blurb: 'Solo conviene si la nueva tasa es más baja, las comisiones son pequeñas y deja de usar la tarjeta vieja.' },
      label: 'Check personal loan and balance transfer rates',
      blurb: 'Only worth it if the new APR is lower, the fees are small, and you stop adding to the old card.',
      url: 'https://REPLACE_ME/debt',
    },
    credit: {
      es: { label: 'Revisar su puntaje de crédito gratis', blurb: 'Tiene derecho a reportes de crédito gratis cada semana en AnnualCreditReport.com.' },
      label: 'Check your credit score for free',
      blurb: 'You are entitled to free weekly credit reports at AnnualCreditReport.com. Score tracking apps can alert you to changes.',
      url: 'https://REPLACE_ME/credit',
    },
  },

  // Optional privacy-friendly analytics, e.g. Plausible: set the domain and it loads.
  analytics: { plausibleDomain: '' },
};
