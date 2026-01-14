/**
 * Sidebar Navigation Component
 * Left navigation menu for dashboard
 */

import React, { useState } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  FaChartBar, 
  FaNetworkWired, 
  FaBell, 
  FaLightbulb, 
  FaChartLine,
  FaBars,
  FaTimes
} from 'react-icons/fa'

const Sidebar = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  const navItems = [
    { path: '/', label: 'Dashboard', icon: FaChartBar },
    { path: '/traffic', label: 'Traffic Overview', icon: FaNetworkWired },
    { path: '/alerts', label: 'Alerts', icon: FaBell },
    { path: '/recommendations', label: 'Recommendations', icon: FaLightbulb },
    { path: '/analytics', label: 'Analytics', icon: FaChartLine },
  ]

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-gray-900 text-white rounded-lg shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        aria-label="Toggle menu"
        aria-expanded={isMobileMenuOpen}
        aria-controls="main-navigation"
      >
        <FaBars className="w-6 h-6" aria-hidden="true" />
      </button>

      {/* Sidebar */}
      <aside 
        id="main-navigation"
        className={`
          fixed lg:static inset-y-0 left-0 z-40
          w-64 bg-gray-900 text-white
          transform transition-transform duration-300 ease-in-out
          ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
        role="navigation"
        aria-label="Main navigation"
      >
        <nav className="p-4">
          <div className="mb-6 lg:hidden flex justify-end">
            <button
              onClick={() => setIsMobileMenuOpen(false)}
              className="p-2 text-gray-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
              aria-label="Close menu"
            >
              <FaTimes className="w-6 h-6" aria-hidden="true" />
            </button>
          </div>
          <ul className="space-y-2" role="list">
            {navItems.map((item) => (
              <li key={item.path} role="listitem">
                <NavLink
                  to={item.path}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      isActive
                        ? 'bg-blue-600 text-white shadow-lg'
                        : 'text-gray-300 hover:bg-gray-800 hover:text-white hover:translate-x-1'
                    }`
                  }
                  aria-current={({ isActive }) => isActive ? 'page' : undefined}
                >
                  <item.icon className="w-5 h-5" aria-hidden="true" />
                  <span className="font-medium">{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>
      </aside>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="lg:hidden fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}
    </>
  )
}

export default Sidebar

