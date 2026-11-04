"use client";
import { useCallback, useMemo, useRef, useState, useTransition } from "react";
import { useRouter } from "next/navigation";
import {
  DndContext, DragOverlay, KeyboardSensor, PointerSensor, TouchSensor, closestCorners, useDroppable, useSensor, useSensors,
  type Announcements, type DragEndEvent, type DragOverEvent, type DragStartEvent,
} from "@dnd-kit/core";
import { SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { Plus } from "lucide-react";
import type { ActivityStatus, Board as BoardData, BoardCard } from "@/lib/data/types";
import { Badge } from "@/components/ui/Badge";
import { cn } from "@/lib/cn";
import { ActivityCard } from "./ActivityCard";
import { COLUMN_EMPTY, COLUMN_LABELS, COLUMNS, positionBetween } from "./columns";
import { moveActivityAction } from "./actions";
import { NewActivityDialog } from "./NewActivityDialog";

type Cols = Record<ActivityStatus, BoardCard[]>;
interface Opt { id: string; name: string }

function findColumn(cols: Cols, id: string): ActivityStatus | null {
  if ((COLUMNS as string[]).includes(id)) return id as ActivityStatus;
  for (const c of COLUMNS) if (cols[c].some((x) => x.id === id)) return c;
  return null;
}

function SortableCard({ card, onMove }: { card: BoardCard; onMove: (c: BoardCard, to: ActivityStatus) => void }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: card.id });
  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      {...attributes}
      {...listeners}
      aria-roledescription="attività trascinabile"
      aria-label={`${card.title}, ${COLUMN_LABELS[card.status]}`}
      className="cursor-grab touch-manipulation rounded-md focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus active:cursor-grabbing"
    >
      <ActivityCard card={card} dragging={isDragging} onMove={(to) => onMove(card, to)} />
    </li>
  );
}

function Column({ status, cards, hidden, onMove, onAdd }: {
  status: ActivityStatus; cards: BoardCard[]; hidden: boolean;
  onMove: (c: BoardCard, to: ActivityStatus) => void; onAdd: (s: ActivityStatus) => void;
}) {
  const { setNodeRef, isOver } = useDroppable({ id: status });
  return (
    <section
      aria-labelledby={`col-${status}`}
      className={cn("min-w-0 flex-col gap-2 rounded-lg bg-surface-sunken p-2 md:flex", hidden ? "hidden" : "flex",
        isOver && "outline-dashed outline-2 outline-accent")}
    >
      <header className="sticky top-header z-10 flex items-center justify-between gap-2 rounded-md bg-surface-sunken px-1 py-1">
        <h2 id={`col-${status}`} className="text-sm font-semibold">{COLUMN_LABELS[status]}</h2>
        <Badge>{cards.length}<span className="sr-only"> attività</span></Badge>
      </header>
      <SortableContext items={cards.map((c) => c.id)} strategy={verticalListSortingStrategy}>
        <ul ref={setNodeRef} className="grid min-h-column grid-cols-[minmax(0,1fr)] content-start gap-2" aria-label={`${COLUMN_LABELS[status]}: ${cards.length} attività`}>
          {cards.map((c) => <SortableCard key={c.id} card={c} onMove={onMove} />)}
          {cards.length === 0 && (
            <li className="grid justify-items-center gap-2 px-2 py-6 text-center text-sm text-text-muted">
              {COLUMN_EMPTY[status]}
              <button type="button" onClick={() => onAdd(status)}
                className="inline-flex items-center gap-1 rounded-md px-2 py-1 text-sm font-semibold text-accent hover:bg-surface focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
                <Plus aria-hidden className="h-4 w-4" /> Aggiungi
              </button>
            </li>
          )}
        </ul>
      </SortableContext>
    </section>
  );
}

