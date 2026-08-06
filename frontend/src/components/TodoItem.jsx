/**
 * @param {{
 *   todo: { id: number, title: string, completed: boolean },
 *   onToggle: (id: number) => void,
 *   onRemove: (id: number) => void,
 * }} props
 */
export function TodoItem({ todo, onToggle, onRemove }) {
  return (
    <li className={`todo-item${todo.completed ? ' completed' : ''}`}>
      <label className="todo-label">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id)}
          aria-label={`Mark "${todo.title}" as ${
            todo.completed ? 'incomplete' : 'complete'
          }`}
        />
        <span className="todo-title">{todo.title}</span>
      </label>
      <button
        type="button"
        className="todo-delete"
        onClick={() => onRemove(todo.id)}
        aria-label={`Delete "${todo.title}"`}
      >
        ×
      </button>
    </li>
  )
}
