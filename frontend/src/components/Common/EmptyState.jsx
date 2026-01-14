/**
 * Empty State Component
 * Displays a friendly empty state when there's no data to show
 */

import React from 'react'
import { FaInbox, FaChartLine, FaBell, FaLightbulb, FaNetworkWired, FaExclamationTriangle } from 'react-icons/fa'

const EmptyState = ({
  icon = 'default',
  title = 'No data available',
  message = 'There is no data to display at this time.',
  actionLabel = null,
  onAction = null,
  helpText = null,
  className = ''
}) => {
  const iconMap = {
    default: FaInbox,
    alerts: FaBell,
    recommendations: FaLightbulb,
    traffic: FaNetworkWired,
    analytics: FaChartLine,
    error: FaExclamationTriangle,
  }

  const IconComponent = iconMap[icon] || iconMap.default

  return (
    <div className={`flex flex-col items-center justify-center py-12 px-4 ${className}`}>
      <div className="mb-4">
        <IconComponent className="w-16 h-16 text-gray-300" />
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {title}
      </h3>
      
      <p className="text-sm text-gray-500 text-center max-w-md mb-6">
        {message}
      </p>

      {helpText && (
        <p className="text-xs text-gray-400 text-center max-w-md mb-6">
          {helpText}
        </p>
      )}

      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium text-sm"
        >
          {actionLabel}
        </button>
      )}
    </div>
  )
}

export default EmptyState

