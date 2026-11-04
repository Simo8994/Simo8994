import {
  LayoutGrid, Repeat, CalendarDays, Columns3, KanbanSquare, BarChart3, Users, Building2, GraduationCap,
  Briefcase, Shapes, Flag, ListChecks, Inbox, AlertTriangle, CalendarClock, FileInput, Wrench, type LucideIcon,
} from "lucide-react";

export interface NavItem { href: string; label: string; icon: LucideIcon; screen: string }

export const MAIN_NAV: NavItem[] = [
  { href: "/commesse", label: "Commesse", icon: LayoutGrid, screen: "S02" },
  { href: "/ricorrenze", label: "Ricorrenze", icon: Repeat, screen: "S07" },
  { href: "/calendario", label: "Calendario", icon: CalendarDays, screen: "S06" },
  { href: "/kanban", label: "Kanban", icon: KanbanSquare, screen: "S05" },
  { href: "/scrum", label: "Bacheca settimanale", icon: Columns3, screen: "S03" },
  { href: "/cruscotto", label: "Cruscotto", icon: BarChart3, screen: "S08" },
];

export const SETTINGS_NAV: NavItem[] = [
  { href: "/impostazioni/persone", label: "Persone", icon: Users, screen: "S13" },
  { href: "/impostazioni/sedi", label: "Sedi", icon: Building2, screen: "S14" },
  { href: "/impostazioni/competenze", label: "Competenze", icon: GraduationCap, screen: "S15" },
  { href: "/impostazioni/uffici", label: "Uffici", icon: Briefcase, screen: "S16" },
  { href: "/impostazioni/tipi-progetto", label: "Tipi di progetto", icon: Shapes, screen: "S17" },
  { href: "/impostazioni/scadenze", label: "Tipi di scadenza", icon: Flag, screen: "S18" },
  { href: "/impostazioni/catalogo-attivita", label: "Catalogo attività", icon: ListChecks, screen: "S19" },
  { href: "/impostazioni/code-lavoro", label: "Code di lavoro", icon: Inbox, screen: "S20" },
  { href: "/impostazioni/motivi-ritardo", label: "Motivi di ritardo", icon: AlertTriangle, screen: "S21" },
  { href: "/impostazioni/calendari", label: "Calendari lavorativi", icon: CalendarClock, screen: "S22" },
  { href: "/impostazioni/importazioni", label: "Importazioni", icon: FileInput, screen: "S23" },
  { href: "/impostazioni/bacheca", label: "Configura bacheca", icon: Wrench, screen: "S24" },
];

export const ALL_NAV = [...MAIN_NAV, ...SETTINGS_NAV];
