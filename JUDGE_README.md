# Judge Quick Start

## The idea in one sentence
**One blocker. One next move. One proof that it worked.**

Bureaucracy Outcome Accelerator is a stateful agent that treats bureaucracy as a changing dependency problem instead of a question-answer problem.

## 90-second judge path
1. Run `python server.py --port 8765`.
2. Open `http://127.0.0.1:8765/`.
3. Use the pre-filled municipal waste-bin case and click **Run the agent**.
4. Observe `WAITING_APPROVAL`, the blocker, controller, smallest safe next move, and verification rule.
5. Click **Approve & resume**. Observe `AWAITING_VERIFICATION`.
6. Click **Not verified — reroute**. The fallback becomes a new `WAITING_APPROVAL` action rather than executing automatically.
7. Repeat approval only if you want to continue that exact fallback action.
8. For the competition video, confirm the provider/model badge shows Nebius Token Factory + NVIDIA Nemotron before recording.

## What to look for
The important part is not a single model response. It is the closed loop around it:

**Goal → Blocker → Next move → Human Gate → Resume → Verify / Re-route**

The model reasons. The application owns state, verification, rerouting, and the human approval boundary.

## Verification
Run `python -m unittest discover -s tests -v`.

Expected result: **18 / 18 tests PASS**.

A promise is not counted as success. The workflow closes only when evidence supports the real-world outcome.