const NETWORK_ERROR = 'No se pudo conectar con el servidor.'
const OPERATION_ERROR = 'No se pudo completar la operación. Intentá de nuevo.'

export class TaskApiError extends Error {
  constructor(message, status = null) {
    super(message)
    this.name = 'TaskApiError'
    this.status = status
  }
}

async function requestTasks(path, token, options = {}) {
  let response
  try {
    response = await fetch(path, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new TaskApiError(NETWORK_ERROR)
  }

  if (!response.ok) {
    throw new TaskApiError(OPERATION_ERROR, response.status)
  }
  if (response.status === 204) return null

  try {
    return await response.json()
  } catch {
    throw new TaskApiError(OPERATION_ERROR, response.status)
  }
}

export function getTasks(token, status = 'all') {
  return requestTasks(`/tasks?status=${encodeURIComponent(status)}`, token)
}

export function createTask(token, task) {
  return requestTasks('/tasks', token, {
    method: 'POST',
    body: JSON.stringify(task),
  })
}

export function updateTask(token, id, updates) {
  return requestTasks(`/tasks/${encodeURIComponent(id)}`, token, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  })
}

export function deleteTask(token, id) {
  return requestTasks(`/tasks/${encodeURIComponent(id)}`, token, { method: 'DELETE' })
}
