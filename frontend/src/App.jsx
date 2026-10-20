import LoginForm from './components/LoginForm.jsx'
import ThemeToggle from './components/ThemeToggle.jsx'
import { useLogin } from './hooks/useLogin.js'
import { useTheme } from './hooks/useTheme.js'

export default function App() {
  const { session, loading, error, login, logout } = useLogin()
  const { theme, toggleTheme } = useTheme()
  return <main className="min-h-screen flex items-center justify-center px-4 py-10">
    <section className="surface w-full max-w-md rounded-2xl border p-8 shadow-lg" style={{ borderColor: 'var(--border)' }}>
      <div className="mb-6 flex justify-between items-center">
        <span className="text-sm font-semibold text-muted">Evaluación 2</span>
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </div>
      {session ? <>
        <h1 className="text-2xl font-bold">Planificador de Visitas</h1>
        <p className="my-4">Bienvenido, <strong>{session.correo}</strong>.</p>
        <p className="text-muted text-sm mb-6">Vista de bienvenida temporal. El Planificador real corresponde a la SPEC 008.</p>
        <button onClick={logout} type="button" className="btn-primary rounded-lg px-4 py-3">Cerrar sesión</button>
      </> : <>
        <h1 className="mb-2 text-2xl font-bold">Iniciar sesión</h1>
        <p className="text-muted mb-6 text-sm">Ingresa tu correo y contraseña.</p>
        <LoginForm onLogin={login} loading={loading} error={error} />
      </>}
    </section>
  </main>
}
