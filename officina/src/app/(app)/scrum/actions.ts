"use server";
import { revalidatePath } from "next/cache";
import { createActivity, moveActivity } from "@/lib/data";
import type { ActivityStatus, BoardCard, NewActivityInput, Result } from "@/lib/data/types";
import { requireSession } from "@/lib/session";
import { isDate, mondayOf } from "@/lib/week";

export async function moveActivityAction(input: { id: string; status: ActivityStatus; position: number; version: string }): Promise<Result<BoardCard>> {
  const session = await requireSession();
  const res = await moveActivity(session, input);
  if (res.ok) revalidatePath("/scrum");
  return res;
}

export async function createActivityAction(form: FormData): Promise<Result<BoardCard>> {
  const session = await requireSession();
  const week = String(form.get("weekStart") ?? "");
  const hours = Number(form.get("hours") || 0);
  const minutes = Number(form.get("minutes") || 0);
  const input: NewActivityInput = {
    title: String(form.get("title") ?? ""),
    weekStart: week === "backlog" ? null : isDate(week) ? mondayOf(week) : null,
    status: (String(form.get("status") || "da_fare") as ActivityStatus),
    assigneeId: String(form.get("assigneeId") || "") || null,
    officeId: String(form.get("officeId") || "") || null,
    estimatedMinutes: Math.round(hours * 60 + minutes),
    isIndirect: form.get("isIndirect") === "on",
    phaseId: null,
    description: String(form.get("description") ?? "") || null,
  };
  if (!["da_fare", "in_corso", "eseguito", "backlog"].includes(input.status)) return { ok: false, error: "invalid", message: "Colonna non valida." };
  const res = await createActivity(session, input);
  if (res.ok) revalidatePath("/scrum");
  return res;
}
