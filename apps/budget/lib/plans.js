// What the free plan includes and what Pro unlocks. Change the numbers here.
export const PLANS = {
  free: {
    name: 'Free',
    maxCategories: 10,
    csvImport: false,
    history: false,  // free shows the current month only
    goals: 1,
    backup: true,    // never lock people out of their own data
  },
  pro: {
    name: 'Pro',
    maxCategories: Infinity,
    csvImport: true,
    history: true,
    goals: Infinity,
    backup: true,
  },
};

export const planFor = (license) => (license && license.valid ? PLANS.pro : PLANS.free);

export function can(license, feature) {
  const p = planFor(license);
  return Boolean(p[feature]);
}
