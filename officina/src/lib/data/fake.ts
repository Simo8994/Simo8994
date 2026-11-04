// Livello dati finto, in memoria. Stesse firme del livello reale: cambiare
// implementazione non tocca le schermate. Solo per sviluppo.
import "server-only";
import { seed, type Store } from "./seed";
import type {
  ActivityStatus, Board, BoardCard, BoardFilters, CommessaListItem, CommessaStatus, DelayReason,
  Member, NewActivityInput, Office, Result, Session, Division,
} from "./types";

const g = globalThis as unknown as { __officinaStore?: Store };
function db(): Store {
  if (!g.__officinaStore) g.__officinaStore = seed();
  return g.__officinaStore;
}

const STATUSES: ActivityStatus[] = ["backlog", "da_fare", "in_corso", "eseguito"];
const nextId = (p: string) => `${p}-${++db().seq}`;
const stamp = () => new Date(Date.now() + db().seq).toISOString(); // sempre diverso: fa da versione

// ------------------------------------------------------------------ auth
export async function verifyLogin(username: string, password: string): Promise<Member | null> {
  const s = db();
  const u = username.trim().toLowerCase();
  const member = s.members.find((m) => m.username === u && m.active);
  if (!member || s.passwords[u] !== password) return null;
  return member;
}

export async function getSessionFor(memberId: string): Promise<Session | null> {
  const s = db();
  const member = s.members.find((m) => m.id === memberId && m.active);
  if (!member) return null;
  const org = s.orgs.find((o) => o.id === member.orgId)!;
  return { member, org };
}

// ------------------------------------------------------------------ anagrafiche
export async function listOffices(orgId: string): Promise<Office[]> {
  return db().offices.filter((o) => o.orgId === orgId);
}
export async function listDivisions(orgId: string): Promise<Division[]> {
  return db().divisions.filter((d) => d.orgId === orgId);
}
export async function listMembers(orgId: string): Promise<Member[]> {
  return db().members.filter((m) => m.orgId === orgId && m.active);
}
export async function listDelayReasons(orgId: string): Promise<DelayReason[]> {
  return db().delayReasons.filter((r) => r.orgId === orgId);
}

// ------------------------------------------------------------------ commesse
export async function listCommesse(orgId: string, statuses: CommessaStatus[]): Promise<CommessaListItem[]> {
  const s = db();
  return s.commesse
    .filter((c) => c.orgId === orgId && (statuses.length === 0 || statuses.includes(c.status)))
    .sort((a, b) => b.code.localeCompare(a.code))
    .map((c) => ({
      ...c,
      projectType: s.projectTypes.find((p) => p.id === c.projectTypeId)!,
      customerName: s.customers.find((x) => x.id === c.customerId)?.name ?? null,
    }));
}

// ------------------------------------------------------------------ bacheca
function toCard(s: Store, id: string): BoardCard {
  const a = s.activities.find((x) => x.id === id)!;
  const phase = s.phases.find((p) => p.id === a.phaseId);
  const commessa = phase ? s.commesse.find((c) => c.id === phase.commessaId) : undefined;
  const entries = s.timeEntries.filter((t) => t.activityId === a.id);
  const logged = entries.reduce((sum, t) => (t.endedAt ? sum + (Date.parse(t.endedAt) - Date.parse(t.startedAt)) / 60000 : sum), 0);
  const running = entries.find((t) => !t.endedAt);
  const assignee = s.members.find((m) => m.id === a.assigneeId);
  const lastDelay = s.delays.filter((d) => d.activityId === a.id).at(-1);
  return {
    ...a,
    loggedMinutes: Math.round(logged),
    runningSince: running?.startedAt ?? null,
    commessaCode: commessa?.code ?? null,
    commessaName: commessa?.name ?? null,
    projectTypeName: commessa ? s.projectTypes.find((p) => p.id === commessa.projectTypeId)?.name ?? null : null,
    customerName: commessa?.customerId ? s.customers.find((x) => x.id === commessa.customerId)?.name ?? null : commessa ? "Interna" : null,
    officeName: s.offices.find((o) => o.id === a.officeId)?.name ?? null,
    assignee: assignee ? { id: assignee.id, fullName: assignee.fullName } : null,
    milestoneWeek: s.milestones.find((m) => m.id === a.milestoneId)?.dueWeek ?? null,
    lastDelay: lastDelay ? s.delayReasons.find((r) => r.id === lastDelay.reasonId)?.name ?? null : null,
  };
}

