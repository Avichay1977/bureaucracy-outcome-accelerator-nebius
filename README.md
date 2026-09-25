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
- The stateful MCP layer preserves the case and handles verified outcome vs reroute.
- If no API key is configured, the local heuristic is available only as a development fallback; the competition demo must show the live Token Factory path.

## Run locally
`NEBIUS_API_KEY` must be set for the live competition path.

```powershell
$env:NEBIUS_API_KEY='YOUR_TOKEN_FACTORY_KEY'
$env:NEBIUS_MODEL='nvidia/nemotron-3-super-120b-a12b'
python server.py --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765/`.

## Verify
```powershell
python -m unittest discover -s tests -v
```

Current local verification: 13 automated tests pass.

## MCP tools
- `break_bureaucracy` — reason backward from goal to the active blocker and smallest safe action.
- `record_outcome` — record what happened and either close as verified or reroute.
- `case_status` — return compact current case state.

## Privacy / safety boundary
The demo does not log in to government systems, send messages, make payments, sign declarations, or submit forms. External commitments remain behind a human approval gate.

## Existing-project disclosure
The bureaucracy-resolution concept and earlier MCP implementation predate this Nebius submission. See `SIGNIFICANT_UPDATE.md` for the hackathon-period changes.

License: MIT.