import React from 'react'

function WeatherWidget({ weather }) {
  if (!weather) return null

  const items = [
    {
      label: 'Temperature',
      value: `${weather.temperature_2m.toFixed(1)} °C`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 14.76V3.5a2.5 2.5 0 0 0-5 0v11.26a4.5 4.5 0 1 0 5 0z" />
        </svg>
      )
    },
    {
      label: 'Wind Speed',
      value: `${weather.wind_speed_10m.toFixed(1)} km/h`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9.59 4.59A2 2 0 1 1 11 8H2m10.59 11.41A2 2 0 1 0 14 16H2m15.73-8.27A2.5 2.5 0 1 1 19.5 12H2" />
        </svg>
      )
    },
    {
      label: 'Wind Gusts',
      value: `${weather.wind_gusts_10m.toFixed(1)} km/h`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M2 10h20m-4-4l4 4-4 4" />
        </svg>
      )
    },
    {
      label: 'Surface Pressure',
      value: `${weather.surface_pressure.toFixed(0)} hPa`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10" />
          <path d="M12 6v6l3 3" />
        </svg>
      )
    },
    {
      label: 'Humidity',
      value: `${weather.relative_humidity_2m.toFixed(0)} %`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" />
        </svg>
      )
    },
    {
      label: 'Cloud Cover',
      value: `${weather.cloud_cover.toFixed(0)} %`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M19 16.9A5 5 0 0 0 18 7h-1.26a8 8 0 1 0-11.62 8.58" />
        </svg>
      )
    },
    {
      label: 'Precipitation',
      value: `${weather.precipitation.toFixed(2)} mm/h`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25" />
          <path d="M8 19v3m4-3v3m4-3v3" />
        </svg>
      )
    },
    {
      label: 'Visibility',
      value: `${weather.visibility.toFixed(1)} km`,
      icon: (
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
          <circle cx="12" cy="12" r="3" />
        </svg>
      )
    }
  ]

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
        <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          Atmospheric Conditions
        </h3>
        <span style={{
          fontSize: '0.7rem',
          padding: '2px 8px',
          borderRadius: '4px',
          background: 'var(--badge-bg)',
          border: '1px solid var(--badge-border)',
          color: 'var(--cyan)',
          textTransform: 'uppercase',
          fontWeight: '500'
        }}>
          Open-Meteo {weather.api_used}
        </span>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '12px',
        flex: 1
      }}>
        {items.map((item, index) => (
          <div key={index} style={{
            background: 'var(--widget-bg)',
            border: '1px solid var(--widget-border)',
            borderRadius: '10px',
            padding: '12px 14px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            transition: 'border-color 0.2s',
          }}>
            <div style={{ color: 'var(--cyan)', display: 'flex', alignItems: 'center' }}>
              {item.icon}
            </div>
            <div>
              <span style={{ display: 'block', fontSize: '0.72rem', color: 'var(--text-secondary)', fontWeight: '400' }}>
                {item.label}
              </span>
              <span style={{ fontSize: '0.95rem', fontWeight: '600', color: 'var(--text-primary)', fontFamily: 'Outfit' }}>
                {item.value}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default WeatherWidget
