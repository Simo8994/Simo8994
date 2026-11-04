// Dati di prova inventati (nessun dato reale). Le settimane sono relative a oggi,
// così la bacheca ha sempre qualcosa da mostrare.
import type { Activity, ActivityDelay, Commessa, Customer, DelayReason, Division, Member, Milestone, Office, Org, Phase, ProjectType, TimeEntry } from "./types";
import { addWeeks, mondayOf, todayIn } from "../week";

export interface Store {
  orgs: Org[];
  divisions: Division[];
  offices: Office[];
  members: Member[];
  passwords: Record<string, string>; // solo per il livello finto
  customers: Customer[];
  projectTypes: ProjectType[];
  commesse: Commessa[];
  phases: Phase[];
  milestones: Milestone[];
  delayReasons: DelayReason[];
  activities: Activity[];
  timeEntries: TimeEntry[];
  delays: ActivityDelay[];
  seq: number;
}

export function seed(): Store {
  const now = new Date().toISOString();
  const org: Org = { id: "org-demo", name: "Metalli Demo", slug: "demo", timezone: "Europe/Rome" };
  const week = mondayOf(todayIn(org.timezone));
  const next = addWeeks(week, 1);
  const prev = addWeeks(week, -1);

  const divisions: Division[] = [
    { id: "div-nord", orgId: org.id, name: "Sede Nord" },
    { id: "div-sud", orgId: org.id, name: "Sede Sud" },
  ];
  const offices: Office[] = [
    { id: "off-tec", orgId: org.id, divisionId: "div-nord", name: "Ufficio tecnico", code: "UT" },
    { id: "off-man", orgId: org.id, divisionId: "div-nord", name: "Manutenzione", code: "MA" },
    { id: "off-qua", orgId: org.id, divisionId: "div-sud", name: "Qualità", code: "QU" },
  ];
  const m = (id: string, username: string, fullName: string, role: Member["role"], officeId: string, divisionId: string): Member => ({
    id, orgId: org.id, userId: "u-" + id, username, fullName, role, officeId, divisionId, weeklyCapacityMinutes: 2400, active: true,
  });
  const members: Member[] = [
    m("mem-anna", "anna.rossi", "Anna Rossi", "admin", "off-tec", "div-nord"),
    m("mem-luca", "luca.bianchi", "Luca Bianchi", "member", "off-tec", "div-nord"),
    m("mem-giulia", "giulia.verdi", "Giulia Verdi", "member", "off-man", "div-nord"),
    m("mem-paolo", "paolo.neri", "Paolo Neri", "member", "off-qua", "div-sud"),
  ];
  const passwords = Object.fromEntries(members.map((x) => [x.username, "demo"]));

  const customers: Customer[] = [
    { id: "cus-1", orgId: org.id, name: "Componenti Alfa Srl" },
    { id: "cus-2", orgId: org.id, name: "Beta Automotive SpA" },
  ];
  const projectTypes: ProjectType[] = [
    { id: "pt-man", orgId: org.id, name: "Manutenzione", codePrefix: "MAN", color: "#c9d3dd" },
    { id: "pt-cam", orgId: org.id, name: "Campionatura", codePrefix: "CAM", color: "#d8cfe0" },
    { id: "pt-sta", orgId: org.id, name: "Stampi", codePrefix: "STA", color: "#d6dccd" },
    { id: "pt-pro", orgId: org.id, name: "Progetto cliente", codePrefix: "PRG", color: "#e3d6c8" },
  ];
  const c = (id: string, pt: string, code: string, name: string, status: Commessa["status"], customerId: string | null, portfolio: string | null, quantity: number | null): Commessa => ({
    id, orgId: org.id, divisionId: "div-nord", projectTypeId: pt, customerId, code, name, subtitle: null, status, portfolio, quantity, updatedAt: now,
  });
  const commesse: Commessa[] = [
    c("com-1", "pt-man", "MAN26000012", "Revisione presse linea 2", "in_corso", null, null, null),
    c("com-2", "pt-cam", "CAM26000004", "Campioni staffa A12", "in_attesa", "cus-1", "Automotive", 50),
    c("com-3", "pt-sta", "STA26000007", "Stampo progressivo coperchio", "in_corso", "cus-2", "Automotive", 1),
    c("com-4", "pt-pro", "PRG26000021", "Supporto batteria con nome molto lungo per provare il troncamento su due righe", "inserita", "cus-2", "E-mobility", 1200),
  ];
  const phases: Phase[] = commesse.map((x) => ({ id: "ph-" + x.id, orgId: org.id, commessaId: x.id, seq: 1, name: "Fase 1" }));
  const milestones: Milestone[] = [
    { id: "ms-1", orgId: org.id, commessaId: "com-1", phaseId: "ph-com-1", name: "Fermo linea", dueWeek: week },
    { id: "ms-2", orgId: org.id, commessaId: "com-2", phaseId: "ph-com-2", name: "Invio campioni", dueWeek: next },
    { id: "ms-3", orgId: org.id, commessaId: "com-3", phaseId: "ph-com-3", name: "Prova stampo", dueWeek: prev },
  ];
  const delayReasons: DelayReason[] = [
    { id: "dr-1", orgId: org.id, name: "Materiale non arrivato" },
    { id: "dr-2", orgId: org.id, name: "Attesa dati dal cliente" },
    { id: "dr-3", orgId: org.id, name: "Macchina occupata" },
  ];
  const a = (id: string, phase: string | null, ms: string | null, code: string, title: string, status: Activity["status"], ws: string | null, assignee: string | null, office: string | null, est: number, pos: number, extra: Partial<Activity> = {}): Activity => ({
    id, orgId: org.id, phaseId: phase, milestoneId: ms, officeId: office, assigneeId: assignee, predecessorId: null, code, title,
    description: null, weekStart: ws, status, position: pos, estimatedMinutes: est, isIndirect: false, alert: false,
    doneAt: status === "eseguito" ? now : null, updatedAt: now, ...extra,
  });
  const activities: Activity[] = [
    a("act-1", "ph-com-2", "ms-2", "CAM26000004-001-02", "Misura campioni al banco", "backlog", null, null, "off-qua", 120, 1),
    a("act-2", "ph-com-1", "ms-1", "MAN26000012-001-01", "Sostituzione guide stampo 3", "da_fare", week, "mem-giulia", "off-man", 150, 1, { alert: true }),
    a("act-3", null, null, "IND-0001", "Riunione di reparto", "da_fare", week, "mem-luca", "off-tec", 60, 2, { isIndirect: true }),
    a("act-4", "ph-com-2", "ms-2", "CAM26000004-001-01", "Programmazione CAM staffa", "in_corso", week, "mem-luca", "off-tec", 180, 1),
    a("act-5", "ph-com-3", "ms-3", "STA26000007-001-01", "Aggiornare scheda tecnica con modifiche disegno", "eseguito", week, "mem-anna", "off-tec", 15, 1),
    a("act-6", "ph-com-3", "ms-3", "STA26000007-001-02", "Verifica dimensionale primo pezzo", "da_fare", week, "mem-paolo", "off-qua", 90, 3, { predecessorId: "act-5" }),
    a("act-7", "ph-com-4", null, "PRG26000021-001-01", "Studio di fattibilità", "da_fare", next, "mem-anna", "off-tec", 240, 1),
  ];
  const at = (h: number) => new Date(Date.now() - h * 3_600_000).toISOString();
  const timeEntries: TimeEntry[] = [
    { id: "te-1", orgId: org.id, activityId: "act-4", memberId: "mem-luca", startedAt: at(26), endedAt: at(23) },
    { id: "te-2", orgId: org.id, activityId: "act-4", memberId: "mem-luca", startedAt: at(0.7), endedAt: null },
    { id: "te-3", orgId: org.id, activityId: "act-5", memberId: "mem-anna", startedAt: at(30), endedAt: at(29.75) },
  ];
  const delays: ActivityDelay[] = [
    { id: "dl-1", orgId: org.id, activityId: "act-2", reasonId: "dr-1", note: null, createdAt: now },
  ];
  return { orgs: [org], divisions, offices, members, passwords, customers, projectTypes, commesse, phases, milestones, delayReasons, activities, timeEntries, delays, seq: 100 };
}
