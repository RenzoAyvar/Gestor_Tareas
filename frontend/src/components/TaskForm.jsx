import { useState } from 'react'
import { validateTask } from '../validation/validateTask.js'

const INITIAL_TASK = { titulo: '', descripcion: '', fecha_limite: '' }

export default function TaskForm({ onCreate, loading = false }) {
  const [values, setValues] = useState(INITIAL_TASK)
  const [errors, setErrors] = useState({})

  function updateField(event) {
    const { name, value } = event.target
    setValues(current => ({ ...current, [name]: value }))
    setErrors(current => ({ ...current, [name]: undefined }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (loading) return
    const nextErrors = validateTask(values)
    setErrors(nextErrors)
    if (Object.keys(nextErrors).length > 0) return

    const payload = {
      titulo: values.titulo.trim(),
      descripcion: values.descripcion.trim(),
      fecha_limite: values.fecha_limite || null,
    }
    if (await onCreate(payload)) {
      setValues(INITIAL_TASK)
      setErrors({})
    }
  }

  return <form onSubmit={handleSubmit} noValidate className="task-form surface rounded-2xl border p-5 shadow-sm" aria-labelledby="new-task-title">
    <h2 id="new-task-title" className="text-xl font-bold">Nueva tarea</h2>
    <div>
      <label htmlFor="task-title" className="mb-1 block text-sm font-medium">Título</label>
      <input id="task-title" name="titulo" value={values.titulo} onChange={updateField}
        maxLength={120} aria-invalid={Boolean(errors.titulo)}
        aria-describedby={errors.titulo ? 'task-title-error' : undefined}
        className="field w-full rounded-lg p-3" />
      {errors.titulo && <p id="task-title-error" className="error mt-1 text-sm">{errors.titulo}</p>}
    </div>
    <div>
      <label htmlFor="task-description" className="mb-1 block text-sm font-medium">Descripción</label>
      <textarea id="task-description" name="descripcion" value={values.descripcion} onChange={updateField}
        maxLength={1000} rows={4} aria-invalid={Boolean(errors.descripcion)}
        aria-describedby={errors.descripcion ? 'task-description-error' : undefined}
        className="field w-full resize-y rounded-lg p-3" />
      {errors.descripcion && <p id="task-description-error" className="error mt-1 text-sm">{errors.descripcion}</p>}
    </div>
    <div>
      <label htmlFor="task-due-date" className="mb-1 block text-sm font-medium">Fecha límite <span className="text-muted">(opcional)</span></label>
      <input id="task-due-date" name="fecha_limite" type="date" value={values.fecha_limite} onChange={updateField}
        aria-invalid={Boolean(errors.fecha_limite)} aria-describedby={errors.fecha_limite ? 'task-date-error' : undefined}
        className="field w-full rounded-lg p-3" />
      {errors.fecha_limite && <p id="task-date-error" className="error mt-1 text-sm">{errors.fecha_limite}</p>}
    </div>
    <button type="submit" disabled={loading} className="btn-primary w-full rounded-lg p-3 font-semibold">
      {loading ? 'Guardando tarea…' : 'Agregar tarea'}
    </button>
  </form>
}
