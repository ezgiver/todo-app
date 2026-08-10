import { useState } from 'react'

/**
 * @param {{ onAdd: (title: string, dueAt?: string | null) => Promise<void> }} props
 */
export function TodoForm({ onAdd }) {
  const [title, setTitle] = useState('')
  const [dueAt, setDueAt] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    const trimmed = title.trim()
    if (!trimmed) return
    setSubmitting(true)
    setError(null)
    try {
      await onAdd(trimmed, dueAt || null)
      setTitle('')
      setDueAt('')
    } catch (err) {
      setError(err.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <form className="todo-form" onSubmit={handleSubmit}>
      <label className="sr-only" htmlFor="new-todo">
        New todo
      </label>
      <input
        id="new-todo"
        type="text"
        placeholder="What needs to be done?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        disabled={submitting}
        autoFocus
        aria-describedby="new-todo-hint"
      />
      <label htmlFor="new-todo-due" className="todo-form-field">
        <span className="todo-form-label">
          <span>Due date</span>
          <small>(optional)</small>
        </span>
        <input
          id="new-todo-due"
          type="datetime-local"
          value={dueAt}
          onChange={(e) => setDueAt(e.target.value)}
          disabled={submitting}
        />
      </label>
      <button type="submit" disabled={submitting || !title.trim()}>
        {submitting ? 'Adding…' : 'Add'}
      </button>
      <p id="new-todo-hint" className="form-hint">
        Press Enter to add a task quickly. Due date is optional.
      </p>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
    </form>
  )
}
