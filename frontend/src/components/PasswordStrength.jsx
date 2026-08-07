import { scorePassword } from '../lib/passwordStrength'

const LEVELS = [
  { min: 0, label: 'Too short', className: 'strength-0' },
  { min: 20, label: 'Weak', className: 'strength-1' },
  { min: 40, label: 'Fair', className: 'strength-2' },
  { min: 65, label: 'Strong', className: 'strength-3' },
  { min: 85, label: 'Excellent', className: 'strength-4' },
]

/**
 * @param {{ password: string, email?: string }} props
 */
export function PasswordStrength({ password, email }) {
  const score = scorePassword(password, email)
  const level = LEVELS.filter((l) => score >= l.min).at(-1) ?? LEVELS[0]

  return (
    <div className="strength" aria-live="polite">
      <div className="strength-bar">
        <div
          className={`strength-fill ${level.className}`}
          style={{ width: `${score}%` }}
        />
      </div>
      <span className="strength-label">{level.label}</span>
    </div>
  )
}
