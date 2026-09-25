# Devpost Final Packet — Nebius × NVIDIA Global AI Hackathon

Status: READY EXCEPT LIVE TOKEN FACTORY PROOF + YOUTUBE URL + FINAL SUBMIT

## Project name
Bureaucracy Outcome Accelerator

## Tagline
One blocker. One next move. One proof that it worked.

## Track
Best Apps & Agents

## Working demo
https://bureaucracy-outcome-accelerator-nebius.netlify.app

## Public code repository
https://github.com/Avichay1977/bureaucracy-outcome-accelerator-nebius

## Project description
Bureaucracy is rarely just an information problem. People can know the rules and still be stuck because they do not know what is blocking the outcome right now, who controls that dependency, or whether the last action changed anything.

Bureaucracy Outcome Accelerator works backward from a desired real-world outcome. It identifies the earliest unresolved dependency, identifies the controller, proposes one smallest safe next move, defines what evidence would count as success, and keeps the case alive until the outcome is verified.

The core loop is:

**Goal → Blocker → Controller → Smallest Safe Action → Verify → Re-route**

A promise is not treated as an outcome. If the evidence is missing, the case stays open and the agent changes route instead of repeating the same advice.

## Demo case
A municipal official agrees to add a waste bin.

A normal assistant may stop at the agreement. Bureaucracy Outcome Accelerator asks whether the bin was actually installed.

If it was not, the case moves to `REROUTE` and the next move changes to obtaining the work-order/reference number, placement date, or exact unresolved operational dependency.

That is the product behavior we want to demonstrate: the agent remembers what happened, rejects a false finish line, and changes the route.

## How Nebius + NVIDIA are used
NVIDIA Nemotron is called through the Nebius Token Factory inference API at runtime.

The model receives the active goal, known facts, and constraints and returns a structured dependency analysis with:
- blocker
- controller
- next action
- evidence needed
- verification rule
- fallback route

The application owns the deterministic process around that model call: case state, MCP session state, verification, rerouting, and the explicit human approval boundary.

**The model reasons. The product owns the process.**

Default competition model:
`nvidia/nemotron-3-super-120b-a12b`

## Why this is more than a single API-call demo
The model call is one component inside a multi-step workflow.

The product:
1. creates a case from a real-world goal;
2. turns the model output into a compact current state;
3. preserves the case across steps;
4. records the observed outcome;
5. refuses to call progress “done” without verification;
6. transitions either to `VERIFIED_OUTCOME` or `REROUTE`;
7. exposes the next action rather than repeating the original answer.

## What changed during the hackathon
The bureaucracy-resolution concept and an earlier deterministic MCP workflow existed before the submission period.

The hackathon-period build significantly updated the project by adding:
- a live Nebius Token Factory inference adapter;
- NVIDIA Nemotron as the structured decision-dependency reasoner;
- explicit provider/model provenance in the demo;
- a clean separation between probabilistic model reasoning and deterministic case-state transitions;
- Token Factory contract tests;
- a public judge-facing Netlify demo path;
- GitHub Actions CI on clean Python 3.11 and 3.12 environments;
- a public MIT-licensed repository and judge documentation.

This is an architectural update, not a rebrand: the earlier deterministic workflow is now designed around an NVIDIA Nemotron runtime reasoning layer served by Nebius.

## What we built
- Python stateful MCP server.
- Browser demo.
- Three MCP tools: `break_bureaucracy`, `record_outcome`, and `case_status`.
- Nebius Token Factory / NVIDIA Nemotron adapter.
- Explicit verification and reroute state transitions.
- Public Netlify test build.
- Automated test suite and GitHub Actions CI.

## Design
The interface deliberately shows one blocker, one action, and one verification rule at a time.

This avoids turning bureaucracy into another long checklist. The user should always be able to answer one question: **What is the smallest useful move now?**

## Potential impact
The target users are people who are stuck inside multi-step administrative processes: permits, benefits, municipal services, licensing, and similar workflows.

The system is designed around a measurable product outcome:

**Human Minutes per Verified Outcome**

The goal is not to generate more instructions. It is to reduce human effort while increasing the number of cases that reach externally verified outcomes.

## Safety / human control
The demo does not log in to government systems, send messages, submit forms, make payments, sign declarations, or impersonate the user.

Consequential external actions remain behind an explicit human approval gate.

## What we learned
A capable model is not enough.

The hard product problem is deciding:
- what the model should reason about;
- what the application should remember deterministically;
- what counts as real evidence;
- when a failed route should be abandoned;
- what must remain under human approval.

## Feedback
See `PRODUCT_FEEDBACK.md` in the public repository.

Short form:
Token Factory provides a compact inference surface that is easy to isolate behind a narrow adapter. The main onboarding friction we encountered is that promotional-credit activation currently requires billing onboarding with a supported payment card, and Nebius Support confirmed there is no hackathon-specific cardless activation path at this time. A single hackathon-readiness diagnostic covering registration, promotional credit, API-key readiness, and model access would reduce setup friction substantially.

## Demo video
BLOCKED until a real Token Factory request is verified.

Required final URL:
`YOUTUBE_URL_TODO`

The video must show the provider badge reading:
**Nebius Token Factory · nvidia/nemotron-3-super-120b-a12b**

Do not record the final competition video while the demo reports `local heuristic fallback`.

## Final pre-submit gate
Do not click Submit until all four are true:
- [ ] Public demo reports `provider_configured=true`.
- [ ] A real runtime response shows `reasoning_provider=Nebius Token Factory`.
- [ ] Public YouTube demo URL is inserted.
- [ ] Devpost registration/terms and final submission are explicitly approved at the human gate.
