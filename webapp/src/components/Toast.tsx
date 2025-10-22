import React, { createContext, useContext, useMemo, useState } from 'react'

type Toast = { id: number; message: string; type?: 'info' | 'success' | 'error' }

type ToastCtx = {
  toasts: Toast[]
  push: (message: string, type?: Toast['type']) => void
  remove: (id: number) => void
}

const Ctx = createContext<ToastCtx | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const api = useMemo<ToastCtx>(() => ({
    toasts,
    push: (message, type='info') => {
      const id = Date.now() + Math.random()
      setToasts((t) => [...t, { id, message, type }])
      setTimeout(() => {
        setToasts((t) => t.filter(x => x.id !== id))
      }, 3500)
    },
    remove: (id) => setToasts((t) => t.filter(x => x.id !== id)),
  }), [toasts])

  return (
    <Ctx.Provider value={api}>
      {children}
      <div className="toast-container">
        {toasts.map(t => (
          <div key={t.id} className={`toast ${t.type || 'info'}`}>{t.message}</div>
        ))}
      </div>
    </Ctx.Provider>
  )
}

export function useToast() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
