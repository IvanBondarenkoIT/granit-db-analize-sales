export type Store = {
  id: number;
  name: string;
};

export type SalesRecord = {
  store_name: string;
  order_date: string;
  allcup: number;
  packages_kg: number;
  total_cash: number;
};

export type SalesResponse = {
  items: SalesRecord[];
  count: number;
};

