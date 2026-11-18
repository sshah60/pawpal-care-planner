# PawPal Care Planner

PawPal helps one caregiver plan a day of care across multiple pets. Given saved tasks and a budget in minutes, it recommends a conflict-free schedule, explains deferred work, and flags any unscheduled high-priority care for human review.

## Base project

This extends **PawPal+**, the Module 2 Show project. The original app modeled owners, pets, and recurring tasks, saved them as JSON, and offered a Streamlit interface and command-line demonstration. Its budget scheduler considered tasks in priority and time order, while its conflict check flagged identical start times separately. [Original Module 2 repository](https://github.com/sshah60/ai110-module2show-pawpal-starter)

## Architecture and design

The [system diagram](diagrams/architecture.md) shows how the new CLI loads the existing PawPal JSON with `Owner.load_from_json` and queries pending tasks through the original `Scheduler`. A deterministic planning workflow tries two orderings, one by priority then time and one by priority then duration. Each candidate respects fixed start times, interval overlaps, overnight carryover, and the user's care-minute budget. A verifier checks task accounting, elapsed minutes, and timing before any recommendation is returned.

The planner compares the counts of high-, medium-, and low-priority tasks in that order, then prefers fewer occupied minutes. The fixed orderings are fast to inspect and reproduce. They can miss a better combination, and the shorter-first ordering may favor short tasks within a priority level. Every deferred high-priority task carries a review flag, and the CLI leaves the saved plan untouched. The workflow uses symbolic planning in Python and requires no model API.

## Setup and run

Use Python 3.10 or later. The planner and its focused tests use the standard library.

```bash
git clone https://github.com/sshah60/pawpal-care-planner.git
cd pawpal-care-planner
python3 -m venv .venv
source .venv/bin/activate
python plan_care.py examples/morning.json 2026-11-18 25
python -m unittest discover -s tests -p test_care_planner.py -v
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. To run the full suite and the original Streamlit app, install the inherited dependencies.

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python -m streamlit run app.py
```

Use the bundled synthetic data or pass a JSON file produced by the original app. The arguments are the JSON path, ISO date, and whole-number minutes from 0 to 1440.

## Sample interactions

### 25 minutes with overlapping tasks

```text
$ python plan_care.py examples/morning.json 2026-11-18 25
Care plan for 2026-11-18 | 25/25 minutes
Verified priority then time: 1 high, 0 medium, 0 low
Verified priority then duration: 2 high, 1 medium, 0 low
Recommended: priority then duration
  08:10 | Luna / Breakfast | 10 min | high
  08:20 | Mochi / Refill water | 5 min | high
  08:25 | Luna / Brush coat | 10 min | medium
  REVIEW REQUIRED: Mochi / Long walk (overlaps Mochi / Refill water)
Review the recommendation before acting. Saved tasks are unchanged.
```

### Zero minutes

```text
$ python plan_care.py examples/morning.json 2026-11-18 0
Care plan for 2026-11-18 | 0/0 minutes
Verified priority then time: 0 high, 0 medium, 0 low
Verified priority then duration: 0 high, 0 medium, 0 low
Recommended: priority then time
No tasks selected.
  REVIEW REQUIRED: Mochi / Long walk (exceeds the care-minute budget)
  REVIEW REQUIRED: Luna / Breakfast (exceeds the care-minute budget)
  REVIEW REQUIRED: Mochi / Refill water (exceeds the care-minute budget)
  Deferred: Luna / Brush coat (exceeds the care-minute budget)
Review the recommendation before acting. Saved tasks are unchanged.
```

### Invalid budget

```text
$ python plan_care.py examples/morning.json 2026-11-18 -1
Unable to plan: Budget must be a whole number from 0 to 1440.
```

## Testing summary

The focused suite passed 7 of 7 checks. With 25 minutes, the time-first candidate picked one high-priority task, and comparing candidates found a valid plan with two. The selected plan still deferred one high-priority task and showed the overlap that caused it. The full suite passed 43 of 43 tests, including the inherited scheduler and UI tests.

| Input or condition | Expected behavior | Result |
| --- | --- | --- |
| Conflicting tasks, 25-minute budget | Select the better verified candidate and give a deferral reason | Pass |
| Zero budget | Select no tasks and account for all four deferrals | Pass |
| Negative budget | Reject input before generating a plan | Pass |
| Date without tasks | Return an empty plan | Pass |
| Previous-day task continues past midnight | Defer the overlapping morning task | Pass |
| Tampered plan total | Verifier rejects the plan | Pass |
| Existing owner and task objects | Planning leaves them unchanged | Pass |

## Portfolio and reflection

This project demonstrates how I would design an AI-assisted planning tool that makes its decisions inspectable. The comparison exposed an assumption in the original approach: sorting by time within a priority level favors an earlier long task even when two shorter high-priority tasks could fit. Showing the alternatives and surfacing an unresolved conflict gives a caregiver enough information to decide what to do next.

[Project repository](https://github.com/sshah60/pawpal-care-planner) · [Model card](model_card.md) · [Six-minute presentation](presentation.md)
