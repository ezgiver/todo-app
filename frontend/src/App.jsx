import { useMemo, useState } from 'react'
import { AuthForm } from './components/AuthForm'
import { TodoForm } from './components/TodoForm'
import { TodoList } from './components/TodoList'
import { useAuth } from './hooks/useAuth'
import { useTodos } from './hooks/useTodos'

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest first' },
  { value: 'oldest', label: 'Oldest first' },
  { value: 'completed', label: 'Completed first' },
]

function sortTodos(todos, sortOrder) {
  const withFallback = [...todos]

  if (sortOrder === 'oldest') {
    return withFallback.sort((a, b) => {
      const dateDiff =
        new Date(a.created_at ?? 0).getTime() -
        new Date(b.created_at ?? 0).getTime()
      return dateDiff || a.id - b.id
    })
  }

  if (sortOrder === 'completed') {
    return withFallback.sort((a, b) => {
      if (a.completed !== b.completed) return Number(b.completed) - Number(a.completed)
      const dateDiff =
        new Date(b.created_at ?? 0).getTime() -
        new Date(a.created_at ?? 0).getTime()
      return dateDiff || b.id - a.id
    })
  }

  return withFallback.sort((a, b) => {
    const dateDiff =
      new Date(b.created_at ?? 0).getTime() - new Date(a.created_at ?? 0).getTime()
    return dateDiff || b.id - a.id
  })
}

export default function App() {
  const { user, loading: authLoading, login, register, logout, clearOn401 } =
    useAuth()
  const { todos, loading, error, add, update, toggle, remove } = useTodos({
    enabled: !!user,
    onUnauthorized: clearOn401,
  })
  const [sortOrder, setSortOrder] = useState('newest')
  const visibleTodos = useMemo(
    () => sortTodos(todos, sortOrder),
    [todos, sortOrder],
  )

  if (authLoading) {
    return (
      <main className="app">
        <p className="state" role="status" aria-live="polite">
          Loading…
        </p>
      </main>
    )
  }

  if (!user) {
    return <AuthForm onLogin={login} onRegister={register} />
  }

  const remaining = todos.filter((t) => !t.completed).length
  const completed = todos.length - remaining

  return (
    <main className="app" aria-busy={loading}>
      <header className="app-header">
        <div className="header-row">
          <h1>Hi {user.display_name || user.email}!</h1>
          <button type="button" className="link-button" onClick={logout}>
            Sign out
          </button>
        </div>
        <p className="subtitle">
          {loading
            ? 'Loading your list…'
            : `${remaining} remaining · ${todos.length} total`}
        </p>
        <p className="app-help">
          Click Edit to change a task. Click Save to keep it. Click Cancel or
          press Esc to discard the change. Use Sort to change task order, and
          set a due date to see overdue tasks.
        </p>
      </header>

      <TodoForm onAdd={add} />

      <div className="todo-toolbar">
        <label className="sort-control" htmlFor="todo-sort">
          <span>Sort</span>
          <select
            id="todo-sort"
            value={sortOrder}
            onChange={(event) => setSortOrder(event.target.value)}
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <section className="todo-summary" aria-label="Todo summary">
        <span>{remaining} left</span>
        <span>{completed} done</span>
        <span>{todos.length} total</span>
      </section>

      <TodoList
        todos={visibleTodos}
        loading={loading}
        error={error}
        onToggle={toggle}
        onRemove={remove}
        onUpdate={update}
      />
    </main>
  )
}
