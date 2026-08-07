const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:5001/api'

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (res.status === 204) return null

  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = new Error(body.error ?? `Request failed (${res.status})`)
    err.status = res.status
    throw err
  }
  return body
}

export { request }

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
