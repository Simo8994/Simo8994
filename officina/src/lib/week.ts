// Settimane ISO su date senza orario (YYYY-MM-DD). Calcoli in UTC sulle sole date,
// "oggi" nel fuso dell'organizzazione: niente effetti dell'ora legale.

const DAY = 86_400_000;

export function todayIn(timezone: string, now = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-CA", { timeZone: timezone, year: "numeric", month: "2-digit", day: "2-digit" }).format(now);
  return parts; // en-CA => YYYY-MM-DD
}

function toUtc(date: string): number {
  const [y, m, d] = date.split("-").map(Number);
  return Date.UTC(y, m - 1, d);
}

function fromUtc(ms: number): string {
  return new Date(ms).toISOString().slice(0, 10);
}

export function isDate(value: string | undefined | null): value is string {
  return !!value && /^\d{4}-\d{2}-\d{2}$/.test(value) && !Number.isNaN(toUtc(value));
}

export function mondayOf(date: string): string {
  const ms = toUtc(date);
  const isoDow = ((new Date(ms).getUTCDay() + 6) % 7) + 1; // 1 = lunedì
  return fromUtc(ms - (isoDow - 1) * DAY);
}

export function addWeeks(weekStart: string, n: number): string {
  return fromUtc(toUtc(weekStart) + n * 7 * DAY);
}

export function isoWeek(date: string): { week: number; year: number } {
  const ms = toUtc(date);
  const isoDow = ((new Date(ms).getUTCDay() + 6) % 7) + 1;
  const thursday = new Date(ms + (4 - isoDow) * DAY);
  const year = thursday.getUTCFullYear();
  const jan1 = Date.UTC(year, 0, 1);
  const week = Math.floor((thursday.getTime() - jan1) / DAY / 7) + 1;
  return { week, year };
}

const MONTHS = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"];

export function weekLabel(weekStart: string): string {
  const { week, year } = isoWeek(weekStart);
  const end = addWeeks(weekStart, 1);
  const last = fromUtc(toUtc(end) - DAY);
  const [, m1, d1] = weekStart.split("-").map(Number);
  const [, m2, d2] = last.split("-").map(Number);
  const range = m1 === m2 ? `${d1}–${d2} ${MONTHS[m2 - 1]}` : `${d1} ${MONTHS[m1 - 1]} – ${d2} ${MONTHS[m2 - 1]}`;
  return `Sett. ${week} · ${range} ${year}`;
}

export function shortWeek(weekStart: string): string {
  const { week, year } = isoWeek(weekStart);
  return `sett. ${week}/${year}`;
}

export function formatMinutes(min: number): string {
  const sign = min < 0 ? "-" : "";
  const abs = Math.abs(Math.round(min));
  return `${sign}${Math.floor(abs / 60)}:${String(abs % 60).padStart(2, "0")}`;
}
