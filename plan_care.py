"""CLI for PawPal's verified, read-only care recommendations."""
import argparse
from datetime import date

from care_planner import recommend
from pawpal_system import Owner


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data", help="PawPal owner JSON")
    parser.add_argument("day", type=date.fromisoformat, help="Date in YYYY-MM-DD format")
    parser.add_argument("budget", type=int, help="Available care minutes")
    args = parser.parse_args()
    try:
        owner = Owner.load_from_json(args.data)
        plan, candidates = recommend(owner, args.day, args.budget)
    except (OSError, ValueError, OverflowError, RuntimeError) as error:
        parser.exit(2, f"Unable to plan: {error}\n")

    print(f"Care plan for {args.day.isoformat()} | {plan.minutes}/{args.budget} minutes")
    for candidate in candidates:
        high, medium, low, _ = candidate.score
        print(f"Verified {candidate.strategy}: {high} high, {medium} medium, {low} low")
    print(f"Recommended: {plan.strategy}")
    if not plan.selected:
        print("No tasks selected.")
    for pet, task in plan.selected:
        print(f"  {task.time} | {pet.name} / {task.title} | {task.duration_minutes} min | {task.priority}")
    for pet, task, reason in plan.deferred:
        label = "REVIEW REQUIRED" if task.priority == "high" else "Deferred"
        print(f"  {label}: {pet.name} / {task.title} ({reason})")
    print("Review the recommendation before acting. Saved tasks are unchanged.")


if __name__ == "__main__":
    main()
