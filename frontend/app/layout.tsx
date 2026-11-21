import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resolve AI",
  description: "AI copilot for IT support tickets",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
