// POST /api/subscribe for this app deployed on its own. Logic in lib/sender.js (synced from shared/).
import { handleSubscribe } from '../../lib/sender.js';

export default (req) => handleSubscribe(req, process.env);
export const config = { path: '/api/subscribe' };
