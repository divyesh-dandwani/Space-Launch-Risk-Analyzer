import React from 'react'

function ContributingFactors({ factors }) {
  if (!factors || factors.length === 0) return null

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Key Contributing Factors
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {factors.map((factor, index) => {
          const isPositive = factor.impact === 'Positive'
          const borderStyle = isPositive 
            ? 'rgba(16, 185, 129, 0.15)' 
            : 'rgba(239, 68, 68, 0.15)'
          const bgStyle = isPositive
            ? 'rgba(16, 185, 129, 0.03)'
            : 'rgba(239, 68, 68, 0.03)'
          const iconColor = isPositive ? 'var(--success)' : 'var(--danger)'

          return (
            <div 
              key={index}
              style={{
                display: 'flex',
                gap: '16px',
                alignItems: 'flex-start',
                padding: '14px 18px',
                borderRadius: '12px',
                border: `1px solid ${borderStyle}`,
                background: bgStyle,
                transition: 'transform 0.2s',
              }}
            >
              {/* Icon container */}
              <div style={{ color: iconColor, marginTop: '2px', display: 'flex', alignItems: 'center' }}>
                {isPositive ? (
                  // Checkmark outline
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  // Warning triangle
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                    <line x1="12" y1="9" x2="12" y2="13" />
                    <line x1="12" y1="17" x2="12.01" y2="17" />
                  </svg>
                )}
              </div>

              {/* Text content */}
              <div style={{ flex: 1 }}>
                <h4 style={{ 
                  fontSize: '0.95rem', 
                  fontWeight: '600', 
                  color: isPositive ? 'var(--success)' : 'var(--danger)',
                  marginBottom: '4px',
                  fontFamily: 'Outfit'
                }}>
                  {factor.factor}
                </h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                  {factor.description}
                </p>
              </div>

              {/* Impact Tag */}
              <span style={{
                fontSize: '0.7rem',
                padding: '2px 8px',
                borderRadius: '4px',
                fontWeight: '600',
                textTransform: 'uppercase',
                background: isPositive ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                color: iconColor,
                border: `1px solid ${isPositive ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)'}`,
                alignSelf: 'center'
              }}>
                {isPositive ? 'Favorable' : 'Risk Driver'}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ContributingFactors
