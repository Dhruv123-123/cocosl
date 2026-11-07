// Scam Shield settings. Links containing REPLACE_ME stay hidden until you swap in real ones.
export default {
  brand: 'Scam Shield',
  siteUrl: 'https://scamshield.netlify.app',

  email: {
    provider: 'netlify', // 'netlify' | 'buttondown' | 'kit' | 'mailerlite' | 'formspree' | 'none'
    formName: 'scam-alerts',
    action: '',
    emailField: 'email',
    thanksUrl: './thanks.html',
    pitch: 'One email a week with the scams going around right now and how to spot them. Free.',
  },

  // Shown under every result. Order = display order. Affiliate programs from research/: Aura, NordVPN, 1Password.
  offers: [
    { id: 'identity', title: 'Identity theft protection', blurb: 'Monitors your SSN, bank and credit for misuse and helps you recover if it happens.', label: 'See identity protection plans', es: { title: 'Protección contra robo de identidad', blurb: 'Vigila tu número de Seguro Social, tu banco y tu crédito, y te ayuda a recuperarte si pasa algo.', label: 'Ver planes de protección' }, url: 'https://REPLACE_ME/aura', showWhen: ['medium', 'high'] },
    { id: 'passwords', title: 'A password manager', blurb: 'Unique passwords everywhere means one leaked password can\'t open your other accounts. It also won\'t autofill on fake sites.', label: 'Try a password manager', es: { title: 'Un administrador de contraseñas', blurb: 'Contraseñas distintas en cada sitio: si se filtra una, no abre tus otras cuentas. Además no se autocompleta en sitios falsos.', label: 'Probar un administrador de contraseñas' }, url: 'https://REPLACE_ME/1password', showWhen: ['low', 'medium', 'high'] },
    { id: 'vpn', title: 'Threat protection on public Wi-Fi', blurb: 'Some VPNs block known scam and malware sites before they load.', label: 'Compare VPN plans', es: { title: 'Protección en Wi-Fi público', blurb: 'Algunas VPN bloquean sitios de estafa y malware conocidos antes de que carguen.', label: 'Comparar VPN' }, url: 'https://REPLACE_ME/nordvpn', showWhen: ['low', 'medium'] },
  ],

  // Paid product: a printable family scam-safety kit (sell on Gumroad / Stripe Payment Link).
  product: {
    name: 'Family Scam Safety Kit',
    price: '$9',
    url: 'https://REPLACE_ME.gumroad.com/l/family-scam-kit',
    pitch: 'Printable fridge checklist, a "verify before you pay" card for parents and grandparents, and scripts for what to say when a scammer calls.',
  },

  analytics: { plausibleDomain: '' },
};
