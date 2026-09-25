# Product Feedback — Amazon Build, Ship, Shape

## Developer tools / APIs / SDKs used
Primary track: **Alexa+**.

The project uses the hackathon's supported **self-hosted MCP** path rather than gated Alexa+ preview tooling. The server implements MCP protocol version `2025-11-25` over a Streamable HTTP endpoint and is exercised through a local web simulator.

## What worked well
- The official rules provide a clear alternative path for Alexa+ submissions: a self-hosted MCP server is sufficient and does not require access to preview-only Alexa+ tools.
- The minimum MCP version and Streamable HTTP requirement are explicit, which made the technical acceptance boundary testable.
- Allowing a custom web simulator makes it possible to demonstrate the user experience without proprietary hardware or partner-only tooling.
- The judging criteria explicitly reward stateful, agentic workflows rather than single-turn Q&A, which is a good fit for real workflow products.

## What needs work
- The distinction between generally available hackathon paths and preview-only Alexa+ developer tooling is easy to miss when moving between documentation pages.
- Private-repository review requires several individual collaborator invitations, and those invitations expire. This adds avoidable submission administration.
- The rules are precise about MCP version and transport but do not provide a small official conformance test specifically for hackathon entrants. A judge-facing smoke-test reference would reduce ambiguity.

## Onboarding experience: zero to hello world
The shortest successful path was:
1. Read the Official Rules first rather than assuming preview tooling was required.
2. Select the self-hosted MCP route.
3. Implement `initialize`, session handling, `tools/list` and `tools/call` over HTTP.
4. Add a local simulator.
5. Add automated tests for version/session/origin behavior.

The main onboarding friction was discovering that the gated Alexa+ Category SDK / MCP Toolkit / CLI / Web Simulator were not required for the competition path.

## Would I build with this approach again?
**Yes.** A standards-based MCP surface is a good fit for stateful agent tools because the business logic remains portable and testable outside a proprietary client. I would prefer a single hackathon quick-start page that cleanly separates the public self-hosted MCP path from partner-preview tooling.

## AWS Builder mini-challenge
Not claimed in this baseline submission. No AWS runtime integration is represented or implied.