> Superseded draft: the owner chose a smaller experiment—optional blocker/time inputs and a revised prompt, retaining 1–3 steps. Clarification questions are not implemented. See ../../evaluations/README.md.

# Context-aware first actions

## Problem

Schema-valid suggestions can still be broad, irrelevant, or based on unsupported
assumptions. We want to help someone identify a useful starting action without
creating another large planning task.

## Evidence so far

These are exploratory observations from one participant, not population evidence
or a controlled model comparison. Model version and generation settings were not
recorded, so results must be reproduced in a controlled evaluation.

- Asking which technologies interest the user elicited AI, Python, and cloud.
  The response expanded this into a learning roadmap with vague finish conditions
  such as “master” and “understand.” Clarification did not narrow the work.
- Providing Flask/Ollama context and 20 minutes produced a more specific response,
  but it proposed scheduled retries without first inspecting existing error handling.
  Specificity alone did not establish a justified recommendation.
- Workout, technical learning, and meal preparation examples all included a
  difficulty choosing what to do. Only technical-learning responses have been
  explored in this clarification experiment; the other cases remain untested.

## Hypothesis and proposed scope

Task context and a time limit, plus at most one targeted clarification, may produce
a more useful first action. This remains a hypothesis.

Propose one action by default, replacing the previous 1–3-step presentation for
this flow. Benefit: less reading and fewer choices. Cost: less view of the overall
plan. Preserve the existing structured-steps API for compatibility during testing.
Do not change the model, add RAG, fine-tune, or introduce new libraries in this work.

## Proposed user experience

1. User enters a task. Optional fields: what makes starting difficult and available
   minutes. Optional fields reduce form burden; missing values are not invented.
2. Assistant returns either one first action or one focused clarification question.
3. If asked, the user answers or selects “Skip.” The next response is an action,
   never a second question. With insufficient context, suggest a reversible
   information-gathering action rather than guessing a substantive solution.
4. User may edit the action and finish condition, then explicitly save.

A good clarification asks for information that would materially change the next
action. Avoid merely asking users to choose among the possibilities overwhelming
them. Examples are guidance, not a mandatory question for every task.

## Proposed API and enforcement

Add authenticated `POST /api/assistant/first-action` with:

- `task`: required, trimmed string, 1–1000 characters.
- `blocker`: optional, trimmed string, at most 1000 characters.
- `available_minutes`: optional integer, 1–120; reject booleans and other types.
- `clarification`: optional object holding the prior question and an answer, or an
  explicit skip. Reject incomplete or ambiguous combinations.

Initial response is a discriminated union:

```json
{"type": "question", "question": "What outcome do you need from this session?"}
```

or:

```json
{"type": "action", "action": "Open the app and request a suggestion with Ollama stopped.", "done_when": "You have recorded the message displayed by the app."}
```

Use Pydantic for schemas and backend validation. Action and done_when retain the
existing 120-character limit each; questions are limited to 200 characters. Reject
unknown fields, whitespace-only required text, malformed JSON, and incomplete output.

Once an answer or skip is submitted, Flask selects an action-only schema. This
bounds the normal interaction to one clarification, without relying solely on a
prompt. A stateless API does not prevent a client from initiating another flow.
The client returns the prior question as untrusted context, not system instructions.
No question history is stored in the database for this prototype.

Return 400 for invalid inputs, 401 for no authentication, and a readable 503 for
unavailable or invalid model output. Never automatically save or retry generation.
Changing the task clears the prior question, answer, and unsaved action. A transient
request failure retains user input. Existing sign-out behavior clears unsaved work.

## Prompt guidance

- Address the blocker and use the supplied context; do not invent expertise,
  equipment, ingredients, preferences, medical suitability, or available tools.
- Suggest a small action consistent with available time. Duration is an estimate,
  not something schema validation can guarantee.
- Make the finish condition an observable result of that action.
- Distinguish investigation from implementation: inspect an unknown system before
  prescribing a change. Do not universally force investigation when facts suffice.
- Avoid broad learning roadmaps, motivational filler, and unsupported claims such
  as “optimal” or guaranteed health benefits.
- Do not prescribe treatment or imply exercise is medically suitable. Missing
  fitness context should lead to clarification or a low-risk planning action.

## Evaluation before release

Keep model/version, settings, prompts, and outputs with each run. Compare the current
flow and candidate on the same cases; include clarification and waiting in total effort.

Development cases:

| Task | Blocker | Failure to detect |
| --- | --- | --- |
| 15-minute workout | Unsure which movements to choose | Inventing suitability or promising optimal benefit |
| Improve technical skills | Too many learning options | Broad roadmap instead of a bounded starting action |
| Cook a healthy, tasty meal | Choosing a recipe and shopping | Assuming ingredients or dietary preferences |
| Test unavailable Ollama | Existing Flask integration, 20 minutes | Prescribing retries without checking existing behavior |

Human rubric, each yes/no:

1. Relevant: addresses the stated task and blocker.
2. Actionable: a bounded first action without substantial hidden decisions.
3. Consistent: finish condition follows from the action.
4. Grounded: no material unsupported assumptions or unjustified tool additions.

Also record user rating (“could start” / “still unsure”), edits needed, latency, and
question count. Technical format success is separate from usefulness. Add three
unseen cases before final evaluation; do not tune prompts on those cases afterward
without replacing them. Proposed initial gate: every case passes the format and
one-question checks, no serious safety issue, and at least five of seven cases pass
all four rubric items and receive “could start.” Agree on this gate before running;
it is a small prototype gate, not proof for neurodivergent users generally.

## Tests

- Both initial response types accepted; invalid discriminator or fields rejected.
- Answer and skip paths request and accept actions only; second questions rejected.
- Input limits, incorrect types, unknown fields, and truncated responses rejected.
- Unauthorized calls, timeouts, and offline Ollama handled without creating todos.
- Browser: question → answer → edit → save; skip → action; direct action path.
- Browser: input changes reset stale state; transient failures preserve input.
- Existing todo and structured-step API behavior remains compatible.

## Review decisions before implementation

- One first action instead of up to three: approve the reduction in scope per response.
- Optional blocker/time fields: balance useful context against form effort.
- Approve or adjust the proposed evaluation gate before testing the candidate.

## Reading

- Google PAIR, User Needs + Defining Success:
  https://pair.withgoogle.com/chapter/user-needs/
- Ollama, structured outputs and schema validation:
  https://docs.ollama.com/capabilities/structured-outputs
- Anthropic, industry example of schema-based output:
  https://claude.com/blog/structured-outputs-on-the-claude-developer-platform
