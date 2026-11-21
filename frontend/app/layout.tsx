import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Resolve AI",
  description: "AI copilot for IT support tickets",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="topbar">
          <Link href="/" className="brand">
            Resolve AI
          </Link>
          <nav>
            <Link href="/tickets">Tickets</Link>
            <Link href="/tickets/new">New ticket</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
