import Link from "next/link";
export const metadata = { title: "Recupero password" };
export default function Recupero() {
  return (
    <main className="grid min-h-screen place-items-center bg-bg px-4">
      <div className="w-full max-w-login rounded-lg border border-border bg-surface p-6 shadow-card">
        <h1 className="text-lg font-semibold">Recupero password</h1>
        <p className="mt-2 text-sm text-text-muted">L&apos;invio del link di reset arriva con il backend (Supabase Auth). Per ora chiedi a un amministratore.</p>
        <Link href="/login" className="mt-4 inline-block text-sm text-accent hover:underline">Torna all&apos;accesso</Link>
      </div>
    </main>
  );
}
