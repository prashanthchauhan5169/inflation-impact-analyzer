"""
test_scoring.py – Unit tests for scoring.py
Run with:  python test_scoring.py  OR  python -m pytest test_scoring.py -v
"""

import unittest
from scoring import (
    compute_spend_shares,
    compute_personal_rate,
    coping_penalty,
    compute_adjusted_rate,
    classify_impact,
    category_impact_breakdown,
    full_score,
    COPING_PENALTIES,
)

# Shared fixture CPI dict (no file I/O needed in tests)
SAMPLE_CPI = {
    "food":          8.5,
    "transport":     6.2,
    "housing":       5.8,
    "education":     7.1,
    "healthcare":    9.4,
    "entertainment": 3.2,
    "other":         5.0,
    "headline":      6.4,
}

SAMPLE_SPEND = {
    "food":          400.0,
    "transport":     150.0,
    "housing":       800.0,
    "education":     100.0,
    "healthcare":    80.0,
    "entertainment": 60.0,
    "other":         50.0,
}  # total = 1640


class TestComputeSpendShares(unittest.TestCase):

    def test_shares_sum_to_one(self):
        shares = compute_spend_shares(SAMPLE_SPEND)
        self.assertAlmostEqual(sum(shares.values()), 1.0, places=6)

    def test_proportions_correct(self):
        shares = compute_spend_shares({"a": 100, "b": 300})
        self.assertAlmostEqual(shares["a"], 0.25, places=6)
        self.assertAlmostEqual(shares["b"], 0.75, places=6)

    def test_zero_total_returns_zeros(self):
        shares = compute_spend_shares({"food": 0, "housing": 0})
        for v in shares.values():
            self.assertEqual(v, 0.0)

    def test_single_category(self):
        shares = compute_spend_shares({"food": 500})
        self.assertAlmostEqual(shares["food"], 1.0, places=6)


class TestComputePersonalRate(unittest.TestCase):

    def test_known_value(self):
        # Simple 2-category: 50% food @8.5, 50% housing @5.8 → 7.15
        spend = {"food": 100, "housing": 100}
        cpi = {"food": 8.5, "housing": 5.8}
        rate = compute_personal_rate(spend, cpi)
        self.assertAlmostEqual(rate, 7.15, places=4)

    def test_rate_within_cpi_range(self):
        rate = compute_personal_rate(SAMPLE_SPEND, SAMPLE_CPI)
        cpi_values = [v for k, v in SAMPLE_CPI.items() if k != "headline"]
        self.assertGreaterEqual(rate, min(cpi_values) - 0.01)
        self.assertLessEqual(rate, max(cpi_values) + 0.01)

    def test_zero_spend_returns_zero(self):
        spend = {k: 0 for k in SAMPLE_SPEND}
        rate = compute_personal_rate(spend, SAMPLE_CPI)
        self.assertEqual(rate, 0.0)

    def test_unknown_category_uses_other(self):
        spend = {"widgetry": 100}
        cpi = {"other": 5.0, "headline": 6.4}
        rate = compute_personal_rate(spend, cpi)
        self.assertAlmostEqual(rate, 5.0, places=4)


class TestCopingPenalty(unittest.TestCase):

    def test_no_behaviours(self):
        self.assertEqual(coping_penalty([]), 0.0)

    def test_single_behaviour(self):
        self.assertAlmostEqual(
            coping_penalty(["cut_non_essentials"]),
            COPING_PENALTIES["cut_non_essentials"],
        )

    def test_all_behaviours(self):
        all_keys = list(COPING_PENALTIES.keys())
        expected = sum(COPING_PENALTIES.values())
        self.assertAlmostEqual(coping_penalty(all_keys), expected, places=6)

    def test_unknown_behaviour_ignored(self):
        self.assertEqual(coping_penalty(["nonexistent_key"]), 0.0)

    def test_penalty_non_negative(self):
        self.assertGreaterEqual(coping_penalty(list(COPING_PENALTIES)), 0.0)


