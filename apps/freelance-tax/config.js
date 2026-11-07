// Everything you need to edit lives here. Links that still contain REPLACE_ME are hidden
// automatically, so the site is safe to deploy before the product and affiliates are live.
export default {
  brand: '1099 Money',
  handle: '@1099money',
  siteUrl: 'https://1099money.netlify.app',            // update after deploying

  // Email capture. provider: 'netlify' (zero setup on Netlify), 'buttondown', 'kit', 'mailerlite',
  // 'formspree' or 'none'. For anything except netlify, paste the form action URL.
  email: {
    provider: 'netlify',
    formName: 'tax-calendar',                          // one list for the calculator and the /free/ page
    action: '',
    emailField: 'email',
    // Where the form sends people: each form's data-thanks attribute (the /free/thanks/ download page).
    pitch: 'Get the free 2027 Freelancer Tax Calendar (every federal date, a payment checklist and a set-aside table), plus a reminder a week before each quarterly deadline.',
  },

  // The paid product (Gumroad, Stripe Payment Link, Lemon Squeezy...).
  product: {
    name: 'The Quarterly Tax Tracker',
    price: '$15',
    url: 'https://REPLACE_ME.gumroad.com/l/quarterly-tax-tracker',
    pitch: 'Log income, expenses and miles as you go. Before each deadline it tells you what to pay, with the safe harbor and a set-aside check built in. Spreadsheet + 10-page guide.',
  },

  // The rest of the ladder (launch/1099-money/products/). Shown on the download page once the URL is real.
  upsells: [
    {
      name: 'The Freelancer Money Bundle',
      price: '$49',
      url: 'https://REPLACE_ME.gumroad.com/l/freelancer-money-bundle',
      pitch: 'The tracker, plus a tax-aware rate calculator, proposal, contract, change order and invoice templates, and 14 client email scripts (bundle only).',
    },
    {
      name: 'The Rate & Contract Kit',
      price: '$29',
      url: 'https://REPLACE_ME.gumroad.com/l/rate-contract-kit',
      pitch: 'Work out a rate that covers your taxes, then get it in writing: rate calculator, project pricer, proposal, services agreement, change order and invoices.',
    },
  ],

  // Affiliate offers. Keep the disclosure on anything that pays you.
  // `banking` and `invoicing` are the two offers under the calculator result.
  affiliates: {
    banking: {
      label: 'Open a separate business checking account',
      blurb: 'Keep client money and tax savings out of your personal account. Look for no monthly fee and FDIC insurance (for apps, check the partner bank).',
      url: 'https://REPLACE_ME/found',
    },
    invoicing: {
      label: 'Invoicing and bookkeeping software',
      blurb: 'Send invoices with a pay-now link and track expenses in one place, so your profit number is always current.',
      url: 'https://REPLACE_ME/freshbooks',
    },
    // Comparison pages (compare/). Until a URL is real, the button goes to the provider's own homepage
    // with no affiliate label. Programs and payouts: research/06-freelancer-affiliate-programs.md.
    found: { url: 'https://REPLACE_ME/found' },            // Impact
    lili: { url: 'https://REPLACE_ME/lili' },              // email Lili (no public creator program)
    bluevine: { url: 'https://REPLACE_ME/bluevine' },      // partnerinquiry@bluevine.com
    novo: { url: 'https://REPLACE_ME/novo' },              // PartnerStack
    relay: { url: 'https://REPLACE_ME/relay' },
    keeper: { url: 'https://REPLACE_ME/keeper' },          // Tune, up to $50 per referral
    freetaxusa: { url: 'https://REPLACE_ME/freetaxusa' },  // direct, 50% per sale
    turbotax: { url: 'https://REPLACE_ME/turbotax' },
    hrblock: { url: 'https://REPLACE_ME/hrblock' },
    quickbooks: { url: 'https://REPLACE_ME/quickbooks' },  // QuickBooks Business Affiliate Program (needs an EIN)
    freshbooks: { url: 'https://REPLACE_ME/freshbooks' },  // PartnerStack, up to $200 per paid subscriber
    wave: { url: 'https://REPLACE_ME/wave' },
    collective: { url: 'https://REPLACE_ME/collective' },  // $600 per S corp referral; confirm publisher use first
    gusto: { url: 'https://REPLACE_ME/gusto' },
    healthsherpa: { url: 'https://REPLACE_ME/healthsherpa' },
    stride: { url: 'https://REPLACE_ME/stride' },
  },

  // Plausible (cookieless). Add this domain in Plausible with the goals in docs/UTM.md section 3.
  // Empty turns analytics off. Never loads on localhost.
  analytics: { plausibleDomain: '1099money.netlify.app', plausibleHost: 'https://plausible.io' },
};
