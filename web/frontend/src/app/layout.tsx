import type { Metadata } from "next";
import Providers from "./providers";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Firebird Sales Dashboard",
  description: "Mobile-first analytics dashboard for Firebird sales via Proxy API"
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className="min-h-screen bg-slate-50 text-slate-900">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}

