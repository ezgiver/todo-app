import { useRef, useState } from 'react'
import { suggestSteps } from '../api/assistant'
const valid = (s) => s.trim().length > 0 && [...s.trim()].length <= 120

export function NextStep({ onAdd, onUnauthorized }) {
  const [task, setTask] = useState('')
  const [steps, setSteps] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const pending = useRef(false)
  function failure(err) {
    if (err.status === 401) onUnauthorized()
    else setError(err.name === 'TimeoutError' ? 'This took too long. Please try again.' : err.message)
  }
  async function generate(event) {
    event.preventDefault()
    if (pending.current) return
    pending.current = true
    setBusy(true); setError(''); setSteps([])
    try {
      const result = await suggestSteps(task.trim())
      setSteps(result.steps.map((step) => ({ ...step, saved: false })))
    } catch (err) { failure(err) }
    finally { pending.current = false; setBusy(false) }
  }
  function edit(index, field, value) {
    setSteps((previous) => previous.map((step, i) => i === index ? { ...step, [field]: value } : step))
    setError('')
  }
  async function save(index) {
    const step = steps[index]
    if (pending.current || step.saved) return
    if (!valid(step.action) || !valid(step.done_when)) { setError('Each field needs 1–120 characters.'); return }
    pending.current = true
    setBusy(true); setError('')
    try {
      await onAdd(`${step.action.trim()} — Done when: ${step.done_when.trim()}`)
      setSteps((previous) => previous.map((item, i) => i === index ? { ...item, saved: true } : item))
    } catch (err) { failure(err) }
    finally { pending.current = false; setBusy(false) }
  }
  return (
    <section className="next-step" aria-labelledby="next-step-heading">
      <h2 id="next-step-heading">Help me start</h2>
      <p>Break a task into up to three small steps. Edit them before adding to your list.</p>
      <form onSubmit={generate}>
        <label htmlFor="stuck-task">What are you finding hard to start?</label>
        <textarea id="stuck-task" value={task} maxLength={1000} required disabled={busy} rows={3}
          placeholder="For example: start working on my app"
          onChange={(event) => { setTask(event.target.value); setSteps([]); setError('') }} />
        <button disabled={busy || !task.trim()} type="submit">Suggest steps</button>
      </form>
      <p role="status" aria-live="polite">
        {busy ? (steps.length ? 'Saving your step…' : 'Finding steps. This may take a minute.') : ''}
        {!busy && steps.length > 0 ? `${steps.length} suggested steps. ${steps.filter((step) => step.saved).length} added to your list.` : ''}
      </p>
      {steps.map((step, index) => (
        <fieldset className="next-step-result" key={index} disabled={busy || step.saved}>
          <legend>Step {index + 1}{step.saved ? ' — Added to your list' : ''}</legend>
          <label htmlFor={`action-${index}`}>Action</label>
          <textarea id={`action-${index}`} value={step.action} maxLength={120} rows={2}
            onChange={(event) => edit(index, 'action', event.target.value)} />
          <label htmlFor={`finish-${index}`}>Done when</label>
          <textarea id={`finish-${index}`} value={step.done_when} maxLength={120} rows={2}
            onChange={(event) => edit(index, 'done_when', event.target.value)} />
          <button type="button" onClick={() => save(index)}
            disabled={busy || step.saved || !valid(step.action) || !valid(step.done_when)}>
            {step.saved ? 'Added to your list' : `Add step ${index + 1} to my list`}
          </button>
        </fieldset>
      ))}
      {error && <p role="alert">{error}</p>}
    </section>
  )
}
