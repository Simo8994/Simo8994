import { notFound } from "next/navigation";
import { Placeholder } from "@/components/shell/Placeholder";
import { SETTINGS_NAV } from "@/lib/nav";

export default async function Page({ params }: { params: Promise<{ section: string }> }) {
  const { section } = await params;
  const item = SETTINGS_NAV.find((i) => i.href === `/impostazioni/${section}`);
  if (!item) notFound();
  return <Placeholder title={item.label} screen={item.screen} text="Gestione di questa anagrafica" />;
}
