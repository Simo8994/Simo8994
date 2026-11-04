import { cn } from "@/lib/cn";

const TINTS = ["bg-accent-soft text-on-accent-soft", "bg-success-soft text-success", "bg-warning-soft text-warning", "bg-danger-soft text-danger", "bg-surface-sunken text-text"];

export function initials(name: string): string {
  const p = name.trim().split(/\s+/);
  return ((p[0]?.[0] ?? "") + (p.length > 1 ? p[p.length - 1][0] : "")).toUpperCase();
}

export function Avatar({ name, size = "sm" }: { name: string; size?: "sm" | "md" }) {
  const tint = TINTS[[...name].reduce((h, ch) => h + ch.charCodeAt(0), 0) % TINTS.length];
  return (
    <span
      role="img"
      aria-label={name}
      title={name}
      className={cn("inline-grid shrink-0 place-items-center rounded-pill font-semibold", tint,
        size === "sm" ? "h-avatar-sm w-avatar-sm text-xs" : "h-avatar-md w-avatar-md text-xs")}
    >
      {initials(name)}
    </span>
  );
}
