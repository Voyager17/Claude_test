"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
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
  description: string | null;
}

const genreGradients: Record<string, string> = {
  Drama:    "from-violet-600 to-purple-900",
  Action:   "from-orange-500 to-red-900",
  "Sci-Fi": "from-cyan-500 to-blue-900",
  Comedy:   "from-yellow-400 to-orange-700",
  Thriller: "from-slate-500 to-slate-900",
  Crime:    "from-rose-600 to-red-950",
  History:  "from-amber-500 to-yellow-900",
};

function posterGradient(genre: string) {
  return genreGradients[genre] ?? "from-slate-400 to-slate-800";
}

export default function MovieDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(true);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    fetch(`${API}/movies/${id}`)
      .then(r => r.ok ? r.json() : Promise.reject())
      .then(setMovie)
      .catch(() => router.replace("/movies"))
      .finally(() => setLoading(false));
  }, [id, router]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-10 bg-slate-100 dark:bg-slate-800 rounded w-32" />
        <div className="h-72 bg-slate-100 dark:bg-slate-800 rounded-2xl" />
        <div className="flex gap-8">
          <div className="w-48 shrink-0 h-72 bg-slate-100 dark:bg-slate-800 rounded-xl" />
          <div className="flex-1 space-y-3">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-5 bg-slate-100 dark:bg-slate-800 rounded w-3/4" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!movie) return null;

  const showImage = movie.image_url && !imgError;
  const ratingPercent = (movie.rating / 10) * 100;

  return (
    <div>
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="group relative z-10 inline-flex items-center gap-2 mb-6 text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white text-sm font-medium transition-colors"
      >
        <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm group-hover:-translate-x-0.5 transition-transform">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M19 12H5M12 5l-7 7 7 7"/>
          </svg>
        </span>
        Назад
      </button>

      {/* Hero banner */}
      <div className={`relative z-10 rounded-2xl overflow-hidden mb-8 bg-gradient-to-br ${posterGradient(movie.genre)}`} style={{ minHeight: "260px" }}>
        {/* Blurred bg image */}
        {showImage && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={movie.image_url!}
            alt=""
            className="absolute inset-0 w-full h-full object-cover"
            style={{ filter: "blur(10px) brightness(0.35)", transform: "scale(1.05)" }}
          />
        )}
        <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/40 to-transparent" />

        {/* Content */}
        <div className="relative z-10 flex items-end gap-6 p-8">
          {/* Mini poster */}
          <div className="hidden sm:block shrink-0 w-36 rounded-xl overflow-hidden shadow-2xl border border-white/10" style={{ aspectRatio: "2/3" }}>
            {showImage ? (
              <Image
                src={movie.image_url!}
                alt={movie.title}
                width={144}
                height={216}
                className="w-full h-full object-cover"
                onError={() => setImgError(true)}
                unoptimized
              />
            ) : (
              <div className={`w-full h-full bg-gradient-to-br ${posterGradient(movie.genre)} flex items-center justify-center`}>
                <span className="text-white text-5xl font-black opacity-40 select-none">{movie.title.charAt(0)}</span>
              </div>
            )}
          </div>

          {/* Title block */}
          <div className="flex-1 min-w-0">
            <div className="flex flex-wrap items-center gap-2 mb-3">
              <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-white/20 text-white backdrop-blur-sm border border-white/20">
                {movie.genre}
              </span>
              <span className={`text-xs font-semibold px-2.5 py-1 rounded-full backdrop-blur-sm border ${
                movie.available_copies > 0
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-400/30"
                  : "bg-red-500/20 text-red-300 border-red-400/30"
              }`}>
                {movie.available_copies > 0 ? `${movie.available_copies} копий доступно` : "Нет в наличии"}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-black text-white leading-tight mb-2 drop-shadow-lg">
              {movie.title}
            </h1>
            <p className="text-white/70 text-sm">
              {movie.director} · {movie.year}
            </p>
          </div>

          {/* Rating */}
          <div className="hidden md:flex shrink-0 flex-col items-center bg-black/30 backdrop-blur-sm border border-white/10 rounded-2xl px-5 py-4">
            <span className="text-amber-400 text-2xl mb-1">★</span>
            <span className="text-white text-3xl font-black leading-none">{movie.rating}</span>
            <span className="text-white/50 text-xs mt-1">из 10</span>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="relative z-10 grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left: stats */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">Характеристики</h2>

          {/* Rating bar */}
          <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Рейтинг</span>
              <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-1">
                <span className="text-amber-400">★</span> {movie.rating} / 10
              </span>
            </div>
            <div className="h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full transition-all"
                style={{ width: `${ratingPercent}%` }}
              />
            </div>
          </div>

          <StatRow icon="💰" label="Цена аренды" value={`${movie.rental_price_per_day} ₽ / день`} />
          <StatRow icon="🎬" label="Жанр" value={movie.genre} />
          <StatRow icon="📅" label="Год выпуска" value={String(movie.year)} />
          <StatRow
            icon="📦"
            label="Наличие"
            value={movie.available_copies > 0 ? `${movie.available_copies} шт.` : "Нет в наличии"}
            valueClass={movie.available_copies > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-500 dark:text-red-400"}
          />
          <StatRow
            icon="✅"
            label="Статус"
            value={movie.is_active ? "Активен" : "Снят с аренды"}
            valueClass={movie.is_active ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"}
          />
        </div>

        {/* Right: description */}
        <div className="lg:col-span-2 flex flex-col">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-3">О фильме</h2>
          <div className="flex-1 flex flex-col rounded-xl overflow-hidden border border-slate-100 dark:border-slate-800">
            <div className="bg-white dark:bg-slate-900 p-5">
              {movie.description ? (
                <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-sm">
                  {movie.description}
                </p>
              ) : (
                <p className="text-slate-400 text-sm">Описание не добавлено</p>
              )}
            </div>
            <div className={`flex-1 relative overflow-hidden flex items-end px-6 py-5 bg-gradient-to-br ${posterGradient(movie.genre)}`}>
              <div className="absolute inset-0 bg-black/40" />
              <span className="relative text-white/70 font-black text-5xl leading-none select-none truncate drop-shadow-lg">
                {movie.title}
              </span>
              <span className="relative ml-auto shrink-0 text-white/90 text-xs font-semibold">{movie.year}</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

function StatRow({ icon, label, value, valueClass }: {
  icon: string;
  label: string;
  value: string;
  valueClass?: string;
}) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-base">{icon}</span>
        <span className="text-sm text-slate-500 dark:text-slate-400">{label}</span>
      </div>
      <span className={`text-sm font-semibold ${valueClass ?? "text-slate-900 dark:text-white"}`}>{value}</span>
    </div>
  );
}
