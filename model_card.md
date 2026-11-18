# PawPal Care Planner model card

## Intended use

PawPal is a deterministic assistant for one caregiver reviewing fixed-time pet-care tasks. It uses priorities, durations, and dates the caregiver supplies. It compares two feasible candidate schedules and exposes how many tasks of each priority they cover. It runs locally without a hosted model or training data.

## Limitations and biases

The planner inherits any mislabeling or omissions in the schedule. It treats two tasks of the same priority as equally important, so a candidate with more short jobs may win even when a longer task matters more in practice. It assumes a single caregiver and fixed appointments. The two heuristics can miss a feasible combination that serves more tasks. A future version could compare results with an exact optimizer, add explicit owner-defined protected tasks, and evaluate both on schedules with varied task lengths and priorities.

## Misuse and safeguards

Someone could treat the recommendation as permission to skip essential care. The CLI explicitly flags every deferred high-priority task, reports why it was deferred, and asks the caregiver to review the recommendation. It never moves, completes, or saves tasks. The demo contains synthetic data. Any real records should stay local, particularly if entries reveal household routines.

## Reliability results and what surprised us

Seven focused tests and all 43 tests in the full suite passed. The same 25-minute input produced one high-priority task under time-first and two under duration-first. The surprising part was that both schedules passed the constraints and still served different numbers of urgent tasks. A feasibility check alone could not catch the quality gap. Separate cases confirmed that a zero budget preserves all deferrals and that the verifier rejects a tampered total. The examples cover the supplied fixture and regression cases, so their results do not establish performance on other households' schedules.

## AI collaboration

Codex implemented and tested this extension in response to a request to complete the CodePath final project and follow its rubric. It inspected the inherited scheduler and used the course requirements to select a planning and verification workflow. The implementation adopted the idea of comparing two deterministic orderings, since the resulting choices can be reproduced on the same data. It scoped down the initial option of an exhaustive search to two inspectable heuristics, trading an optimality guarantee for a smaller implementation and clearer demonstration. Codex used the test suite and actual CLI transcripts to check the resulting design.
