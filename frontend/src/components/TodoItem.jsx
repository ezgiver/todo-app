import { useEffect, useRef, useState } from 'react'
import {
  formatTodoDateTime,
  isTodoOverdue,
  toDatetimeLocalValue,
} from '../lib/todoDates'

/**
 * @param {{
 *   todo: {
 *     id: number,
 *     title: string,
 *     completed: boolean,
 *     due_at: string | null,
 *     created_at: string | null,
 *     updated_at: string | null,
 *   },
 *   onToggle: (id: number) => void,
 *   onRemove: (id: number) => void,
 *   onUpdate: (
 *     id: number,
 *     patch: { title?: string, completed?: boolean, due_at?: string | null },
 *   ) => Promise<void>,
 * }} props
 */
export function TodoItem({ todo, onToggle, onRemove, onUpdate }) {
  const [isEditing, setIsEditing] = useState(false)
  const [draftTitle, setDraftTitle] = useState(todo.title)
  const [draftDueAt, setDraftDueAt] = useState(toDatetimeLocalValue(todo.due_at))
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)

  useEffect(() => {
    if (!isEditing) {
      setDraftTitle(todo.title)
      setDraftDueAt(toDatetimeLocalValue(todo.due_at))
      return
    }

    setDraftTitle(todo.title)
    setDraftDueAt(toDatetimeLocalValue(todo.due_at))
    const frame = requestAnimationFrame(() => {
      inputRef.current?.focus()
      inputRef.current?.select()
    })
    return () => cancelAnimationFrame(frame)
  }, [isEditing, todo.title, todo.due_at])

  function startEditing() {
    setError(null)
    setDraftTitle(todo.title)
    setDraftDueAt(toDatetimeLocalValue(todo.due_at))
    setIsEditing(true)
  }

  function cancelEditing() {
    setError(null)
    setDraftTitle(todo.title)
    setDraftDueAt(toDatetimeLocalValue(todo.due_at))
    setIsEditing(false)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    const nextTitle = draftTitle.trim()
    const nextDueAt = draftDueAt || null
    const originalDueAt = toDatetimeLocalValue(todo.due_at)
    if (!nextTitle) {
      setError('Todo title cannot be empty.')
      return
    }
    if (nextTitle === todo.title && nextDueAt === originalDueAt) {
      cancelEditing()
      return
    }

    setSaving(true)
    setError(null)
    try {
      await onUpdate(todo.id, {
        title: nextTitle,
        due_at: nextDueAt,
      })
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

  const addedAt = formatTodoDateTime(todo.created_at)
  const updatedAt = formatTodoDateTime(todo.updated_at)
  const dueAt = formatTodoDateTime(todo.due_at)
  const overdue = isTodoOverdue(todo)
  const wasEdited =
    todo.created_at && todo.updated_at && todo.created_at !== todo.updated_at
  const metaItems = []

  if (addedAt) metaItems.push(`Added ${addedAt}`)
  if (wasEdited && updatedAt) metaItems.push(`Updated ${updatedAt}`)

  return (
    <li
      className={`todo-item${todo.completed ? ' completed' : ''} ${
        overdue ? ' overdue' : ''
      }`}
    >
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

      {metaItems.length > 0 || dueAt ? (
        <div className="todo-meta">
          {metaItems.map((item) => (
            <span key={item}>{item}</span>
          ))}
          {dueAt && (
            <span className={`todo-meta-due${overdue ? ' overdue' : ''}`}>
              {overdue ? 'Overdue · ' : 'Due · '}
              {dueAt}
            </span>
          )}
        </div>
      ) : null}

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
          <label className="todo-edit-field" htmlFor={`todo-due-${todo.id}`}>
            <span>Due date</span>
            <input
              id={`todo-due-${todo.id}`}
              className="todo-edit-input"
              type="datetime-local"
              value={draftDueAt}
              onChange={(event) => setDraftDueAt(event.target.value)}
              disabled={saving}
            />
          </label>
          {draftDueAt && (
            <button
              type="button"
              className="todo-clear"
              onClick={() => setDraftDueAt('')}
              disabled={saving}
            >
              Clear due date
            </button>
          )}
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
