// Netlify Function for the all-in-one site: the email opt-in box posts here. Logic in shared/sender.js.
import { handleSubscribe } from '../shared/sender.js';

export default (req) => handleSubscribe(req, process.env);
export const config = { path: '/api/subscribe' };
