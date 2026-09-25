# Judge Quick Start

## The idea in one sentence
**One blocker. One next move. One proof that it worked.**

Bureaucracy Outcome Accelerator is a stateful agent that treats bureaucracy as a changing dependency problem instead of a question-answer problem.

## 90-second judge path
1. Run `python server.py --port 8765`.
2. Open `http://127.0.0.1:8765/`.
3. Use the pre-filled municipal waste-bin case and click **Ask the agent**.
4. Observe the blocker, controller, smallest safe next move, and verification evidence.
5. Click **Not verified — reroute**.
6. Observe the state change to `REROUTE` and the new route instead of repeated advice.
7. Confirm the provider/model badge for Nebius Token Factory + NVIDIA Nemotron.

## What to look for
The important part is not a single model response. It is the closed loop around it:

**Goal → Blocker → Next move → Evidence → Verify / Reroute**

The model reasons. The application owns state, verification, rerouting, and the human approval boundary.

## Verification
Run `python -m unittest discover -s tests -v`.

A promise is not counted as success. The workflow closes only when evidence supports the real-world outcome.