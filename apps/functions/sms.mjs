// Netlify Functions for the all-in-one site (base directory apps/). See verify-license.mjs.
import handler from '../scam-checker/netlify/functions/sms.mjs';

export default handler;
export const config = { path: '/api/sms' };
