import type { LucideIcon } from "lucide-react";

export function EmptyState({ icon: Icon, title, text, action }: { icon: LucideIcon; title: string; text?: string; action?: React.ReactNode }) {
  return (
    <div className="grid justify-items-center gap-2 px-4 py-6 text-center">
      <Icon aria-hidden className="h-control-md w-control-md text-text-muted" strokeWidth={1.5} />
      <p className="text-base font-semibold">{title}</p>
      {text && <p className="max-w-prose text-sm text-text-muted">{text}</p>}
      {action}
    </div>
  );
}
