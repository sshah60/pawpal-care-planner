"""Generate and verify candidate daily plans without changing saved tasks."""
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from pawpal_system import Scheduler


@dataclass
class Plan:
    strategy: str
    selected: list
    deferred: list
    minutes: int
    score: tuple


def interval(task):
    start = datetime.combine(task.due_date, time.fromisoformat(task.time))
    return start, start + timedelta(minutes=task.duration_minutes)


def overlap(first, second):
    start, end = interval(first)
    other_start, other_end = interval(second)
    return start < other_end and other_start < end


def rejection(task, selected, budget, day_end, carryover):
    if interval(task)[1] > day_end:
        return "extends past midnight"
    if any(overlap(task, old) for old in carryover):
        return "overlaps unfinished care from the previous day"
    for pet, other in selected:
        if overlap(task, other):
            return f"overlaps {pet.name} / {other.title}"
    if sum(other.duration_minutes for _, other in selected) + task.duration_minutes > budget:
        return "exceeds the care-minute budget"
    return None


def verify(plan, expected, budget, day_end, carryover):
    """Independently check that all source tasks are accounted for and timing is feasible."""
    assigned_ids = [task.task_id for _, task in plan.selected]
    deferred_ids = [task.task_id for _, task, _ in plan.deferred]
    if sorted(assigned_ids + deferred_ids) != sorted(task.task_id for _, task in expected):
        raise RuntimeError("Plan did not account for every pending task.")
    if plan.minutes != sum(task.duration_minutes for _, task in plan.selected) or plan.minutes > budget:
        raise RuntimeError("Plan violated the minute budget.")
    intervals = sorted(interval(task) for _, task in plan.selected)
    if any(end > day_end for _, end in intervals):
        raise RuntimeError("Plan crossed midnight.")
    if any(left[1] > right[0] for left, right in zip(intervals, intervals[1:])):
        raise RuntimeError("Plan contains overlapping tasks.")
    if any(overlap(task, old) for _, task in plan.selected for old in carryover):
        raise RuntimeError("Plan overlaps care from the previous day.")


def recommend(owner, day, budget):
    """Plan, compare and verify two fixed-time schedules before recommending one."""
    if type(budget) is not int or not 0 <= budget <= 1440:
        raise ValueError("Budget must be a whole number from 0 to 1440.")
    if not date.min < day < date.max:
        raise ValueError("Choose a date that can be checked against adjacent days.")
    scheduler = Scheduler(owner)
    pending = scheduler.filter_tasks(day=day, completed=False)
    day_start = datetime.combine(day, time.min)
    day_end = day_start + timedelta(days=1)
    carryover = [
        task for _, task in scheduler.filter_tasks(completed=False)
        if task.due_date < day and interval(task)[1] > day_start
    ]
    priority = {"high": 0, "medium": 1, "low": 2}
    candidates = {
        "priority then time": scheduler.sort_by_priority(pending),
        "priority then duration": sorted(
            pending, key=lambda pair: (priority[pair[1].priority], pair[1].duration_minutes, pair[1].time)
        ),
    }
    plans = []
    for strategy, ordered in candidates.items():
        selected, deferred = [], []
        for pet, task in ordered:
            reason = rejection(task, selected, budget, day_end, carryover)
            if reason:
                deferred.append((pet, task, reason))
            else:
                selected.append((pet, task))
        minutes = sum(task.duration_minutes for _, task in selected)
        counts = tuple(sum(task.priority == level for _, task in selected) for level in priority)
        plan = Plan(strategy, scheduler.sort_by_time(selected), deferred, minutes, (*counts, -minutes))
        verify(plan, pending, budget, day_end, carryover)
        plans.append(plan)
    return max(plans, key=lambda plan: plan.score), plans
