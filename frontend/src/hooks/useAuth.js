import { useCallback, useEffect, useState } from 'react'
import * as api from '../api/auth'

export function useAuth() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    api
      .fetchMe()
      .then((me) => {
        if (!cancelled) setUser(me)
      })
      .catch((err) => {
        if (!cancelled && err.status !== 401) console.error(err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [])

  const login = useCallback(async (email, password) => {
    const me = await api.login(email, password)
    setUser(me)
  }, [])

  const register = useCallback(async (email, password, displayName) => {
    // Explicitly does NOT auto-login. Caller shows a "please sign in" message.
    await api.register(email, password, displayName)
  }, [])

  const logout = useCallback(async () => {
    await api.logout()
    setUser(null)
  }, [])

  const clearOn401 = useCallback(() => {
    setUser(null)
  }, [])

  return { user, loading, login, register, logout, clearOn401 }
}