class TestComputeAdjustedRate(unittest.TestCase):

    def test_adjusted_ge_personal(self):
        rate = compute_adjusted_rate(SAMPLE_SPEND, SAMPLE_CPI,
                                     ["cheaper_brands"])
        base = compute_personal_rate(SAMPLE_SPEND, SAMPLE_CPI)
        self.assertGreaterEqual(rate, base)

    def test_no_behaviours_equals_personal(self):
        rate = compute_adjusted_rate(SAMPLE_SPEND, SAMPLE_CPI, [])
        base = compute_personal_rate(SAMPLE_SPEND, SAMPLE_CPI)
        self.assertAlmostEqual(rate, base, places=4)


class TestClassifyImpact(unittest.TestCase):

    def test_high_when_much_above_headline(self):
        label, _ = classify_impact(10.0, 6.4)  # +3.6pp
        self.assertEqual(label, "High")

    def test_moderate_near_headline(self):
        label, _ = classify_impact(6.5, 6.4)   # +0.1pp
        self.assertEqual(label, "Moderate")

    def test_low_below_headline(self):
        label, _ = classify_impact(4.0, 6.4)   # -2.4pp
        self.assertEqual(label, "Low")

    def test_boundary_moderate_lower(self):
        # exactly h - 1.0 → Moderate
        label, _ = classify_impact(5.4, 6.4)
        self.assertEqual(label, "Moderate")

    def test_boundary_high_lower(self):
        # exactly h + 2.0 → High
        label, _ = classify_impact(8.4, 6.4)
        self.assertEqual(label, "High")

    def test_returns_string_explanation(self):
        _, explanation = classify_impact(8.0, 6.4)
        self.assertIsInstance(explanation, str)
        self.assertGreater(len(explanation), 10)


class TestCategoryImpactBreakdown(unittest.TestCase):

    def test_keys_match_spend(self):
        breakdown = category_impact_breakdown(SAMPLE_SPEND, SAMPLE_CPI)
        self.assertEqual(set(breakdown.keys()), set(SAMPLE_SPEND.keys()))

    def test_shares_sum_to_100(self):
        breakdown = category_impact_breakdown(SAMPLE_SPEND, SAMPLE_CPI)
        total_share = sum(v["share"] for v in breakdown.values())
        self.assertAlmostEqual(total_share, 100.0, places=1)  # rounding artefact ≤ 0.05

    def test_contribution_equals_share_times_rate(self):
        spend = {"food": 200, "housing": 200}
        cpi   = {"food": 8.0, "housing": 4.0, "headline": 6.0}
        bd = category_impact_breakdown(spend, cpi)
        self.assertAlmostEqual(bd["food"]["contribution"],
                               bd["food"]["share"] / 100 * 8.0, places=4)


class TestFullScore(unittest.TestCase):

    def test_returns_required_keys(self):
        result = full_score(SAMPLE_SPEND, SAMPLE_CPI, ["cheaper_brands"])
        for key in ("personal_rate", "penalty", "adjusted_rate",
                    "headline_rate", "label", "explanation", "breakdown"):
            self.assertIn(key, result)

    def test_adjusted_equals_personal_plus_penalty(self):
        result = full_score(SAMPLE_SPEND, SAMPLE_CPI, ["cut_non_essentials"])
        self.assertAlmostEqual(
            result["adjusted_rate"],
            result["personal_rate"] + result["penalty"],
            places=4,
        )

    def test_label_is_valid(self):
        result = full_score(SAMPLE_SPEND, SAMPLE_CPI, [])
        self.assertIn(result["label"], ("Low", "Moderate", "High"))

    def test_high_healthcare_spend_pushes_rate_up(self):
        # Skew heavily toward healthcare (highest CPI)
        heavy = {k: 50 for k in SAMPLE_SPEND}
        heavy["healthcare"] = 2000
        result = full_score(heavy, SAMPLE_CPI, [])
        self.assertGreater(result["personal_rate"], SAMPLE_CPI["headline"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
