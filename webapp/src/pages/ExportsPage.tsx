import { useEffect, useState } from 'react'
import { api } from '../services/api'

export default function ExportsPage() {
  const [json, setJson] = useState<string>('')
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    try {
      const res = await api.summary.monthly()
      setJson(JSON.stringify(res, null, 2))
    } catch (err) { setError(String(err)) }
  }

  useEffect(() => { load() }, [])

  const onDownload = () => {
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'monthly_summary.json'
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div>
      <h2>Exports</h2>
      <div className="actions">
        <button onClick={load}>Refresh Monthly Summary</button>
        <button onClick={onDownload} disabled={!json}>Download</button>
      </div>
      {error && <div className="error">{error}</div>}
      <pre>{json}</pre>
    </div>
  )
}
