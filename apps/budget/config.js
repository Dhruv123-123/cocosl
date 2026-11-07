// The 20-Minute Budget app settings. Checkout links containing REPLACE_ME are hidden.
export default {
  appName: 'The 20-Minute Budget',
  brand: 'Money Made Simple',
  siteUrl: 'https://moneymadesimple.netlify.app',
  // Buy buttons for Pro (index.html upgrade dialog and pricing.html). Paste a checkout link from
  // ONE provider per plan; links containing REPLACE_ME stay hidden. Lemon Squeezy is the easiest
  // (it handles sales tax as merchant of record and issues license keys):
  //   Lemon Squeezy  https://STORE.lemonsqueezy.com/buy/VARIANT-ID   + LEMONSQUEEZY_STORE_ID on Netlify
  //   Gumroad        https://STORE.gumroad.com/l/PRODUCT              + GUMROAD_PRODUCT_ID on Netlify
  //   Stripe         https://buy.stripe.com/LINK-ID                   + STRIPE_SECRET_KEY on Netlify,
  //                  success URL https://YOUR-SITE/budget/?session_id={CHECKOUT_SESSION_ID}
  // Full steps: CHECKOUT.md.
  pricing: {
    monthly: { label: '$3/month', note: 'Cancel any time', url: 'https://REPLACE_ME.lemonsqueezy.com/buy/budget-pro-monthly' },
    lifetime: { label: '$29 once', note: 'Pay once, keep Pro', best: true, url: 'https://REPLACE_ME.lemonsqueezy.com/buy/budget-pro-lifetime' },
    stripe: { label: 'Pay by card', note: 'Stripe checkout', url: '' },
  },
  // Price wording used in upgrade prompts and the pricing page.
  priceLine: '$3/month or $29 once',
  // Shown on pricing.html. Your call: set the policy you will honour, or '' to hide it.
  refundPolicy: 'Changed your mind? Reply to your receipt within 30 days for a full refund.',
  // Email capture for the free subscription finder (same options as the calculators' config).
  email: {
    provider: 'netlify',
    formName: 'subscription-finder',
    action: '',
    emailField: 'email',
    thanksUrl: 'https://moneymadesimple.netlify.app/free/thanks/',
  },
  // Upsell on the subscription finder (from the product ladder in launch/products/).
  billCutKit: {
    name: 'The Bill Cut Kit',
    price: '$5',
    url: 'https://REPLACE_ME.gumroad.com/l/bill-cut-kit',
    pitch: 'Scripts and a checklist for calling your phone, internet and insurance providers to get a lower rate.',
  },
  // Upsell on the Money Dashboard maker (money-dashboard.html, tablero-dinero.html). Hidden while the link has REPLACE_ME.
  sheetTemplate: {
    name: 'Money Dashboard Pro', nameEs: 'Tablero de dinero Pro',
    price: '$12',
    url: 'https://REPLACE_ME.gumroad.com/l/money-dashboard-pro',
    pitch: 'The version you keep using: paste each month in and get 12-month trends, budget vs actual in red and green, sinking funds and charts. Google Sheets and Excel.',
    pitchEs: 'La versión para usar cada mes: pega tus movimientos y ve tendencias de 12 meses, presupuesto vs real, fondos de ahorro y gráficas. Google Sheets y Excel.',
  },
  // Wedding budget spreadsheet (products thread). Shown on wedding-budget.html once the URL is live.
  weddingTemplate: {
    name: 'Wedding Budget Spreadsheet', nameEs: 'Hoja de presupuesto de boda',
    price: '[PRICE]',
    url: 'https://REPLACE_ME.etsy.com/listing/wedding-budget-spreadsheet',
    pitch: 'Vendors, deposits and due dates, guest list and RSVP tracker in one sheet. Paste your plan from this page straight in. Google Sheets and Excel.',
    pitchEs: 'Proveedores, anticipos y fechas de pago, lista de invitados y confirmaciones en una sola hoja. Pega aquí tu plan. Google Sheets y Excel.',
  },
  // Paid add-on shown on Rate My Budget (Gumroad, Stripe Payment Link or a Calendly paid booking).
  review: {
    name: 'Personal budget review',
    price: '$19',
    url: 'https://REPLACE_ME.gumroad.com/l/budget-review',
    pitch: 'Send your numbers and get a written review within 48 hours: what to change first, with the maths. Drafted with AI help, checked and signed off by a person.',
  },
  // Privacy-friendly analytics (Plausible, no cookies). Set the domain to turn it on. See docs/UTM.md.
  analytics: { plausibleDomain: '' },
  // 'web' (default), 'play' or 'appstore'. Store builds hide the web checkout links, because
  // both stores require their own billing for in-app digital purchases. See STORES.md.
  distribution: 'web',
  verifyEndpoint: '/api/verify-license',
  proFeatures: [
    'Unlimited categories',
    'Import your bank\'s CSV export, auto-sorted into categories',
    'Every month kept: look back and plan ahead',
    'Unlimited savings goals',
    'Bill negotiation tracker for every bill, with call scripts and promo-end reminders',
    'Countdown for every 0% and deferred-interest deal, with calendar reminders',
  ],
};
