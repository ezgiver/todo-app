import { useState } from 'react'
import { PasswordStrength } from './PasswordStrength'

/**
 * @param {{
 *   onLogin: (email: string, password: string) => Promise<void>,
 *   onRegister: (email: string, password: string, displayName: string) => Promise<void>,
 * }} props
 */
export function AuthForm({ onLogin, onRegister }) {
  const [mode, setMode] = useState('login')
  const [email, setEmail] = useState('')
  const [displayName, setDisplayName] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [flash, setFlash] = useState(null)

  const isRegister = mode === 'register'
  const passwordsMatch = !isRegister || password === confirm
  const passwordTooShort = isRegister && password.length > 0 && password.length < 12

  function switchMode(next) {
    setError(null)
    setFlash(null)
    setPassword('')
    setConfirm('')
    setMode(next)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setFlash(null)

    if (isRegister) {
      if (!passwordsMatch) {
        setError('Passwords do not match.')
        return
      }
      if (password.length < 12) {
        setError('Password must be at least 12 characters.')
        return
      }
      if (password.toLowerCase() === email.toLowerCase()) {
        setError('Password cannot equal your email.')
        return
      }
    }

    setSubmitting(true)
    try {
      if (isRegister) {
        await onRegister(email, password, displayName.trim())
        // No auto-login — bounce user to sign-in with email prefilled.
        setMode('login')
        setPassword('')
        setConfirm('')
        setFlash('Account created. Please sign in.')
      } else {
        await onLogin(email, password)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  const submitDisabled =
    submitting ||
    !email ||
    !password ||
    (isRegister && (!displayName.trim() || !passwordsMatch || passwordTooShort))

  return (
    <main className="app">
      <header className="app-header">
        <h1>{isRegister ? 'Create account' : 'Sign in'}</h1>
        <p className="subtitle">
          {isRegister ? 'It only takes an email.' : 'Welcome back.'}
        </p>
      </header>

      {flash && (
        <p className="flash" role="status">
          {flash}
        </p>
      )}

      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          <span>Email</span>
          <input
            type="email"
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={submitting}
          />
        </label>

        {isRegister && (
          <label>
            <span>Display name</span>
            <input
              type="text"
              autoComplete="nickname"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              maxLength={50}
              required
              disabled={submitting}
            />
          </label>
        )}

        <label>
          <span>Password</span>
          <input
            type="password"
            autoComplete={isRegister ? 'new-password' : 'current-password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            minLength={isRegister ? 12 : undefined}
            disabled={submitting}
          />
          {isRegister && password && (
            <PasswordStrength password={password} email={email} />
          )}
          {isRegister && !password && (
            <small className="hint">At least 12 characters.</small>
          )}
        </label>

        {isRegister && (
          <label>
            <span>Confirm password</span>
            <input
              type="password"
              autoComplete="new-password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              disabled={submitting}
            />
            {confirm && !passwordsMatch && (
              <small className="hint hint-error">Passwords do not match.</small>
            )}
          </label>
        )}

        <button type="submit" disabled={submitDisabled}>
          {submitting
            ? isRegister
              ? 'Creating…'
              : 'Signing in…'
            : isRegister
              ? 'Create account'
              : 'Sign in'}
        </button>

        {error && (
          <p role="alert" className="form-error">
            {error}
          </p>
        )}
      </form>

      <p className="auth-switch">
        {isRegister ? 'Already have an account?' : 'New here?'}{' '}
        <button
          type="button"
          className="link-button"
          onClick={() => switchMode(isRegister ? 'login' : 'register')}
        >
          {isRegister ? 'Sign in' : 'Create an account'}
        </button>
      </p>
    </main>
  )
}
