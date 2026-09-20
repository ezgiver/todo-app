import { request } from './todos'

export function suggestStep(task) {
  return request('/assistant/next-step', {
    method: 'POST',
    body: JSON.stringify({ task }),
    signal: AbortSignal.timeout(100000),
  })
}
