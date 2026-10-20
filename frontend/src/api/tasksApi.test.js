import { afterEach, describe, expect, it, vi } from 'vitest'
import { createTask, deleteTask, getTasks, updateTask } from './tasksApi.js'

afterEach(() => vi.unstubAllGlobals())

describe('tasksApi', () => {
  it('envía Bearer y serializa las operaciones', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => [] })
      .mockResolvedValueOnce({ ok: true, status: 201, json: async () => ({ id: '1' }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ id: '1', completada: true }) })
      .mockResolvedValueOnce({ ok: true, status: 204 })
    vi.stubGlobal('fetch', fetchMock)

    await getTasks('jwt', 'pending')
    await createTask('jwt', { titulo: 'T', descripcion: 'D', fecha_limite: null })
    await updateTask('jwt', '1', { completada: true })
    await deleteTask('jwt', '1')

    expect(fetchMock.mock.calls[0]).toEqual(['/tasks?status=pending', expect.objectContaining({
      headers: expect.objectContaining({ Authorization: 'Bearer jwt' }),
    })])
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({ titulo: 'T', descripcion: 'D', fecha_limite: null })
    expect(fetchMock.mock.calls[2][1].method).toBe('PATCH')
    expect(fetchMock.mock.calls[3][1].method).toBe('DELETE')
  })

  it('mapea red y respuestas inválidas a errores seguros', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValueOnce(new Error('interno')))
    await expect(getTasks('jwt')).rejects.toThrow('No se pudo conectar con el servidor.')

    fetch.mockResolvedValueOnce({ ok: false, status: 401 })
    await expect(getTasks('jwt')).rejects.toThrow('No se pudo completar la operación. Intentá de nuevo.')
  })
})
