import { addDays } from './dates.js';

// Calendar file (.ics) for reminders: all-day events with a morning alarm. No server needed:
// the page offers the file as a download and the phone or computer calendar imports it.
const esc = (s) => String(s ?? '').replace(/\\/g, '\\\\').replace(/;/g, '\\;').replace(/,/g, '\\,').replace(/\r?\n/g, '\\n');
const fold = (line) => {
  const out = [];
  let s = line;
  while (s.length > 74) { out.push(s.slice(0, 74)); s = ` ${s.slice(74)}`; }
  out.push(s);
  return out.join('\r\n');
};
const compact = (day) => day.replace(/-/g, '');

/** events: [{ uid, date: 'YYYY-MM-DD', title, description }] */
export function buildIcs(events, { name = 'Invoice reminders', stamp = new Date() } = {}) {
  const dtstamp = stamp.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '');
  const lines = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//1099 Money//Invoices//EN', 'CALSCALE:GREGORIAN', `X-WR-CALNAME:${esc(name)}`];
  for (const e of events) {
    const end = addDays(e.date, 1);
    lines.push('BEGIN:VEVENT', `UID:${esc(e.uid)}@1099money`, `DTSTAMP:${dtstamp}`, `DTSTART;VALUE=DATE:${compact(e.date)}`,
      `DTEND;VALUE=DATE:${compact(end)}`, `SUMMARY:${esc(e.title)}`, `DESCRIPTION:${esc(e.description)}`,
      'BEGIN:VALARM', 'ACTION:DISPLAY', `DESCRIPTION:${esc(e.title)}`, 'TRIGGER:PT9H', 'END:VALARM', 'END:VEVENT');
  }
  lines.push('END:VCALENDAR');
  return lines.map(fold).join('\r\n') + '\r\n';
}
