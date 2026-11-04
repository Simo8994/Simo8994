import type { Metadata } from "next";
import Link from "next/link";
import { FolderSearch, X } from "lucide-react";
import { listCommesse } from "@/lib/data";
import type { CommessaStatus } from "@/lib/data/types";
import { requireSession } from "@/lib/session";
import { Badge } from "@/components/ui/Badge";
import { EmptyState } from "@/components/ui/EmptyState";
import { buttonClass } from "@/components/ui/Button";
import { cn } from "@/lib/cn";
import { COMMESSA_STATUS_LABEL as STATUS_LABEL, COMMESSA_STATUS_TONE as STATUS_TONE } from "@/lib/labels";

export const metadata: Metadata = { title: "Commesse" };

const ALL = Object.keys(STATUS_LABEL) as CommessaStatus[];
const DEFAULT: CommessaStatus[] = ["inserita", "in_corso", "in_attesa"];

export default async function CommessePage({ searchParams }: { searchParams: Promise<{ stato?: string | string[] }> }) {
  const { org } = await requireSession();
  const sp = await searchParams;
  const raw = sp.stato === undefined ? DEFAULT : ([] as string[]).concat(sp.stato).filter((s) => s !== "");
  const selected = raw.filter((s): s is CommessaStatus => (ALL as string[]).includes(s));
  const items = await listCommesse(org.id, selected);
  const href = (list: CommessaStatus[]) => list.length ? `/commesse?${list.map((s) => `stato=${s}`).join("&")}` : "/commesse?stato=";

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-4 px-4 py-5">
      <nav aria-label="Percorso" className="text-sm text-text-muted">
        <ol className="flex items-center gap-1"><li><Link href="/scrum" className="hover:underline">Inizio</Link></li><li aria-hidden>›</li><li aria-current="page" className="text-text">Commesse</li></ol>
      </nav>
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-xl font-bold">Commesse</h1>
        <Link href="/commesse/nuova" className={buttonClass("primary", "md")}>Nuova commessa</Link>
      </div>

      <div className="flex flex-wrap items-center gap-2" aria-label="Filtri attivi">
        {selected.length === 0 && <span className="text-sm text-text-muted">Tutti gli stati</span>}
        {selected.map((s) => (
          <span key={s} className="inline-flex h-control-sm items-center gap-1 rounded-pill border border-border bg-surface pl-3 pr-1 text-sm">
            Stato: {STATUS_LABEL[s]}
            <Link href={href(selected.filter((x) => x !== s))} aria-label={`Rimuovi filtro Stato: ${STATUS_LABEL[s]}`}
              className="grid h-6 w-6 place-items-center rounded-pill bg-surface-sunken text-text-muted hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
              <X aria-hidden className="h-3 w-3" />
            </Link>
          </span>
        ))}
        <details className="relative">
          <summary className="cursor-pointer list-none rounded-md px-2 py-1 text-sm font-semibold text-accent hover:bg-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">+ Stato</summary>
          <div className="absolute left-0 top-full z-10 mt-1 grid w-sidebar rounded-md border border-border bg-surface p-1 shadow-pop">
            {ALL.filter((s) => !selected.includes(s)).map((s) => (
              <Link key={s} href={href([...selected, s])} className="rounded-md px-3 py-2 text-sm hover:bg-surface-sunken">{STATUS_LABEL[s]}</Link>
            ))}
          </div>
        </details>
      </div>

      {items.length === 0 ? (
        <EmptyState icon={FolderSearch} title="Nessuna commessa con questi filtri" text="Togli un filtro o crea una nuova commessa."
          action={<Link href="/commesse?stato=" className={buttonClass("secondary", "md")}>Mostra tutte</Link>} />
      ) : (
        <ul className="grid gap-4 [grid-template-columns:repeat(auto-fill,minmax(var(--size-sidebar),1fr))]">
          {items.map((c) => (
            <li key={c.id}>
              <Link href={`/commesse/${c.id}`}
                className="block h-full overflow-hidden rounded-lg border border-border bg-surface shadow-card transition-shadow duration-fast hover:shadow-pop focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus">
                <div aria-hidden className="flex h-cover items-end p-3" style={{ background: c.projectType.color }}>
                  <span className="rounded-pill bg-surface px-2 py-px text-xs font-semibold">{c.projectType.name}</span>
                </div>
                <div className="grid gap-2 p-4">
                  <span className="font-mono text-xs text-text-muted">{c.code}</span>
                  <h2 className="line-clamp-2 break-words text-lg">{c.name}</h2>
                  <dl className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-sm">
                    <dt className="text-text-muted">Cliente</dt><dd className="truncate">{c.customerName ?? "Interna"}</dd>
                    <dt className="text-text-muted">Stato</dt><dd><Badge tone={STATUS_TONE[c.status]}>{STATUS_LABEL[c.status]}</Badge></dd>
                    <dt className="text-text-muted">Portfolio</dt><dd className={cn(!c.portfolio && "text-text-muted")}>{c.portfolio ?? "—"}</dd>
                    <dt className="text-text-muted">Quantità</dt><dd className={cn(c.quantity == null && "text-text-muted")}>{c.quantity ?? "—"}</dd>
                  </dl>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
