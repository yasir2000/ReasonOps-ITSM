export function LoadingSkeleton({ type = 'card' }: { type?: 'card' | 'table' | 'text' }) {
  if (type === 'card') {
    return (
      <div className="card" style={{ animation: 'pulse 1.5s ease-in-out infinite' }}>
        <div style={{ 
          height: '20px', 
          width: '40%', 
          background: 'var(--bg-tertiary)', 
          borderRadius: 'var(--radius-sm)',
          marginBottom: '12px' 
        }} />
        <div style={{ 
          height: '40px', 
          width: '60%', 
          background: 'var(--bg-tertiary)', 
          borderRadius: 'var(--radius-sm)',
          marginBottom: '8px' 
        }} />
        <div style={{ 
          height: '16px', 
          width: '50%', 
          background: 'var(--bg-tertiary)', 
          borderRadius: 'var(--radius-sm)' 
        }} />
      </div>
    )
  }

  if (type === 'table') {
    return (
      <div className="card">
        {[...Array(5)].map((_, i) => (
          <div 
            key={i}
            style={{ 
              height: '48px', 
              background: 'var(--bg-tertiary)', 
              borderRadius: 'var(--radius-sm)',
              marginBottom: '8px',
              animation: `pulse 1.5s ease-in-out ${i * 0.1}s infinite`
            }} 
          />
        ))}
      </div>
    )
  }

  return (
    <div style={{ 
      height: '20px', 
      width: '100%', 
      background: 'var(--bg-tertiary)', 
      borderRadius: 'var(--radius-sm)',
      animation: 'pulse 1.5s ease-in-out infinite'
    }} />
  )
}

export function CardGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <div className="cards">
      {[...Array(count)].map((_, i) => (
        <LoadingSkeleton key={i} type="card" />
      ))}
    </div>
  )
}
