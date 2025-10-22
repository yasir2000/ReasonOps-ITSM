import { useState, useEffect } from 'react'
import { useToast } from '../components/Toast'

interface Decision {
  agent_name: string
  event_type: string
  decision: string
  timestamp: string
  confidence?: number
}

interface ProviderHealth {
  status: string
  latency_ms?: number
  error_count: number
  consecutive_failures: number
  message: string
  last_check_ago: number
}

export default function AgentsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [health, setHealth] = useState<Record<string, ProviderHealth>>({})
  const [providers, setProviders] = useState<any>(null)
  const [selectedProvider, setSelectedProvider] = useState('ollama')
  const [selectedModel, setSelectedModel] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [temperature, setTemperature] = useState(0.7)
  const [eventType, setEventType] = useState('incident')
  const [eventData, setEventData] = useState('{"severity": "high", "description": "Test incident"}')
  const [loading, setLoading] = useState(false)
  const [filterEventType, setFilterEventType] = useState('')
  const [filterAgent, setFilterAgent] = useState('')
  const toast = useToast()

  useEffect(() => {
    loadDecisions()
    loadProviders()
    checkHealth()
  }, [])

  const loadDecisions = async () => {
    try {
      const response = await fetch('/api/agents/decisions?limit=100')
      const data = await response.json()
      setDecisions(data.decisions || [])
    } catch (err) {
      console.error('Failed to load decisions:', err)
    }
  }

  const loadProviders = async () => {
    try {
      const response = await fetch('/api/agents/providers')
      const data = await response.json()
      setProviders(data)
    } catch (err) {
      console.error('Failed to load providers:', err)
    }
  }

  const checkHealth = async () => {
    try {
      const response = await fetch('/api/agents/health')
      const data = await response.json()
      setHealth(data.providers || {})
    } catch (err) {
      console.error('Failed to check health:', err)
    }
  }

  const configureLLM = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/agents/configure-llm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: selectedProvider,
          model: selectedModel || undefined,
          api_key: apiKey || undefined,
          temperature
        })
      })
      const data = await response.json()
      toast.push(`✓ LLM configured: ${data.config?.provider}`, 'success')
      await checkHealth()
    } catch (err) {
      toast.push(`Failed to configure LLM: ${err}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const runAgent = async () => {
    setLoading(true)
    try {
      const parsedData = JSON.parse(eventData)
      const response = await fetch('/api/agents/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          event_type: eventType,
          event_data: parsedData
        })
      })
      const data = await response.json()
      toast.push(`✓ Agent executed: ${data.decisions?.length || 0} decisions`, 'success')
      await loadDecisions()
    } catch (err) {
      toast.push(`Failed to run agent: ${err}`, 'error')
    } finally {
      setLoading(false)
    }
  }

  const filteredDecisions = decisions.filter(d => {
    if (filterEventType && d.event_type !== filterEventType) return false
    if (filterAgent && d.agent_name !== filterAgent) return false
    return true
  })

  const getHealthIcon = (status: string) => {
    if (status === 'healthy') return '✓'
    if (status === 'degraded') return '⚠'
    return '✗'
  }

  const getHealthColor = (status: string) => {
    if (status === 'healthy') return '#4caf50'
    if (status === 'degraded') return '#ff9800'
    return '#f44336'
  }

  return (
    <div style={{ padding: '20px' }}>
      <h2>AI Agent Management</h2>

      {/* LLM Provider Configuration */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>LLM Provider Configuration</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Provider</label>
            <select 
              value={selectedProvider} 
              onChange={(e) => setSelectedProvider(e.target.value)}
              style={{ width: '100%', padding: '8px' }}
            >
              {providers?.providers?.map((p: string) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Model</label>
            <select 
              value={selectedModel} 
              onChange={(e) => setSelectedModel(e.target.value)}
              style={{ width: '100%', padding: '8px' }}
            >
              <option value="">Default</option>
              {providers?.models?.[selectedProvider]?.map((m: string) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>API Key (optional)</label>
            <input 
              type="password" 
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Leave empty for local providers"
              style={{ width: '100%', padding: '8px' }}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Temperature</label>
            <input 
              type="number" 
              min="0" 
              max="1" 
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              style={{ width: '100%', padding: '8px' }}
            />
          </div>
        </div>
        <div className="actions">
          <button onClick={configureLLM} disabled={loading}>
            {loading ? 'Configuring...' : 'Configure LLM Provider'}
          </button>
          <button onClick={checkHealth} disabled={loading}>
            Refresh Health
          </button>
        </div>
      </div>

      {/* Provider Health Status */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Provider Health Status</h3>
        {Object.keys(health).length === 0 ? (
          <p style={{ color: '#888' }}>No health data available. Click "Refresh Health" to check.</p>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '15px' }}>
            {Object.entries(health).map(([provider, h]) => (
              <div 
                key={provider} 
                style={{ 
                  border: `2px solid ${getHealthColor(h.status)}`,
                  borderRadius: '8px',
                  padding: '15px'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
                  <span style={{ fontSize: '24px', marginRight: '10px' }}>{getHealthIcon(h.status)}</span>
                  <div>
                    <strong>{provider}</strong>
                    <div style={{ fontSize: '12px', color: '#888' }}>{h.status}</div>
                  </div>
                </div>
                {h.latency_ms && (
                  <div style={{ fontSize: '14px' }}>Latency: {h.latency_ms.toFixed(0)}ms</div>
                )}
                {h.error_count > 0 && (
                  <div style={{ fontSize: '14px', color: '#f44336' }}>Errors: {h.error_count}</div>
                )}
                {h.message && h.status !== 'healthy' && (
                  <div style={{ fontSize: '12px', color: '#888', marginTop: '5px' }}>{h.message}</div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Execute Agent */}
      <div className="card" style={{ marginBottom: '20px' }}>
        <h3>Execute Agent Orchestration</h3>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '15px', marginBottom: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Event Type</label>
            <select 
              value={eventType} 
              onChange={(e) => setEventType(e.target.value)}
              style={{ width: '100%', padding: '8px' }}
            >
              <option value="incident">Incident</option>
              <option value="capacity_alert">Capacity Alert</option>
              <option value="outage">Outage</option>
              <option value="security_threat">Security Threat</option>
              <option value="performance_degradation">Performance Degradation</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>Event Data (JSON)</label>
            <textarea 
              value={eventData}
              onChange={(e) => setEventData(e.target.value)}
              rows={3}
              style={{ width: '100%', padding: '8px', fontFamily: 'monospace' }}
              placeholder='{"severity": "high", "description": "..."}'
            />
          </div>
        </div>
        <div className="actions">
          <button onClick={runAgent} disabled={loading}>
            {loading ? 'Running...' : 'Execute Agent'}
          </button>
        </div>
      </div>

      {/* Decision History */}
      <div className="card">
        <h3>Agent Decision History ({filteredDecisions.length})</h3>
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>Filter by Event Type</label>
            <select 
              value={filterEventType} 
              onChange={(e) => setFilterEventType(e.target.value)}
              style={{ padding: '6px' }}
            >
              <option value="">All</option>
              <option value="incident">Incident</option>
              <option value="capacity_alert">Capacity Alert</option>
              <option value="outage">Outage</option>
              <option value="security_threat">Security Threat</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '12px' }}>Filter by Agent</label>
            <input 
              type="text"
              value={filterAgent}
              onChange={(e) => setFilterAgent(e.target.value)}
              placeholder="Agent name"
              style={{ padding: '6px' }}
            />
          </div>
          <button onClick={loadDecisions} style={{ alignSelf: 'flex-end' }}>Refresh</button>
        </div>
        {filteredDecisions.length === 0 ? (
          <p style={{ color: '#888' }}>No decisions yet. Execute an agent to see results.</p>
        ) : (
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ position: 'sticky', top: 0, background: '#1e1e1e' }}>
                <tr style={{ borderBottom: '2px solid #333' }}>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Timestamp</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Agent</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Event Type</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Decision</th>
                  <th style={{ padding: '10px', textAlign: 'left' }}>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {filteredDecisions.map((d, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #333' }}>
                    <td style={{ padding: '10px', fontSize: '12px', color: '#888' }}>
                      {new Date(d.timestamp).toLocaleString()}
                    </td>
                    <td style={{ padding: '10px' }}>
                      <span style={{ 
                        background: '#2196f3', 
                        padding: '3px 8px', 
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}>
                        {d.agent_name}
                      </span>
                    </td>
                    <td style={{ padding: '10px' }}>{d.event_type}</td>
                    <td style={{ padding: '10px', fontSize: '14px' }}>
                      {d.decision.length > 100 ? d.decision.substring(0, 100) + '...' : d.decision}
                    </td>
                    <td style={{ padding: '10px' }}>
                      {d.confidence ? `${(d.confidence * 100).toFixed(0)}%` : 'N/A'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
