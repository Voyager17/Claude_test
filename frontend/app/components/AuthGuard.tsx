"use client";

import { usePathname } from "next/navigation";
import NavBar from "./NavBar";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  if (pathname === "/login") {
    return <>{children}</>;
  }

  return (
    <>
      <NavBar />
      <main className="relative z-10 max-w-7xl mx-auto px-6 py-8">{children}</main>
    </>
  );
}
