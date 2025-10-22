import { useEffect, useState } from 'react'
import { api } from '../services/api'
import type { Dashboard } from '../types'
import { CardGridSkeleton } from '../components/LoadingSkeleton'

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      const result = await api.dashboard()
      setData(result)
      setLastUpdated(new Date())
      setError(null)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboard, 30000)
    return () => clearInterval(interval)
  }, [])

  if (error) {
    return (
      <div className="error">
        <strong>❌ Error loading dashboard</strong>
        <p>{error}</p>
        <button onClick={fetchDashboard} style={{ marginTop: '12px' }}>
          Retry
        </button>
      </div>
    )
  }

  if (loading && !data) {
    return (
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2>Integrated Dashboard</h2>
          </div>
        </div>
        <CardGridSkeleton count={4} />
      </div>
    )
  }

  if (!data) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 style={{ marginBottom: '4px' }}>Integrated Dashboard</h2>
          {lastUpdated && (
            <p style={{ fontSize: '14px', color: 'var(--text-muted)', margin: 0 }}>
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
        <button onClick={fetchDashboard} disabled={loading}>
          {loading ? '⟳ Refreshing...' : '↻ Refresh'}
        </button>
      </div>

      {/* Key Metrics */}
      <div className="cards">
        <div className="card">
          <div className="label">Services</div>
          <div className="value">{data.services}</div>
          <div className="trend up">↑ Active services</div>
        </div>
        <div className="card">
          <div className="label">Offerings</div>
          <div className="value">{data.offerings}</div>
          <div className="trend">Service catalog items</div>
        </div>
        <div className="card">
          <div className="label">Availability</div>
          <div className="value">
            {data.service_level?.availability ?? '—'}
            {data.service_level?.availability && '%'}
          </div>
          <div className={`trend ${(data.service_level?.availability ?? 0) >= 99 ? 'up' : 'down'}`}>
            {(data.service_level?.availability ?? 0) >= 99 ? '↑ Above target' : '↓ Below target'}
          </div>
        </div>
        <div className="card">
          <div className="label">Penalties</div>
          <div className="value">{data.financials?.penalties ?? 0}</div>
          <div className="trend">
            {(data.financials?.penalties ?? 0) === 0 ? '✓ No penalties' : '⚠ Action required'}
          </div>
        </div>
      </div>

      {/* Service Level Details */}
      {data.service_level && (
        <div style={{ marginTop: 'var(--spacing-2xl)' }}>
          <h3>Service Level Metrics</h3>
          <div className="cards">
            <div className="card">
              <div className="label">Incidents</div>
              <div className="value">{data.service_level.incidents ?? 0}</div>
            </div>
            <div className="card">
              <div className="label">Response Time</div>
              <div className="value">{data.service_level.response_time ?? '—'}</div>
            </div>
            <div className="card">
              <div className="label">MTTR</div>
              <div className="value">{data.service_level.mttr ?? '—'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Suppliers */}
      {data.suppliers && data.suppliers.length > 0 && (
        <div style={{ marginTop: 'var(--spacing-2xl)' }}>
          <h3>Suppliers</h3>
          <div className="card">
            <table>
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Status</th>
                  <th>Services</th>
                </tr>
              </thead>
              <tbody>
                {data.suppliers.map((supplier: any, idx: number) => (
                  <tr key={idx}>
                    <td>{supplier.name || 'Unknown'}</td>
                    <td>
                      <span className={`badge ${supplier.status === 'active' ? 'success' : 'error'}`}>
                        {supplier.status || 'unknown'}
                      </span>
                    </td>
                    <td>{supplier.services || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Security */}
      {data.security && (
        <div style={{ marginTop: 'var(--spacing-2xl)' }}>
          <h3>Security Status</h3>
          <div className="cards">
            <div className="card">
              <div className="label">Vulnerabilities</div>
              <div className="value">{data.security.vulnerabilities ?? 0}</div>
              <div className={`trend ${(data.security.vulnerabilities ?? 0) === 0 ? 'up' : 'down'}`}>
                {(data.security.vulnerabilities ?? 0) === 0 ? '✓ All clear' : '⚠ Needs attention'}
              </div>
            </div>
            <div className="card">
              <div className="label">Compliance Score</div>
              <div className="value">{data.security.compliance_score ?? '—'}%</div>
            </div>
            <div className="card">
              <div className="label">Last Audit</div>
              <div className="value" style={{ fontSize: '16px' }}>
                {data.security.last_audit || '—'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Financials Summary */}
      {data.financials && (
        <div style={{ marginTop: 'var(--spacing-2xl)' }}>
          <h3>Financial Summary</h3>
          <div className="cards">
            <div className="card">
              <div className="label">Total Cost</div>
              <div className="value">
                ${(data.financials.total_cost ?? 0).toLocaleString()}
              </div>
            </div>
            <div className="card">
              <div className="label">Revenue</div>
              <div className="value">
                ${(data.financials.revenue ?? 0).toLocaleString()}
              </div>
            </div>
            <div className="card">
              <div className="label">Profit Margin</div>
              <div className="value">
                {data.financials.profit_margin ?? 0}%
              </div>
              <div className={`trend ${(data.financials.profit_margin ?? 0) > 0 ? 'up' : 'down'}`}>
                {(data.financials.profit_margin ?? 0) > 0 ? '↑ Profitable' : '↓ Loss'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Raw Data (Collapsible) */}
      <details style={{ marginTop: 'var(--spacing-2xl)' }}>
        <summary style={{ cursor: 'pointer', padding: 'var(--spacing-md)', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)' }}>
          <strong>View Raw Data</strong>
        </summary>
        <pre style={{ marginTop: 'var(--spacing-md)' }}>
          {JSON.stringify(data, null, 2)}
        </pre>
      </details>
    </div>
  )
}
