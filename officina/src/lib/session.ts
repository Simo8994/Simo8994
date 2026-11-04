import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { createHmac, timingSafeEqual } from "node:crypto";
import { getSessionFor } from "./data";
import type { Session } from "./data/types";

const COOKIE = "officina_session";
const MAX_AGE = 60 * 60 * 12;
const secret = () => process.env.SESSION_SECRET ?? "solo-per-sviluppo-cambiami";

function sign(value: string): string {
  return createHmac("sha256", secret()).update(value).digest("base64url");
}

export async function startSession(memberId: string): Promise<void> {
  const exp = Math.floor(Date.now() / 1000) + MAX_AGE;
  const payload = `${memberId}.${exp}`;
  (await cookies()).set(COOKIE, `${payload}.${sign(payload)}`, {
    httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", maxAge: MAX_AGE,
  });
}

export async function endSession(): Promise<void> {
  (await cookies()).delete(COOKIE);
}

export async function readSession(): Promise<Session | null> {
  const raw = (await cookies()).get(COOKIE)?.value;
  if (!raw) return null;
  const i = raw.lastIndexOf(".");
  const payload = raw.slice(0, i);
  const sig = Buffer.from(raw.slice(i + 1));
  const expected = Buffer.from(sign(payload));
  if (sig.length !== expected.length || !timingSafeEqual(sig, expected)) return null;
  const [memberId, exp] = payload.split(".");
  if (Number(exp) < Date.now() / 1000) return null;
  return getSessionFor(memberId);
}

export async function requireSession(): Promise<Session> {
  const s = await readSession();
  if (!s) redirect("/login");
  return s;
}
