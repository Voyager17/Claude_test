"use client";

import { useState, useEffect, type ReactNode } from "react";

const API = "http://localhost:8001/api/v1";

interface Rental {
  id: number;
  customer_id: number;
  movie_id: number;
  rented_at: string;
  due_date: string;
  total_price: number;
  is_returned: boolean;
  returned_at: string | null;
}

interface Movie { id: number; title: string; available_copies: number; }
interface Customer { id: number; full_name: string; email: string; }

const emptyForm = { customer_id: "", movie_id: "", rental_days: 1 };

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("ru-RU", { day: "2-digit", month: "2-digit", year: "numeric" });
}

function isOverdue(due: string, returned: boolean) {
  return !returned && new Date(due) < new Date();
}

export default function RentalsPage() {
  const [rentals, setRentals] = useState<Rental[]>([]);
  const [movies, setMovies] = useState<Movie[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchAll() {
    const [r, m, c] = await Promise.all([
      fetch(`${API}/rentals/`).then(r => r.json()),
      fetch(`${API}/movies/`).then(r => r.json()),
      fetch(`${API}/customers/`).then(r => r.json()),
    ]);
    setRentals(r);
    setMovies(m);
    setCustomers(c);
    setLoading(false);
  }

  useEffect(() => { fetchAll(); }, []);

  const movieMap = Object.fromEntries(movies.map(m => [m.id, m.title]));
  const customerMap = Object.fromEntries(customers.map(c => [c.id, c.full_name]));

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await fetch(`${API}/rentals/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        customer_id: +form.customer_id,
        movie_id: +form.movie_id,
        rental_days: +form.rental_days,
      }),
    });
    if (res.ok) {
      setShowForm(false);
      setForm(emptyForm);
      fetchAll();
    } else {
      const data = await res.json();
      setError(data.detail ?? "Ошибка при создании аренды");
    }
  }

  async function handleReturn(id: number) {
    setError("");
    const res = await fetch(`${API}/rentals/${id}/return`, { method: "POST" });
    if (!res.ok) {
      const data = await res.json();
      setError(data.detail ?? "Ошибка при возврате");
    }
    fetchAll();
  }

  const active = rentals.filter(r => !r.is_returned).length;

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Аренды</h1>
          <div className="flex items-center gap-3 mt-1">
            {active > 0 && (
              <span className="text-xs font-medium bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 border border-orange-100 dark:border-orange-800 px-2 py-0.5 rounded-full">
                {active} активн{active === 1 ? "а" : "о"}
              </span>
            )}
            <span className="text-slate-400 dark:text-slate-500 text-sm">{rentals.length} всего</span>
          </div>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setError(""); }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            showForm
              ? "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-600"
              : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
          }`}
        >
          {showForm ? "Отмена" : "+ Новая аренда"}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-6 px-4 py-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Form */}
      {showForm && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl shadow-sm p-6 mb-8">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-5">Новая аренда</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-3 gap-4">
            <Field label="Клиент">
              <select required className={inp} value={form.customer_id} onChange={e => setForm({ ...form, customer_id: e.target.value })}>
                <option value="">Выберите клиента</option>
                {customers.map(c => (
                  <option key={c.id} value={c.id}>{c.full_name}</option>
                ))}
              </select>
            </Field>
            <Field label="Фильм">
              <select required className={inp} value={form.movie_id} onChange={e => setForm({ ...form, movie_id: e.target.value })}>
                <option value="">Выберите фильм</option>
                {movies.filter(m => m.available_copies > 0).map(m => (
                  <option key={m.id} value={m.id}>{m.title} ({m.available_copies} шт.)</option>
                ))}
              </select>
            </Field>
            <Field label="Дней аренды">
              <input required type="number" min="1" className={inp} value={form.rental_days} onChange={e => setForm({ ...form, rental_days: +e.target.value })} />
            </Field>
            <div className="col-span-3 flex justify-end pt-2">
              <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-medium transition-colors shadow-sm">
                Создать аренду
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Content */}
      {loading ? (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm divide-y divide-slate-100 dark:divide-slate-800">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4 animate-pulse">
              <div className="flex-1 grid grid-cols-4 gap-4">
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded" />
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded" />
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded" />
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      ) : rentals.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <p className="text-4xl mb-3">📋</p>
          <p className="font-medium">Аренд пока нет</p>
          <p className="text-sm mt-1">Создайте первую аренду</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Клиент</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Фильм</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Взят</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Вернуть до</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Цена</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Статус</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
              {rentals.map(r => (
                <tr key={r.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                  <td className="px-5 py-4 text-sm font-medium text-slate-800 dark:text-slate-200">
                    {customerMap[r.customer_id] ?? `#${r.customer_id}`}
                  </td>
                  <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-400">
                    {movieMap[r.movie_id] ?? `#${r.movie_id}`}
                  </td>
                  <td className="px-5 py-4 text-sm text-slate-500 dark:text-slate-500">{fmt(r.rented_at)}</td>
                  <td className="px-5 py-4 text-sm">
                    <span className={isOverdue(r.due_date, r.is_returned) ? "text-red-600 dark:text-red-400 font-medium" : "text-slate-500 dark:text-slate-400"}>
                      {fmt(r.due_date)}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-sm font-medium text-slate-700 dark:text-slate-300">{r.total_price} ₽</td>
                  <td className="px-5 py-4">
                    {r.is_returned ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800 px-2.5 py-1 rounded-full">
                        Возвращён
                      </span>
                    ) : isOverdue(r.due_date, r.is_returned) ? (
                      <span className="inline-flex items-center gap-1 text-xs font-medium bg-red-50 dark:bg-red-900/30 text-red-700 dark:text-red-400 border border-red-100 dark:border-red-800 px-2.5 py-1 rounded-full">
                        Просрочен
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-xs font-medium bg-orange-50 dark:bg-orange-900/20 text-orange-600 dark:text-orange-400 border border-orange-100 dark:border-orange-800 px-2.5 py-1 rounded-full">
                        Активна
                      </span>
                    )}
                  </td>
                  <td className="px-5 py-4 text-right">
                    {!r.is_returned && (
                      <button
                        onClick={() => handleReturn(r.id)}
                        className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 border border-blue-200 dark:border-blue-700 hover:border-blue-400 dark:hover:border-blue-500 px-3 py-1 rounded-lg transition-colors"
                      >
                        Вернуть
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
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
