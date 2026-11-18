# PawPal Care Planner presentation

## 0:00–0:55 · The problem and base project

Open the README. Explain that Module 2 PawPal+ gave a caregiver one place to record care across pets, save data, and generate a priority-based schedule. Point out the problem with a shared morning schedule. An early long task can use the entire budget, and unequal start times can still overlap. The final project recommends a schedule the caregiver can review against the actual time windows.

## 0:55–1:55 · How the system works

Open the [rendered architecture diagram](diagrams/architecture.md). Follow the saved owner data and entered budget into the scheduler. Describe the two candidate orderings. Explain that the verifier checks overlaps, task accounting, and minutes, then the comparison prefers more high-priority tasks, followed by medium and low counts. Follow the result to caregiver review.

## 1:55–3:35 · Run the main demo

```bash
python plan_care.py examples/morning.json 2026-11-18 25
```

Show that trying time first schedules one high-priority task. Trying duration first schedules two high-priority tasks plus brushing for 25 minutes total. Point to the deferred walk and its overlap with the water refill. The caregiver can decide which task is more important and make that change in the original scheduler. The planner only reads the saved data.

## 3:35–4:35 · Show the guardrails

```bash
python plan_care.py examples/morning.json 2026-11-18 0
python plan_care.py examples/morning.json 2026-11-18 -1
```

Show that a zero-minute budget reports every deferral, while a negative budget exits with an error. Point to the test results and mention the tampered-total and overnight-carryover cases.

## 4:35–6:00 · What the project taught me

Discuss how two feasible schedules can differ in quality and why human review still matters. A short high-priority job may count equally with a longer one whose real-world importance is higher. Explain how an exact optimizer, protected tasks, and more representative evaluation cases could improve a later version. End by opening the repository README with the commands and actual results.

[Public GitHub repository](https://github.com/sshah60/pawpal-care-planner)
