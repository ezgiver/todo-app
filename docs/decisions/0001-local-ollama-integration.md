# 0001 — Prototype task suggestions through Flask and local Ollama

Date: 2026-09-20  
Related spec: [Ollama integration](../specs/ollama-integration.md).

## Decision implemented

Route requests through Flask to local Ollama. Start with prompt instructions and
an existing model. Return a complete suggestion and require the user to explicitly
save it using the existing todo endpoint. Keep model calls in a separate service
module and the model name and address in configuration.

## Alternatives considered in this retrospective record

These alternatives explain the current choice; they were not all experimentally
compared before implementation.

| Option | Benefit | Why not chosen for this iteration |
| --- | --- | --- |
| Browser calls Ollama directly | Fewer backend steps | Couples clients to model access and moves shared request policy out of Flask |
| Hosted inference API | Can support a deployed app without a laptop | Adds provider, data handling, and cost decisions before local validation |
| Fine-tune immediately | Could specialize behavior with suitable examples | No dataset or baseline yet; adds training and evaluation work |
| Stream generated text | Earlier visible feedback | More complex response handling for a short suggestion |
| Fixed rule-based suggestions | Predictable, cheap, easy to test | Less flexible; remains a useful comparison for the next evaluation |

## Consequences

The prompt and model configuration have one backend owner. Existing authentication
and todo persistence are reused, and Python's standard HTTP library avoids a new
runtime dependency. The prototype is easy to inspect and run locally.

In exchange, synchronous inference occupies a Flask worker and the user waits
for completion. Local inference is not a public hosting solution. Prompts do not
guarantee useful suggestions; the 255-character limit can reject valid responses.
Inference capacity and rate limiting are still unresolved.

## Revisit when

- Preparing a public deployment: decide hosting, access controls, concurrency,
  request limits, latency targets, and operating budget.
- Repeated measured failures remain after prompt/model comparisons: evaluate
  fine-tuning against a held-out test set.
- Waiting causes users to abandon the flow: compare streaming or other feedback.
- User testing shows simpler fixed suggestions work as well: reconsider AI's role.

## Ownership and acceptance

The owner requested the integration. The coding assistant selected and implemented
the initial technical details. Owner review of this record is pending; do not
represent these choices as independently designed or formally accepted by the owner.
