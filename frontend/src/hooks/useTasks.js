import { useCallback, useEffect, useState } from 'react'
import { createTask, deleteTask, getTasks, updateTask } from '../api/tasksApi.js'

const OPERATION_ERROR = 'No se pudo completar la operación. Intentá de nuevo.'
const SAFE_ERRORS = new Set(['No se pudo conectar con el servidor.', OPERATION_ERROR])

function safeMessage(error) {
  return SAFE_ERRORS.has(error?.message) ? error.message : OPERATION_ERROR
}

export function useTasks(token) {
  const [tasks, setTasks] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [pendingId, setPendingId] = useState(null)
  const [error, setError] = useState('')

  const loadTasks = useCallback(async (status = filter) => {
    setLoading(true)
    setError('')
    try {
      const result = await getTasks(token, status)
      setTasks(Array.isArray(result) ? result : [])
      return true
    } catch (err) {
      setError(safeMessage(err))
      return false
    } finally {
      setLoading(false)
    }
  }, [filter, token])

  useEffect(() => {
    loadTasks(filter)
  }, [filter, loadTasks])

  const addTask = async (task) => {
    setSubmitting(true)
    setError('')
    try {
      await createTask(token, task)
      await loadTasks(filter)
      return true
    } catch (err) {
      setError(safeMessage(err))
      return false
    } finally {
      setSubmitting(false)
    }
  }

  const toggleTask = async (task) => {
    setPendingId(task.id)
    setError('')
    try {
      await updateTask(token, task.id, { completada: !task.completada })
      await loadTasks(filter)
      return true
    } catch (err) {
      setError(safeMessage(err))
      return false
    } finally {
      setPendingId(null)
    }
  }

  const removeTask = async (id) => {
    setPendingId(id)
    setError('')
    try {
      await deleteTask(token, id)
      await loadTasks(filter)
      return true
    } catch (err) {
      setError(safeMessage(err))
      return false
    } finally {
      setPendingId(null)
    }
  }

  return {
    tasks,
    filter,
    loading,
    submitting,
    pendingId,
    error,
    setFilter,
    loadTasks,
    addTask,
    toggleTask,
    removeTask,
  }
}
