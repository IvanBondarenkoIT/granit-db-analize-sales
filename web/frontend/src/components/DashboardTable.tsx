import { useMemo } from "react";
import type { SalesRecord } from "@/types";

interface DashboardTableProps {
  records: SalesRecord[];
  isLoading: boolean;
}

export default function DashboardTable({ records, isLoading }: DashboardTableProps) {
  const sortedRecords = useMemo(() => {
    return [...records].sort((a, b) => a.store_name.localeCompare(b.store_name));
  }, [records]);

  if (isLoading) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Таблица загружается...</p>
      </section>
    );
  }

  if (sortedRecords.length === 0) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm text-slate-500">Нет данных для отображения</p>
      </section>
    );
  }

  return (
    <section className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm">
      <div className="max-h-[480px] overflow-y-auto">
        <table className="min-w-full divide-y divide-slate-200 text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th scope="col" className="px-4 py-3 text-left">
                Магазин
              </th>
              <th scope="col" className="px-4 py-3 text-left">
                Дата
              </th>
              <th scope="col" className="px-4 py-3 text-right">
                Чашки
              </th>
              <th scope="col" className="px-4 py-3 text-right">
                Пачки (кг)
              </th>
              <th scope="col" className="px-4 py-3 text-right">
                Сумма (₾)
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {sortedRecords.map((record, index) => (
              <tr key={`${record.store_name}-${record.order_date}-${index}`} className="hover:bg-slate-50">
                <td className="px-4 py-3 text-slate-900">{record.store_name}</td>
                <td className="px-4 py-3 text-slate-600">
                  {new Date(record.order_date).toLocaleDateString("ru-RU")}
                </td>
                <td className="px-4 py-3 text-right text-slate-900">
                  {record.allcup.toLocaleString("ru-RU", { maximumFractionDigits: 0 })}
                </td>
                <td className="px-4 py-3 text-right text-slate-900">
                  {record.packages_kg.toLocaleString("ru-RU", { maximumFractionDigits: 2 })}
                </td>
                <td className="px-4 py-3 text-right text-emerald-600">
                  {record.total_cash.toLocaleString("ru-RU", { maximumFractionDigits: 2 })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
