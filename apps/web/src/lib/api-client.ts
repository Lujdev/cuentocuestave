const API_BASE = import.meta.env.PUBLIC_API_URL ?? "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export const api = {
  products: {
    list: (params?: { category?: string; search?: string; page?: number }) =>
      apiFetch<{ items: ProductListItem[]; total: number }>("/api/products?" + new URLSearchParams(params as Record<string, string>)),
    get: (slug: string) => apiFetch<ProductDetail>(`/api/products/${slug}`),
    history: (slug: string, days = 90) => apiFetch<PriceHistory>(`/api/products/${slug}/history?days=${days}`),
    forecast: (slug: string, horizon = 14) => apiFetch<Forecast>(`/api/products/${slug}/forecast?horizon=${horizon}`),
  },
  basket: {
    index: () => apiFetch<BasketIndex>("/api/basket/index"),
  },
  exchangeRates: {
    latest: () => apiFetch<ExchangeRates>("/api/exchange-rates/latest"),
  },
  analytics: {
    clusters: () => apiFetch<Clusters>("/api/analytics/clusters"),
  },
};

// Types — expanded in Fase 3
export type ProductListItem = { slug: string; display_name: string; brand?: string; category: string; cheapest_price_usd?: number; cheapest_supermarket?: string };
export type ProductDetail = { slug: string; display_name: string; latest_prices: LatestPrice[] };
export type LatestPrice = { supermarket: { slug: string; display_name: string }; price_usd: number; available: boolean; observed_at: string };
export type PriceHistory = { slug: string; days: number; prices: { date: string; price_usd: number; supermarket_slug: string }[] };
export type Forecast = { slug: string; horizon: number; forecast: { date: string; yhat: number; yhat_lower: number; yhat_upper: number }[] };
export type BasketIndex = { basket_usd: number; min_wage_usd: number; ratio: number; history: { date: string; ratio: number }[] };
export type ExchangeRates = { bcv: number; paralelo: number };
export type Clusters = { clusters: { id: number; products: string[] }[] };
