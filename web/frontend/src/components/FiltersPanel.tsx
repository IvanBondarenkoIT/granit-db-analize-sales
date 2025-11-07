import { ChangeEvent } from "react";
import type { Store } from "@/types";

const formatDateInput = (value: string) => value;

type FiltersPanelProps = {
  stores: Store[];
  selectedStores: number[];
  onStoresChange: (ids: number[]) => void;
  startDate: string;
  endDate: string;
  onStartDateChange: (value: string) => void;
  onEndDateChange: (value: string) => void;
  isDisabled?: boolean;
};

export default function FiltersPanel({
  stores,
  selectedStores,
  onStoresChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  isDisabled
}: FiltersPanelProps) {
  const handleStoreToggle = (storeId: number) => {
    if (selectedStores.includes(storeId)) {
      onStoresChange(selectedStores.filter((id) => id !== storeId));
    } else {
      onStoresChange([...selectedStores, storeId]);
    }
  };

  const handleStartDate = (event: ChangeEvent<HTMLInputElement>) => {
    onStartDateChange(event.target.value);
  };

  const handleEndDate = (event: ChangeEvent<HTMLInputElement>) => {
    onEndDateChange(event.target.value);
  };

  return (
    <section className="grid gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm sm:grid-cols-2">
      <div>
        <label className="block text-sm font-medium text-slate-600">Период</label>
        <div className="mt-2 grid grid-cols-1 gap-2 sm:grid-cols-2">
          <input
            type="date"
            value={formatDateInput(startDate)}
            onChange={handleStartDate}
            disabled={isDisabled}
            className="rounded-md border-slate-300 text-sm shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
          />
          <input
            type="date"
            value={formatDateInput(endDate)}
            onChange={handleEndDate}
            disabled={isDisabled}
            className="rounded-md border-slate-300 text-sm shadow-sm focus:border-emerald-500 focus:ring-emerald-500"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-slate-600">Магазины</label>
        <div className="mt-2 flex max-h-40 flex-wrap gap-2 overflow-y-auto">
          {stores.length === 0 ? (
            <p className="text-sm text-slate-500">Магазины не загружены</p>
          ) : (
            stores.map((store) => {
              const active = selectedStores.length === 0 || selectedStores.includes(store.id);
              return (
                <button
                  key={store.id}
                  type="button"
                  onClick={() => handleStoreToggle(store.id)}
                  className={`rounded-full border px-3 py-1 text-sm transition focus:outline-none focus:ring-2 focus:ring-emerald-500 ${
                    active ? "border-emerald-500 bg-emerald-50 text-emerald-700" : "border-slate-200 bg-white text-slate-600"
                  }`}
                >
                  {store.name}
                </button>
              );
            })
          )}
        </div>
        <p className="mt-2 text-xs text-slate-500">
          Если не выбрано ни одного магазина, будут использованы все доступные.
        </p>
      </div>
    </section>
  );
}
