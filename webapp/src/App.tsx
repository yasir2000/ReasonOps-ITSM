import { Link, Outlet, useLocation } from 'react-router-dom'

export default function App() {
  const { pathname } = useLocation()
  return (
    <div className="app">
      <aside className="sidebar">
        <h1>ReasonOps ITSM</h1>
        <nav>
          <Link to="/" className={pathname === '/' ? 'active' : ''}>Dashboard</Link>
          <Link to="/slm" className={pathname.startsWith('/slm') ? 'active' : ''}>SLM</Link>
          <Link to="/capacity" className={pathname.startsWith('/capacity') ? 'active' : ''}>Capacity</Link>
          <Link to="/financials" className={pathname.startsWith('/financials') ? 'active' : ''}>Financials</Link>
          <Link to="/agents" className={pathname.startsWith('/agents') ? 'active' : ''}>Agents</Link>
          <Link to="/exports" className={pathname.startsWith('/exports') ? 'active' : ''}>Exports</Link>
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
