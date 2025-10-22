import React, { createContext, useContext, useMemo, useState } from 'react'

type User = {
  name: string
  roles: string[]
}

export type AuthCtx = {
  user: User | null
  login: (name: string, roles: string[]) => void
  logout: () => void
  hasRole: (role: string) => boolean
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem('reasonops:user')
    return raw ? JSON.parse(raw) : null
  })

  const api = useMemo<AuthCtx>(() => ({
    user,
    login: (name, roles) => {
      const u = { name, roles }
      setUser(u)
      localStorage.setItem('reasonops:user', JSON.stringify(u))
    },
    logout: () => {
      setUser(null)
      localStorage.removeItem('reasonops:user')
    },
    hasRole: (role) => !!user?.roles.includes(role)
  }), [user])

  return <Ctx.Provider value={api}>{children}</Ctx.Provider>
}

export function useAuth() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
