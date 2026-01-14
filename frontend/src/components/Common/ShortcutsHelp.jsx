/**
 * Keyboard Shortcuts Help Component
 * Displays available keyboard shortcuts in a modal
 */

import React from 'react'
import Modal from './Modal'
import { FaTimes } from 'react-icons/fa'

const ShortcutsHelp = ({ isOpen, onClose }) => {
  const shortcuts = [
    { keys: ['Ctrl', 'K'], description: 'Open global search' },
    { keys: ['Ctrl', '/'], description: 'Show keyboard shortcuts' },
    { keys: ['Esc'], description: 'Close modals/dropdowns' },
    { keys: ['↑', '↓'], description: 'Navigate lists (when focused)' },
    { keys: ['Enter'], description: 'Submit forms' },
  ]

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Keyboard Shortcuts"
      size="md"
    >
      <div className="space-y-4">
        <p className="text-sm text-gray-600">
          Use these keyboard shortcuts to navigate and interact with the dashboard more efficiently.
        </p>
        <div className="space-y-3">
          {shortcuts.map((shortcut, index) => (
            <div
              key={index}
              className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
            >
              <span className="text-sm text-gray-700">{shortcut.description}</span>
              <div className="flex items-center space-x-1">
                {shortcut.keys.map((key, keyIndex) => (
                  <React.Fragment key={keyIndex}>
                    <kbd className="px-2 py-1 text-xs font-semibold text-gray-800 bg-white border border-gray-300 rounded shadow-sm">
                      {key}
                    </kbd>
                    {keyIndex < shortcut.keys.length - 1 && (
                      <span className="text-gray-400 mx-1">+</span>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Note: Some shortcuts may vary depending on your operating system.
          </p>
        </div>
      </div>
    </Modal>
  )
}

export default ShortcutsHelp

