import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { SLMMetrics } from '../types'
import ChartCard from '../components/ChartCard'

export default function SlmPage() {
  const [metrics, setMetrics] = useState<SLMMetrics | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [labels, setLabels] = useState<string[]>([])
  const [availability, setAvailability] = useState<number[]>([])
  const [burn, setBurn] = useState<number[]>([])

  const load = async () => {
    setLoading(true)
    try {
      const m = await api.slm.metrics(30)
      setMetrics(m)
      const t = await api.slm.trend(30)
      setLabels(t.series.map((s: any) => s.date.slice(5)))
      setAvailability(t.series.map((s: any) => s.availability_pct))
      setBurn(t.series.map((s: any) => s.burn_rate))
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const syncAvailability = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.slm.syncAvailability(30)
      await load()
    } catch (err) {
      setError(String(err))
    } finally { setLoading(false) }
  }

  const syncOutage = async () => {
    setLoading(true)
    setError(null)
    try {
      await api.slm.syncOutageAvailability(45)
      await load()
    } catch (err) {
      setError(String(err))
    } finally { setLoading(false) }
  }

  if (error) return <div className="error">{error}</div>
  if (!metrics) return <div className="loading">Loading SLM metrics…</div>

  return (
    <div>
      <h2>Service Level Management</h2>
      <div className="cards">
        <div className="card"><div className="label">Availability</div><div className="value">{metrics.availability_pct}%</div></div>
        <div className="card"><div className="label">MTTR</div><div className="value">{metrics.mttr_minutes ?? '—'} min</div></div>
        <div className="card"><div className="label">MTBF</div><div className="value">{metrics.mtbf_hours ?? '—'} h</div></div>
        <div className="card"><div className="label">Burn rate</div><div className="value">{metrics.error_budget?.burn_rate ?? '—'}</div></div>
      </div>

      <div className="cards">
        <ChartCard title="Availability trend" labels={labels} data={availability} />
        <ChartCard title="Burn rate" labels={labels} data={burn} color="#ff6b6b" />
      </div>

      <div className="actions">
        <button disabled={loading} onClick={syncAvailability}>Sync Availability</button>
        <button disabled={loading} onClick={syncOutage}>Sync Outage-Adjusted Availability</button>
      </div>
    </div>
  )
}
