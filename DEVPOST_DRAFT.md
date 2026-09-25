# Devpost Draft — Nebius × NVIDIA Global AI Hackathon

## Project name
Bureaucracy Outcome Accelerator

## Tagline
One blocker. One next move. One proof that it worked.

## Track
Best Apps & Agents

## The problem
Bureaucracy is rarely just an information problem. People can know the rules and still be stuck because they do not know what is blocking the outcome *right now*, who controls that dependency, or whether the last action changed anything.

Most assistants explain the process. This one holds the state of the process.

## The product
Bureaucracy Outcome Accelerator works backward from a desired real-world outcome. It finds the earliest unresolved dependency, identifies the controller, proposes the smallest safe next move, defines what evidence would count as success, and keeps the case alive until the outcome is verified.

**Blocker → Next move → Proof.**
If the evidence is missing, the case does not close. The agent reroutes instead of repeating the same advice.

## The demo
A municipal official agrees to add a waste bin. A normal assistant might call that progress and stop.

Our agent does not.

It asks: **Was the bin actually installed?**

If not, the state changes to REROUTE and the next move becomes obtaining the work-order/reference number and exact placement details. A promise is not treated as an outcome.

## How it works
NVIDIA Nemotron, served through Nebius Token Factory, reasons over the active case and returns a compact structured plan: blocker, controller, next move, verification evidence, and fallback.

A stateful MCP application owns everything around that reasoning call: session memory, case state, verification, rerouting, and human approval boundaries.

The model reasons. The product owns the process.

## Why it is different
- **Outcome, not answer:** success requires evidence that reality changed.
- **One move at a time:** the user sees the smallest useful action, not a wall of instructions.
- **Closed loop:** every action leads to verification or rerouting.
- **Stateful:** the case survives across attempts.
- **Human control:** consequential external actions remain behind an explicit approval gate.
## What changed during the hackathon
The bureaucracy-resolution concept and an earlier deterministic MCP workflow existed before this event. The competition build adds the Nebius Token Factory adapter, NVIDIA Nemotron as the structured dependency reasoner, provider/model provenance in the demo, model-contract tests, and a judge path designed around the Apps & Agents track.

The change is architectural, not cosmetic: model reasoning is now separated from an explicit state machine that verifies outcomes and reroutes failures.

## What we built
- Python stateful MCP server with a browser demo.
- Three focused tools: `break_bureaucracy`, `record_outcome`, and `case_status`.
- Nebius Token Factory / NVIDIA Nemotron reasoning adapter.
- Explicit verification and reroute state transitions.
- 13 automated local tests.

## What we learned
A capable model is not enough. The hard part is deciding what the model may reason about, what the application must remember deterministically, and what requires human approval.

## What's next
Institution-specific evidence schemas, approved tool adapters for real-world actions, and one product metric: **Human Minutes per Verified Outcome**.

## Closing
**Bureaucracy does not need another chatbot. It needs a finish line.**