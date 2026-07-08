import React, { useState, useEffect } from 'react'
import LaunchForm from './components/LaunchForm'
import RiskMeter from './components/RiskMeter'
import WeatherWidget from './components/WeatherWidget'
import ContributingFactors from './components/ContributingFactors'
import DashboardCharts from './components/DashboardCharts'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001'

function App() {
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const [activeTab, setActiveTab] = useState('analyzer')
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  
  // Metadata state
  const [sites, setSites] = useState([])
  const [rockets, setRockets] = useState([])
  const [companies, setCompanies] = useState([])
  const [stats, setStats] = useState(null)
  const [statsLoading, setStatsLoading] = useState(false)

  // Fetch sites and rockets dropdown metadata on mount
  useEffect(() => {
    async function fetchMetadata() {
      try {
        const sitesRes = await fetch(`${API_BASE_URL}/api/sites`)
        const sitesData = await sitesRes.json()
        setSites(sitesData)

        const rocketsRes = await fetch(`${API_BASE_URL}/api/rockets`)
        const rocketsData = await rocketsRes.json()
        setRockets(rocketsData.rockets || [])
        setCompanies(rocketsData.companies || [])
      } catch (err) {
        console.error("Error loading initial metadata:", err)
      }
    }
    fetchMetadata()
  }, [])

  // Fetch historical statistics when dashboard tab is active
  useEffect(() => {
    if (activeTab === 'dashboard' && !stats) {
      async function fetchStats() {
        setStatsLoading(true)
        try {
          const res = await fetch(`${API_BASE_URL}/api/stats`)
          const data = await res.json()
          setStats(data)
        } catch (err) {
          console.error("Error loading statistics:", err)
        } finally {
          setStatsLoading(false)
        }
      }
      fetchStats()
    }
  }, [activeTab, stats])

  const handlePredict = async (formData) => {
    setLoading(true)
    setError(null)
    setPrediction(null)

    try {
      const res = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })

      if (!res.ok) {
        let errorDetail = 'Prediction API failed. Ensure the backend server is running.'
        try {
          const errData = await res.json()
          if (errData && errData.detail) {
            if (typeof errData.detail === 'string') {
              errorDetail = errData.detail
            } else if (Array.isArray(errData.detail)) {
              errorDetail = errData.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(' | ')
            }
          }
        } catch (e) {}
        throw new Error(errorDetail)
      }

      const data = await res.json()
      setPrediction(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <button 
        onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')} 
        className="theme-toggle"
        title={`Switch to ${theme === 'light' ? 'Dark' : 'Light'} Mode`}
        aria-label="Toggle theme"
      >
        {theme === 'light' ? (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
        ) : (
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
        )}
      </button>

      <header className="header">
        <h1>Space Launch Risk Analyzer</h1>
        <p>
          Predict mission success probability and analyze atmospheric launch constraints using historical launches and real-time/forecast weather conditions.
        </p>
      </header>

      <div className="tabs-container">
        <button 
          className={`tab ${activeTab === 'analyzer' ? 'active' : ''}`}
          onClick={() => setActiveTab('analyzer')}
        >
          Risk Analyzer
        </button>
        <button 
          className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          Historical Stats
        </button>
      </div>

      {activeTab === 'analyzer' && (
        <div className="dashboard-grid">
          <LaunchForm 
            onSubmit={handlePredict} 
            loading={loading} 
            sites={sites} 
            rockets={rockets} 
            companies={companies}
          />

          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', minHeight: '500px' }}>
            {error && (
              <div className="glass-panel" style={{ borderColor: 'var(--danger)', color: 'var(--danger)', padding: '20px' }}>
                <h3 style={{ marginBottom: '8px' }}>Analysis Failed</h3>
                <p>{error}</p>
              </div>
            )}

            {loading && (
              <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  border: '5px solid rgba(255,255,255,0.1)',
                  borderTopColor: 'var(--primary)',
                  borderRadius: '50%',
                  animation: 'spin-slow 1s linear infinite',
                  marginBottom: '16px'
                }}></div>
                <h3 style={{ fontFamily: 'Outfit', fontWeight: '500' }}>Querying Atmospheric Forecasts...</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '8px' }}>Retrieving weather variables from Open-Meteo API</p>
              </div>
            )}

            {!prediction && !loading && !error && (
              <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '300px', textAlign: 'center' }}>
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)', marginBottom: '16px' }}>
                  <path d="M4.5 16.5c-1.5 1.26-2.5 3.19-2.5 5.5h20c0-2.31-1-4.24-2.5-5.5" />
                  <path d="M12 2v14" />
                  <path d="M9 5l3-3 3 3" />
                  <path d="M12 22a4 4 0 0 0 4-4v-2H8v2a4 4 0 0 0 4 4z" />
                </svg>
                <h3 style={{ fontFamily: 'Outfit', color: 'var(--text-secondary)' }}>Launch System Ready</h3>
                <p style={{ color: 'var(--text-muted)', maxWidth: '400px', margin: '8px auto 0', fontSize: '0.9rem' }}>
                  Enter launch parameters, date, and space vehicle details on the left, then click Analyze.
                </p>
              </div>
            )}

            {prediction && !loading && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: '1.25fr 1.75fr', gap: '24px' }}>
                  <RiskMeter 
                    success={prediction.success_probability} 
                    failure={prediction.failure_risk} 
                    level={prediction.risk_level}
                    color={prediction.risk_color}
                  />
                  <WeatherWidget weather={prediction.weather_summary} />
                </div>
                <ContributingFactors factors={prediction.contributing_factors} />
              </>
            )}
          </div>
        </div>
      )}

      {activeTab === 'dashboard' && (
        <DashboardCharts stats={stats} loading={statsLoading} />
      )}
    </div>
  )
}

export default App
