import type { FormEvent } from 'react'
import { useState } from 'react'
import { loginUser, saveAccessToken } from './services/travelapi'

type LoginProps = {
  onLogin: () => void
  onShowSignup: () => void
  notice: string
}

export default function Login({ onLogin, onShowSignup, notice }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleLogin = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const result = await loginUser({ email: email.trim(), password })
      if (!result.access_token) {
        throw new Error('Login succeeded, but no access token was returned.')
      }

      saveAccessToken(result.access_token)
      onLogin()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Unable to connect to backend.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #dbeafe, #e0f2fe)',
        fontFamily: 'Arial, sans-serif',
        padding: '20px',
      }}
    >
      <form
        onSubmit={handleLogin}
        style={{
          background: 'white',
          padding: '35px',
          borderRadius: '18px',
          width: '100%',
          maxWidth: '360px',
          boxShadow: '0 8px 30px rgba(0,0,0,0.1)',
        }}
      >
        <h1 style={{ textAlign: 'center', color: '#1d4ed8' }}>
          ✈️ AI Travel Planner
        </h1>

        <p style={{ textAlign: 'center', color: '#64748b' }}>
          Login to plan your next trip
        </p>

        {notice && (
          <p role="status" style={{ color: '#b45309' }}>
            {notice}
          </p>
        )}

        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          style={{
            display: 'block',
            width: '100%',
            padding: '12px',
            margin: '8px 0 18px',
            boxSizing: 'border-box',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
          }}
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your password"
          minLength={8}
          required
          style={{
            display: 'block',
            width: '100%',
            padding: '12px',
            margin: '8px 0 22px',
            boxSizing: 'border-box',
            border: '1px solid #cbd5e1',
            borderRadius: '8px',
          }}
        />

        {error && (
          <p role="alert" style={{ color: '#dc2626' }}>
            {error}
          </p>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: '13px',
            background: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: loading ? 'wait' : 'pointer',
          }}
        >
          {loading ? 'Logging in...' : 'Login'}
        </button>

        <p
          style={{
            textAlign: 'center',
            fontSize: '12px',
            color: '#64748b',
            marginTop: '20px',
          }}
        >
          AI-powered travel planning made easy
        </p>

        <p
          style={{
            textAlign: 'center',
            marginTop: '12px',
            color: '#2563eb',
          }}
        >
          New user?{' '}
          <button
            type="button"
            onClick={onShowSignup}
            style={{
              background: 'none',
              border: 'none',
              color: '#2563eb',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            Sign Up
          </button>
        </p>
      </form>
    </div>
  )
}
