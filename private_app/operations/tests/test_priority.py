from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from operations.enums import PriorityLevel
from operations.models import BusinessConfig
from operations.priorities import calculate_priority, indicative_price, time_component

from .factories import mission, owner, prerequisite, tenant


class PriorityEngineTests(TestCase):
    def setUp(self):
        self.owner = owner()
        self.tenant = tenant("Alpha")
        self.mission = mission(self.tenant)
        self.config = BusinessConfig.get_solo()

    def test_formula_and_thresholds(self):
        item = prerequisite(
            self.mission,
            self.owner,
            client_criticality=3,
            due_hours=24,
            confirmation_score=3,
            dependency_score=1,
            inertia_score=1,
        )
        result = calculate_priority(item, self.config)
        self.assertEqual(result.score, Decimal("14.00"))
        self.assertEqual(result.level, PriorityLevel.P0)

    def test_unknown_input_stays_unknown(self):
        item = prerequisite(self.mission, self.owner, client_criticality=None)
        result = calculate_priority(item, self.config)
        self.assertEqual(result.level, PriorityLevel.UNKNOWN)
        self.assertIsNone(result.score)
        self.assertIn("criticité client", result.explanation)

    def test_time_buckets_cover_49_hours_without_invented_gap(self):
        now = timezone.now()
        self.assertEqual(time_component(now + timedelta(hours=48), self.config, now), 3)
        self.assertEqual(time_component(now + timedelta(hours=49), self.config, now), 2)
        self.assertEqual(time_component(now + timedelta(days=6), self.config, now), 1)
        self.assertEqual(time_component(now + timedelta(days=11), self.config, now), 0)

    def test_overdue_missing_confirmation_is_p0_override(self):
        item = prerequisite(self.mission, self.owner, due_hours=-2)
        result = calculate_priority(item, self.config)
        self.assertEqual(result.level, PriorityLevel.P0)
        self.assertTrue(result.overridden)
        self.assertIsNone(result.score)

    def test_manual_override_requires_reason(self):
        item = prerequisite(self.mission, self.owner)
        item.manual_p0_override = True
        item.override_reason = ""
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_indicative_prices_are_valid_currency_amounts_for_every_urgency(self):
        now = timezone.now()
        cases = [
            (2, Decimal("3000.00")),
            (5, Decimal("2250.00")),
            (10, Decimal("1875.00")),
            (20, Decimal("1500.00")),
        ]
        for days, expected in cases:
            with self.subTest(days=days):
                self.mission.protected_at = now + timedelta(days=days)
                amount, size, _ = indicative_price(self.mission, self.config, now=now)
                self.assertEqual(amount, expected)
                self.assertEqual(amount.as_tuple().exponent, -2)
                self.assertEqual(size, "S")
