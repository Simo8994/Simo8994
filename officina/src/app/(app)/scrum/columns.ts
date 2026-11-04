import type { ActivityStatus } from "@/lib/data/types";

export const COLUMNS: ActivityStatus[] = ["backlog", "da_fare", "in_corso", "eseguito"];

export const COLUMN_LABELS: Record<ActivityStatus, string> = {
  backlog: "Backlog",
  da_fare: "Da iniziare",
  in_corso: "In lavorazione",
  eseguito: "Completate",
};

export const COLUMN_EMPTY: Record<ActivityStatus, string> = {
  backlog: "Niente in attesa di pianificazione.",
  da_fare: "Settimana libera: nessuna attività pianificata.",
  in_corso: "Nessuno ci sta lavorando adesso.",
  eseguito: "Ancora niente di completato questa settimana.",
};

// Posizione tra due vicini: media, oppure +/-1 agli estremi.
export function positionBetween(before?: number, after?: number): number {
  if (before === undefined && after === undefined) return 1;
  if (before === undefined) return after! - 1;
  if (after === undefined) return before + 1;
  return (before + after) / 2;
}
