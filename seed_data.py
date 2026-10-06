"""
seed_data.py – Insert 40 realistic fake survey responses into the database.
Run once:  python seed_data.py
"""

import random
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, insert_response, response_count
from scoring import full_score, load_cpi

random.seed(42)

AGE_BANDS     = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
INCOME_RANGES = ["Under £20k", "£20k-£35k", "£35k-£50k", "£50k-£75k", "Over £75k"]
FAMILY_SIZES  = [1, 2, 3, 4, 5, 6]
CATEGORIES    = ["food", "transport", "housing", "education",
                 "healthcare", "entertainment", "other"]
BEHAVIOURS    = ["cheaper_brands", "cut_non_essentials",
                 "fewer_shopping_trips", "delayed_big_purchases"]

# Spend profiles anchored to income bands (mean monthly spend, £)
INCOME_PROFILES = {
    "Under £20k":   {"food": 200, "transport": 80,  "housing": 600, "education": 30,  "healthcare": 50,  "entertainment": 40,  "other": 60},
    "£20k-£35k":    {"food": 300, "transport": 120, "housing": 800, "education": 60,  "healthcare": 70,  "entertainment": 80,  "other": 90},
    "£35k-£50k":    {"food": 400, "transport": 180, "housing": 1000,"education": 100, "healthcare": 90,  "entertainment": 120, "other": 120},
    "£50k-£75k":    {"food": 550, "transport": 250, "housing": 1400,"education": 200, "healthcare": 110, "entertainment": 200, "other": 180},
    "Over £75k":    {"food": 700, "transport": 350, "housing": 2000,"education": 350, "healthcare": 140, "entertainment": 350, "other": 280},
}

def jitter(value: float, pct: float = 0.30) -> float:
    """Add ±pct random noise to a value, clamp to minimum 0."""
    return max(0.0, value * (1 + random.uniform(-pct, pct)))


def make_response(cpi: dict) -> dict:
    age_band     = random.choice(AGE_BANDS)
    income_range = random.choice(INCOME_RANGES)
    family_size  = random.choice(FAMILY_SIZES)
    profile      = INCOME_PROFILES[income_range]

    # Scale spend by family size (larger families spend more, but not linearly)
    scale = 1 + (family_size - 1) * 0.18
    spend = {cat: round(jitter(val * scale), 2) for cat, val in profile.items()}

    # Randomly select 0-4 coping behaviours, weighted by income (lower → more)
    income_idx = INCOME_RANGES.index(income_range)
    n_behaviours = max(0, random.randint(0, 4) - income_idx // 2)
    behaviours = random.sample(BEHAVIOURS, min(n_behaviours, len(BEHAVIOURS)))

    score = full_score(spend, cpi, behaviours)

    return {
        "age_band":     age_band,
        "income_range": income_range,
        "family_size":  family_size,
        "spend":        spend,
        "behaviours":   behaviours,
        "score":        score,
    }


def main():
    init_db()
    existing = response_count()
    if existing >= 40:
        print(f"Database already has {existing} responses – skipping seed.")
        return

    cpi = load_cpi("data/cpi.csv")
    inserted = 0
    for i in range(40):
        r = make_response(cpi)
        insert_response(
            age_band=r["age_band"],
            income_range=r["income_range"],
            family_size=r["family_size"],
            spend=r["spend"],
            behaviours=r["behaviours"],
            score=r["score"],
        )
        inserted += 1
        label = r["score"]["label"]
        rate  = r["score"]["adjusted_rate"]
        print(f"  [{i+1:02d}] {r['age_band']:6s} | {r['income_range']:15s} | "
              f"family={r['family_size']} | rate={rate:.2f}% | {label}")

    print(f"\nDone! Seeded {inserted} responses into inflation_survey.db")


if __name__ == "__main__":
    main()
