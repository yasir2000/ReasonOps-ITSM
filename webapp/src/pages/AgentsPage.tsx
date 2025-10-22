import { useState } from 'react'
import { api } from '../services/api'

export default function AgentsPage() {
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const runJobs = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await api.jobs.run()
      setResult(r)
    } catch (err) { setError(String(err)) }
    finally { setLoading(false) }
  }

  return (
    <div>
      <h2>Agents & Periodic Jobs</h2>
      <div className="actions">
        <button onClick={runJobs} disabled={loading}>Run Periodic Jobs</button>
      </div>
      {error && <div className="error">{error}</div>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
