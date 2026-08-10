import { useEffect, useRef, useState } from 'react'

/**
 * @param {{
 *   todo: { id: number, title: string, completed: boolean },
 *   onToggle: (id: number) => void,
 *   onRemove: (id: number) => void,
 *   onUpdate: (id: number, patch: { title?: string, completed?: boolean }) => Promise<void>,
 * }} props
 */
export function TodoItem({ todo, onToggle, onRemove, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false)
  const [draftTitle, setDraftTitle] = useState(todo.title)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!isEditing) {
      setDraftTitle(todo.title)
      return
    }

    setDraftTitle(todo.title)
    const frame = requestAnimationFrame(() => {
      inputRef.current?.focus()
      inputRef.current?.select()
    })
    return () => cancelAnimationFrame(frame)
  }, [isEditing, todo.title])

  function startEditing() {
    setError(null)
    setDraftTitle(todo.title)
    setIsEditing(true)
  }

  function cancelEditing() {
    setError(null)
    setDraftTitle(todo.title)
    setIsEditing(false)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextTitle = draftTitle.trim()
    if (!nextTitle) {
      setError('Todo title cannot be empty.')
      return
    }
    if (nextTitle === todo.title) {
      cancelEditing()
      return
    }

    setSaving(true)
    setError(null)
    try {
      await onUpdate(todo.id, { title: nextTitle })
      setIsEditing(false)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  function handleKeyDown(event) {
    if (event.key !== 'Escape') return
    event.preventDefault()
    event.stopPropagation()
    cancelEditing()
  }

  return (
    <li className={`todo-item${todo.completed ? ' completed' : ''}`}>
      <label className="todo-label">
        <input
          type="checkbox"
          checked={todo.completed}
          onChange={() => onToggle(todo.id)}
          disabled={saving || isEditing}
          aria-label={`Mark "${todo.title}" as ${
            todo.completed ? 'incomplete' : 'complete'
          }`}
        />
        <span className="todo-title">{todo.title}</span>
      </label>

      {isEditing ? (
        <form className="todo-edit-form" onSubmit={handleSubmit} onKeyDown={handleKeyDown}>
          <label className="sr-only" htmlFor={`todo-edit-${todo.id}`}>
            Edit todo title
          </label>
          <input
            ref={inputRef}
            id={`todo-edit-${todo.id}`}
            className="todo-edit-input"
            type="text"
            value={draftTitle}
            onChange={(event) => setDraftTitle(event.target.value)}
            disabled={saving}
            aria-keyshortcuts="Escape"
          />
          <div className="todo-actions">
            <button type="submit" className="todo-save" disabled={saving}>
              {saving ? 'Saving…' : 'Save'}
            </button>
            <button
              type="button"
              className="todo-cancel"
              onClick={cancelEditing}
              disabled={saving}
              aria-label="Cancel edit and discard changes"
            >
              Cancel
            </button>
          </div>
        </form>
      ) : (
        <div className="todo-actions">
          <button
            type="button"
            className="todo-edit"
            onClick={startEditing}
            aria-label={`Edit "${todo.title}"`}
          >
            Edit
          </button>
          <button
            type="button"
            className="todo-delete"
            onClick={() => onRemove(todo.id)}
            aria-label={`Delete "${todo.title}"`}
          >
            Delete
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="todo-error">
          {error}
        </p>
      )}
    </li>
  )
}
