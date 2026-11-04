// Tipi condivisi tra livello dati finto (memoria) e reale (Supabase, replica-backend).
// Rispecchiano replica/schema.sql.

export type Role = "owner" | "admin" | "planner" | "member";
export type CommessaStatus = "inserita" | "in_corso" | "in_attesa" | "chiusa" | "annullata";
export type ActivityStatus = "backlog" | "da_fare" | "in_corso" | "eseguito";

export interface Org { id: string; name: string; slug: string; timezone: string }
export interface Division { id: string; orgId: string; name: string }
export interface Office { id: string; orgId: string; divisionId: string; name: string; code: string | null }

export interface Member {
  id: string;            // membership id
  orgId: string;
  userId: string;
  username: string;
  fullName: string;
  role: Role;
  divisionId: string | null;
  officeId: string | null;
  weeklyCapacityMinutes: number | null;
  active: boolean;
}

export interface Customer { id: string; orgId: string; name: string }
export interface ProjectType { id: string; orgId: string; name: string; codePrefix: string; color: string }

export interface Commessa {
  id: string;
  orgId: string;
  divisionId: string | null;
  projectTypeId: string;
  customerId: string | null;
  code: string;
  name: string;
  subtitle: string | null;
  status: CommessaStatus;
  portfolio: string | null;
  quantity: number | null;
  updatedAt: string;
}

export interface Phase { id: string; orgId: string; commessaId: string; seq: number; name: string }
export interface Milestone { id: string; orgId: string; commessaId: string; phaseId: string | null; name: string; dueWeek: string }
export interface DelayReason { id: string; orgId: string; name: string }

export interface Activity {
  id: string;
  orgId: string;
  phaseId: string | null;
  milestoneId: string | null;
  officeId: string | null;
  assigneeId: string | null;
  predecessorId: string | null;
  code: string;
  title: string;
  description: string | null;
  weekStart: string | null;   // YYYY-MM-DD, lunedì
  status: ActivityStatus;
  position: number;
  estimatedMinutes: number;
  isIndirect: boolean;
  alert: boolean;
  doneAt: string | null;
  updatedAt: string;          // usato come versione
}

export interface TimeEntry { id: string; orgId: string; activityId: string; memberId: string; startedAt: string; endedAt: string | null }
export interface ActivityDelay { id: string; orgId: string; activityId: string; reasonId: string; note: string | null; createdAt: string }

// Card pronta per la bacheca: attività + dati collegati già risolti.
export interface BoardCard extends Activity {
  loggedMinutes: number;
  runningSince: string | null;
  commessaCode: string | null;
  commessaName: string | null;
  projectTypeName: string | null;
  customerName: string | null;
  officeName: string | null;
  assignee: { id: string; fullName: string } | null;
  milestoneWeek: string | null;
  lastDelay: string | null;
}

export interface BoardFilters { officeId?: string; memberId?: string; predecessor?: "all" | "with" | "without" }

export interface Board {
  weekStart: string;
  columns: Record<ActivityStatus, BoardCard[]>;
}

export interface CommessaListItem extends Commessa {
  projectType: ProjectType;
  customerName: string | null;
}

export interface Session { member: Member; org: Org }

export type Result<T> = { ok: true; value: T } | { ok: false; error: "not_found" | "forbidden" | "conflict" | "invalid"; message: string };

export interface NewActivityInput {
  title: string;
  weekStart: string | null;
  status: ActivityStatus;
  assigneeId: string | null;
  officeId: string | null;
  estimatedMinutes: number;
  isIndirect: boolean;
  phaseId: string | null;
  description: string | null;
}