export function Board({ board, week, meId, offices, members, defaultOfficeId }: {
  board: BoardData; week: string; meId: string; offices: Opt[]; members: Opt[]; defaultOfficeId: string | null;
}) {
  const router = useRouter();
  const [cols, setCols] = useState<Cols>(board.columns);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [tab, setTab] = useState<ActivityStatus>("da_fare");
  const [toast, setToast] = useState<{ tone: "info" | "error"; text: string; undo?: () => void } | null>(null);
  const [dialog, setDialog] = useState<ActivityStatus | null>(null);
  const [, startTransition] = useTransition();
  const snapshot = useRef<Cols | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout>>(undefined);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(TouchSensor, { activationConstraint: { delay: 220, tolerance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const showToast = useCallback((t: NonNullable<typeof toast>) => {
    clearTimeout(toastTimer.current);
    setToast(t);
    toastTimer.current = setTimeout(() => setToast(null), 5000);
  }, []);

  const all = useMemo(() => COLUMNS.flatMap((c) => cols[c]), [cols]);
  const active = activeId ? all.find((c) => c.id === activeId) ?? null : null;

  // Salva lo spostamento; in caso di errore ripristina lo stato precedente.
  const persist = useCallback((next: Cols, cardId: string, before: Cols, original: BoardCard) => {
    const to = findColumn(next, cardId)!;
    const list = next[to];
    const i = list.findIndex((c) => c.id === cardId);
    const position = positionBetween(list[i - 1]?.position, list[i + 1]?.position);
    const optimistic = { ...list[i], status: to, position };
    const withPos = { ...next, [to]: list.map((c) => (c.id === cardId ? optimistic : c)) };
    setCols(withPos);
    startTransition(async () => {
      const res = await moveActivityAction({ id: cardId, status: to, position, version: original.updatedAt });
      if (!res.ok) {
        setCols(before);
        showToast({ tone: "error", text: res.message });
        if (res.error === "conflict") router.refresh();
        return;
      }
      setCols((cur) => ({ ...cur, [to]: cur[to].map((c) => (c.id === cardId ? res.value : c)) }));
      if (original.status !== to) {
        showToast({
          tone: "info",
          text: `«${original.title}» spostata in ${COLUMN_LABELS[to]}.`,
          undo: () => {
            startTransition(async () => {
              const back = await moveActivityAction({ id: cardId, status: original.status, position: original.position, version: res.value.updatedAt });
              if (!back.ok) showToast({ tone: "error", text: back.message });
              else { setToast(null); router.refresh(); }
            });
          },
        });
      }
    });
  }, [router, showToast]);

  const moveTo = useCallback((card: BoardCard, to: ActivityStatus) => {
    const before = cols;
    const from = findColumn(cols, card.id)!;
    const next: Cols = { ...cols, [from]: cols[from].filter((c) => c.id !== card.id), [to]: [...cols[to], { ...card, status: to }] };
    persist(next, card.id, before, card);
  }, [cols, persist]);

  const onDragStart = (e: DragStartEvent) => {
    snapshot.current = cols;
    setActiveId(String(e.active.id));
  };

  const onDragOver = ({ active: a, over }: DragOverEvent) => {
    if (!over) return;
    const from = findColumn(cols, String(a.id));
    const to = findColumn(cols, String(over.id));
    if (!from || !to || from === to) return;
    setCols((cur) => {
      const card = cur[from].find((c) => c.id === a.id);
      if (!card) return cur;
      const overIndex = cur[to].findIndex((c) => c.id === over.id);
      const target = [...cur[to]];
      target.splice(overIndex < 0 ? target.length : overIndex, 0, { ...card, status: to });
      return { ...cur, [from]: cur[from].filter((c) => c.id !== a.id), [to]: target };
    });
  };

  const onDragEnd = ({ active: a, over }: DragEndEvent) => {
    setActiveId(null);
    const before = snapshot.current;
    snapshot.current = null;
    if (!before) return;
    const id = String(a.id);
    const original = COLUMNS.flatMap((c) => before[c]).find((c) => c.id === id);
    if (!over || !original) { setCols(before); return; }
    const col = findColumn(cols, id)!;
    const list = [...cols[col]];
    const from = list.findIndex((c) => c.id === id);
    const overIdx = list.findIndex((c) => c.id === over.id);
    if (overIdx >= 0 && overIdx !== from) {
      const [moved] = list.splice(from, 1);
      list.splice(overIdx, 0, moved);
    }
    const next = { ...cols, [col]: list };
    const unchanged = original.status === col && before[col].map((c) => c.id).join() === list.map((c) => c.id).join();
    if (unchanged) { setCols(before); return; }
    persist(next, id, before, original);
  };

  const announcements: Announcements = {
    onDragStart: ({ active: a }) => `Attività presa: ${all.find((c) => c.id === a.id)?.title ?? ""}. Usa le frecce per spostarla, Spazio per lasciarla, Esc per annullare.`,
    onDragOver: ({ over }) => (over ? `Sopra ${COLUMN_LABELS[findColumn(cols, String(over.id)) ?? "da_fare"]}.` : "Fuori dalle colonne."),
    onDragEnd: ({ over }) => (over ? `Attività lasciata in ${COLUMN_LABELS[findColumn(cols, String(over.id)) ?? "da_fare"]}.` : "Spostamento annullato."),
    onDragCancel: () => "Spostamento annullato.",
  };

  return (
    <>
      <div role="tablist" aria-label="Colonne" className="flex gap-1 overflow-x-auto md:hidden">
        {COLUMNS.map((c) => (
          <button key={c} role="tab" type="button" aria-selected={tab === c} onClick={() => setTab(c)}
            className={cn("flex h-control-md shrink-0 items-center gap-2 rounded-md px-3 text-sm font-semibold focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus",
              tab === c ? "bg-accent text-on-accent" : "bg-surface text-text")}>
            {COLUMN_LABELS[c]} <span className="text-xs">{cols[c].length}</span>
          </button>
        ))}
      </div>

      <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={onDragStart} onDragOver={onDragOver}
        onDragEnd={onDragEnd} onDragCancel={() => { if (snapshot.current) setCols(snapshot.current); setActiveId(null); }}
        accessibility={{ announcements, screenReaderInstructions: { draggable: "Premi Spazio per prendere l'attività. Frecce per spostarla, Spazio per lasciarla, Esc per annullare. In alternativa usa il menu Sposta sulla card." } }}>
        <div className="grid grid-cols-[minmax(0,1fr)] gap-3 md:grid-cols-2 xl:grid-cols-4">
          {COLUMNS.map((c) => <Column key={c} status={c} cards={cols[c]} hidden={tab !== c} onMove={moveTo} onAdd={setDialog} />)}
        </div>
        <DragOverlay>{active ? <ActivityCard card={active} overlay /> : null}</DragOverlay>
      </DndContext>

      <button type="button" aria-label="Nuova attività" onClick={() => setDialog("da_fare")}
        className="fixed bottom-5 right-5 z-20 grid h-fab w-fab place-items-center rounded-pill bg-accent text-on-accent shadow-pop hover:bg-accent-hover focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus">
        <Plus aria-hidden className="h-6 w-6" />
      </button>
      <div className="h-fab" aria-hidden />

      <NewActivityDialog open={dialog !== null} status={dialog ?? "da_fare"} week={week} meId={meId} offices={offices} members={members}
        defaultOfficeId={defaultOfficeId} onClose={() => setDialog(null)}
        onCreated={(card) => {
          setCols((cur) => ({ ...cur, [card.status]: [...cur[card.status].filter((c) => c.id !== card.id), card] }));
          setDialog(null);
          setTab(card.status);
          showToast({ tone: "info", text: `Attività «${card.title}» creata.` });
        }} />

      <div aria-live={toast?.tone === "error" ? "assertive" : "polite"} className="pointer-events-none fixed inset-x-0 bottom-5 z-30 flex justify-center px-4">
        {toast && (
          <div className={cn("pointer-events-auto flex max-w-content items-center gap-3 rounded-md px-4 py-3 text-sm shadow-pop",
            toast.tone === "error" ? "bg-danger text-on-danger" : "bg-text text-surface")}
            onMouseEnter={() => clearTimeout(toastTimer.current)}>
            <span>{toast.text}</span>
            {toast.undo && <button type="button" onClick={toast.undo} className="font-semibold underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-surface">Annulla</button>}
          </div>
        )}
      </div>
    </>
  );
}
