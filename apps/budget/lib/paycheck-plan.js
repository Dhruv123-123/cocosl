// Paycheck-to-budget planner (paycheck-plan.html, plan-quincena.html). Pure functions, no DOM.
// Take-home pay per paycheck -> a monthly amount -> a 50/30/20 split and a zero-based plan, in the same
// categories the money dashboard maker uses (lib/dashboard.js), so the plan exports straight into it.
//
// 50/30/20: half of take-home on needs, 30% on wants, 20% on savings and extra debt payments
// (popularised by Elizabeth Warren and Amelia Warren Tyagi, "All Your Worth", 2005).
// Zero-based: every dollar gets a job, so income minus the plan is exactly $0.
import { CATEGORIES, catName } from './dashboard.js';

export const FREQS = { weekly: 52, biweekly: 26, semimonthly: 24, monthly: 12 };
// Paychecks you can count on every month. Weekly and every-two-weeks pay give some months an extra check.
const BASE = { weekly: 4, biweekly: 2, semimonthly: 2, monthly: 1 };

export const BUCKETS = {
  needs: ['housing', 'utilities', 'groceries', 'transport', 'insurance', 'health', 'debt', 'kids'],
  wants: ['dining', 'fun', 'shopping', 'subscriptions', 'giving', 'cash'],
  savings: ['savings'],
};
export const PLAN_KEYS = [...BUCKETS.needs, ...BUCKETS.wants, ...BUCKETS.savings];
export const bucketOf = (key) => Object.keys(BUCKETS).find((b) => BUCKETS[b].includes(key)) || 'wants';

// How each bucket is usually shared out, as a starting point people then change.
const SHARES = {
  needs: { housing: 0.5, utilities: 0.1, groceries: 0.16, transport: 0.12, insurance: 0.05, health: 0.04, debt: 0.03, kids: 0 },
  wants: { dining: 0.3, fun: 0.25, shopping: 0.25, subscriptions: 0.1, giving: 0.1, cash: 0 },
  savings: { savings: 1 },
};

const num = (v) => { const x = Number(String(v ?? '').replace(/[$,\s]/g, '')); return Number.isFinite(x) && x >= 0 ? x : NaN; };
const r2 = (n) => Math.round((n + Number.EPSILON) * 100) / 100;

/** pay: take-home per paycheck. planOn: 'base' (only the checks every month gets) or 'average'. */
export function monthlyIncome({ pay, freq = 'biweekly', planOn = 'base' } = {}, msg = 'Enter your take-home pay per paycheck.') {
  const p = num(pay);
  if (!(p > 0) || p > 1e6) throw new Error(msg);
  const f = FREQS[freq] ? freq : 'biweekly';
  const year = p * FREQS[f];
  const average = r2(year / 12);
  const base = r2(p * BASE[f]);
  const monthly = planOn === 'average' ? average : base;
  const extraChecks = FREQS[f] - BASE[f] * 12; // 2 for every two weeks, 4 for weekly
  return { pay: p, freq: f, year: r2(year), average, base, monthly, planOn: planOn === 'average' ? 'average' : 'base', extraChecks, extra: planOn === 'average' ? 0 : r2(year - base * 12) };
}

/** Whole-dollar shares that add up exactly to the total (the biggest share takes the rounding). */
function shareOut(total, shares) {
  const keys = Object.keys(shares);
  const out = Object.fromEntries(keys.map((k) => [k, Math.floor(total * shares[k])]));
  const big = keys.reduce((a, b) => (shares[b] > shares[a] ? b : a));
  out[big] += Math.round(total) - keys.reduce((t, k) => t + out[k], 0);
  return out;
}

export function split503020(monthly) {
  const m = Math.round(monthly);
  const needs = Math.round(m * 0.5);
  const wants = Math.round(m * 0.3);
  const savings = m - needs - wants;
  const amounts = { ...shareOut(needs, SHARES.needs), ...shareOut(wants, SHARES.wants), ...shareOut(savings, SHARES.savings) };
  return { buckets: { needs, wants, savings }, amounts };
}

/** A zero-based plan: what's planned, what's left to give a job, and how it compares with 50/30/20. */
export function zeroBased(monthly, amounts = {}) {
  const clean = {};
  for (const k of PLAN_KEYS) { const v = num(amounts[k]); if (v > 0) clean[k] = r2(v); }
  const planned = r2(Object.values(clean).reduce((a, b) => a + b, 0));
  const left = r2(monthly - planned);
  const buckets = { needs: 0, wants: 0, savings: 0 };
  for (const [k, v] of Object.entries(clean)) buckets[bucketOf(k)] = r2(buckets[bucketOf(k)] + v);
  const pct = Object.fromEntries(Object.entries(buckets).map(([b, v]) => [b, monthly ? Math.round((v / monthly) * 100) : 0]));
  return { amounts: clean, planned, left, balanced: Math.abs(left) < 0.005, over: left < -0.004, buckets, pct };
}

const csvCell = (s) => (/[",\n]/.test(s) ? `"${String(s).replace(/"/g, '""')}"` : String(s));
export const PLAN_HEAD = { en: ['Category', 'Monthly budget'], es: ['Categoría', 'Presupuesto mensual'] };

/** CSV the money dashboard maker reads back (drop it in with your bank files), and that pastes into the Pro sheet's Categories tab. */
export function planCsv(amounts, lang = 'en') {
  const rows = [PLAN_HEAD[lang === 'es' ? 'es' : 'en']];
  for (const k of PLAN_KEYS) if (amounts[k] > 0) rows.push([catName(k, lang), String(amounts[k])]);
  return `${rows.map((r) => r.map(csvCell).join(',')).join('\r\n')}\r\n`;
}

/** Reads a plan CSV back (either language). Returns { key: amount } or null if the text isn't a plan. */
export function parsePlanCsv(text) {
  const lines = String(text || '').replace(/^﻿/, '').split(/\r?\n/).filter((l) => l.trim());
  if (!lines.length) return null;
  const head = lines[0].toLowerCase().replace(/"/g, '');
  if (!/^(category|categoría|categoria)\s*,\s*(monthly budget|presupuesto mensual)/.test(head)) return null;
  const byName = new Map();
  for (const c of CATEGORIES) { byName.set(c.en.toLowerCase(), c.key); byName.set(c.es.toLowerCase(), c.key); }
  const out = {};
  for (const line of lines.slice(1)) {
    const m = /^\s*(?:"((?:[^"]|"")*)"|([^,]*))\s*,\s*"?\$?([\d,.]+)"?\s*$/.exec(line);
    if (!m) continue;
    const key = byName.get((m[1] ?? m[2]).replace(/""/g, '"').trim().toLowerCase());
    const v = num(m[3]);
    if (key && v > 0) out[key] = v;
  }
  return out;
}

export const PLAN_STORE = 'mms-budget-plan-v1';
