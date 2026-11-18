import unittest
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

from care_planner import recommend, verify
from pawpal_system import Owner, Task

DAY = date(2026, 11, 18)
FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "morning.json"


class CarePlannerTests(unittest.TestCase):
    def setUp(self):
        self.owner = Owner.load_from_json(FIXTURE)

    def test_comparison_selects_more_high_priority_tasks(self):
        plan, candidates = recommend(self.owner, DAY, 25)
        self.assertEqual([candidate.score[0] for candidate in candidates], [1, 2])
        self.assertEqual(plan.minutes, 25)
        self.assertEqual([task.title for _, task in plan.selected],
                         ["Breakfast", "Refill water", "Brush coat"])
        self.assertIn("overlaps", plan.deferred[0][2])

    def test_zero_budget_defers_every_task(self):
        plan, _ = recommend(self.owner, DAY, 0)
        self.assertFalse(plan.selected)
        self.assertEqual(len(plan.deferred), 4)
        self.assertTrue(all("budget" in reason for _, _, reason in plan.deferred))

    def test_invalid_budget_fails(self):
        with self.assertRaisesRegex(ValueError, "Budget"):
            recommend(self.owner, DAY, -1)

    def test_no_tasks_on_another_day(self):
        plan, _ = recommend(self.owner, DAY + timedelta(days=1), 25)
        self.assertEqual((plan.selected, plan.deferred, plan.minutes), ([], [], 0))

    def test_carryover_blocks_a_morning_task(self):
        pet = self.owner.pets[0]
        pet.add_task(Task("Previous care", "23:50", DAY - timedelta(days=1), 20))
        pet.add_task(Task("Early care", "00:00", DAY, 5))
        plan, _ = recommend(self.owner, DAY, 60)
        reasons = {task.title: reason for _, task, reason in plan.deferred}
        self.assertIn("previous day", reasons["Early care"])

    def test_verifier_rejects_bad_total(self):
        from datetime import datetime, time
        plan, _ = recommend(self.owner, DAY, 25)
        with self.assertRaisesRegex(RuntimeError, "budget"):
            verify(replace(plan, minutes=24), self.owner.get_all_tasks(), 25,
                   datetime.combine(DAY + timedelta(days=1), time.min), [])

    def test_planner_does_not_mutate_owner(self):
        from dataclasses import asdict
        before = asdict(self.owner)
        recommend(self.owner, DAY, 25)
        self.assertEqual(asdict(self.owner), before)
