"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { format, subDays } from "date-fns";
import { fetchHealth, fetchSales, fetchStores } from "@/lib/api";
import FiltersPanel from "@/components/FiltersPanel";
import SummaryCards from "@/components/SummaryCards";
import DashboardTable from "@/components/DashboardTable";

const formatDate = (date: Date) => format(date, "yyyy-MM-dd");

export default function HomePage() {
  const [startDate, setStartDate] = useState(() => formatDate(subDays(new Date(), 30)));
  const [endDate, setEndDate] = useState(() => formatDate(new Date()));
  const [selectedStores, setSelectedStores] = useState<number[]>([]);

  const healthQuery = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth
  });

  const storesQuery = useQuery({
    queryKey: ["stores"],
    queryFn: fetchStores
  });

  const salesQuery = useQuery({
    queryKey: ["sales", selectedStores, startDate, endDate],
    queryFn: async () => {
      const stores = selectedStores.length ? selectedStores : storesQuery.data?.map((s) => s.id) ?? [];
      if (stores.length === 0) {
        return { items: [], count: 0 };
      }
      return fetchSales(stores, startDate, endDate);
    },
    enabled: !!startDate && !!endDate
  });

  const isLoading = healthQuery.isLoading || storesQuery.isLoading || salesQuery.isLoading;
  const hasError = healthQuery.isError || storesQuery.isError || salesQuery.isError;

  return (
    <main className="p-4 sm:p-10">
      <section className="mx-auto flex w-full max-w-6xl flex-col gap-6">
        <header className="space-y-3">
          <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Firebird Sales Dashboard
          </h1>
          <p className="text-base text-slate-600">
            Mobile-first интерфейс для работы с Proxy API. Используйте фильтры для выбора магазинов и
            периода, затем анализируйте продажи и экспортируйте данные.
          </p>
        </header>

        <FiltersPanel
          stores={storesQuery.data ?? []}
          selectedStores={selectedStores}
          onStoresChange={setSelectedStores}
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
          isDisabled={storesQuery.isLoading}
        />

        <SummaryCards
          health={healthQuery.data}
          storesCount={storesQuery.data?.length ?? 0}
          sales={salesQuery.data}
          startDate={startDate}
          endDate={endDate}
          isLoading={isLoading}
        />

        <DashboardTable records={salesQuery.data?.items ?? []} isLoading={salesQuery.isLoading} />

        {hasError ? (
          <p className="text-sm text-red-600">
            Обнаружены ошибки загрузки данных. Проверьте соединение с backend и Proxy API.
          </p>
        ) : null}

        {isLoading ? <p className="text-sm text-slate-500">Загрузка данных...</p> : null}
      </section>
    </main>
  );
}

