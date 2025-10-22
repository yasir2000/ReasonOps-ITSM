import { describe, it, expect } from 'vitest'
import { api } from '../services/api'

// Minimal smoke test: ensure API client functions exist and can be called
// The withFallback in api.ts ensures these will return mock data even if backend is down.

describe('api client smoke', () => {
  it('dashboard returns object', async () => {
    const d = await api.dashboard()
    expect(typeof d).toBe('object')
    expect(d).toHaveProperty('services')
  })

  it('slm metrics returns shape', async () => {
    const m = await api.slm.metrics(7)
    expect(m).toHaveProperty('availability_pct')
    expect(m).toHaveProperty('error_budget')
  })
})
