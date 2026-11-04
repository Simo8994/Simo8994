import { requireSession } from "@/lib/session";
import { listDivisions } from "@/lib/data";
import { AppShell } from "@/components/shell/AppShell";
import { logout } from "../login/actions";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { member, org } = await requireSession();
  const divisions = await listDivisions(org.id);
  return (
    <AppShell orgName={org.name} userName={member.fullName} username={member.username}
      divisions={divisions.map((d) => ({ id: d.id, name: d.name }))} divisionId={member.divisionId} logout={logout}>
      {children}
    </AppShell>
  );
}
