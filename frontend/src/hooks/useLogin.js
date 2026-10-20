import { useState } from 'react'
import { loginApi } from '../api/authApi.js'

export function useLogin() {
  const [session, setSession] = useState(null) // JWT vive solo en memoria de React.
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const login = async (credentials) => {
    setLoading(true)
    setError('')
    try {
      const result = await loginApi(credentials)
      setSession(result)
      return true
    } catch (err) {
      setError(err.message || 'No se pudo iniciar sesión. Intentá de nuevo.')
      return false
    } finally {
      setLoading(false)
    }
  }

  const logout = () => {
    setSession(null)
    setError('')
  }
  return { session, loading, error, login, logout }
}
