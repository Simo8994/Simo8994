import { useId, type InputHTMLAttributes, type SelectHTMLAttributes, type TextareaHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

const control = cn(
  "w-full rounded-md border bg-surface px-3 text-sm text-text",
  "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-focus",
  "disabled:opacity-50",
);

interface Wrap { label: string; error?: string | null; hint?: string; className?: string }

function Shell({ id, label, error, hint, className, children }: Wrap & { id: string; children: React.ReactNode }) {
  return (
    <div className={cn("grid gap-1", className)}>
      <label htmlFor={id} className="text-xs text-text-muted">{label}</label>
      {children}
      {error ? <p id={`${id}-msg`} className="text-xs text-danger">{error}</p> : hint ? <p id={`${id}-msg`} className="text-xs text-text-muted">{hint}</p> : null}
    </div>
  );
}

export function TextField({ label, error, hint, className, ...rest }: Wrap & InputHTMLAttributes<HTMLInputElement>) {
  const id = useId();
  return (
    <Shell id={id} label={label} error={error} hint={hint} className={className}>
      <input id={id} aria-invalid={!!error || undefined} aria-describedby={error || hint ? `${id}-msg` : undefined}
        className={cn(control, "h-control-md", error ? "border-danger" : "border-border-input")} {...rest} />
    </Shell>
  );
}

export function TextArea({ label, error, hint, className, ...rest }: Wrap & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const id = useId();
  return (
    <Shell id={id} label={label} error={error} hint={hint} className={className}>
      <textarea id={id} aria-invalid={!!error || undefined} aria-describedby={error || hint ? `${id}-msg` : undefined}
        className={cn(control, "min-h-control-lg py-2", error ? "border-danger" : "border-border-input")} {...rest} />
    </Shell>
  );
}

export function SelectField({ label, error, hint, className, children, ...rest }: Wrap & SelectHTMLAttributes<HTMLSelectElement>) {
  const id = useId();
  return (
    <Shell id={id} label={label} error={error} hint={hint} className={className}>
      <select id={id} aria-invalid={!!error || undefined} aria-describedby={error || hint ? `${id}-msg` : undefined}
        className={cn(control, "h-control-md", error ? "border-danger" : "border-border-input")} {...rest}>
        {children}
      </select>
    </Shell>
  );
}
