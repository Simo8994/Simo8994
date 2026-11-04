import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = { title: { default: "Officina", template: "%s · Officina" }, description: "Pianificazione settimanale di commesse e attività." };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body>{children}</body>
    </html>
  );
}
