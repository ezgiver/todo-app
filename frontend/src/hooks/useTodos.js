import { useCallback, useEffect, useState } from 'react'
import * as api from '../api/todos'

export function useTodos({ enabled = true, onUnauthorized } = {}) {
  const [todos, setTodos] = useState([])
  const [loading, setLoading] = useState(enabled)
  const [error, setError] = useState(null)

  const handle = useCallback(
    (err) => {
      if (err.status === 401 && onUnauthorized) {
        onUnauthorized()
        return
      }
      setError(err.message)
    },
    [onUnauthorized],
  )

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.fetchTodos()
      setTodos(data)
    } catch (err) {
      handle(err)
    } finally {
      setLoading(false)
    }
  }, [handle])

  useEffect(() => {
    if (enabled) load()
  }, [enabled, load])

  const add = useCallback(
    async (title) => {
      try {
        const created = await api.createTodo(title)
        setTodos((prev) => [created, ...prev])
      } catch (err) {
        handle(err)
        throw err
      }
    },
    [handle],
  )

  const toggle = useCallback(
    async (id) => {
      const current = todos.find((t) => t.id === id)
      if (!current) return
      try {
        const updated = await api.updateTodo(id, {
          completed: !current.completed,
        })
        setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)))
      } catch (err) {
        handle(err)
      }
    },
    [todos, handle],
  )

  const remove = useCallback(
    async (id) => {
      try {
        await api.deleteTodo(id)
        setTodos((prev) => prev.filter((t) => t.id !== id))
      } catch (err) {
        handle(err)
      }
    },
    [handle],
  )

  return { todos, loading, error, add, toggle, remove, reload: load }
}
