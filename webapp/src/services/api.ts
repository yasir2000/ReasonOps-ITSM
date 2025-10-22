import { mock } from './mock'

const BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || ''

async function request(path: string, init?: RequestInit) {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`Request failed ${res.status}: ${text}`)
  }
  return res.json()
}

async function withFallback<T>(fn: () => Promise<T>, fallback: () => T): Promise<T> {
  try {
    return await fn()
  } catch {
    return fallback()
  }
}

export const api = {
  health: () => withFallback(() => request('/api/health'), () => ({ status: 'ok-mock' } as any)),
  dashboard: () => withFallback(() => request('/api/dashboard'), mock.dashboard),
  slm: {
    metrics: (periodDays: number) => withFallback(
      () => request(`/api/slm/metrics?period_days=${periodDays}`),
      () => mock.slm.metrics(periodDays)
    ),
    syncAvailability: (lookbackDays: number) => withFallback(
      () => request(`/api/slm/sync-availability?lookback_days=${lookbackDays}`, { method: 'POST' }),
      () => mock.slm.syncAvailability(lookbackDays)
    ),
    syncOutageAvailability: (lookbackDays: number) => withFallback(
      () => request(`/api/slm/sync-outage-availability?lookback_days=${lookbackDays}`, { method: 'POST' }),
      () => mock.slm.syncOutageAvailability(lookbackDays)
    ),
    trend: (days: number) => withFallback(
      () => request(`/api/slm/metrics/trend?days=${days}`),
      () => ({ days, series: Array.from({ length: days }).map((_, i) => ({
        date: new Date(Date.now() - (days - 1 - i) * 86400000).toISOString().slice(0,10),
        availability_pct: 99.8 + (i % 5) * 0.05,
        burn_rate: Math.max(0, 0.02 - (i % 7) * 0.002)
      })) })
    ),
  },
  capacity: {
    feedKpis: (lookbackDays: number) => withFallback(
      () => request(`/api/capacity/feed-kpis?lookback_days=${lookbackDays}`, { method: 'POST' }),
      () => mock.capacity.feedKpis(lookbackDays)
    ),
  },
  financial: {
    applyPenalties: () => withFallback(
      () => request('/api/financial/apply-penalties', { method: 'POST' }),
      mock.financial.applyPenalties
    ),
    applyChargeback: () => withFallback(
      () => request('/api/financial/apply-chargeback', { method: 'POST' }),
      mock.financial.applyChargeback
    ),
  },
  summary: {
    monthly: (month?: string) => withFallback(
      () => request(`/api/summary/monthly${month ? `?month=${month}` : ''}`),
      () => mock.summary.monthly(month)
    ),
  },
  jobs: {
    run: () => withFallback(
      () => request('/api/jobs/run', { method: 'POST' }),
      mock.jobs.run
    ),
  },
  storage: {
    clear: () => withFallback(
      () => request('/api/storage/clear', { method: 'POST' }),
      mock.storage.clear
    ),
  },
}
