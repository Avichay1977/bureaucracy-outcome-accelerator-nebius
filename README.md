# Bureaucracy Outcome Accelerator — Nebius × NVIDIA

Track: **Best Apps & Agents**

A stateful agent that turns a bureaucratic goal into the earliest unresolved decision dependency, proposes one smallest safe action, then verifies whether reality changed and reroutes if it did not.

## Why it matters
Most bureaucracy assistants explain procedures. This project treats bureaucracy as a live dependency graph:

**Goal → Bottleneck → Controller → Smallest Safe Action → Verify → Re-route**

An agreement is not counted as success. The workflow only closes when evidence shows the real-world outcome happened.

## Nebius + NVIDIA implementation
- Runtime reasoning calls Nebius Token Factory.
- Default model: `nvidia/nemotron-3-super-120b-a12b`.
- The Token Factory call identifies the blocker, controller, next action, verification evidence, and fallback route.
- The stateful MCP layer preserves the case, enforces an external Human Gate, resumes the exact approved action, and handles verified outcome vs reroute.
- If no API key is configured, the local heuristic is available only as a development fallback; the competition demo must show the live Token Factory path.

## Run locally
`NEBIUS_API_KEY` must be set for the live competition path.

```powershell
$env:NEBIUS_API_KEY='YOUR_TOKEN_FACTORY_KEY'
$env:NEBIUS_MODEL='nvidia/nemotron-3-super-120b-a12b'
python server.py --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`.

## Public web demo
Public test build: https://bureaucracy-outcome-accelerator-nebius.netlify.app

The repository also contains a Netlify-compatible test build:
- static UI: `web/`
- serverless endpoint: `/api/agent`
- secret: `NEBIUS_API_KEY` stored as a Netlify environment variable
- optional model override: `NEBIUS_MODEL`

The public test build carries the current case in the browser request between steps. The **canonical stateful MCP implementation remains the Python server**. The public build is a judge/demo surface, not a replacement architecture.

Verified locally and in CI on 2026-09-26:
- 18 / 18 automated tests pass
- Human Gate flow passes end-to-end: WAITING_APPROVAL → APPROVED_TO_EXECUTE → AWAITING_VERIFICATION → VERIFIED_OUTCOME
- resume without approval is blocked
- mismatched approval fingerprints are blocked
- outcome recording before approval/resume is blocked
- the public Netlify deployment is still on the previous build until the latest commit can be deployed
- Token Factory remains unconfigured until a real API key is available

If no Nebius API key is configured, the UI explicitly shows `local heuristic fallback`; it must not be represented as a live Token Factory call.

## Verify
```powershell
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the same suite on clean Python 3.11 and 3.12 environments.

## MCP tools
- `break_bureaucracy` — reason backward from goal to the active blocker and smallest safe action, then pause at the Human Gate.
- `resume_case` — resume only after a valid external approval matches the exact pending action.
- `record_outcome` — record what happened and either close as verified or create a newly gated fallback action.
- `case_status` — return compact current case state.

## Privacy / safety boundary
The demo does not log in to government systems, send messages, make payments, sign declarations, or submit forms. External commitments remain behind a Human Gate whose approval is bound to the exact action fingerprint and expires after a short TTL.

## Existing-project disclosure
The bureaucracy-resolution concept and earlier MCP implementation predate this Nebius submission. See `SIGNIFICANT_UPDATE.md` for the hackathon-period changes.

License: MIT.