export async function getBoard(orgId: string, weekStart: string, f: BoardFilters): Promise<Board> {
  const s = db();
  const columns = Object.fromEntries(STATUSES.map((st) => [st, [] as BoardCard[]])) as Board["columns"];
  for (const a of s.activities) {
    if (a.orgId !== orgId) continue;
    if (a.status === "backlog" ? a.weekStart !== null && a.weekStart !== weekStart : a.weekStart !== weekStart) continue;
    if (f.officeId && a.officeId !== f.officeId) continue;
    if (f.memberId && a.assigneeId !== f.memberId) continue;
    if (f.predecessor === "with" && !a.predecessorId) continue;
    if (f.predecessor === "without" && a.predecessorId) continue;
    columns[a.status].push(toCard(s, a.id));
  }
  for (const st of STATUSES) columns[st].sort((x, y) => x.position - y.position);
  return { weekStart, columns };
}

function canEdit(session: Session, assigneeId: string | null): boolean {
  const r = session.member.role;
  return r === "owner" || r === "admin" || r === "planner" || assigneeId === session.member.id || assigneeId === null;
}

export async function moveActivity(
  session: Session,
  input: { id: string; status: ActivityStatus; position: number; version: string },
): Promise<Result<BoardCard>> {
  const s = db();
  const a = s.activities.find((x) => x.id === input.id && x.orgId === session.org.id);
  if (!a) return { ok: false, error: "not_found", message: "Attività non trovata." };
  if (!canEdit(session, a.assigneeId)) return { ok: false, error: "forbidden", message: "Puoi spostare solo le tue attività." };
  if (a.updatedAt !== input.version) return { ok: false, error: "conflict", message: "Qualcuno ha appena modificato questa attività. La bacheca è stata aggiornata." };
  if (!STATUSES.includes(input.status) || !Number.isFinite(input.position)) return { ok: false, error: "invalid", message: "Spostamento non valido." };
  if (input.status !== "backlog" && !a.weekStart) return { ok: false, error: "invalid", message: "Assegna prima una settimana all'attività." };
  a.status = input.status;
  a.position = input.position;
  a.doneAt = input.status === "eseguito" ? a.doneAt ?? new Date().toISOString() : null;
  a.updatedAt = stamp();
  return { ok: true, value: toCard(s, a.id) };
}

export async function createActivity(session: Session, input: NewActivityInput): Promise<Result<BoardCard>> {
  const s = db();
  const title = input.title.trim();
  if (title.length < 2 || title.length > 200) return { ok: false, error: "invalid", message: "Il titolo deve avere tra 2 e 200 caratteri." };
  if (!Number.isInteger(input.estimatedMinutes) || input.estimatedMinutes < 0 || input.estimatedMinutes > 100 * 60)
    return { ok: false, error: "invalid", message: "La stima deve essere tra 0 e 100 ore." };
  const status = input.weekStart ? input.status : "backlog";
  if (input.assigneeId && !s.members.some((m) => m.id === input.assigneeId && m.orgId === session.org.id))
    return { ok: false, error: "invalid", message: "Persona non valida." };
  if (input.officeId && !s.offices.some((o) => o.id === input.officeId && o.orgId === session.org.id))
    return { ok: false, error: "invalid", message: "Ufficio non valido." };
  const sameCol = s.activities.filter((x) => x.orgId === session.org.id && x.status === status && x.weekStart === input.weekStart);
  const position = sameCol.reduce((mx, x) => Math.max(mx, x.position), 0) + 1;
  const id = nextId("act");
  const code = input.isIndirect ? `IND-${String(s.seq).padStart(4, "0")}` : `ATT-${String(s.seq).padStart(4, "0")}`;
  const now = stamp();
  s.activities.push({
    id, orgId: session.org.id, phaseId: input.phaseId, milestoneId: null, officeId: input.officeId, assigneeId: input.assigneeId,
    predecessorId: null, code, title, description: input.description?.trim() || null, weekStart: input.weekStart, status,
    position, estimatedMinutes: input.estimatedMinutes, isIndirect: input.isIndirect, alert: false,
    doneAt: status === "eseguito" ? now : null, updatedAt: now,
  });
  return { ok: true, value: toCard(s, id) };
}

// Solo per i test: riporta i dati allo stato iniziale.
export async function resetStore(): Promise<void> {
  g.__officinaStore = seed();
}
