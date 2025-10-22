import { useState } from 'react'
import { api } from '../services/api'

export default function FinancialsPage() {
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const applyPenalties = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.financial.applyPenalties()
      setResult(r)
    } catch (err) { setError(String(err)) }
    finally { setLoading(false) }
  }

  const applyChargeback = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.financial.applyChargeback()
      setResult(r)
    } catch (err) { setError(String(err)) }
    finally { setLoading(false) }
  }

  return (
    <div>
      <h2>Financial Operations</h2>
      <div className="actions">
        <button onClick={applyPenalties} disabled={loading}>Apply Penalties</button>
        <button onClick={applyChargeback} disabled={loading}>Apply Chargeback</button>
      </div>
      {error && <div className="error">{error}</div>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
