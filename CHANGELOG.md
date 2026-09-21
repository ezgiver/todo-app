# Changelog

This file records notable changes from the introduction of this log onward.
Earlier releases have not been reconstructed. Unreleased does not mean deployed.

## Unreleased

### Added

- Local Ollama integration: “Help me start” suggests one action and lets the user
  explicitly add it to their todo list.
- Authenticated assistant API with input validation and model failure handling.
- Assistant configuration, setup documentation, and automated tests.
- [Technical spec](docs/specs/ollama-integration.md) and
  [decision record](docs/decisions/0001-local-ollama-integration.md), including
  tradeoffs, validation evidence, and outstanding limitations.

### Known limitations

- Inference is configured for local use; public hosting is not implemented.
- Model suggestions vary in usefulness; no fine-tuning or user-value validation
  has been completed.

### Structured steps (in development)

- Add schema-validated 1–3 AI steps with action and finish condition.
- Let users edit and save individual steps, preserving both fields in the title.
- Reject invalid and incomplete model responses without automatically retrying.
