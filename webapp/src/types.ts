export type Dashboard = {
  services: number
  offerings: number
  service_level: Record<string, any>
  security: Record<string, any>
  suppliers: Record<string, any>
  financials: Record<string, any>
  history: Record<string, any>
}

export type SLMMetrics = {
  period_days: number
  availability_pct: number
  error_budget: Record<string, any>
  mttr_minutes?: number
  mtbf_hours?: number
}
