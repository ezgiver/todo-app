# Structured AI steps

Branch: `codex/structured-ai-steps`

## Goal

Return steps the app can validate, display, and let a user edit before saving.
A predictable format does not guarantee useful advice. No model change or
fine-tuning is included in this work.

## Agreed decisions

- Return one to three steps, each containing `action` and `done_when`.
- Ask Ollama for JSON matching a schema; validate the response again in Flask.
- Reject missing, empty, or oversized fields.
- Allow editing before saving. Never automatically save generated suggestions.
- Show a retry message for invalid responses; do not automatically retry inference.

Example response:

```json
{
  "steps": [
    {
      "action": "Open the app and create a task called Test",
      "done_when": "Test appears in your task list"
    }
  ]
}
```

## Why this approach

Free text is flexible but requires fragile parsing to separate steps and fields.
A schema makes the boundary explicit. Backend validation protects the app from
malformed or truncated output and checks business limits independently of the
model. The cost is additional schema, validation, and editing code.

## Proposed implementation

Keep the existing task input and local model configuration. Add
`POST /api/assistant/steps` with the existing authenticated request shape
`{"task": "..."}`. Return the agreed JSON object. Keep the old next-step endpoint
until the UI migration is complete; do not silently change its response contract.

Use a Pydantic model as the source for both the Ollama JSON schema and backend
validation. This adds a runtime dependency but avoids maintaining separate rules
for schema generation and validation. Reject unknown fields and non-string values.
Trim both fields and reject whitespace-only content. Proposed maximum length:
120 characters per field. Reject incomplete generation as well as invalid JSON.

Return 400 for invalid user input, 401 for no session, and 503 for unavailable,
incomplete, or invalid model output. Render generated content as text, not HTML.

Display editable action and finish fields. Save steps individually so there is
no partially successful batch or automatic duplicate retry. Lock a saved step's
save button. Clear unsaved suggestions when the original task changes.

### Saving without a database migration

The current todo model only stores a title (maximum 255 characters). Proposed
first version: save each edited step as `action — Done when: done_when` using the
existing todo API. Two 120-character fields plus the 14-character separator fit
in 254 characters. Validate edited fields before saving as well.

Benefit: preserves both pieces of information with no schema migration.
Cost: action and finish become a single title after saving. Separate persistent
fields would support richer editing later but require a migration and changes to
the existing todo contract. This tradeoff needs owner review before coding.

## Acceptance tests

- Accept one and three valid steps; reject zero and four.
- Reject invalid JSON, missing or extra fields, wrong types, blank strings,
  oversized text, and incomplete generation.
- Unauthenticated generation fails; offline Ollama and timeouts show errors.
- Generation alone creates no database records.
- Editing changes the values saved, including the finish condition.
- Saving one step does not save others; repeated clicks while saving are blocked.
- A failed save retains edits for retry; an expired session returns to sign-in.
- Ordinary todo creation, editing, and completion still work.

Automated tests verify the contract and failures. A browser check verifies edit
and save behavior. A live local-model test verifies schema compatibility. Assess
usefulness separately with the owner; passing the schema is not product validation.

## Reading

- Ollama documentation, “Generating structured JSON with a schema”:
  https://docs.ollama.com/capabilities/structured-outputs
- Industry example — Anthropic, “Structured outputs on the Claude Developer Platform”:
  https://claude.com/blog/structured-outputs-on-the-claude-developer-platform



## Implementation and validation record

Implemented locally on `codex/structured-ai-steps`; not published.

- Pydantic generates the schema and validates the parsed model response.
- Added `/api/assistant/steps`; preserved the old endpoint's response contract.
- Editable steps save independently through the existing todo API.
- 72 backend tests passed, including 22 new structured-step cases.
- Frontend lint and production build passed.
- Live local llama2 returned three schema-valid steps.
- Browser check on 2026-09-21: edited both fields of one generated step, saved it,
  verified the edited title appeared, and confirmed the other steps were not saved.
  The saved step's fields and save button became disabled.

Observed limitation: the model paired “Open Todo app” with “Task added
successfully.” The format was valid, but the finish condition did not match the
action. This is evidence that schema validation does not establish usefulness.

Additional browser checks on 2026-09-21:
- Stopped the local backend, edited an unsaved step, and attempted to save it.
  The UI displayed an error and retained both edited fields.
- Restarted the backend and retried. Exactly one new task appeared with the edit;
  that step's save button became disabled.
- Signed out in another tab, then attempted to save a remaining step in the
  original tab. The API rejected it and the original tab returned to sign-in.
  This exercises the unauthorized-session path, not elapsed-time cookie expiry.

Known limitation: sign-out removes unsaved step edits. Ordinary connection failure
retains them. No claim of production readiness is made. Installing existing frontend dependencies reports one high-severity npm
audit finding; its applicability has not yet been assessed.
