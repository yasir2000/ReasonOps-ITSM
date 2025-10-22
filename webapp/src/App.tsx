import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'

export default function App() {
  const { pathname } = useLocation()
  const auth = useAuth()
  return (
    <div className="app">
      <aside className="sidebar">
        <h1>ReasonOps ITSM</h1>
        <nav>
          <Link to="/" className={pathname === '/' ? 'active' : ''}>Dashboard</Link>
          {auth.hasRole('slm') && <Link to="/slm" className={pathname.startsWith('/slm') ? 'active' : ''}>SLM</Link>}
          {auth.hasRole('ops') && <Link to="/capacity" className={pathname.startsWith('/capacity') ? 'active' : ''}>Capacity</Link>}
          {auth.hasRole('finance') && <Link to="/financials" className={pathname.startsWith('/financials') ? 'active' : ''}>Financials</Link>}
          {auth.hasRole('ops') && <Link to="/agents" className={pathname.startsWith('/agents') ? 'active' : ''}>Agents</Link>}
          <Link to="/exports" className={pathname.startsWith('/exports') ? 'active' : ''}>Exports</Link>
        </nav>
        <div style={{ marginTop: 'auto' }}>
          {auth.user ? (
            <div>
              <div className="label">Signed in</div>
              <div style={{ fontSize: 12 }}>{auth.user.name}</div>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>{auth.user.roles.join(', ')}</div>
              <button style={{ marginTop: 8 }} onClick={() => auth.logout()}>Logout</button>
            </div>
          ) : (
            <Link to="/login">Login</Link>
          )}
        </div>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
