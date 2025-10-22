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
import './styles.css'

const router = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'slm', element: <SlmPage /> },
      { path: 'capacity', element: <CapacityPage /> },
      { path: 'financials', element: <FinancialsPage /> },
      { path: 'agents', element: <AgentsPage /> },
      { path: 'exports', element: <ExportsPage /> },
    ]
  }
])

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
)
