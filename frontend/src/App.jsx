import { TodoForm } from './components/TodoForm'
import { TodoList } from './components/TodoList'
import { useTodos } from './hooks/useTodos'

export default function App() {
  const { todos, loading, error, add, toggle, remove } = useTodos()

  const remaining = todos.filter((t) => !t.completed).length

  return (
    <main className="app">
      <header className="app-header">
        <h1>Todos</h1>
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
