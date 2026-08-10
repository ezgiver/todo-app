const DATE_TIME_FORMATTER = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
})

export function formatTodoDateTime(value) {
  if (!value) return null
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return null
  return DATE_TIME_FORMATTER.format(date)
}

export function toDatetimeLocalValue(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const offset = date.getTimezoneOffset()
  const local = new Date(date.getTime() - offset * 60_000)
  return local.toISOString().slice(0, 16)
}

export function isTodoOverdue(todo, now = Date.now()) {
  if (todo.completed || !todo.due_at) return false
  const dueAt = new Date(todo.due_at).getTime()
  return !Number.isNaN(dueAt) && dueAt < now
}
