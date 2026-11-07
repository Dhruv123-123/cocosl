// The 20-Minute Budget app settings. Checkout links containing REPLACE_ME are hidden.
export default {
  appName: 'The 20-Minute Budget',
  brand: 'Money Made Simple',
  siteUrl: 'https://moneymadesimple.netlify.app',
  pricing: {
    monthly: { label: '$3/month', url: 'https://REPLACE_ME.gumroad.com/l/budget-pro-monthly' },
    lifetime: { label: '$29 once', url: 'https://REPLACE_ME.gumroad.com/l/budget-pro-lifetime' },
    // Stripe alternative: paste a Payment Link here and set its success URL to
    // https://YOUR-SITE/?session_id={CHECKOUT_SESSION_ID}
    stripe: { label: 'Pay by card', url: '' },
  },
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
  verifyEndpoint: '/api/verify-license',
  proFeatures: [
    'Unlimited categories',
    'Import your bank\'s CSV export, auto-sorted into categories',
    'Every month kept: look back and plan ahead',
    'Unlimited savings goals',
  ],
};
