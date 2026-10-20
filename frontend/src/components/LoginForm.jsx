import { useState } from 'react'
import { validateLogin } from '../validation/validateLogin.js'

export default function LoginForm({ onLogin, loading, error }) {
  const [correo, setCorreo] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [showPassword, setShowPassword] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (loading) return
    const nextErrors = validateLogin({ correo, password })
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return
    await onLogin({ correo, password })
  }

  return <form onSubmit={handleSubmit} noValidate className="space-y-4" aria-label="Formulario de login">
    <div>
      <label htmlFor="correo" className="block mb-1 text-sm font-medium">Correo electrónico</label>
      <input id="correo" name="correo" autoComplete="username" type="email" value={correo}
        onChange={e => setCorreo(e.target.value)} aria-invalid={Boolean(errors.correo)}
        aria-describedby={errors.correo ? 'correo-error' : undefined}
        className="field w-full rounded-lg p-3" placeholder="admin@practica.com" />
      {errors.correo && <p id="correo-error" className="error mt-1 text-sm">{errors.correo}</p>}
    </div>
    <div>
      <label htmlFor="password" className="block mb-1 text-sm font-medium">Contraseña</label>
      <div className="flex gap-2">
        <input id="password" name="password" autoComplete="current-password"
          type={showPassword ? 'text' : 'password'} value={password}
          onChange={e => setPassword(e.target.value)} aria-invalid={Boolean(errors.password)}
          aria-describedby={errors.password ? 'password-error' : undefined}
          className="field w-full rounded-lg p-3" />
        <button type="button" className="field rounded-lg px-3" aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
          onClick={() => setShowPassword(v => !v)}>{showPassword ? '🙈' : '👁️'}</button>
      </div>
      {errors.password && <p id="password-error" className="error mt-1 text-sm">{errors.password}</p>}
    </div>
    {error && <p role="alert" className="error rounded-lg p-2 text-sm">{error}</p>}
    <button type="submit" disabled={loading} className="btn-primary w-full rounded-lg p-3 font-semibold">
      {loading ? 'Iniciando sesión…' : 'Iniciar sesión'}
    </button>
  </form>
}
