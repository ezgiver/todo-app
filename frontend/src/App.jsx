import { AuthForm } from './components/AuthForm'
import { TodoForm } from './components/TodoForm'
import { TodoList } from './components/TodoList'
import { useAuth } from './hooks/useAuth'
import { useTodos } from './hooks/useTodos'

export default function App() {
  const { user, loading: authLoading, login, register, logout, clearOn401 } =
    useAuth()
  const { todos, loading, error, add, toggle, remove } = useTodos({
    enabled: !!user,
    onUnauthorized: clearOn401,
  })

  if (authLoading) {
    return (
      <main className="app">
        <p className="state">Loading…</p>
      </main>
    )
  }

  if (!user) {
    return <AuthForm onLogin={login} onRegister={register} />
  }

  const remaining = todos.filter((t) => !t.completed).length

  return (
    <main className="app">
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
      </header>

      <TodoForm onAdd={add} />

      <TodoList
        todos={todos}
        loading={loading}
        error={error}
        onToggle={toggle}
        onRemove={remove}
      />
    </main>
  )
}
