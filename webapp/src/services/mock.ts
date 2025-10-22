// Lightweight mock data used by the UI if the backend is unavailable.
export const mock = {
  dashboard: () => ({
    services: 3,
    offerings: 5,
    service_level: { availability: 99.95 },
    security: { incidents: 0 },
    suppliers: { count: 2 },
    financials: { penalties: 0, chargebacks: 0 },
    history: {},
  }),
  slm: {
    metrics: (periodDays: number) => ({
      period_days: periodDays,
      availability_pct: 99.95,
      error_budget: { target: 0.05, consumed: 0.0, burn_rate: 0.0 },
      mttr_minutes: 10,
      mtbf_hours: 240,
    }),
    syncAvailability: (lookbackDays: number) => ({ synced: true, lookback_days: lookbackDays }),
    syncOutageAvailability: (lookbackDays: number) => ({ synced: true, lookback_days: lookbackDays }),
  },
  capacity: {
    feedKpis: (lookbackDays: number) => ({ fed: true, lookback_days: lookbackDays }),
  },
  financial: {
    applyPenalties: () => ({ applied: true, total: 0 }),
    applyChargeback: () => ({ applied: true, total: 0 }),
  },
  summary: {
    monthly: (month?: string) => ({
      month: month || '2025-10',
      penalties: {},
      chargebacks: {},
      agent_decisions: {},
    }),
  },
  jobs: {
    run: () => ({ ran: true }),
  },
  storage: {
    clear: () => ({ cleared: true }),
  },
}
