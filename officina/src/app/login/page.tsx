import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { readSession } from "@/lib/session";
import { LoginForm } from "./LoginForm";

export const metadata: Metadata = { title: "Accedi" };

export default async function LoginPage({ searchParams }: { searchParams: Promise<{ next?: string }> }) {
  if (await readSession()) redirect("/scrum");
  const { next = "" } = await searchParams;
  return (
    <main className="grid min-h-screen place-items-center bg-bg px-4">
      <div className="w-full max-w-login rounded-lg border border-border bg-surface p-6 shadow-card">
        <p className="text-lg font-bold">Officina</p>
        <h1 className="mb-5 mt-1 text-sm text-text-muted">Accedi per vedere le attività della settimana.</h1>
        <LoginForm next={next} />
        {process.env.NODE_ENV !== "production" && (
          <p className="mt-5 border-t border-border pt-3 text-xs text-text-muted">Dati di prova: anna.rossi, luca.bianchi, giulia.verdi, paolo.neri · password <code>demo</code></p>
        )}
      </div>
    </main>
  );
}
