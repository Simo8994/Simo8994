import Link from "next/link";
import { Construction } from "lucide-react";
import { buttonClass } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";

export function Placeholder({ title, screen, text }: { title: string; screen: string; text: string }) {
  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-4 px-4 py-5">
      <h1 className="text-xl font-bold">{title}</h1>
      <div className="rounded-lg border border-border bg-surface">
        <EmptyState icon={Construction} title="In costruzione" text={`${text} (${screen})`}
          action={<Link href="/scrum" className={buttonClass("secondary", "md")}>Vai alla bacheca</Link>} />
      </div>
    </div>
  );
}
