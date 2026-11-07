// Medical bill letters settings. Links containing REPLACE_ME stay hidden until you swap in real ones.
export default {
  brand: 'Money Made Simple',
  siteUrl: 'https://moneymadesimple.netlify.app',

  email: {
    provider: 'sender', // 'sender' (posts to /api/subscribe; falls back to Netlify Forms until Sender is connected) | 'netlify' | 'buttondown' | 'kit' | 'mailerlite' | 'formspree' | 'none'
    formName: 'medical-bills',
    action: '',
    emailField: 'email',
    thanksUrl: 'https://moneymadesimple.netlify.app/free/thanks/',
  },

  // Optional paid add-on: a $19 letter pack (certified-mail guide, follow-up letters, call log,
  // state resources). Paste its Gumroad or Stripe link; hidden while it contains REPLACE_ME.
  product: {
    name: 'The Medical Bill Fight Pack',
    price: '$19',
    url: 'https://REPLACE_ME.gumroad.com/l/medical-bill-pack',
    pitch: 'Follow-up letters for when they don\'t answer, a certified-mail checklist, a call log and where to get free help in your state.',
  },

  // Plausible (no cookies). Set the domain to turn on page views and the Product Click / Signup events. See docs/UTM.md.
  analytics: { plausibleDomain: '' },
};
