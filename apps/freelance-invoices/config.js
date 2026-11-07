// Freelancer invoice tracker settings (1099 Money). Links containing REPLACE_ME stay hidden.
export default {
  brand: '1099 Money',
  siteUrl: 'https://1099money.netlify.app',

  // Paid upsell: invoice, proposal and contract templates. This is the $29 Rate & Contract Kit
  // (content-factory/1099-money/products/rate-contract-kit/). Paste its Gumroad, Lemon Squeezy or
  // Stripe link; the offer stays hidden while the URL contains REPLACE_ME.
  product: {
    name: 'The Rate & Contract Kit',
    price: '$29',
    url: 'https://REPLACE_ME.gumroad.com/l/rate-contract-kit',
    pitch: 'Invoice, proposal, contract and change-order templates (Word and Google Docs), plus a rate calculator and invoice log spreadsheet. Put late fees in writing before the work starts.',
  },

  // Netlify form for the email list (free invoice reminder scripts).
  formName: 'freelance-invoices',

  // Plausible (no cookies). Set the domain to turn on page views and the Product Click / Signup events. See docs/UTM.md.
  analytics: { plausibleDomain: '' },
};
