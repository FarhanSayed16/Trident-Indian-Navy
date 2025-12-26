import { useState } from 'react'
import './styles/App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            TRIDENT
          </h1>
          <p className="text-lg text-gray-600">
            ML-Enabled Network Anomaly Detection Module for WAF
          </p>
        </header>

        <main className="bg-white rounded-lg shadow-md p-6">
          <div className="text-center">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4">
              Welcome to TRIDENT Dashboard
            </h2>
            <p className="text-gray-600 mb-6">
              Dashboard components will be implemented in Phase 9
            </p>
            
            <div className="inline-flex items-center gap-4 p-4 bg-blue-50 rounded-lg">
              <button
                onClick={() => setCount((count) => count + 1)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Count is {count}
              </button>
            </div>
          </div>
        </main>

        <footer className="mt-8 text-center text-gray-500 text-sm">
          <p>TRIDENT v0.1.0 - Development Phase</p>
        </footer>
      </div>
    </div>
  )
}

export default App

