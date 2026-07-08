import React, { useEffect, useState } from 'react'

function RiskMeter({ success, failure, level, color }) {
  const [offset, setOffset] = useState(314.159) // Fully empty state on mount
  
  const radius = 50
  const circumference = 2 * Math.PI * radius // ~314.159

  useEffect(() => {
    // Animate fill-in on component mount or prediction change
    const progressOffset = circumference - (circumference * success) / 100
    const timer = setTimeout(() => {
      setOffset(progressOffset)
    }, 150)
    return () => clearTimeout(timer)
  }, [success])

  return (
    <div className="glass-panel" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
      <h3 style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
        Safety Assessment
      </h3>

      {/* Radial Progress Gauge */}
      <div style={{ position: 'relative', width: '130px', height: '130px', margin: '10px 0 20px' }}>
        <svg width="100%" height="100%" viewBox="0 0 120 120" style={{ transform: 'rotate(-90deg)' }}>
          {/* Background circle */}
          <circle 
            cx="60" 
            cy="60" 
            r={radius} 
            fill="none" 
            stroke="var(--meter-circle-bg)" 
            strokeWidth="8"
          />
          {/* Animated Progress circle */}
          <circle 
            cx="60" 
            cy="60" 
            r={radius} 
            fill="none" 
            stroke={color} 
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            style={{ transition: 'stroke-dashoffset 1s ease-out, stroke 0.5s ease-out' }}
          />
        </svg>
        {/* Center Text */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center'
        }}>
          <span style={{ fontSize: '1.75rem', fontWeight: '800', fontFamily: 'Outfit', color: 'var(--text-primary)' }}>
            {success}%
          </span>
          <span style={{ display: 'block', fontSize: '0.65rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '-4px' }}>
            Success
          </span>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', width: '100%' }}>
        <span className={`risk-badge ${level.toLowerCase()}`} style={{ alignSelf: 'center' }}>
          {level} Risk
        </span>
        
        <div style={{
          display: 'flex', 
          justifyContent: 'space-between', 
          width: '100%', 
          borderTop: '1px solid var(--meter-border-top)', 
          paddingTop: '12px',
          marginTop: '12px',
          fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Success Prob.</span>
            <span style={{ fontWeight: '600', color: 'var(--success)' }}>{success}%</span>
          </div>
          <div style={{ textAlign: 'right' }}>
            <span style={{ display: 'block', color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase' }}>Failure Risk</span>
            <span style={{ fontWeight: '600', color: color }}>{failure}%</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RiskMeter
