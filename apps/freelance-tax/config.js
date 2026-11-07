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

  // Affiliate offers. Keep the disclosure on anything that pays you.
  affiliates: {
    banking: {
      label: 'Open a separate business checking account',
      blurb: 'Keep client money and tax savings out of your personal account. Look for no monthly fee and FDIC insurance (for apps, check the partner bank).',
      url: 'https://REPLACE_ME/novo',
    },
    invoicing: {
      label: 'Invoicing and bookkeeping software',
      blurb: 'Send invoices with a pay-now link and track expenses in one place, so your profit number is always current.',
      url: 'https://REPLACE_ME/freshbooks',
    },
  },

  analytics: { plausibleDomain: '' },
};
