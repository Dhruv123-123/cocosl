// Everything you need to edit lives here. Links that still contain REPLACE_ME are hidden
// automatically, so the site is safe to deploy before your affiliate accounts are approved.
export default {
  brand: 'Money Made Simple',
  siteUrl: 'https://moneymadesimple.netlify.app',       // the main brand site (site/ in the repo)
  calculatorsUrl: 'https://moneymadesimple.netlify.app/calculators',

  // Email capture. provider: 'sender' (Sender via /api/subscribe, Netlify Forms until it's connected), 'netlify' (works with zero setup on Netlify), 'buttondown', 'kit',
  // 'mailerlite', 'formspree' or 'none'. For anything except netlify, paste the form action URL.
  email: {
    provider: 'sender', // 'sender' (posts to /api/subscribe; falls back to Netlify Forms until Sender is connected) | 'netlify' | 'buttondown' | 'kit' | 'mailerlite' | 'formspree' | 'none'
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
      pitch: 'Recibe cada semana un paso sencillo para ordenar tu dinero, en español.',
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

  // The budget app (apps/budget). Used for the Budget Pro upsell box on the emergency fund
  // calculator. Relative paths work on the all-in-one apps site; use full URLs if the budget app
  // is deployed on its own. Set url to '' to hide the box.
  budgetApp: { url: '../../budget/', pricingUrl: '../../budget/pricing.html' },

  // Affiliate offers. Keep `disclosure` true for anything that pays you.
  // complianceReview: brokerage / adviser offers need a FINRA 2210 / SEC Marketing Rule check before going live.
  affiliates: {
    hysa: {
      es: { label: 'Comparar cuentas de ahorro de alto rendimiento', blurb: 'Los bancos en línea han pagado mucho más que el ahorro de los bancos grandes. Revisa el APY actual y el seguro de la FDIC antes de abrir una.' },
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
      es: { label: 'Revisar tasas de préstamos personales y transferencias de saldo', blurb: 'Solo conviene si la nueva tasa es más baja, las comisiones son pequeñas y dejas de usar la tarjeta vieja.' },
      label: 'Check personal loan and balance transfer rates',
      blurb: 'Only worth it if the new APR is lower, the fees are small, and you stop adding to the old card.',
      url: 'https://REPLACE_ME/debt',
    },
    credit: {
      es: { label: 'Revisar tu puntaje de crédito gratis', blurb: 'Tienes derecho a reportes de crédito gratis cada semana en AnnualCreditReport.com.' },
      label: 'Check your credit score for free',
      blurb: 'You are entitled to free weekly credit reports at AnnualCreditReport.com. Score tracking apps can alert you to changes.',
      url: 'https://REPLACE_ME/credit',
    },
    remit: {
      es: { label: 'Comparar empresas de envío de dinero', blurb: 'Compara al menos dos empresas con la misma cantidad el mismo día. Mira cuánto llega, no solo la comisión.' },
      label: 'Compare money transfer providers',
      blurb: 'Compare at least two providers with the same amount on the same day. Look at how much arrives, not just the fee.',
      url: 'https://REPLACE_ME/remit',
    },
  },

  // Embeddable widgets (see /embed/). The credit link back to you is the point of the free tier:
  // every embed is a backlink. allowUnbranded lets paying licensees add &brand=0.
  embed: {
    showOffers: false,
    allowUnbranded: false,
    licenceUrl: 'mailto:hello@example.com?subject=Calculator%20licence',
    // White-label licensees: { key, name, domains: ['example-cu.org'], cta: { label, url } }.
    // Their embeds (data-licence="KEY") drop the credit link and show their own button, on their domains only.
    // The demo key works on localhost so the embed page can preview it; leave it in.
    licensees: [
      { key: 'demo', name: 'Demo Credit Union', domains: ['localhost', '127.0.0.1'], cta: { label: 'Open a savings account', url: 'https://example.org/savings' } },
    ],
  },

  // Plausible (no cookies). Set the domain to turn on page views, outbound clicks and the
  // Affiliate Click / Product Click / Signup events. Optional plausibleHost for self-hosting. See docs/UTM.md.
  analytics: { plausibleDomain: '' },
};
