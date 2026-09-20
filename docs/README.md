# Project documentation

Keep the reasoning alongside the code so future contributors and reviewers can
see the problem, the alternatives, the evidence, and the limits of each change.

| Document | Purpose | When to update |
| --- | --- | --- |
| [Technical specs](specs/ollama-integration.md) | Describe a feature's problem, behavior, design, validation, and open questions | Draft before substantial implementation; update when scope changes |
| [Decision records](decisions/0001-local-ollama-integration.md) | Explain a significant choice, alternatives, consequences, and when to revisit it | When an architectural decision is made |
| [Changelog](../CHANGELOG.md) | Summarize user-visible changes and release status | Add under Unreleased as changes are built; date releases when shipped |

## Working agreement

- Create a meaningfully named branch before editing code, for example
  `codex/integrate-ollama`.
- Keep documentation in the same branch and review as the implementation.
- Use a short spec for substantial features; do not require one for every small fix.
- Number decision records sequentially. Include date and status: proposed,
  accepted, or superseded. If a decision changes, add a new record and link it
  from the old one rather than erasing the history.
- Distinguish implemented behavior, proposed work, assumptions, and measured results.
- Record failures and limitations as well as successful checks. Do not present
  automated test results as evidence of user value.
- Keep personal information, credentials, and private user feedback out of public
  documentation. Use synthetic examples or feedback approved for publication.
- Describe AI assistance honestly. The project owner reviews and owns the final
  decisions; generated implementation is not evidence of independent authorship.

## Starting point

Read the [Ollama integration spec](specs/ollama-integration.md), then
[decision 0001](decisions/0001-local-ollama-integration.md).
These initial documents were written retrospectively after the local prototype;
future substantial changes should start with a draft spec.
