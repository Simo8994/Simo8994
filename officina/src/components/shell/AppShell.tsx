"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { ChevronDown, HelpCircle, LogOut, Menu, X } from "lucide-react";
import { MAIN_NAV, SETTINGS_NAV, type NavItem } from "@/lib/nav";
import { Avatar } from "@/components/ui/Avatar";
import { cn } from "@/lib/cn";

interface Props {
  orgName: string;
  userName: string;
  username: string;
  divisions: { id: string; name: string }[];
  divisionId: string | null;
  logout: () => Promise<void>;
  children: React.ReactNode;
}

function NavLink({ item, active, onNavigate }: { item: NavItem; active: boolean; onNavigate: () => void }) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "relative flex h-control-lg items-center gap-3 rounded-md px-3 text-sm font-medium",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus",
        active ? "bg-accent-soft text-on-accent-soft before:absolute before:inset-y-2 before:left-0 before:w-1 before:rounded-pill before:bg-accent" : "text-text hover:bg-surface-sunken",
      )}
    >
      <Icon aria-hidden className="h-icon w-icon shrink-0" strokeWidth={1.75} />
      {item.label}
    </Link>
  );
}

export function AppShell({ orgName, userName, username, divisions, divisionId, logout, children }: Props) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(pathname.startsWith("/impostazioni"));
  const [userOpen, setUserOpen] = useState(false);
  const drawerRef = useRef<HTMLElement>(null);
  const menuBtn = useRef<HTMLButtonElement>(null);

  useEffect(() => setOpen(false), [pathname]);
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") { setOpen(false); menuBtn.current?.focus(); }
      if (e.key === "Tab" && drawerRef.current) {
        const f = drawerRef.current.querySelectorAll<HTMLElement>("a,button");
        const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    };
    document.addEventListener("keydown", onKey);
    drawerRef.current?.querySelector<HTMLElement>("a,button")?.focus();
    return () => document.removeEventListener("keydown", onKey);
  }, [open]);

  const isActive = (href: string) => pathname === href || pathname.startsWith(href + "/");
  const close = () => setOpen(false);

  const nav = (
    <nav aria-label="Principale" className="grid gap-1 p-3">
      {MAIN_NAV.map((i) => <NavLink key={i.href} item={i} active={isActive(i.href)} onNavigate={close} />)}
      <button
        type="button"
        aria-expanded={settingsOpen}
        aria-controls="nav-settings"
        onClick={() => setSettingsOpen((v) => !v)}
        className="mt-2 flex h-control-lg items-center gap-2 rounded-md px-3 text-sm font-semibold text-text-muted hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus"
      >
        <ChevronDown aria-hidden className={cn("h-icon w-icon transition-transform duration-fast", !settingsOpen && "-rotate-90")} />
        Impostazioni
      </button>
      <div id="nav-settings" hidden={!settingsOpen} className="grid gap-1">
        {SETTINGS_NAV.map((i) => <NavLink key={i.href} item={i} active={isActive(i.href)} onNavigate={close} />)}
      </div>
    </nav>
  );

  return (
    <div className="min-h-screen bg-bg">
      <a href="#contenuto" className="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded-md focus:bg-surface focus:p-2">Vai al contenuto</a>
      <header className="sticky top-0 z-30 flex h-header items-center gap-2 border-b border-border bg-surface px-2 lg:px-4">
        <button ref={menuBtn} type="button" aria-label="Apri menu" aria-expanded={open} aria-controls="drawer"
          onClick={() => setOpen(true)}
          className="grid h-control-md w-control-md place-items-center rounded-md hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus lg:hidden">
          <Menu aria-hidden className="h-icon w-icon" />
        </button>
        <Link href="/scrum" className="truncate text-lg font-bold focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">{orgName}</Link>
        <span className="flex-1" />
        {divisions.length > 0 && (
          <label className="hidden items-center gap-2 text-sm sm:flex">
            <span className="text-text-muted">Sede</span>
            <select defaultValue={divisionId ?? ""} className="h-control-sm rounded-md border border-border-input bg-surface px-2 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
              {divisions.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
          </label>
        )}
        <Link href="/aiuto" aria-label="Aiuto" className="grid h-control-md w-control-md place-items-center rounded-md hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
          <HelpCircle aria-hidden className="h-icon w-icon" />
        </Link>
        <div className="relative">
          <button type="button" aria-expanded={userOpen} aria-haspopup="menu" onClick={() => setUserOpen((v) => !v)}
            className="flex h-control-md items-center gap-2 rounded-md px-1 hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
            <Avatar name={userName} size="md" />
            <span className="hidden text-sm md:inline">{username}</span>
            <ChevronDown aria-hidden className="hidden h-icon w-icon md:inline" />
          </button>
          {userOpen && (
            <div role="menu" className="absolute right-0 top-full mt-1 w-sidebar rounded-md border border-border bg-surface p-1 shadow-pop">
              <p className="px-3 py-2 text-sm"><span className="font-semibold">{userName}</span><br /><span className="text-text-muted">{username}</span></p>
              <form action={logout}>
                <button role="menuitem" type="submit" className="flex h-control-md w-full items-center gap-2 rounded-md px-3 text-sm hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
                  <LogOut aria-hidden className="h-icon w-icon" /> Esci
                </button>
              </form>
            </div>
          )}
        </div>
      </header>

      <div className="lg:flex">
        <aside className="sticky top-header hidden h-[calc(100vh-var(--layout-header))] w-sidebar shrink-0 overflow-y-auto border-r border-border bg-surface lg:block">
          {nav}
        </aside>
        {open && (
          <div className="fixed inset-0 z-40 lg:hidden">
            <div className="absolute inset-0 bg-overlay" onClick={close} aria-hidden />
            <aside id="drawer" ref={drawerRef} role="dialog" aria-modal="true" aria-label="Menu"
              className="absolute inset-y-0 left-0 w-sidebar max-w-full overflow-y-auto bg-surface shadow-pop">
              <div className="flex h-header items-center justify-between border-b border-border px-3">
                <span className="font-bold">{orgName}</span>
                <button type="button" aria-label="Chiudi menu" onClick={() => { close(); menuBtn.current?.focus(); }}
                  className="grid h-control-md w-control-md place-items-center rounded-md hover:bg-surface-sunken focus-visible:outline focus-visible:outline-2 focus-visible:outline-focus">
                  <X aria-hidden className="h-icon w-icon" />
                </button>
              </div>
              {nav}
            </aside>
          </div>
        )}
        <main id="contenuto" className="min-w-0 flex-1">{children}</main>
      </div>
    </div>
  );
}
