import { useCallback, useEffect, useState } from 'react'
import * as api from '../api/todos'

export function useTodos() {
  const [todos, setTodos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await api.fetchTodos()
      setTodos(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const add = useCallback(async (title) => {
    const created = await api.createTodo(title)
    setTodos((prev) => [created, ...prev])
  }, [])

  const toggle = useCallback(
    async (id) => {
      const current = todos.find((t) => t.id === id)
      if (!current) return
      const updated = await api.updateTodo(id, { completed: !current.completed })
      setTodos((prev) => prev.map((t) => (t.id === id ? updated : t)))
    },
    [todos],
  )

  const remove = useCallback(async (id) => {
    await api.deleteTodo(id)
    setTodos((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return { todos, loading, error, add, toggle, remove, reload: load }
}
