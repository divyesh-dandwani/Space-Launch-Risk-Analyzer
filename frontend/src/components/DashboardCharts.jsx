import React from 'react'

function DashboardCharts({ stats, loading }) {
  if (loading) {
    return (
      <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '400px' }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '5px solid var(--panel-border)',
          borderTopColor: 'var(--cyan)',
          borderRadius: '50%',
          animation: 'spin-slow 1s linear infinite',
          marginBottom: '16px'
        }}></div>
        <h3 style={{ fontFamily: 'Outfit' }}>Compiling Historical Analytics...</h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '8px' }}>Processing database records and weather metrics</p>
      </div>
    )
  }

  if (!stats || !stats.success_by_year || stats.success_by_year.length === 0) {
    return (
      <div className="glass-panel" style={{ textAlign: 'center', padding: '40px' }}>
        <h3>No Historical Data Found</h3>
        <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>
          Please complete weather enrichment and model training to populate these analytics.
        </p>
      </div>
    )
  }

  const { success_by_year, success_by_company, weather_compare } = stats

  // Chart 1 Helpers: success_by_year
  // We take the last 30 years to avoid drawing 60 crammed bars, or we group them
  const recent_years = success_by_year.slice(-25)
  const max_launches = Math.max(...recent_years.map(y => y.total), 1)

  // Chart 2 Helpers: success_by_company
  const top_companies = success_by_company.slice(0, 7)
  const max_comp_launches = Math.max(...top_companies.map(c => c.total), 1)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
      
      {/* Overview Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        <div className="glass-panel" style={{ textAlign: 'center', padding: '20px' }}>
          <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Total Database Records
          </span>
          <span style={{ fontSize: '2rem', fontWeight: '800', fontFamily: 'Outfit', color: 'var(--cyan)' }}>
            {success_by_year.reduce((acc, y) => acc + y.total, 0)}
          </span>
        </div>
        <div className="glass-panel" style={{ textAlign: 'center', padding: '20px' }}>
          <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Global Launch Successes
          </span>
          <span style={{ fontSize: '2rem', fontWeight: '800', fontFamily: 'Outfit', color: 'var(--success)' }}>
            {success_by_year.reduce((acc, y) => acc + y.successes, 0)}
          </span>
        </div>
        <div className="glass-panel" style={{ textAlign: 'center', padding: '20px' }}>
          <span style={{ display: 'block', fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Historical Success Rate
          </span>
          <span style={{ fontSize: '2rem', fontWeight: '800', fontFamily: 'Outfit', color: '#a5b4fc' }}>
            {(
              (success_by_year.reduce((acc, y) => acc + y.successes, 0) /
                success_by_year.reduce((acc, y) => acc + y.total, 1)) *
              100
            ).toFixed(1)}%
          </span>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 0.8fr', gap: '32px' }}>
        
        {/* Chart 1: Historical Launch Volume by Year (SVG Bar Chart) */}
        <div className="glass-panel" style={{ minHeight: '350px', display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '4px', fontFamily: 'Outfit' }}>
            Launch Volume & Success Rates (Last 25 Years)
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Bars indicate launch volume. The line represents the success rate.
          </p>

          <div style={{ flex: 1, position: 'relative', minHeight: '220px' }}>
            <svg width="100%" height="220" style={{ overflow: 'visible' }}>
              {/* Grid Lines */}
              {[0, 0.25, 0.5, 0.75, 1.0].map((ratio, i) => (
                <line 
                  key={i} 
                  x1="30" 
                  y1={20 + ratio * 160} 
                  x2="100%" 
                  y2={20 + ratio * 160} 
                  stroke="var(--chart-grid-line)" 
                  strokeWidth="1"
                />
              ))}

              {/* Connection Lines (Success Rate Line) */}
              {recent_years.map((y, idx) => {
                if (idx === 0) return null
                const prev_y = recent_years[idx - 1]
                const x1 = 6 + ((idx - 1) / (recent_years.length - 1)) * 88
                const x2 = 6 + (idx / (recent_years.length - 1)) * 88
                const y1 = 180 - (prev_y.rate * 160)
                const y2 = 180 - (y.rate * 160)
                return (
                  <line
                    key={`line-${idx}`}
                    x1={`${x1}%`}
                    y1={y1}
                    x2={`${x2}%`}
                    y2={y2}
                    stroke="var(--cyan)"
                    strokeWidth="2.5"
                  />
                )
              })}

              {recent_years.map((y, idx) => {
                const x = 6 + (idx / (recent_years.length - 1)) * 88
                const bar_height = (y.total / max_launches) * 160
                const bar_y = 180 - bar_height
                
                // Coordinates for line chart (success rate)
                const line_y = 180 - (y.rate * 160)
                
                return (
                  <g key={y.year}>
                    <title>{`Year: ${y.year}\nLaunches: ${y.total}\nSuccesses: ${y.successes}\nSuccess Rate: ${(y.rate * 100).toFixed(1)}%`}</title>
                    {/* Bar */}
                    <rect 
                      x={`${x}%`} 
                      y={bar_y} 
                      width="12" 
                      height={bar_height} 
                      fill="var(--chart-volume-bg)" 
                      rx="2"
                      transform="translate(-6, 0)"
                    />
                    <rect 
                      x={`${x}%`} 
                      y={180 - ((y.successes / max_launches) * 160)} 
                      width="12" 
                      height={(y.successes / max_launches) * 160} 
                      fill="var(--primary)" 
                      rx="2"
                      transform="translate(-6, 0)"
                    />

                    {/* Dot on Line */}
                    <circle 
                      cx={`${x}%`} 
                      cy={line_y} 
                      r="3.5" 
                      fill="var(--cyan)"
                    />

                    {/* X Axis label (Year) */}
                    {idx % 3 === 0 && (
                      <text 
                        x={`${x}%`} 
                        y="200" 
                        fill="var(--text-muted)" 
                        fontSize="9" 
                        textAnchor="middle"
                      >
                        {y.year}
                      </text>
                    )}
                  </g>
                )
              })}
            </svg>
          </div>
        </div>

        {/* Chart 2: Success Rate by Company */}
        <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column' }}>
          <h3 style={{ fontSize: '1rem', color: 'var(--text-primary)', marginBottom: '4px', fontFamily: 'Outfit' }}>
            Top Launch Operators
          </h3>
          <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Comparison of historical launch volume and success metrics.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', flex: 1 }}>
            {top_companies.map((c) => {
              const width_pct = (c.total / max_comp_launches) * 100
              const rate_pct = (c.rate * 100).toFixed(0)
              
              return (
                <div key={c.company}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '500', color: 'var(--text-primary)' }}>{c.company}</span>
                    <span style={{ color: 'var(--text-secondary)' }}>
                      {c.successes}/{c.total} Launches <span style={{ color: 'var(--cyan)', fontWeight: '600', marginLeft: '6px' }}>{rate_pct}%</span>
                    </span>
                  </div>
                  {/* Stacked bar */}
                  <div style={{ width: '100%', height: '8px', background: 'var(--widget-bg)', borderRadius: '9999px', overflow: 'hidden' }}>
                    <div style={{ 
                      width: `${width_pct}%`, 
                      height: '100%', 
                      background: `linear-gradient(90deg, var(--primary) 0%, var(--cyan) 100%)`, 
                      borderRadius: '9999px' 
                    }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Atmospheric profiles comparisons */}
      {weather_compare && Object.keys(weather_compare).length > 0 && (
        <div className="glass-panel">
          <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', marginBottom: '6px', fontFamily: 'Outfit' }}>
            Atmospheric Profile Comparison (Successes vs Failures)
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '24px' }}>
            Compares average weather attributes of successful missions versus failed missions in history.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
            {/* Wind speed */}
            {weather_compare.wind_speed_10m && (
              <div style={{ background: 'var(--widget-bg)', border: '1px solid var(--widget-border)', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Avg Wind Speed
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--success)' }}>SUCCESS: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.wind_speed_10m.success_mean.toFixed(1)} km/h
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--danger)' }}>FAILURE: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.wind_speed_10m.failure_mean.toFixed(1)} km/h
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Cloud cover */}
            {weather_compare.cloud_cover && (
              <div style={{ background: 'var(--widget-bg)', border: '1px solid var(--widget-border)', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Avg Cloud Cover
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--success)' }}>SUCCESS: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.cloud_cover.success_mean.toFixed(0)}%
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--danger)' }}>FAILURE: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.cloud_cover.failure_mean.toFixed(0)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Temperature */}
            {weather_compare.temperature_2m && (
              <div style={{ background: 'var(--widget-bg)', border: '1px solid var(--widget-border)', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Avg Temperature
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--success)' }}>SUCCESS: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.temperature_2m.success_mean.toFixed(1)} °C
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--danger)' }}>FAILURE: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.temperature_2m.failure_mean.toFixed(1)} °C
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Pressure */}
            {weather_compare.surface_pressure && (
              <div style={{ background: 'var(--widget-bg)', border: '1px solid var(--widget-border)', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                <span style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px' }}>
                  Avg Surface Pressure
                </span>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--success)' }}>SUCCESS: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.surface_pressure.success_mean.toFixed(0)} hPa
                    </span>
                  </div>
                  <div>
                    <span style={{ fontSize: '0.72rem', color: 'var(--danger)' }}>FAILURE: </span>
                    <span style={{ fontSize: '1rem', fontWeight: '700', fontFamily: 'Outfit' }}>
                      {weather_compare.surface_pressure.failure_mean.toFixed(0)} hPa
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardCharts
