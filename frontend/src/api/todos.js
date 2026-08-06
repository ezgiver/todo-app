const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5001/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (res.status === 204) return null

  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    throw new Error(body.error ?? `Request failed (${res.status})`)
  }
  return body
}

export function fetchTodos() {
  return request('/todos/')
}

export function createTodo(title) {
  return request('/todos/', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}

export function updateTodo(id, patch) {
  return request(`/todos/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(patch),
  })
}

export function deleteTodo(id) {
  return request(`/todos/${id}`, { method: 'DELETE' })
}
