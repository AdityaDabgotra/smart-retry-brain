"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL;

type Summary = {
  smart: { total_attempts: number; successful_recoveries: number; transactions_recovered: number; recovered_revenue: number };
  naive: { total_attempts: number; successful_recoveries: number; transactions_recovered: number; recovered_revenue: number };
  comparison: { revenue_uplift: number; additional_transactions_recovered: number; wasted_attempts_avoided: number };
};

type Txn = {
  id: string;
  external_txn_id: string;
  amount: number;
  payment_method: string;
  error_description: string;
  status: string;
  category: string | null;
  action: string | null;
  explanation: string | null;
  created_at: string;
};

const STATUS_COLOR: Record<string, string> = {
  RECOVERED: "text-mint",
  FAILED_PERMANENTLY: "text-coral",
  NEEDS_USER_ACTION: "text-amber",
  SCHEDULED: "text-ledger-muted",
  CLASSIFIED: "text-ledger-muted",
  PENDING: "text-ledger-muted",
};

const CATEGORY_COLOR: Record<string, string> = {
  INSUFFICIENT_FUNDS: "bg-amber",
  BANK_TIMEOUT: "bg-coral",
  NETWORK_ERROR: "bg-mint",
  OTP_MISMATCH: "bg-ledger-muted",
  CARD_EXPIRED: "bg-ledger-text",
  UNKNOWN: "bg-hairline",
};

function inr(n: number) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
}

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [txns, setTxns] = useState<Txn[]>([]);

  useEffect(() => {
    fetch(`${API}/analytics/summary`).then((r) => r.json()).then(setSummary);
    fetch(`${API}/transactions?limit=30`).then((r) => r.json()).then(setTxns);
  }, []);

  const categoryCounts = txns.reduce<Record<string, number>>((acc, t) => {
    if (t.category) acc[t.category] = (acc[t.category] ?? 0) + 1;
    return acc;
  }, {});
  const totalCategorized = Object.values(categoryCounts).reduce((a, b) => a + b, 0) || 1;

  return (
    <main className="min-h-screen px-8 py-10 max-w-6xl mx-auto">
      <header className="mb-10 flex items-baseline justify-between border-b border-hairline pb-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-ledger-muted mb-1">Recovery Ledger</p>
          <h1 className="text-2xl font-semibold">Smart Retry Brain</h1>
        </div>
        <p className="text-xs text-ledger-muted font-mono">live · qwen2.5 classification engine</p>
      </header>

      {/* Hero: revenue uplift */}
      {summary && (
        <section className="mb-12 grid grid-cols-3 gap-8 items-end">
          <div className="col-span-2">
            <p className="text-xs uppercase tracking-widest text-ledger-muted mb-2">Revenue recovered above naive baseline</p>
            <p className="font-mono text-6xl font-medium text-mint tabular-nums">
              {inr(summary.comparison.revenue_uplift)}
            </p>
            <p className="mt-2 text-sm text-ledger-muted">
              {summary.comparison.additional_transactions_recovered} more transactions recovered ·{" "}
              {summary.comparison.wasted_attempts_avoided} fewer wasted retry attempts
            </p>
          </div>
          <div className="space-y-4 border-l border-hairline pl-6">
            <div>
              <p className="text-xs text-ledger-muted mb-1">Smart</p>
              <p className="font-mono text-xl text-ledger-text tabular-nums">{inr(summary.smart.recovered_revenue)}</p>
              <p className="text-xs text-ledger-muted font-mono">
                {summary.smart.transactions_recovered} recovered · {summary.smart.total_attempts} attempts
              </p>
            </div>
            <div>
              <p className="text-xs text-ledger-muted mb-1">Naive (retry hourly, blind)</p>
              <p className="font-mono text-xl text-ledger-muted tabular-nums">{inr(summary.naive.recovered_revenue)}</p>
              <p className="text-xs text-ledger-muted font-mono">
                {summary.naive.transactions_recovered} recovered · {summary.naive.total_attempts} attempts
              </p>
            </div>
          </div>
        </section>
      )}

      {/* Signature: category flow bar */}
      <section className="mb-12">
        <p className="text-xs uppercase tracking-widest text-ledger-muted mb-3">Failure category breakdown</p>
        <div className="flex h-3 w-full overflow-hidden rounded-none border border-hairline">
          {Object.entries(categoryCounts).map(([cat, count]) => (
            <div
              key={cat}
              className={CATEGORY_COLOR[cat] ?? "bg-hairline"}
              style={{ width: `${(count / totalCategorized) * 100}%` }}
              title={`${cat}: ${count}`}
            />
          ))}
        </div>
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-ledger-muted font-mono">
          {Object.entries(categoryCounts).map(([cat, count]) => (
            <span key={cat} className="flex items-center gap-1.5">
              <span className={`inline-block h-2 w-2 ${CATEGORY_COLOR[cat] ?? "bg-hairline"}`} />
              {cat} · {count}
            </span>
          ))}
        </div>
      </section>

      {/* Ledger table */}
      <section>
        <p className="text-xs uppercase tracking-widest text-ledger-muted mb-3">Recent transactions</p>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-hairline text-left text-xs text-ledger-muted uppercase tracking-wide">
              <th className="pb-2 font-normal">Txn</th>
              <th className="pb-2 font-normal">Reason</th>
              <th className="pb-2 font-normal">Category</th>
              <th className="pb-2 font-normal">Status</th>
              <th className="pb-2 font-normal text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="font-mono">
            {txns.map((t) => (
              <tr key={t.id} className="border-b border-hairline/60">
                <td className="py-2.5 pr-4 text-ledger-muted">{t.external_txn_id}</td>
                <td className="py-2.5 pr-4 max-w-xs truncate font-sans text-ledger-text">
                  {t.explanation ?? t.error_description}
                </td>
                <td className="py-2.5 pr-4 text-xs">{t.category}</td>
                <td className={`py-2.5 pr-4 text-xs ${STATUS_COLOR[t.status] ?? ""}`}>{t.status}</td>
                <td className="py-2.5 text-right tabular-nums">{inr(t.amount)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}