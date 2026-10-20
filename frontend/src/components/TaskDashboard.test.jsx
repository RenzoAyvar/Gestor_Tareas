import { beforeEach, describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import TaskDashboard from './TaskDashboard.jsx'
import * as tasksApi from '../api/tasksApi.js'

vi.mock('../api/tasksApi.js', () => ({
  getTasks: vi.fn(),
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
}))

const session = { correo: 'student@example.com', token: 'jwt' }
const task = {
  id: 'task-1', titulo: 'Leer capítulo', descripcion: 'Preparar resumen',
  fecha_limite: '2026-10-30', completada: false, creada_en: '2026-10-20T12:00:00Z',
}

function renderDashboard() {
  return render(<TaskDashboard session={session} onLogout={vi.fn()} theme="light" onToggleTheme={vi.fn()} />)
}

beforeEach(() => {
  tasksApi.getTasks.mockReset().mockResolvedValue([])
  tasksApi.createTask.mockReset().mockResolvedValue(task)
  tasksApi.updateTask.mockReset().mockResolvedValue({ ...task, completada: true })
  tasksApi.deleteTask.mockReset().mockResolvedValue(null)
})

describe('TaskDashboard', () => {
  it('crea una tarea válida y actualiza la lista', async () => {
    tasksApi.getTasks.mockResolvedValueOnce([]).mockResolvedValueOnce([task])
    renderDashboard()
    await screen.findByText('No hay tareas para mostrar.')

    fireEvent.change(screen.getByLabelText('Título'), { target: { value: task.titulo } })
    fireEvent.change(screen.getByLabelText('Descripción'), { target: { value: task.descripcion } })
    fireEvent.click(screen.getByRole('button', { name: 'Agregar tarea' }))

    await waitFor(() => expect(tasksApi.createTask).toHaveBeenCalledWith('jwt', {
      titulo: task.titulo, descripcion: task.descripcion, fecha_limite: null,
    }))
    expect(await screen.findByText(task.titulo)).toBeInTheDocument()
  })

  it('no llama al backend con una tarea inválida', async () => {
    renderDashboard()
    await screen.findByText('No hay tareas para mostrar.')
    fireEvent.click(screen.getByRole('button', { name: 'Agregar tarea' }))
    expect(screen.getByText('El título es obligatorio.')).toBeInTheDocument()
    expect(screen.getByText('La descripción es obligatoria.')).toBeInTheDocument()
    expect(tasksApi.createTask).not.toHaveBeenCalled()
  })

  it('filtra tareas por estado', async () => {
    renderDashboard()
    await screen.findByText('No hay tareas para mostrar.')
    fireEvent.click(screen.getByRole('button', { name: 'Completadas' }))
    await waitFor(() => expect(tasksApi.getTasks).toHaveBeenLastCalledWith('jwt', 'completed'))
  })

  it('alterna una tarea entre completada y pendiente', async () => {
    tasksApi.getTasks.mockResolvedValue([task])
    renderDashboard()
    fireEvent.click(await screen.findByRole('checkbox', { name: `Marcar ${task.titulo} como completada` }))
    await waitFor(() => expect(tasksApi.updateTask).toHaveBeenCalledWith('jwt', task.id, { completada: true }))
  })

  it('elimina una tarea', async () => {
    tasksApi.getTasks.mockResolvedValue([task])
    renderDashboard()
    fireEvent.click(await screen.findByRole('button', { name: `Eliminar ${task.titulo}` }))
    await waitFor(() => expect(tasksApi.deleteTask).toHaveBeenCalledWith('jwt', task.id))
  })
})
