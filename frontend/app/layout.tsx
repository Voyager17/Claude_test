import type { Metadata } from "next";
import AuthGuard from "./components/AuthGuard";
import "./globals.css";

export const metadata: Metadata = {
  title: "VideoRent",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body className="bg-slate-50 dark:bg-slate-950 min-h-screen transition-colors">
        <AuthGuard>{children}</AuthGuard>
      </body>
    </html>
  );
}
