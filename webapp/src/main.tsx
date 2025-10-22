import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import App from './App'
import DashboardPage from './pages/DashboardPage'
import SlmPage from './pages/SlmPage'
import CapacityPage from './pages/CapacityPage'
import FinancialsPage from './pages/FinancialsPage'
import AgentsPage from './pages/AgentsPage'
import ExportsPage from './pages/ExportsPage'
import LoginPage from './pages/LoginPage'
import './styles.css'
import { ToastProvider } from './components/Toast'
import { AuthProvider, useAuth } from './auth/AuthContext'

function Protected({ children, role }: { children: JSX.Element; role?: string }) {
  const auth = useAuth()
  if (!auth.user) return <LoginPage />
  if (role && !auth.hasRole(role)) return <div className="error">Access denied (missing role: {role})</div>
  return children
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'slm', element: <Protected role="slm"><SlmPage /></Protected> },
      { path: 'capacity', element: <Protected role="ops"><CapacityPage /></Protected> },
      { path: 'financials', element: <Protected role="finance"><FinancialsPage /></Protected> },
      { path: 'agents', element: <Protected role="ops"><AgentsPage /></Protected> },
      { path: 'exports', element: <ExportsPage /> },
      { path: 'login', element: <LoginPage /> },
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <ToastProvider>
        <RouterProvider router={router} />
      </ToastProvider>
    </AuthProvider>
  </React.StrictMode>
)
