import { request } from './todos'

export function register(email, password, displayName) {
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      email,
      password,
      display_name: displayName,
    }),
  })
}

export function login(email, password) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function logout() {
  return request('/auth/logout', { method: 'POST' })
}

export function fetchMe() {
  return request('/auth/me')
}
