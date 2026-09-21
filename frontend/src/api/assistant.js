import { request } from './todos'

export function suggestStep(task) {
  return request('/assistant/next-step', {
    method: 'POST',
    body: JSON.stringify({ task }),
    signal: AbortSignal.timeout(100000),
  })
}

export function suggestSteps(task, blocker = "", availableMinutes = "") {
  return request('/assistant/steps', {
    method: 'POST',
    body: JSON.stringify({ task, blocker, ...(availableMinutes === "" ? {} : { available_minutes: Number(availableMinutes) }) }),
    signal: AbortSignal.timeout(100000),
  })
}
