"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { SelectField } from "@/components/ui/Field";

interface Opt { id: string; name: string }

export function Filters({ offices, members, value }: { offices: Opt[]; members: Opt[]; value: { office: string; user: string; pred: string } }) {
  const router = useRouter();
  const pathname = usePathname();
  const sp = useSearchParams();
  const set = (key: string, v: string) => {
    const p = new URLSearchParams(sp.toString());
    if (v) p.set(key, v); else p.delete(key);
    const s = p.toString();
    router.push(s ? `${pathname}?${s}` : pathname);
  };
  return (
    <div className="flex flex-wrap gap-3">
      <SelectField label="Ufficio" value={value.office} onChange={(e) => set("office", e.target.value)} className="w-sidebar max-w-full">
        <option value="">Tutti gli uffici</option>
        {offices.map((o) => <option key={o.id} value={o.id}>{o.name}</option>)}
      </SelectField>
      <SelectField label="Persona" value={value.user} onChange={(e) => set("user", e.target.value)} className="w-sidebar max-w-full">
        <option value="">Tutte le persone</option>
        <option value="me">Solo le mie</option>
        {members.map((m) => <option key={m.id} value={m.id}>{m.name}</option>)}
      </SelectField>
      <SelectField label="Dipendenze" value={value.pred} onChange={(e) => set("pred", e.target.value)} className="w-column max-w-full">
        <option value="">Tutte</option>
        <option value="with">Con attività precedente</option>
        <option value="without">Senza attività precedente</option>
      </SelectField>
    </div>
  );
}
