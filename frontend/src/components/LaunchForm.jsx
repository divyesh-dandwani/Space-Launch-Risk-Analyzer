import React, { useState, useEffect } from 'react'

const DEFAULT_SITES = [
  "LC-39A, Kennedy Space Center, Florida, USA",
  "Site 200/39, Baikonur Cosmodrome, Kazakhstan",
  "SLC-4E, Vandenberg AFB, California, USA",
  "First Launch Pad, Satish Dhawan Space Centre, India",
  "ELA-3, Guiana Space Centre, French Guiana",
  "Yoshinobu Launch Complex, Tanegashima Space Center, Japan",
  "Site 9401 (SLS-2), Jiuquan Satellite Launch Center, China"
]

const DEFAULT_ROCKETS = [
  "Falcon 9 Block 5",
  "Long March 2D",
  "Atlas V 541",
  "Proton-M/Briz-M",
  "Ariane 5 ECA",
  "PSLV-XL",
  "Saturn V"
]

const DEFAULT_COMPANIES = [
  "SpaceX",
  "CASC",
  "Roscosmos",
  "ULA",
  "Arianespace",
  "ISRO",
  "NASA"
]

function LaunchForm({ onSubmit, loading, sites, rockets, companies }) {
  // Setup default state values
  const todayStr = new Date().toISOString().split('T')[0]
  
  const [formData, setFormData] = useState({
    site: DEFAULT_SITES[0],
    date: todayStr,
    time: '12:00',
    rocket: DEFAULT_ROCKETS[0],
    company: DEFAULT_COMPANIES[0],
    payload_type: 'Satellite',
    rocket_cost: '62.0',
    // Weather manual overrides
    override_weather: false,
    temperature_2m: 22,
    relative_humidity_2m: 55,
    surface_pressure: 1013,
    wind_speed_10m: 12,
    wind_gusts_10m: 15,
    visibility: 15,
    cloud_cover: 30,
    precipitation: 0.0
  })

  // Set default values once metadata loaded
  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      site: sites.length > 0 ? sites[0].name : DEFAULT_SITES[0],
      rocket: rockets.length > 0 ? rockets[0] : DEFAULT_ROCKETS[0],
      company: companies.length > 0 ? companies[0] : DEFAULT_COMPANIES[0]
    }))
  }, [sites, rockets, companies])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Parse cost and calculate physically realistic dew point (Appx: Temp - (100 - RH)/5)
    const dewPointVal = parseFloat((formData.temperature_2m - (100 - formData.relative_humidity_2m) / 5).toFixed(1))
    
    const reqData = {
      ...formData,
      wind_direction_10m: 180.0, // Default southern wind
      dew_point_2m: dewPointVal
    }

    if (formData.rocket_cost && String(formData.rocket_cost).trim() !== '') {
      reqData.rocket_cost = parseFloat(formData.rocket_cost)
    } else {
      delete reqData.rocket_cost
    }

    onSubmit(reqData)
  }

  const activeSites = sites.length > 0 ? sites.map(s => s.name) : DEFAULT_SITES
  const activeRockets = rockets.length > 0 ? rockets : DEFAULT_ROCKETS
  const activeCompanies = companies.length > 0 ? companies : DEFAULT_COMPANIES

  return (
    <form className="glass-panel" onSubmit={handleSubmit} style={{ animation: 'pulse-glow 8s ease-in-out infinite' }}>
      <h2 style={{ fontFamily: 'Outfit', fontSize: '1.4rem', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
        </svg>
        Launch Parameters
      </h2>

      <div className="form-group">
        <label htmlFor="site">Launch Site</label>
        <select 
          id="site"
          name="site"
          className="input-field" 
          value={formData.site} 
          onChange={handleChange}
        >
          {activeSites.map((site) => (
            <option key={site} value={site}>{site}</option>
          ))}
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div className="form-group">
          <label htmlFor="date">Launch Date</label>
          <input 
            type="date" 
            id="date"
            name="date"
            className="input-field"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="time">Launch Time (UTC)</label>
          <input 
            type="time" 
            id="time"
            name="time"
            className="input-field"
            value={formData.time}
            onChange={handleChange}
            required
          />
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="rocket">Launch Vehicle</label>
        <select 
          id="rocket"
          name="rocket"
          className="input-field"
          value={formData.rocket}
          onChange={handleChange}
        >
          {activeRockets.map((rocket) => (
            <option key={rocket} value={rocket}>{rocket}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="company">Operator / Space Agency</label>
        <select 
          id="company"
          name="company"
          className="input-field"
          value={formData.company}
          onChange={handleChange}
        >
          {activeCompanies.map((comp) => (
            <option key={comp} value={comp}>{comp}</option>
          ))}
        </select>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '16px' }}>
        <div className="form-group">
          <label htmlFor="payload_type">Payload Class</label>
          <select 
            id="payload_type"
            name="payload_type"
            className="input-field"
            value={formData.payload_type}
            onChange={handleChange}
          >
            <option value="Satellite">Satellite (Commercial/Military)</option>
            <option value="Crew">Crewed Spacecraft</option>
            <option value="Cargo">Cargo / Resupply</option>
            <option value="Science">Scientific Instrument / Space Telescope</option>
            <option value="Interplanetary">Interplanetary Probe / Lander</option>
            <option value="Prototype">Experimental Prototype</option>
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="rocket_cost">Cost ($M)</label>
          <input 
            type="number" 
            id="rocket_cost"
            name="rocket_cost"
            placeholder="e.g. 50"
            className="input-field"
            value={formData.rocket_cost}
            onChange={handleChange}
            min="0"
            step="0.1"
          />
        </div>
      </div>

      {/* Weather override checkbox */}
      <div className="form-group" style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <input 
          type="checkbox" 
          id="override_weather"
          name="override_weather"
          checked={formData.override_weather}
          onChange={(e) => setFormData(prev => ({ ...prev, override_weather: e.target.checked }))}
          style={{ cursor: 'pointer', width: '16px', height: '16px', accentColor: 'var(--primary)' }}
        />
        <label htmlFor="override_weather" style={{ cursor: 'pointer', marginBottom: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', fontWeight: 'bold' }}>
          Override Weather Conditions (Manual Input)
        </label>
      </div>

      {/* Manual weather overrides sliders */}
      {formData.override_weather && (
        <div className="weather-overrides-section" style={{
          marginTop: '12px',
          padding: '16px',
          border: '1px solid var(--widget-border)',
          borderRadius: '8px',
          background: 'var(--widget-bg)',
          display: 'grid',
          gap: '12px',
          animation: 'fadeIn 0.3s ease'
        }}>
          <h4 style={{ fontFamily: 'Outfit', fontSize: '0.95rem', color: 'var(--primary)', marginBottom: '4px' }}>
            Atmospheric Conditions (Overrides)
          </h4>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Wind Speed</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.wind_speed_10m} km/h</span>
              </label>
              <input 
                type="range" 
                name="wind_speed_10m"
                min="0" 
                max="70" 
                value={formData.wind_speed_10m} 
                onChange={(e) => setFormData(p => ({ ...p, wind_speed_10m: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
            
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Wind Gusts</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.wind_gusts_10m} km/h</span>
              </label>
              <input 
                type="range" 
                name="wind_gusts_10m"
                min="0" 
                max="100" 
                value={formData.wind_gusts_10m} 
                onChange={(e) => setFormData(p => ({ ...p, wind_gusts_10m: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Temperature</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.temperature_2m} °C</span>
              </label>
              <input 
                type="range" 
                name="temperature_2m"
                min="-15" 
                max="45" 
                value={formData.temperature_2m} 
                onChange={(e) => setFormData(p => ({ ...p, temperature_2m: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
            
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Relative Humidity</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.relative_humidity_2m} %</span>
              </label>
              <input 
                type="range" 
                name="relative_humidity_2m"
                min="10" 
                max="100" 
                value={formData.relative_humidity_2m} 
                onChange={(e) => setFormData(p => ({ ...p, relative_humidity_2m: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Cloud Cover</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.cloud_cover} %</span>
              </label>
              <input 
                type="range" 
                name="cloud_cover"
                min="0" 
                max="100" 
                value={formData.cloud_cover} 
                onChange={(e) => setFormData(p => ({ ...p, cloud_cover: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
            
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Precipitation</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.precipitation} mm/h</span>
              </label>
              <input 
                type="range" 
                name="precipitation"
                min="0" 
                max="20" 
                step="0.1"
                value={formData.precipitation} 
                onChange={(e) => setFormData(p => ({ ...p, precipitation: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Visibility</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.visibility} km</span>
              </label>
              <input 
                type="range" 
                name="visibility"
                min="0" 
                max="50" 
                value={formData.visibility} 
                onChange={(e) => setFormData(p => ({ ...p, visibility: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
            
            <div className="form-group" style={{ marginBottom: 0 }}>
              <label style={{ fontSize: '0.8rem', display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                <span>Surface Pressure</span>
                <span style={{ color: 'var(--primary)', fontWeight: 'bold' }}>{formData.surface_pressure} hPa</span>
              </label>
              <input 
                type="range" 
                name="surface_pressure"
                min="950" 
                max="1050" 
                value={formData.surface_pressure} 
                onChange={(e) => setFormData(p => ({ ...p, surface_pressure: parseFloat(e.target.value) }))}
                style={{ width: '100%', accentColor: 'var(--primary)' }}
              />
            </div>
          </div>
        </div>
      )}

      <button 
        type="submit" 
        className="submit-btn" 
        style={{ marginTop: '16px' }} 
        disabled={loading}
      >
        {loading ? 'Analyzing Parameters...' : 'Analyze Launch Risk'}
      </button>
    </form>
  )
}

export default LaunchForm
