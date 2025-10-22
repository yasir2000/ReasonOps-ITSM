import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Dashboard } from '../types'

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.dashboard()
      .then(setData)
      .catch((e) => setError(String(e)))
  }, [])

  if (error) return <div className="error">{error}</div>
  if (!data) return <div className="loading">Loading dashboard…</div>

  return (
    <div>
      <h2>Integrated Dashboard</h2>
      <div className="cards">
        <div className="card"><div className="label">Services</div><div className="value">{data.services}</div></div>
        <div className="card"><div className="label">Offerings</div><div className="value">{data.offerings}</div></div>
        <div className="card"><div className="label">Availability</div><div className="value">{data.service_level?.availability ?? '—'}%</div></div>
        <div className="card"><div className="label">Penalties</div><div className="value">{data.financials?.penalties ?? 0}</div></div>
      </div>

      <h3>Suppliers</h3>
      <pre>{JSON.stringify(data.suppliers, null, 2)}</pre>

      <h3>Security</h3>
      <pre>{JSON.stringify(data.security, null, 2)}</pre>
    </div>
  )
}
