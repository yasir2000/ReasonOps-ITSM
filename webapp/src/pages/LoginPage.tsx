import { useState } from 'react'
import { useAuth } from '../auth/AuthContext'
import { useNavigate } from 'react-router-dom'

export default function LoginPage() {
  const [name, setName] = useState('user@example.com')
  const [roles, setRoles] = useState('slm,finance,ops')
  const auth = useAuth()
  const nav = useNavigate()

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const list = roles.split(',').map(r => r.trim()).filter(Boolean)
    auth.login(name, list)
    nav('/')
  }

  return (
    <div style={{ maxWidth: 520 }}>
      <h2>Login</h2>
      <p>Temporary auth scaffold. Configure OAuth later and map provider roles to app roles.</p>
      <form onSubmit={onSubmit} className="card" style={{ display:'grid', gap: 8 }}>
        <label>
          <div className="label">Email</div>
          <input value={name} onChange={e => setName(e.target.value)} />
        </label>
        <label>
          <div className="label">Roles (comma-separated)</div>
          <input value={roles} onChange={e => setRoles(e.target.value)} />
        </label>
        <button type="submit">Login</button>
      </form>
    </div>
  )
}
