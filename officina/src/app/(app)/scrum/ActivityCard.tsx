"use client";
import { useEffect, useState } from "react";
import { AlertCircle, Bell, Link2, MoreHorizontal, Timer } from "lucide-react";
import type { ActivityStatus, BoardCard } from "@/lib/data/types";
import { Avatar } from "@/components/ui/Avatar";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/cn";
import { formatMinutes, shortWeek } from "@/lib/week";
import { COLUMN_LABELS, COLUMNS } from "./columns";

function useElapsed(since: string | null): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!since) return;
    const t = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(t);
  }, [since]);
  return since ? Math.max(0, (now - Date.parse(since)) / 60000) : 0;
}

interface Props {
  card: BoardCard;
  dragging?: boolean;
  overlay?: boolean;
  onMove?: (to: ActivityStatus) => void;
}

export function ActivityCard({ card, dragging, overlay, onMove }: Props) {
  const running = useElapsed(card.runningSince);
  const logged = card.loggedMinutes + running;
  const remaining = card.estimatedMinutes - logged;
  const [menu, setMenu] = useState(false);
  const late = !!card.lastDelay;
  const path = [card.projectTypeName, card.commessaCode, card.customerName, card.officeName].filter(Boolean).join(" › ");

  return (
    <div
      className={cn(
        "grid grid-cols-[minmax(0,1fr)] gap-2 rounded-md border-l-4 bg-surface p-3 shadow-card",
        late ? "border-danger" : card.runningSince ? "border-success" : "border-transparent",
        dragging && "opacity-40",
        overlay && "rotate-1 shadow-drag",
      )}
    >
      <div className="flex items-start gap-2">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-1">
            {card.isIndirect ? <Badge>Indiretta</Badge> : <span className="font-mono text-xs text-text-muted">{card.code}</span>}
            {late && <Badge tone="danger"><AlertCircle aria-hidden className="mr-1 h-3 w-3" />In ritardo</Badge>}
            {card.alert && !late && <Badge tone="warning"><Bell aria-hidden className="mr-1 h-3 w-3" />Scadenza vicina</Badge>}
            {card.runningSince && <Badge tone="success"><Timer aria-hidden className="mr-1 h-3 w-3" />{formatMinutes(running)}</Badge>}
            {card.predecessorId && <span title="Dipende da un'altra attività"><Link2 aria-label="Dipende da un'altra attività" className="h-3 w-3 text-text-muted" /></span>}
          </div>
          <p className="mt-1 line-clamp-2 break-words text-sm font-semibold">{card.title}</p>
        </div>
        {onMove && (
          <div className="relative">
            <button
              type="button"
              aria-label={`Sposta ${card.title}`}
              aria-haspopup="menu"
              aria-expanded={menu}
              onClick={(e) => { e.stopPropagation(); setMenu((v) => !v); }}
              onPointerDown={(e) => e.stopPropagation()}
              onKeyDown={(e) => e.stopPropagation()}
              className="grid h-control-sm w-control-sm place-items-center rounded-md text-text-muted hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
            >
              <MoreHorizontal aria-hidden className="h-icon w-icon" />
            </button>
            {menu && (
              <div role="menu" className="absolute right-0 top-full z-20 mt-1 w-sidebar rounded-md border border-border bg-surface p-1 shadow-pop"
                onPointerDown={(e) => e.stopPropagation()} onKeyDown={(e) => { e.stopPropagation(); if (e.key === "Escape") setMenu(false); }}>
                <p className="px-3 py-1 text-xs text-text-muted">Sposta in</p>
                {COLUMNS.filter((c) => c !== card.status).map((c) => (
                  <button key={c} role="menuitem" type="button"
                    onClick={(e) => { e.stopPropagation(); setMenu(false); onMove(c); }}
                    className="flex h-control-md w-full items-center rounded-md px-3 text-sm hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
                    {COLUMN_LABELS[c]}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {(card.milestoneWeek || card.lastDelay) && (
        <p className="text-xs text-text-muted">
          {card.milestoneWeek && <>Scadenza {shortWeek(card.milestoneWeek)}</>}
          {card.milestoneWeek && card.lastDelay && " · "}
          {card.lastDelay && <span className="text-danger">{card.lastDelay}</span>}
        </p>
      )}

      <dl className="grid grid-cols-3 text-xs text-text-muted">
        <div><dt>Stimato</dt><dd className="text-sm font-semibold text-text">{formatMinutes(card.estimatedMinutes)}</dd></div>
        <div><dt>Registrato</dt><dd className="text-sm font-semibold text-text">{formatMinutes(logged)}</dd></div>
        <div><dt>Residuo</dt><dd className={cn("text-sm font-semibold", remaining < 0 ? "text-danger" : "text-text")}>{formatMinutes(remaining)}</dd></div>
      </dl>

      {(path || card.assignee) && (
        <div className="flex items-center justify-between gap-2">
          <p className="min-w-0 truncate text-xs text-text-muted" title={path}>{path}</p>
          {card.assignee ? <Avatar name={card.assignee.fullName} /> : <span className="text-xs text-text-muted">Non assegnata</span>}
        </div>
      )}
    </div>
  );
}
