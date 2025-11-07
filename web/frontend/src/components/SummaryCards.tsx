import type { SalesResponse } from "@/types";

interface SummaryCardsProps {
  health?: any;
  storesCount: number;
  sales?: SalesResponse;
  startDate: string;
  endDate: string;
  isLoading: boolean;
}

const formatNumber = (value: number, fractionDigits = 0) =>
  value.toLocaleString("ru-RU", { maximumFractionDigits: fractionDigits });

export default function SummaryCards({
  health,
  storesCount,
  sales,
  startDate,
  endDate,
  isLoading
}: SummaryCardsProps) {
  const totalSales = sales?.items.reduce((acc, item) => acc + item.total_cash, 0) ?? 0;
  const totalCups = sales?.items.reduce((acc, item) => acc + item.allcup, 0) ?? 0;

  return (
    <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-slate-500">Состояние API</p>
        {isLoading ? (
          <p className="mt-3 text-lg text-slate-600">Загрузка...</p>
        ) : health ? (
          <div className="mt-3 space-y-1 text-sm text-slate-600">
            <p>
              Статус: <span className="font-semibold text-emerald-600">{health.status}</span>
            </p>
            <p>Среда: {health.environment}</p>
            <p>БД доступна: {health.proxy_api?.database_connected ? "да" : "нет"}</p>
          </div>
        ) : (
          <p className="mt-3 text-sm text-red-600">Нет данных</p>
        )}
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-slate-500">Магазины</p>
        <p className="mt-3 text-3xl font-semibold text-slate-900">
          {isLoading ? "…" : formatNumber(storesCount)}
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-slate-500">Сумма продаж (₾)</p>
        <p className="mt-3 text-3xl font-semibold text-slate-900">
          {isLoading ? "…" : formatNumber(totalSales, 2)}
        </p>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-medium text-slate-500">Всего чашек</p>
        <p className="mt-3 text-3xl font-semibold text-slate-900">
          {isLoading ? "…" : formatNumber(totalCups)}
        </p>
        <p className="mt-3 text-xs text-slate-400">
          Период: {startDate} — {endDate}
        </p>
      </div>
    </section>
  );
}
