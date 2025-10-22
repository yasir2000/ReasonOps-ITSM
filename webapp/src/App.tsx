import { useState } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from './auth/AuthContext'

export default function App() {
  const { pathname } = useLocation()
  const auth = useAuth()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  const navItems = [
    { path: '/', label: '📊 Dashboard', role: null },
    { path: '/slm', label: '📋 SLM', role: 'slm' },
    { path: '/capacity', label: '📈 Capacity', role: 'ops' },
    { path: '/financials', label: '💰 Financials', role: 'finance' },
    { path: '/agents', label: '🤖 Agents', role: 'ops' },
    { path: '/exports', label: '📥 Exports', role: null },
  ]

  const filteredNavItems = navItems.filter(item => 
    !item.role || auth.hasRole(item.role)
  )

  const closeMobileMenu = () => setMobileMenuOpen(false)

  return (
    <div className="app">
      {/* Mobile Menu Toggle */}
      <button 
        className="mobile-menu-toggle"
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        aria-label="Toggle menu"
      >
        {mobileMenuOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${mobileMenuOpen ? 'open' : ''}`}>
        <h1>ReasonOps ITSM</h1>
        <nav>
          {filteredNavItems.map(item => (
            <Link 
              key={item.path}
              to={item.path} 
              className={pathname === item.path || pathname.startsWith(item.path + '/') ? 'active' : ''}
              onClick={closeMobileMenu}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div style={{ marginTop: 'auto' }}>
          {auth.user ? (
            <div>
              <div className="label">Signed in</div>
              <div style={{ fontSize: 12 }}>{auth.user.name}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                {auth.user.roles.join(', ')}
              </div>
              <button style={{ marginTop: 8, width: '100%' }} onClick={() => auth.logout()}>
                🚪 Logout
              </button>
            </div>
          ) : (
            <Link to="/login" onClick={closeMobileMenu}>Login</Link>
          )}
        </div>
      </aside>

      {/* Mobile Overlay */}
      {mobileMenuOpen && (
        <div 
          className="mobile-overlay"
          onClick={closeMobileMenu}
        />
      )}

      {/* Main Content */}
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
