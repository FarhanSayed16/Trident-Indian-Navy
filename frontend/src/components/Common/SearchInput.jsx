/**
 * Enhanced Search Input Component
 * Search input with autocomplete, history, and clear button
 */

import React, { useState, useEffect, useRef } from 'react'
import { FaSearch, FaTimes, FaHistory } from 'react-icons/fa'

const SearchInput = ({
  value,
  onChange,
  onSearch,
  placeholder = 'Search...',
  suggestions = [],
  showHistory = true,
  maxHistoryItems = 5,
  className = '',
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [searchHistory, setSearchHistory] = useState([])
  const inputRef = useRef(null)
  const containerRef = useRef(null)

  // Load search history from localStorage
  useEffect(() => {
    if (showHistory) {
      const history = localStorage.getItem('searchHistory')
      if (history) {
        try {
          setSearchHistory(JSON.parse(history).slice(0, maxHistoryItems))
        } catch (e) {
          console.error('Failed to parse search history:', e)
        }
      }
    }
  }, [showHistory, maxHistoryItems])

  // Save to search history
  const saveToHistory = (searchTerm) => {
    if (!searchTerm || !showHistory) return

    const history = [...searchHistory]
    // Remove if already exists
    const index = history.indexOf(searchTerm)
    if (index > -1) {
      history.splice(index, 1)
    }
    // Add to beginning
    history.unshift(searchTerm)
    // Keep only max items
    const trimmedHistory = history.slice(0, maxHistoryItems)
    setSearchHistory(trimmedHistory)
    localStorage.setItem('searchHistory', JSON.stringify(trimmedHistory))
  }

  // Handle search
  const handleSearch = (searchTerm = value) => {
    if (searchTerm.trim()) {
      saveToHistory(searchTerm.trim())
      if (onSearch) {
        onSearch(searchTerm.trim())
      }
    }
    setShowSuggestions(false)
    inputRef.current?.blur()
  }

  // Handle input change
  const handleChange = (e) => {
    onChange(e)
    if (e.target.value && suggestions.length > 0) {
      setShowSuggestions(true)
    } else {
      setShowSuggestions(false)
    }
  }

  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleSearch()
    } else if (e.key === 'Escape') {
      setShowSuggestions(false)
      inputRef.current?.blur()
    }
  }

  // Handle suggestion click
  const handleSuggestionClick = (suggestion) => {
    onChange({ target: { value: suggestion } })
    handleSearch(suggestion)
  }

  // Handle history click
  const handleHistoryClick = (historyItem) => {
    onChange({ target: { value: historyItem } })
    handleSearch(historyItem)
  }

  // Clear search
  const handleClear = () => {
    onChange({ target: { value: '' } })
    setShowSuggestions(false)
    inputRef.current?.focus()
  }

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setShowSuggestions(false)
      }
    }

    if (showSuggestions) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [showSuggestions])

  // Filter suggestions based on input
  const filteredSuggestions = suggestions.filter((suggestion) =>
    suggestion.toLowerCase().includes(value.toLowerCase())
  )

  // Highlight matches in text
  const highlightMatch = (text, query) => {
    if (!query) return text
    const regex = new RegExp(`(${query})`, 'gi')
    const parts = text.split(regex)
    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 font-semibold">{part}</mark>
      ) : (
        part
      )
    )
  }

  const displaySuggestions = showSuggestions && (filteredSuggestions.length > 0 || searchHistory.length > 0)

  return (
    <div className={`relative ${className}`} ref={containerRef}>
      <div className="relative">
        <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
          <FaSearch className="w-5 h-5 text-gray-400" />
        </div>
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleChange}
          onKeyPress={handleKeyPress}
          onFocus={() => {
            setIsFocused(true)
            if (value && (filteredSuggestions.length > 0 || searchHistory.length > 0)) {
              setShowSuggestions(true)
            }
          }}
          onBlur={() => {
            setIsFocused(false)
            // Delay to allow suggestion clicks
            setTimeout(() => setShowSuggestions(false), 200)
          }}
          placeholder={placeholder}
          aria-label={placeholder || 'Search input'}
          aria-autocomplete="list"
          aria-expanded={displaySuggestions}
          aria-controls="search-suggestions"
          className={`
            w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg
            focus:ring-2 focus:ring-blue-500 focus:border-blue-500
            transition-colors duration-200
            ${isFocused ? 'border-blue-500' : ''}
          `}
          {...props}
        />
        {value && (
          <button
            onClick={handleClear}
            className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
            aria-label="Clear search"
          >
            <FaTimes className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Suggestions Dropdown */}
      {displaySuggestions && (
        <div 
          id="search-suggestions"
          className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-auto"
          role="listbox"
          aria-label="Search suggestions"
        >
          {/* Autocomplete Suggestions */}
          {filteredSuggestions.length > 0 && (
            <div className="py-1">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Suggestions
              </div>
              {filteredSuggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
                  aria-label={`Select suggestion: ${suggestion}`}
                >
                  <FaSearch className="w-4 h-4 text-gray-400" aria-hidden="true" />
                  <span>{highlightMatch(suggestion, value)}</span>
                </button>
              ))}
            </div>
          )}

          {/* Search History */}
          {showHistory && searchHistory.length > 0 && (
            <div className="py-1 border-t border-gray-200">
              <div className="px-3 py-2 text-xs font-semibold text-gray-500 uppercase">
                Recent Searches
              </div>
              {searchHistory.map((historyItem, index) => (
                <button
                  key={index}
                  onClick={() => handleHistoryClick(historyItem)}
                  className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 focus:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500 flex items-center space-x-2"
                  aria-label={`Select recent search: ${historyItem}`}
                >
                  <FaHistory className="w-4 h-4 text-gray-400" aria-hidden="true" />
                  <span>{highlightMatch(historyItem, value)}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default SearchInput

