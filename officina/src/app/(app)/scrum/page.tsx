import type { Metadata } from "next";
import Link from "next/link";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { getBoard, listMembers, listOffices } from "@/lib/data";
import type { BoardFilters } from "@/lib/data/types";
import { requireSession } from "@/lib/session";
import { addWeeks, isDate, mondayOf, todayIn, weekLabel } from "@/lib/week";
import { buttonClass } from "@/components/ui/Button";
import { Board } from "./Board";
import { Filters } from "./Filters";

export const metadata: Metadata = { title: "Bacheca settimanale" };

type SP = { week?: string; office?: string; user?: string; pred?: string };

export default async function ScrumPage({ searchParams }: { searchParams: Promise<SP> }) {
  const { org, member } = await requireSession();
  const sp = await searchParams;
  const today = mondayOf(todayIn(org.timezone));
  const week = isDate(sp.week) ? mondayOf(sp.week) : today;
  const filters: BoardFilters = {
    officeId: sp.office || undefined,
    memberId: sp.user === "me" ? member.id : sp.user || undefined,
    predecessor: sp.pred === "with" || sp.pred === "without" ? sp.pred : "all",
  };
  const [board, offices, members] = await Promise.all([getBoard(org.id, week, filters), listOffices(org.id), listMembers(org.id)]);
  const qs = (w: string) => {
    const p = new URLSearchParams();
    if (w !== today) p.set("week", w);
    if (sp.office) p.set("office", sp.office);
    if (sp.user) p.set("user", sp.user);
    if (sp.pred) p.set("pred", sp.pred);
    const s = p.toString();
    return s ? `/scrum?${s}` : "/scrum";
  };

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-4 px-4 py-5">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-xl font-bold">Bacheca settimanale</h1>
      </div>
      <div className="flex flex-wrap items-end gap-3">
        <nav aria-label="Settimana" className="flex items-center gap-1">
          <Link href={qs(addWeeks(week, -1))} aria-label="Settimana precedente" className={buttonClass("ghost", "md", "w-control-md px-0")}><ChevronLeft aria-hidden className="h-icon w-icon" /></Link>
          <p className="min-w-0 px-1 text-sm font-semibold" aria-live="polite">{weekLabel(week)}</p>
          <Link href={qs(addWeeks(week, 1))} aria-label="Settimana successiva" className={buttonClass("ghost", "md", "w-control-md px-0")}><ChevronRight aria-hidden className="h-icon w-icon" /></Link>
          {week !== today && <Link href={qs(today)} className={buttonClass("secondary", "sm")}>Questa settimana</Link>}
        </nav>
        <Filters offices={offices.map((o) => ({ id: o.id, name: o.name }))} members={members.map((m) => ({ id: m.id, name: m.fullName }))}
          value={{ office: sp.office ?? "", user: sp.user ?? "", pred: sp.pred ?? "" }} />
        <div className="flex gap-2">
          <Link href={`/scrum/carico${week !== today ? `?week=${week}` : ""}`} className={buttonClass("secondary", "md")}>Carico persone</Link>
          <Link href={`/scrum/andamento${week !== today ? `?week=${week}` : ""}`} className={buttonClass("secondary", "md")}>Andamento settimana</Link>
        </div>
      </div>
      <Board key={`${week}|${sp.office}|${sp.user}|${sp.pred}`} board={board} week={week} meId={member.id}
        offices={offices.map((o) => ({ id: o.id, name: o.name }))} members={members.map((m) => ({ id: m.id, name: m.fullName }))}
        defaultOfficeId={member.officeId} />
    </div>
  );
}
