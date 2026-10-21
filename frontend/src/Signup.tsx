import type { FormEvent } from 'react'
import { useState } from 'react'
import { registerUser } from './services/travelapi'

type SignupProps = {
  onSignup: () => void
  onBackToLogin: () => void
}

export default function Signup({
  onSignup,
  onBackToLogin,
}: SignupProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSignup = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await registerUser({
        name: name.trim(),
        email: email.trim(),
        password,
      })

      // Registration succeeded. The user must log in to get a token.
      onSignup()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to connect to the backend.'
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
        onSubmit={handleSignup}
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
          Create your account
        </p>

        <label>Name</label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
          minLength={2}
          required
          style={inputStyle}
        />

        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Enter your email"
          required
          style={inputStyle}
        />

        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Create a password"
          minLength={8}
          required
          style={inputStyle}
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
            marginTop: '12px',
            background: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            cursor: loading ? 'wait' : 'pointer',
          }}
        >
          {loading ? 'Creating account...' : 'Sign Up'}
        </button>

        <p style={{ textAlign: 'center', marginTop: '20px' }}>
          Already have an account?{' '}
          <button
            type="button"
            onClick={onBackToLogin}
            style={{
              background: 'none',
              border: 'none',
              color: '#2563eb',
              cursor: 'pointer',
              textDecoration: 'underline',
            }}
          >
            Back to Login
          </button>
        </p>
      </form>
    </div>
  )
}

const inputStyle = {
  display: 'block',
  width: '100%',
  padding: '12px',
  margin: '8px 0 18px',
  boxSizing: 'border-box' as const,
  border: '1px solid #cbd5e1',
  borderRadius: '8px',
}
