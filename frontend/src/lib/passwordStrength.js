/** Cheap client-side strength score in [0, 100]. Not a substitute for server validation. */
export function scorePassword(password, email = '') {
  if (!password) return 0
  if (email && password.toLowerCase() === email.toLowerCase()) return 5

  let score = Math.min(50, password.length * 3)

  const classes = [
    /[a-z]/.test(password),
    /[A-Z]/.test(password),
    /[0-9]/.test(password),
    /[^a-zA-Z0-9]/.test(password),
  ].filter(Boolean).length

  score += (classes - 1) * 10

  const uniqueRatio = new Set(password).size / password.length
  score += Math.round(uniqueRatio * 20)

  return Math.max(0, Math.min(100, score))
}
