import { useState } from 'react'
import { loginApi } from '../api/authApi.js'

const GENERIC_LOGIN_ERROR = 'No se pudo iniciar sesión. Intentá de nuevo.'
const SAFE_LOGIN_ERRORS = new Set([
  'No se pudo conectar con el servidor.',
  'Correo o contraseña incorrectos.',
  GENERIC_LOGIN_ERROR,
])

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
      const message = SAFE_LOGIN_ERRORS.has(err?.message) ? err.message : GENERIC_LOGIN_ERROR
      setError(message)
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
