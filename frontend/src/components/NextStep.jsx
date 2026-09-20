import { useState } from 'react'
import { suggestStep } from '../api/assistant'

export function NextStep({ onAdd, onUnauthorized }) {
  const [task, setTask] = useState('')
  const [step, setStep] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [saved, setSaved] = useState(false)

  async function generate(event) {
    event.preventDefault()
    setBusy(true)
    setError('')
    setStep('')
    setSaved(false)
    try {
      const result = await suggestStep(task.trim())
      setStep(result.step)
    } catch (err) {
      if (err.status === 401) onUnauthorized()
      else setError(err.name === 'TimeoutError' ? 'This took too long. Please try again.' : err.message)
    } finally {
      setBusy(false)
    }
  }

  async function save() {
    setBusy(true)
    setError('')
    try {
      await onAdd(step)
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="next-step" aria-labelledby="next-step-heading">
      <h2 id="next-step-heading">Help me start</h2>
      <p>Something feels too big? Try one small action.</p>
      <form onSubmit={generate}>
        <label htmlFor="stuck-task">What are you finding hard to start?</label>
        <textarea id="stuck-task" value={task} maxLength={1000} required
          disabled={busy} rows={3} placeholder="For example: start working on my app"
          onChange={(event) => { setTask(event.target.value); setStep(''); setSaved(false) }} />
        <button disabled={busy || !task.trim()} type="submit">
          {busy ? 'Working…' : 'Suggest one small action'}
        </button>
      </form>
      <div role="status" aria-live="polite">
        {busy && !step && <p>Finding a small action. This may take a minute.</p>}
        {step && <div className="next-step-result"><p>{step}</p>
          <button type="button" onClick={save} disabled={busy || saved}>
            {saved ? 'Added to your list' : 'Add this to my list'}
          </button>
        </div>}
      </div>
      {error && <p role="alert">{error}</p>}
    </section>
  )
}
