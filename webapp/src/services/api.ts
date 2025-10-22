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

export const api = {
  health: () => request('/api/health'),
  dashboard: () => request('/api/dashboard'),
  slm: {
    metrics: (periodDays: number) => request(`/api/slm/metrics?period_days=${periodDays}`),
    syncAvailability: (lookbackDays: number) => request(`/api/slm/sync-availability?lookback_days=${lookbackDays}`, { method: 'POST' }),
    syncOutageAvailability: (lookbackDays: number) => request(`/api/slm/sync-outage-availability?lookback_days=${lookbackDays}`, { method: 'POST' }),
  },
  capacity: {
    feedKpis: (lookbackDays: number) => request(`/api/capacity/feed-kpis?lookback_days=${lookbackDays}`, { method: 'POST' }),
  },
  financial: {
    applyPenalties: () => request('/api/financial/apply-penalties', { method: 'POST' }),
    applyChargeback: () => request('/api/financial/apply-chargeback', { method: 'POST' }),
  },
  summary: {
    monthly: (month?: string) => request(`/api/summary/monthly${month ? `?month=${month}` : ''}`),
  },
  jobs: {
    run: () => request('/api/jobs/run', { method: 'POST' }),
  },
  storage: {
    clear: () => request('/api/storage/clear', { method: 'POST' }),
  },
}
