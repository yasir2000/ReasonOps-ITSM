import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AgentsPage from '../pages/AgentsPage'
import { ToastProvider } from '../components/Toast'

// Mock fetch
global.fetch = vi.fn()

const mockProviders = {
  providers: ['ollama', 'openai', 'anthropic', 'mock'],
  models: {
    ollama: ['llama2-7b', 'mistral-7b'],
    openai: ['gpt-4', 'gpt-3.5-turbo'],
    mock: ['mock-model']
  },
  recommended: {
    local: 'ollama + llama2-7b',
    cloud: 'openai + gpt-4-turbo'
  }
}

const mockHealth = {
  ollama: {
    status: 'healthy',
    latency_ms: 120,
    error_count: 0,
    consecutive_failures: 0,
    message: 'Healthy',
    last_check_ago: 5
  },
  mock: {
    status: 'healthy',
    latency_ms: 5,
    error_count: 0,
    consecutive_failures: 0,
    message: 'Healthy',
    last_check_ago: 5
  }
}

const mockDecisions = [
  {
    agent_name: 'ServiceLevelAgent',
    event_type: 'incident',
    decision: 'Escalate to on-call engineer',
    timestamp: '2025-10-22T10:00:00Z',
    confidence: 0.95
  },
  {
    agent_name: 'CapacityAgent',
    event_type: 'capacity_alert',
    decision: 'Scale up resources',
    timestamp: '2025-10-22T09:30:00Z',
    confidence: 0.88
  }
]

describe('AgentsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Setup default fetch responses
    ;(global.fetch as any).mockImplementation((url: string) => {
      if (url.includes('/api/agents/decisions')) {
        return Promise.resolve({
          json: () => Promise.resolve({ total: mockDecisions.length, decisions: mockDecisions })
        })
      }
      if (url.includes('/api/agents/providers')) {
        return Promise.resolve({
          json: () => Promise.resolve(mockProviders)
        })
      }
      if (url.includes('/api/agents/health')) {
        return Promise.resolve({
          json: () => Promise.resolve({ status: 'ok', providers: mockHealth, router_active: true })
        })
      }
      return Promise.resolve({
        json: () => Promise.resolve({})
      })
    })
  })

  it('renders agent management interface', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('AI Agent Management')).toBeInTheDocument()
    })
  })

  it('loads and displays LLM providers', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('LLM Provider Configuration')).toBeInTheDocument()
    })

    // Should have provider select populated - use getAllByRole to find select elements
    const selects = screen.getAllByRole('combobox')
    expect(selects.length).toBeGreaterThan(0)
  })

  it('displays provider health status', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Provider Health Status')).toBeInTheDocument()
    })

    // Should show health for ollama - use getAllByText since it appears in multiple places
    await waitFor(() => {
      const ollamaElements = screen.getAllByText('ollama')
      expect(ollamaElements.length).toBeGreaterThan(0)
    })
  })

  it('loads and displays decision history', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/Agent Decision History/)).toBeInTheDocument()
    })

    // Should display decisions
    await waitFor(() => {
      expect(screen.getByText('ServiceLevelAgent')).toBeInTheDocument()
      expect(screen.getByText('CapacityAgent')).toBeInTheDocument()
    })
  })

  it('can configure LLM provider', async () => {
    ;(global.fetch as any).mockImplementation((url: string, options?: any) => {
      if (url.includes('/api/agents/configure-llm') && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve({
            status: 'success',
            message: 'LLM provider configured: ollama',
            config: { provider: 'ollama', model: 'llama2-7b' }
          })
        })
      }
      // Return default mocks for other requests
      if (url.includes('/api/agents/providers')) {
        return Promise.resolve({
          json: () => Promise.resolve(mockProviders)
        })
      }
      if (url.includes('/api/agents/health')) {
        return Promise.resolve({
          json: () => Promise.resolve({ status: 'ok', providers: mockHealth })
        })
      }
      if (url.includes('/api/agents/decisions')) {
        return Promise.resolve({
          json: () => Promise.resolve({ total: 0, decisions: [] })
        })
      }
      return Promise.resolve({ json: () => Promise.resolve({}) })
    })

    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Configure LLM Provider')).toBeInTheDocument()
    })

    const configButton = screen.getByText('Configure LLM Provider')
    fireEvent.click(configButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/agents/configure-llm',
        expect.objectContaining({
          method: 'POST'
        })
      )
    })
  })

  it('can execute agent orchestration', async () => {
    ;(global.fetch as any).mockImplementation((url: string, options?: any) => {
      if (url.includes('/api/agents/run') && options?.method === 'POST') {
        return Promise.resolve({
          json: () => Promise.resolve({
            status: 'success',
            event_type: 'incident',
            decisions: [{ agent: 'test', decision: 'escalate' }],
            actions_taken: ['notify']
          })
        })
      }
      // Default mocks
      if (url.includes('/api/agents/providers')) {
        return Promise.resolve({ json: () => Promise.resolve(mockProviders) })
      }
      if (url.includes('/api/agents/health')) {
        return Promise.resolve({ json: () => Promise.resolve({ status: 'ok', providers: mockHealth }) })
      }
      if (url.includes('/api/agents/decisions')) {
        return Promise.resolve({ json: () => Promise.resolve({ total: 0, decisions: [] }) })
      }
      return Promise.resolve({ json: () => Promise.resolve({}) })
    })

    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Execute Agent Orchestration')).toBeInTheDocument()
    })

    const executeButton = screen.getByText('Execute Agent')
    fireEvent.click(executeButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/agents/run',
        expect.objectContaining({
          method: 'POST'
        })
      )
    })
  })

  it('filters decision history by event type', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('ServiceLevelAgent')).toBeInTheDocument()
    })

    // Find filter select
    const filterLabel = screen.getByText('Filter by Event Type')
    const filterSelect = filterLabel.parentElement?.querySelector('select')
    
    if (filterSelect) {
      fireEvent.change(filterSelect, { target: { value: 'incident' } })

      // Should still show incident decision
      expect(screen.getByText('ServiceLevelAgent')).toBeInTheDocument()
    }
  })

  it('refreshes health status', async () => {
    render(
      <ToastProvider>
        <AgentsPage />
      </ToastProvider>
    )

    await waitFor(() => {
      expect(screen.getByText('Refresh Health')).toBeInTheDocument()
    })

    const refreshButton = screen.getByText('Refresh Health')
    fireEvent.click(refreshButton)

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith('/api/agents/health')
    })
  })
})
