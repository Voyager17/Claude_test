"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState, useEffect } from "react";

const allLinks = [
  { href: "/movies", label: "Фильмы", adminOnly: false },
  { href: "/customers", label: "Клиенты", adminOnly: true },
  { href: "/rentals", label: "Аренды", adminOnly: true },
];

export default function NavBar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isDark, setIsDark] = useState(false);
  const [email, setEmail] = useState<string | null>(null);
  const [role, setRole] = useState<string>("");

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "dark") {
      document.documentElement.classList.add("dark");
      setIsDark(true);
    }
    setEmail(localStorage.getItem("email") ?? "");
    setRole(localStorage.getItem("role") ?? "");
  }, []);

  const isAdmin = role === "admin";

  function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    router.replace("/login");
  }

  function toggleTheme() {
    const next = !isDark;
    setIsDark(next);
    if (next) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }

  return (
    <nav className="bg-slate-900 border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6 py-0 flex items-center gap-10">
        <span className="text-white font-bold text-lg tracking-tight py-4 shrink-0">
          VideoRent
        </span>
        <div className="flex flex-1">
          {allLinks.filter(l => !l.adminOnly || isAdmin).map(l => (
            <Link
              key={l.href}
              href={l.href}
              className={`px-5 py-4 text-sm font-medium border-b-2 transition-colors ${
                pathname.startsWith(l.href)
                  ? "border-blue-500 text-white"
                  : "border-transparent text-slate-400 hover:text-white hover:border-slate-500"
              }`}
            >
              {l.label}
            </Link>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
            title={isDark ? "Светлая тема" : "Тёмная тема"}
          >
            {isDark ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
              </svg>
            )}
          </button>
          <div className="pl-2 border-l border-slate-700">
            {email === null ? null : email ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400 hidden sm:block">{email}</span>
                <button
                  onClick={logout}
                  className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
                >
                  Выйти
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors"
              >
                Войти
              </Link>
            )}
          </div>

        </div>
      </div>
    </nav>
  );
}
