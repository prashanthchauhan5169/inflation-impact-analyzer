"""
scoring.py – Pure scoring logic for the Inflation Impact Analyzer.

All functions are side-effect-free for easy unit testing.
"""

from __future__ import annotations
import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATEGORIES = ["food", "transport", "housing", "education",
               "healthcare", "entertainment", "other"]

# Penalty (percentage-points added to personal rate) for each coping behaviour.
# Behaviours reduce real spending but signal strain; we bump the impact score
# slightly to reflect financial stress.
COPING_PENALTIES: dict[str, float] = {
    "cheaper_brands":         0.15,
    "cut_non_essentials":     0.20,
    "fewer_shopping_trips":   0.10,
    "delayed_big_purchases":  0.25,
}

IMPACT_THRESHOLDS = {
    "High":     lambda pr, h: pr >= h + 2.0,
    "Moderate": lambda pr, h: h - 1.0 <= pr < h + 2.0,
    "Low":      lambda pr, h: pr < h - 1.0,
}

EXPLANATIONS = {
    "High": (
        "Your personal inflation rate is significantly above the headline CPI. "
        "This is typically driven by high spending in fast-rising categories such as "
        "healthcare or food, and is compounded by coping behaviours that signal "
        "financial strain. Consider reviewing your highest-impact categories first."
    ),
    "Moderate": (
        "Your personal inflation rate is broadly in line with the headline figure. "
        "Some categories are eating into your budget more than others — check the "
        "Category Analysis page to see where the pressure is coming from."
    ),
    "Low": (
        "Your personal inflation rate is below the headline CPI. Your spending mix "
        "tilts toward categories that have seen slower price rises, which gives you "
        "a relative cushion. Keep an eye on healthcare and food, which can shift "
        "this picture quickly."
    ),
}

# ---------------------------------------------------------------------------
# CPI loader
# ---------------------------------------------------------------------------

def load_cpi(path: str | Path = "data/cpi.csv") -> dict[str, float]:
    """Load CPI rates from a CSV file.

    Expected columns: category, annual_rate
    Returns a dict mapping category name → float rate (%).
    The 'headline' entry is kept as-is.
    """
    result: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            result[row["category"].strip().lower()] = float(row["annual_rate"])
    return result


# ---------------------------------------------------------------------------
# Core scoring helpers
# ---------------------------------------------------------------------------

def compute_spend_shares(spend: dict[str, float]) -> dict[str, float]:
    """Convert raw monthly spend values to fractional shares (sum to 1.0).

    Args:
        spend: dict mapping category → monthly spend (£ or any currency unit).

    Returns:
        dict mapping category → share [0, 1].  Returns all-zero dict if total
        spend is zero.
    """
    total = sum(spend.values())
    if total == 0:
        return {k: 0.0 for k in spend}
    return {k: v / total for k, v in spend.items()}


def compute_personal_rate(
    spend: dict[str, float],
    cpi: dict[str, float],
) -> float:
    """Compute the user's personal inflation rate.

    Personal rate = Σ (spend_share_i × cpi_rate_i)

    Args:
        spend: dict category → monthly spend amount.
        cpi:   dict category → annual inflation rate (%).

    Returns:
        Weighted personal inflation rate (%).
    """
    shares = compute_spend_shares(spend)
    rate = 0.0
    for category, share in shares.items():
        cat_cpi = cpi.get(category.lower(), cpi.get("other", 5.0))
        rate += share * cat_cpi
    return round(rate, 4)


def coping_penalty(behaviours: list[str]) -> float:
    """Return total penalty (pp) for selected coping behaviours.

    Args:
        behaviours: list of behaviour keys (see COPING_PENALTIES).

    Returns:
        Total penalty in percentage points.
    """
    return sum(COPING_PENALTIES.get(b, 0.0) for b in behaviours)


def compute_adjusted_rate(
    spend: dict[str, float],
    cpi: dict[str, float],
    behaviours: list[str],
) -> float:
    """Personal rate + coping-behaviour penalty.

    Args:
        spend:      category → monthly spend.
        cpi:        category → CPI rate.
        behaviours: selected coping behaviour keys.

    Returns:
        Adjusted personal inflation rate (%).
    """
    base = compute_personal_rate(spend, cpi)
    penalty = coping_penalty(behaviours)
    return round(base + penalty, 4)


def classify_impact(
    personal_rate: float,
    headline_rate: float,
) -> tuple[str, str]:
    """Classify the impact level given personal and headline rates.

    Args:
        personal_rate: adjusted personal inflation rate (%).
        headline_rate: published headline CPI rate (%).

    Returns:
        Tuple of (label, explanation) where label ∈ {"Low","Moderate","High"}.
    """
    for label, condition in IMPACT_THRESHOLDS.items():
        if condition(personal_rate, headline_rate):
            return label, EXPLANATIONS[label]
    # Fallback (should not happen with the three inclusive thresholds)
    return "Moderate", EXPLANATIONS["Moderate"]


def category_impact_breakdown(
    spend: dict[str, float],
    cpi: dict[str, float],
) -> dict[str, dict[str, float]]:
    """Return per-category contribution to personal rate.

    Returns a dict: category → {"share": x, "cpi_rate": y, "contribution": z}
    contribution = share × cpi_rate
    """
    shares = compute_spend_shares(spend)
    result = {}
    for cat, share in shares.items():
        cpi_rate = cpi.get(cat.lower(), cpi.get("other", 5.0))
        result[cat] = {
            "share": round(share * 100, 2),          # as %
            "cpi_rate": cpi_rate,
            "contribution": round(share * cpi_rate, 4),
        }
    return result


# ---------------------------------------------------------------------------
# Convenience: full pipeline
# ---------------------------------------------------------------------------

def full_score(
    spend: dict[str, float],
    cpi: dict[str, float],
    behaviours: list[str],
) -> dict:
    """Run the complete scoring pipeline.

    Returns a dict with:
        personal_rate, penalty, adjusted_rate, headline_rate,
        label, explanation, breakdown
    """
    personal_rate = compute_personal_rate(spend, cpi)
    penalty = coping_penalty(behaviours)
    adjusted = round(personal_rate + penalty, 4)
    headline = cpi.get("headline", 6.4)
    label, explanation = classify_impact(adjusted, headline)
    breakdown = category_impact_breakdown(spend, cpi)

    return {
        "personal_rate":  personal_rate,
        "penalty":        penalty,
        "adjusted_rate":  adjusted,
        "headline_rate":  headline,
        "label":          label,
        "explanation":    explanation,
        "breakdown":      breakdown,
    }
