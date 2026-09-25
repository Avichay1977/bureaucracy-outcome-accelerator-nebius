# Product Feedback — Nebius × NVIDIA Global AI Hackathon

## Developer tools / APIs / SDKs used
Primary track: **Best Apps & Agents**.

The competition build uses:
- **Nebius Token Factory** as the hosted inference endpoint.
- **NVIDIA Nemotron** (`nvidia/nemotron-3-super-120b-a12b`) as the structured reasoning model.
- A stateful Python MCP application for case memory, verification, and rerouting.
- A browser demo for the judge path.
- A separate Netlify public test build that calls the same Nebius model contract when `NEBIUS_API_KEY` is configured.

## What worked well
- Token Factory exposes an OpenAI-compatible chat-completions surface, so the model adapter stays small and auditable.
- The model catalogue makes the NVIDIA model choice explicit instead of hiding provider/model provenance.
- The hackathon allows existing projects when there is a significant event-period update, which makes it possible to improve a real workflow instead of rebuilding a disposable demo.
- The Apps & Agents track fits a closed-loop workflow where model reasoning is only one component of a larger state machine.

## What needs work
- Promotional-credit onboarding currently requires a supported payment card before Token Factory API access can be activated. For a hackathon that advertises promotional access, a clearly documented cardless event path would reduce friction.
- The distinction between hackathon registration, AI Builder review, billing onboarding, promotional credit redemption, and Token Factory API activation is spread across multiple surfaces.
- A small official "hackathon readiness" diagnostic that reports account eligibility, promo-credit state, API-key readiness, and model access would prevent repeated setup loops.

## Onboarding experience: zero to live model call
The shortest path we found is:
1. Join the hackathon / establish the event account context.
2. Complete Nebius account onboarding.
3. Activate billing onboarding.
4. Redeem the eligible promotional credit.
5. Create a Token Factory API key.
6. Call `/v1/chat/completions` with the NVIDIA Nemotron model.
7. Verify provider/model provenance in the application UI.

The main friction is that step 3 currently requires a payment card even when the intent is to use promotional hackathon credit.

## Would I build with Token Factory again?
**Yes, provided onboarding is unblocked.** The inference API is simple enough to isolate behind a narrow adapter, which keeps the rest of the agent architecture portable and testable.

## Safety / human control
The model may identify a blocker and propose one smallest safe action. It does not send messages, submit forms, make payments, sign declarations, or impersonate the user. Consequential actions remain behind an explicit human approval gate.
