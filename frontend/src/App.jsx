/**
 * TRIDENT Frontend - Main App Component
 * Sets up routing and application structure
 */

import React, { useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ToastProvider } from './context/ToastContext'
import useKeyboardShortcuts from './hooks/useKeyboardShortcuts'
import ErrorBoundary from './components/Common/ErrorBoundary'
import ShortcutsHelp from './components/Common/ShortcutsHelp'
import DashboardLayout from './components/Layout/DashboardLayout'
import Dashboard from './pages/Dashboard'
import TrafficOverview from './pages/TrafficOverview'
import Alerts from './pages/Alerts'
import Recommendations from './pages/Recommendations'
import Analytics from './pages/Analytics'
import NotFound from './pages/NotFound'
import './styles/App.css'

function App() {
  const [showShortcuts, setShowShortcuts] = useState(false)

  // Global keyboard shortcuts
  useKeyboardShortcuts({
    'ctrl+k': (e) => {
      // Global search - placeholder for now
      e.preventDefault()
      console.log('Global search triggered')
    },
    'ctrl+/': (e) => {
      e.preventDefault()
      setShowShortcuts(true)
    },
    'escape': (e) => {
      // Close modals/dropdowns - handled by individual components
      setShowShortcuts(false)
    },
  })

  return (
    <ErrorBoundary showDetails={process.env.NODE_ENV === 'development'}>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="traffic" element={<TrafficOverview />} />
              <Route path="alerts" element={<Alerts />} />
              <Route path="recommendations" element={<Recommendations />} />
              <Route path="analytics" element={<Analytics />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Routes>
          <ShortcutsHelp isOpen={showShortcuts} onClose={() => setShowShortcuts(false)} />
        </BrowserRouter>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App

