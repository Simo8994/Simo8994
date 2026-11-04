"use server";
import { redirect } from "next/navigation";
import { verifyLogin } from "@/lib/data";
import { endSession, startSession } from "@/lib/session";

export interface LoginState { error: string | null; username: string }

// Limite semplice per il livello finto; quello reale va su Supabase Auth.
const attempts = new Map<string, { n: number; until: number }>();

export async function login(_prev: LoginState, form: FormData): Promise<LoginState> {
  const username = String(form.get("username") ?? "").trim().toLowerCase();
  const password = String(form.get("password") ?? "");
  const a = attempts.get(username);
  if (a && a.until > Date.now()) return { error: "Troppi tentativi. Riprova tra qualche minuto.", username };
  const member = username && password ? await verifyLogin(username, password) : null;
  if (!member) {
    const n = (a?.n ?? 0) + 1;
    attempts.set(username, { n, until: n >= 5 ? Date.now() + 5 * 60_000 : 0 });
    return { error: "Nome utente o password non corretti.", username };
  }
  attempts.delete(username);
  await startSession(member.id);
  const next = String(form.get("next") ?? "");
  redirect(next.startsWith("/") && !next.startsWith("//") ? next : "/scrum");
}

export async function logout(): Promise<void> {
  await endSession();
  redirect("/login");
}
