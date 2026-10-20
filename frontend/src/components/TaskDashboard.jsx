import TaskForm from './TaskForm.jsx'
import ThemeToggle from './ThemeToggle.jsx'
import { useTasks } from '../hooks/useTasks.js'

const FILTERS = [
  ['all', 'Todas'],
  ['pending', 'Pendientes'],
  ['completed', 'Completadas'],
]

function formatDate(date) {
  if (!date) return null
  return new Intl.DateTimeFormat('es-CO', { timeZone: 'UTC', dateStyle: 'medium' }).format(new Date(`${date}T00:00:00Z`))
}

export default function TaskDashboard({ session, onLogout, theme, onToggleTheme }) {
  const {
    tasks, filter, loading, submitting, pendingId, error,
    setFilter, loadTasks, addTask, toggleTask, removeTask,
  } = useTasks(session.token)

  return <main className="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
    <div className="mx-auto max-w-6xl">
      <header className="surface mb-6 flex flex-col gap-4 rounded-2xl border p-5 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-muted text-sm font-semibold">Evaluación 2</p>
          <h1 className="text-3xl font-bold">MiniTask</h1>
          <p className="mt-1">Bienvenido, <strong>{session.correo}</strong>.</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          <button onClick={onLogout} type="button" className="btn-secondary rounded-lg px-3 py-2 text-sm font-medium">Cerrar sesión</button>
        </div>
      </header>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(17rem,22rem)_1fr]">
        <TaskForm onCreate={addTask} loading={submitting} />
        <section className="surface min-w-0 rounded-2xl border p-5 shadow-sm" aria-labelledby="task-list-title">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 id="task-list-title" className="text-xl font-bold">Mis tareas</h2>
            <div className="filter-group flex" role="group" aria-label="Filtrar tareas">
              {FILTERS.map(([value, label]) => <button key={value} type="button"
                aria-pressed={filter === value} onClick={() => setFilter(value)}
                className="filter-button px-3 py-2 text-sm font-medium">{label}</button>)}
            </div>
          </div>

          {error && <div role="alert" className="error-panel mb-4 flex flex-col gap-2 rounded-lg p-3 text-sm sm:flex-row sm:items-center sm:justify-between">
            <span>{error}</span>
            <button type="button" className="underline" onClick={() => loadTasks(filter)}>Reintentar</button>
          </div>}

          {loading ? <p role="status" className="text-muted py-10 text-center">Cargando tareas…</p>
            : tasks.length === 0 ? <p className="text-muted rounded-xl border border-dashed p-10 text-center">No hay tareas para mostrar.</p>
              : <ul className="space-y-3">
                {tasks.map(task => {
                  const busy = pendingId === task.id
                  return <li key={task.id} className="task-card rounded-xl border p-4">
                    <div className="flex items-start gap-3">
                      <input id={`task-${task.id}`} type="checkbox" checked={task.completada}
                        disabled={busy} onChange={() => toggleTask(task)}
                        className="mt-1 h-5 w-5 accent-blue-700"
                        aria-label={`Marcar ${task.titulo} como ${task.completada ? 'pendiente' : 'completada'}`} />
                      <div className="min-w-0 flex-1">
                        <h3 className={`break-words font-semibold ${task.completada ? 'task-completed' : ''}`}>{task.titulo}</h3>
                        <p className="text-muted mt-1 whitespace-pre-wrap break-words text-sm">{task.descripcion}</p>
                        {task.fecha_limite && <p className="text-muted mt-2 text-xs">Fecha límite: <time dateTime={task.fecha_limite}>{formatDate(task.fecha_limite)}</time></p>}
                      </div>
                      <button type="button" disabled={busy} onClick={() => removeTask(task.id)}
                        className="btn-danger rounded-lg px-3 py-2 text-sm font-medium"
                        aria-label={`Eliminar ${task.titulo}`}>{busy ? 'Procesando…' : 'Eliminar'}</button>
                    </div>
                  </li>
                })}
              </ul>}
        </section>
      </div>
    </div>
  </main>
}
