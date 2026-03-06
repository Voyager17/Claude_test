"use client";

import { useState, useEffect, type ReactNode } from "react";
import { useRouter } from "next/navigation";

const API = "http://localhost:8001/api/v1";

interface Customer {
  id: number;
  full_name: string;
  email: string;
  phone: string | null;
  is_active: boolean;
}

const emptyForm = { full_name: "", email: "", phone: "" };

function initials(name: string) {
  return name.split(" ").map(w => w[0]).slice(0, 2).join("").toUpperCase();
}

export default function CustomersPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyForm);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (localStorage.getItem("role") !== "admin") {
      router.replace("/movies");
    }
  }, [router]);

  async function fetchCustomers() {
    const res = await fetch(`${API}/customers/`);
    setCustomers(await res.json());
    setLoading(false);
  }

  useEffect(() => { fetchCustomers(); }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    const res = await fetch(`${API}/customers/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...form, phone: form.phone || null }),
    });
    if (res.ok) {
      setShowForm(false);
      setForm(emptyForm);
      fetchCustomers();
    } else {
      const data = await res.json();
      setError(data.detail ?? "Ошибка при создании");
    }
  }

  async function handleDelete(id: number) {
    await fetch(`${API}/customers/${id}`, { method: "DELETE" });
    fetchCustomers();
  }

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Клиенты</h1>
          <p className="text-slate-500 dark:text-slate-400 text-sm mt-1">
            {customers.length > 0 ? `${customers.length} клиент${customerPlural(customers.length)}` : ""}
          </p>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setError(""); }}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            showForm
              ? "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 hover:bg-slate-300 dark:hover:bg-slate-600"
              : "bg-blue-600 text-white hover:bg-blue-700 shadow-sm"
          }`}
        >
          {showForm ? "Отмена" : "+ Добавить клиента"}
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
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-5">Новый клиент</h2>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
            <Field label="Полное имя">
              <input required className={inp} placeholder="Иван Иванов" value={form.full_name} onChange={e => setForm({ ...form, full_name: e.target.value })} />
            </Field>
            <Field label="Email">
              <input required type="email" className={inp} placeholder="ivan@example.com" value={form.email} onChange={e => setForm({ ...form, email: e.target.value })} />
            </Field>
            <Field label="Телефон (необязательно)">
              <input className={inp} placeholder="+7 999 000 00 00" value={form.phone} onChange={e => setForm({ ...form, phone: e.target.value })} />
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
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm divide-y divide-slate-100 dark:divide-slate-800">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="flex items-center gap-4 p-4 animate-pulse">
              <div className="w-10 h-10 bg-slate-100 dark:bg-slate-800 rounded-full shrink-0" />
              <div className="flex-1">
                <div className="h-4 bg-slate-100 dark:bg-slate-800 rounded w-1/3 mb-2" />
                <div className="h-3 bg-slate-100 dark:bg-slate-800 rounded w-1/4" />
              </div>
            </div>
          ))}
        </div>
      ) : customers.length === 0 ? (
        <div className="text-center py-20 text-slate-400">
          <p className="text-4xl mb-3">👤</p>
          <p className="font-medium">Клиентов пока нет</p>
          <p className="text-sm mt-1">Добавьте первого клиента</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-slate-900 rounded-xl border border-slate-100 dark:border-slate-800 shadow-sm overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/50">
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Клиент</th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wide">Телефон</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
              {customers.map(c => (
                <CustomerRow key={c.id} customer={c} onDelete={handleDelete} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function CustomerRow({ customer: c, onDelete }: { customer: Customer; onDelete: (id: number) => void }) {
  const [confirming, setConfirming] = useState(false);

  const colors = [
    "bg-violet-100 text-violet-700",
    "bg-blue-100 text-blue-700",
    "bg-emerald-100 text-emerald-700",
    "bg-amber-100 text-amber-700",
    "bg-rose-100 text-rose-700",
  ];
  const color = colors[c.id % colors.length];

  return (
    <tr className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
      <td className="px-5 py-4">
        <div className="flex items-center gap-3">
          <div className={`w-9 h-9 rounded-full flex items-center justify-center text-sm font-bold shrink-0 ${color}`}>
            {initials(c.full_name)}
          </div>
          <div>
            <p className="font-medium text-slate-900 dark:text-white text-sm">{c.full_name}</p>
            <p className="text-xs text-slate-400 dark:text-slate-500">{c.email}</p>
          </div>
        </div>
      </td>
      <td className="px-5 py-4 text-sm text-slate-600 dark:text-slate-400">{c.phone ?? <span className="text-slate-300 dark:text-slate-600">—</span>}</td>
      <td className="px-5 py-4 text-right">
        {confirming ? (
          <div className="flex items-center justify-end gap-3">
            <span className="text-xs text-slate-400 dark:text-slate-500">Удалить?</span>
            <button onClick={() => onDelete(c.id)} className="text-xs font-medium text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">Да</button>
            <button onClick={() => setConfirming(false)} className="text-xs font-medium text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300">Нет</button>
          </div>
        ) : (
          <button onClick={() => setConfirming(true)} className="text-xs text-slate-300 dark:text-slate-600 hover:text-red-500 dark:hover:text-red-400 transition-colors">
            Удалить
          </button>
        )}
      </td>
    </tr>
  );
}

function customerPlural(n: number) {
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
