import { useState } from 'react'
import { api } from '../services/api'

export default function CapacityPage() {
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const feed = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.capacity.feedKpis(30)
      setResult(r)
    } catch (err) {
      setError(String(err))
    } finally { setLoading(false) }
  }

  return (
    <div>
      <h2>Capacity KPIs</h2>
      <div className="actions">
        <button onClick={feed} disabled={loading}>Feed KPIs</button>
      </div>
      {error && <div className="error">{error}</div>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
