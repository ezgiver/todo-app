# Context experiment — 2026-09-21

Compare the original structured-step prompt with a revised prompt plus optional
blocker/time inputs. Same configured local llama2 model, temperature 0.2,
512-token cap; one run per version on each of three cases. No seed was fixed.
This is exploratory and does not isolate the effect of the prompt from context.
Exact installed model digest was not captured; record it for future comparisons.

Raw results: [context-comparison.json](context-comparison.json).
Run from backend: `.venv/bin/python compare_context.py` with Ollama available.
The script uses the local `codex/structured-ai-steps` branch as its baseline and
records the resolved commit. It overwrites this result file on rerun.

## Findings (engineering assessment; user ratings pending)

- Workout: the baseline's durations were inconsistent. The candidate added
  research and choice tasks without resolving the blocker or respecting the total
  15-minute budget. Not sufficient.
- Technology: the candidate mentioned Flask/Ollama, but still asked for research,
  prioritisation, and broad learning with vague finish conditions. Not sufficient.
- Meal: the candidate addressed recipes and shopping, but finding a recipe was
  presented as the finish for opening a website, and possessing ingredients as the
  finish for making a list. The action/finish mismatch remains. Not sufficient.

All six outputs met the structural schema. None of the candidate outputs clearly
resolved the observed quality problems. This supports keeping the work as an
experiment, not claiming a successful quality upgrade. A bounded next comparison
could hold the prompt/context fixed and try another installed model.

## Implementation checks

81 backend tests pass; frontend lint and production build pass. Tests cover
optional-input validation, context passed to the model, and backward-compatible
task-only requests. No model weights were trained and no changes were published.
