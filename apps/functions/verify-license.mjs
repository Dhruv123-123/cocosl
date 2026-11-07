// Netlify Functions for the all-in-one site (base directory apps/). Each file points at the
// function that lives with its app, so single-app deploys keep working too.
import handler from '../budget/netlify/functions/verify-license.mjs';

export default handler;
export const config = { path: '/api/verify-license' };
