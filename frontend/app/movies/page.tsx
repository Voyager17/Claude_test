"use client";

import { useState, useEffect, type ReactNode } from "react";
import Image from "next/image";

const API = "http://localhost:8001/api/v1";

interface Movie {
  id: number;
  title: string;
  director: string;
  year: number;
  genre: string;
  rating: number;
  rental_price_per_day: number;
  available_copies: number;
  is_active: boolean;
  image_url: string | null;
}

const emptyForm = {
  title: "",
  director: "",
  year: new Date().getFullYear(),
  genre: "",
  rating: 0,
  rental_price_per_day: 1,
  available_copies: 1,
  image_url: "",
};

const genreGradients: Record<string, string> = {
  Drama:    "from-violet-500 to-purple-700",
  Action:   "from-orange-500 to-red-700",
  "Sci-Fi": "from-cyan-500 to-blue-700",
  Comedy:   "from-yellow-400 to-orange-500",
  Thriller: "from-slate-600 to-slate-900",
  Crime:    "from-rose-600 to-red-900",
  History:  "from-amber-500 to-yellow-700",
};

function posterGradient(genre: string) {
  return genreGradients[genre] ?? "from-slate-400 to-slate-600";
}

export default function MoviesPage() {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [sortField, setSortField] = useState<"title" | "rating" | "year">("title");
  const [sortAsc, setSortAsc] = useState(true);
  const [page, setPage] = useState(1);
  const [isAdmin, setIsAdmin] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const PAGE_SIZE = 10;

  useEffect(() => {
    setIsAdmin(localStorage.getItem("role") === "admin");
  }, []);

  async function fetchMovies() {
    const res = await fetch(`${API}/movies/`);
    setMovies(await res.json());
    setLoading(false);
  }

  useEffect(() => { fetchMovies(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const body = { ...form, image_url: form.image_url || null };
    const res = await fetch(`${API}/movies/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      setShowForm(false);
      setForm(emptyForm);
      fetchMovies();
    } else {
      const data = await res.json();
      const detail = data.detail;
      setError(
        typeof detail === "string" ? detail
        : Array.isArray(detail) ? detail.map((e: { msg: string }) => e.msg).join("; ")
        : "Ошибка при создании"
      );
    }
  }

  async function handleDelete(id: number) {
    await fetch(`${API}/movies/${id}`, { method: "DELETE" });
    fetchMovies();
  }

  const selectedMovie = movies.find(m => m.id === selectedId) ?? null;

  return (
    <div>
      {/* Blurred background */}
      {selectedMovie && (
        <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
          {selectedMovie.image_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={selectedMovie.image_url}
              alt=""
              className="w-full h-full object-cover"
              style={{ filter: "blur(15px) brightness(0.5)", transform: "scale(1.15)" }}
            />
          ) : (
            <div
              className={`w-full h-full bg-gradient-to-br ${posterGradient(selectedMovie.genre)}`}
              style={{ filter: "blur(15px) brightness(0.55)", transform: "scale(1.15)" }}
            />
          )}
        </div>
      )}

      <div className="relative z-10">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="bg-white/75 dark:bg-slate-900/75 backdrop-blur-sm rounded-xl px-4 py-2">
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Фильмы</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            {movies.length > 0 ? `${movies.length} фильм${plural(movies.length)}` : ""}
          </p>
        </div>
        <div className="flex items-center gap-3">
          {(["title", "rating", "year"] as const).map(field => (
            <button
              key={field}
              onClick={() => {
                if (sortField === field) setSortAsc((v: boolean) => !v);
                else { setSortField(field); setSortAsc(field === "rating" ? false : true); }
              }}
              className={`flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium border transition-all shadow-sm ${
                sortField === field
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              {{ title: "А–Я", rating: "Рейтинг", year: "Год" }[field]}
              {sortField === field && <span className="text-xs">{sortAsc ? "↑" : "↓"}</span>}
            </button>
          ))}
          {isAdmin && (
            <button
              onClick={() => { setShowForm(!showForm); setError(""); }}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                showForm
                  ? "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-600"
                  : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
              }`}
            >
              {showForm ? "Отмена" : "+ Добавить фильм"}
            </button>
          )}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Form */}
      {isAdmin && showForm && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-5">Новый фильм</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
            <Field label="Название">
              <input required className={inp} placeholder="Например: Интерстеллар" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
            </Field>
            <Field label="Режиссёр">
              <input required className={inp} placeholder="Например: Кристофер Нолан" value={form.director} onChange={e => setForm({ ...form, director: e.target.value })} />
            </Field>
            <Field label="Год">
              <input required type="number" className={inp} value={form.year} onChange={e => setForm({ ...form, year: +e.target.value })} />
            </Field>
            <Field label="Жанр">
              <input required className={inp} placeholder="Например: Sci-Fi" value={form.genre} onChange={e => setForm({ ...form, genre: e.target.value })} />
            </Field>
            <Field label="Рейтинг (0–10)">
              <input type="number" step="0.1" min="0" max="10" className={inp} value={form.rating} onChange={e => setForm({ ...form, rating: +e.target.value })} />
            </Field>
            <Field label="Цена аренды в день (₽)">
              <input required type="number" step="0.01" min="0" className={inp} value={form.rental_price_per_day} onChange={e => setForm({ ...form, rental_price_per_day: +e.target.value })} />
            </Field>
            <Field label="Количество копий">
              <input required type="number" min="1" className={inp} value={form.available_copies} onChange={e => setForm({ ...form, available_copies: +e.target.value })} />
            </Field>
            <Field label="Ссылка на постер (необязательно)">
              <input className={inp} placeholder="https://..." value={form.image_url} onChange={e => setForm({ ...form, image_url: e.target.value })} />
            </Field>
            <div className="col-span-2 flex justify-end pt-2">
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
                Сохранить
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="grid grid-cols-3 gap-5">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden animate-pulse">
              <div className="h-48 bg-slate-100 dark:bg-slate-800" />
              <div className="p-4 space-y-2">
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-3/4" />
                <div className="h-3 bg-slate-100 dark:bg-slate-800 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : movies.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <p className="text-4xl mb-3">🎬</p>
          <p className="font-medium">Фильмов пока нет</p>
          <p className="text-sm mt-1">Добавьте первый фильм</p>
        </div>
      ) : (() => {
        const sorted = [...movies].sort((a, b) => {
          let cmp = 0;
          if (sortField === "title") cmp = a.title.localeCompare(b.title);
          else if (sortField === "rating") cmp = a.rating - b.rating;
          else cmp = a.year - b.year;
          return sortAsc ? cmp : -cmp;
        });
        const totalPages = Math.ceil(sorted.length / PAGE_SIZE);
        const paged = sorted.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
        return (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {paged.map(m => (
                <MovieCard
                  key={m.id}
                  movie={m}
                  onDelete={handleDelete}
                  isAdmin={isAdmin}
                  isSelected={m.id === selectedId}
                  onSelect={() => setSelectedId(prev => prev === m.id ? null : m.id)}
                />
              ))}
            </div>
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-1 mt-8">
                <button
                  onClick={() => setPage((p: number) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-3 py-1.5 rounded-lg text-sm border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  ←
                </button>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`w-9 h-9 rounded-lg text-sm font-medium transition-all ${
                      p === page
                        ? "bg-blue-600 text-white border border-blue-600"
                        : "border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500"
                    }`}
                  >
                    {p}
                  </button>
                ))}
                <button
                  onClick={() => setPage((p: number) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className="px-3 py-1.5 rounded-lg text-sm border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:border-slate-300 dark:hover:border-slate-500 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                >
                  →
                </button>
              </div>
            )}
          </>
        );
      })()}

      </div>
    </div>
  );
}

function MovieCard({ movie: m, onDelete, isAdmin, isSelected, onSelect }: {
  movie: Movie;
  onDelete: (id: number) => void;
  isAdmin: boolean;
  isSelected: boolean;
  onSelect: () => void;
}) {
  const [confirming, setConfirming] = useState(false);
  const [imgError, setImgError] = useState(false);

  const showImage = m.image_url && !imgError;

  return (
    <div
      onClick={onSelect}
      className={`relative z-10 bg-white dark:bg-slate-900 rounded-xl border shadow-sm overflow-hidden flex flex-col hover:shadow-md transition-all cursor-pointer ${
        isSelected
          ? "border-blue-500 ring-2 ring-blue-500 shadow-blue-500/20 shadow-lg"
          : "border-slate-100 dark:border-slate-800"
      }`}
    >
      {/* Poster */}
      <div className="relative bg-slate-900 shrink-0" style={{ aspectRatio: "2/3" }}>
        {showImage ? (
          <Image
            src={m.image_url!}
            alt={m.title}
            fill
            className="object-contain"
            onError={() => setImgError(true)}
            unoptimized
          />
        ) : (
          <div className={`w-full h-full bg-gradient-to-br ${posterGradient(m.genre)} flex flex-col items-center justify-center gap-2`}>
            <span className="text-white text-5xl font-black opacity-30 select-none">
              {m.title.charAt(0)}
            </span>
          </div>
        )}
        <span className="absolute top-3 right-3 text-xs font-medium bg-black/40 text-white backdrop-blur-sm px-2 py-1 rounded-full">
          {m.genre}
        </span>
      </div>

      {/* Info */}
      <div className="p-4 flex flex-col gap-2 flex-1">
        <h3 className="font-bold text-slate-900 dark:text-white leading-tight">{m.title}</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400">{m.director} · {m.year}</p>

        <div className="flex items-center gap-1">
          <span className="text-amber-400 text-sm">★</span>
          <span className="text-sm font-semibold text-slate-700 dark:text-slate-200">{m.rating}</span>
          <span className="text-slate-300 dark:text-slate-600 text-sm">/10</span>
        </div>

        <div className="mt-auto pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
          <div>
            <span className="font-bold text-slate-900 dark:text-white">{m.rental_price_per_day} ₽</span>
            <span className="text-slate-400 text-xs"> /день</span>
          </div>
          <span className={`text-xs font-medium px-2 py-1 rounded-full ${
            m.available_copies > 0
              ? "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400"
              : "bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400"
          }`}>
            {m.available_copies > 0 ? `${m.available_copies} шт.` : "Нет в наличии"}
          </span>
        </div>

        {isAdmin && (
          <div className="flex justify-end" onClick={e => e.stopPropagation()}>
            {confirming ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-500 dark:text-slate-400">Удалить?</span>
                <button onClick={() => onDelete(m.id)} className="text-xs font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">Да</button>
                <button onClick={() => setConfirming(false)} className="text-xs font-medium text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200">Нет</button>
              </div>
            ) : (
              <button onClick={() => setConfirming(true)} className="text-xs text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-colors">
                Удалить
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function plural(n: number) {
  if (n % 10 === 1 && n % 100 !== 11) return "";
  if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 >= 20)) return "а";
  return "ов";
}

const inp = "w-full border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-sm bg-white dark:bg-slate-800 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition";

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div>
      <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">{label}</label>
      {children}
    </div>
  );
}
