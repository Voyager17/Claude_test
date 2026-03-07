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
        <div className="h-8 bg-slate-100 dark:bg-slate-800 rounded w-48" />
        <div className="flex gap-8">
          <div className="w-64 shrink-0 h-96 bg-slate-100 dark:bg-slate-800 rounded-xl" />
          <div className="flex-1 space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-5 bg-slate-100 dark:bg-slate-800 rounded w-3/4" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!movie) return null;

  const showImage = movie.image_url && !imgError;

  return (
    <div>
      {/* Back */}
      <button
        onClick={() => router.back()}
        className="inline-flex items-center gap-2 px-4 py-2 mb-6 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-700 hover:border-slate-300 dark:hover:border-slate-600 font-medium text-sm shadow-sm transition-all"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 12H5M12 5l-7 7 7 7"/>
        </svg>
        Назад
      </button>

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Poster */}
        <div className="w-full lg:w-64 shrink-0">
          <div className="relative rounded-xl overflow-hidden bg-slate-900" style={{ aspectRatio: "2/3" }}>
            {showImage ? (
              <Image
                src={movie.image_url!}
                alt={movie.title}
                fill
                className="object-contain"
                onError={() => setImgError(true)}
                unoptimized
              />
            ) : (
              <div className={`w-full h-full bg-gradient-to-br ${posterGradient(movie.genre)} flex items-center justify-center`}>
                <span className="text-white text-7xl font-black opacity-30 select-none">
                  {movie.title.charAt(0)}
                </span>
              </div>
            )}
            <span className="absolute top-3 right-3 text-xs font-medium bg-black/40 text-white backdrop-blur-sm px-2 py-1 rounded-full">
              {movie.genre}
            </span>
          </div>
        </div>

        {/* Info */}
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-1">{movie.title}</h1>
          <p className="text-slate-500 dark:text-slate-400 mb-4">{movie.director} · {movie.year}</p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <InfoCard label="Рейтинг">
              <span className="text-amber-400 mr-1">★</span>
              <span className="font-semibold text-slate-900 dark:text-white">{movie.rating}</span>
              <span className="text-slate-400 text-sm"> / 10</span>
            </InfoCard>

            <InfoCard label="Цена аренды">
              <span className="font-semibold text-slate-900 dark:text-white">{movie.rental_price_per_day} ₽</span>
              <span className="text-slate-400 text-sm"> / день</span>
            </InfoCard>

            <InfoCard label="Доступные копии">
              <span className={`font-semibold ${movie.available_copies > 0 ? "text-emerald-600 dark:text-emerald-400" : "text-red-600 dark:text-red-400"}`}>
                {movie.available_copies > 0 ? `${movie.available_copies} шт.` : "Нет в наличии"}
              </span>
            </InfoCard>

            <InfoCard label="Статус">
              <span className={`font-semibold ${movie.is_active ? "text-emerald-600 dark:text-emerald-400" : "text-slate-400"}`}>
                {movie.is_active ? "Активен" : "Снят с аренды"}
              </span>
            </InfoCard>

            <InfoCard label="Жанр">
              <span className="font-semibold text-slate-900 dark:text-white">{movie.genre}</span>
            </InfoCard>

            <InfoCard label="Год выпуска">
              <span className="font-semibold text-slate-900 dark:text-white">{movie.year}</span>
            </InfoCard>
          </div>

          {movie.description && (
            <div className="mt-4 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl px-4 py-3">
              <p className="text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">Описание</p>
              <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed">{movie.description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function InfoCard({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl px-4 py-3">
      <p className="text-xs font-medium text-slate-400 dark:text-slate-500 mb-1">{label}</p>
      <div className="text-base">{children}</div>
    </div>
  );
}
