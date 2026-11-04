"use client";
import { useEffect, useRef, useState, useTransition } from "react";
import { X } from "lucide-react";
import type { ActivityStatus, BoardCard } from "@/lib/data/types";
import { Button } from "@/components/ui/Button";
import { SelectField, TextArea, TextField } from "@/components/ui/Field";
import { weekLabel } from "@/lib/week";
import { createActivityAction } from "./actions";
import { COLUMN_LABELS, COLUMNS } from "./columns";

interface Opt { id: string; name: string }

export function NewActivityDialog({ open, status, week, meId, offices, members, defaultOfficeId, onClose, onCreated }: {
  open: boolean; status: ActivityStatus; week: string; meId: string; offices: Opt[]; members: Opt[];
  defaultOfficeId: string | null; onClose: () => void; onCreated: (c: BoardCard) => void;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [titleError, setTitleError] = useState<string | null>(null);
  const [pending, start] = useTransition();
  const [inBacklog, setInBacklog] = useState(status === "backlog");

  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) { setError(null); setTitleError(null); setInBacklog(status === "backlog"); d.showModal(); }
    if (!open && d.open) d.close();
  }, [open, status]);

  const submit = (form: FormData) => {
    const title = String(form.get("title") ?? "").trim();
    if (title.length < 2) { setTitleError("Scrivi un titolo di almeno 2 caratteri."); return; }
    setTitleError(null);
    start(async () => {
      const res = await createActivityAction(form);
      if (res.ok) onCreated(res.value);
      else setError(res.message);
    });
  };

  return (
    <dialog ref={ref} onClose={onClose} aria-labelledby="new-activity-title"
      className="m-auto w-full max-w-login rounded-lg bg-surface p-0 text-text shadow-pop backdrop:bg-overlay">
      {open && (
        <form action={submit} className="grid gap-4 p-5" noValidate>
          <div className="flex items-center justify-between">
            <h2 id="new-activity-title" className="text-lg font-semibold">Nuova attività</h2>
            <button type="button" onClick={onClose} aria-label="Chiudi"
              className="grid h-control-md w-control-md place-items-center rounded-md hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
              <X aria-hidden className="h-icon w-icon" />
            </button>
          </div>
          {error && <p role="alert" className="rounded-md bg-danger-soft px-3 py-2 text-sm text-danger">{error}</p>}
          <TextField label="Titolo" name="title" required maxLength={200} autoFocus error={titleError} />
          <SelectField label="Settimana" name="weekStart" defaultValue={status === "backlog" ? "backlog" : week}
            onChange={(e) => setInBacklog(e.target.value === "backlog")}>
            <option value={week}>{weekLabel(week)}</option>
            <option value="backlog">Backlog (senza settimana)</option>
          </SelectField>
          {!inBacklog && (
            <SelectField label="Colonna" name="status" defaultValue={status === "backlog" ? "da_fare" : status}>
              {COLUMNS.filter((c) => c !== "backlog").map((c) => <option key={c} value={c}>{COLUMN_LABELS[c]}</option>)}
            </SelectField>
          )}
          <div className="grid gap-4 sm:grid-cols-2">
            <SelectField label="Persona" name="assigneeId" defaultValue={meId}>
              <option value="">Nessuna</option>
              {members.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
            </SelectField>
            <SelectField label="Ufficio" name="officeId" defaultValue={defaultOfficeId ?? ""}>
              <option value="">Nessuno</option>
              {offices.map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
            </SelectField>
          </div>
          <fieldset className="grid gap-1">
            <legend className="mb-1 text-xs text-text-muted">Stima</legend>
            <div className="grid grid-cols-2 gap-4">
              <TextField label="Ore" name="hours" type="number" inputMode="numeric" min={0} max={100} defaultValue={1} />
              <TextField label="Minuti" name="minutes" type="number" inputMode="numeric" min={0} max={59} step={5} defaultValue={0} />
            </div>
          </fieldset>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" name="isIndirect" className="h-4 w-4 accent-accent" /> Attività indiretta (non legata a una commessa)
          </label>
          <TextArea label="Note" name="description" rows={2} maxLength={2000} />
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={onClose}>Annulla</Button>
            <Button type="submit" loading={pending}>Crea attività</Button>
          </div>
        </form>
      )}
    </dialog>
  );
}
