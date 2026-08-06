import { TodoItem } from './TodoItem'

/**
 * @param {{
 *   todos: Array<{ id: number, title: string, completed: boolean }>,
 *   loading: boolean,
 *   error: string | null,
 *   onToggle: (id: number) => void,
 *   onRemove: (id: number) => void,
 * }} props
 */
export function TodoList({ todos, loading, error, onToggle, onRemove }) {
  if (loading) return <p className="state">Loading…</p>
  if (error) {
    return (
      <p role="alert" className="state state-error">
        {error}
      </p>
    )
  }
  if (todos.length === 0) {
    return <p className="state">No todos yet — add one above.</p>
  }

  return (
    <ul className="todo-list">
      {todos.map((todo) => (
        <TodoItem
          key={todo.id}
          todo={todo}
          onToggle={onToggle}
          onRemove={onRemove}
        />
      ))}
    </ul>
  )
}
