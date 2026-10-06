"""
pages/1_Survey.py – Survey form page.
"""

import streamlit as st
from database import init_db, insert_response
from scoring import full_score, load_cpi
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

st.set_page_config(page_title="Survey – Inflation Impact Analyzer",
                   page_icon=None, layout="wide")

from app_styles import inject_styles
inject_styles()
init_db()

# ── Constants ──────────────────────────────────────────────────────────────────
CATEGORIES = ["food", "transport", "housing", "education",
              "healthcare", "entertainment", "other"]
CATEGORY_LABELS = {
    "food":          "Food & Groceries",
    "transport":     "Transport",
    "housing":       "Housing (rent / mortgage + utilities)",
    "education":     "Education",
    "healthcare":    "Healthcare",
    "entertainment": "Entertainment & Leisure",
    "other":         "Other",
}
CATEGORY_HINTS = {
    "food":          "Supermarkets, takeaways, dining",
    "transport":     "Fuel, fares, car costs",
    "housing":       "Rent, mortgage, bills",
    "education":     "Fees, books, tutoring",
    "healthcare":    "Prescriptions, dentist, insurance",
    "entertainment": "Subscriptions, nights out, hobbies",
    "other":         "Clothing, personal care, misc",
}
AGE_BANDS     = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
INCOME_RANGES = ["Under ₹20k", "₹20k-₹35k", "₹35k-₹50k", "₹50k-₹75k", "Over ₹75k"]

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <div class="section-label">Step 1 of 1</div>
        <h1>Household Survey</h1>
        <p>Enter your details below. All data is stored locally in SQLite — 
           nothing is sent externally.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Form ──────────────────────────────────────────────────────────────────────
with st.form("survey_form", clear_on_submit=False):

    # Section 1: Demographics
    st.markdown('<div class="form-section-title">Profile</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns([1.5, 2, 1.5, 3])
    with c1:
        age_band = st.selectbox("Age band", AGE_BANDS, index=1)
    with c2:
        income_range = st.selectbox("Annual household income", INCOME_RANGES, index=1)
    with c3:
        family_size = st.number_input("Household size", min_value=1, max_value=20,
                                      value=2, step=1,
                                      help="Number of people living in your household")

    # Section 2: Spending
    st.markdown('<div class="form-section-title">Monthly Spending (₹)</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#4e4e72;font-size:0.87rem;margin:-0.3rem 0 1rem;'>"
        "Enter your estimated average monthly spend. Leave a category as 0 if it does not apply.</p>",
        unsafe_allow_html=True,
    )

    spend_values: dict[str, float] = {}
    row1_cols = st.columns(4)
    row2_cols = st.columns(3)

    for i, cat in enumerate(CATEGORIES):
        col = row1_cols[i] if i < 4 else row2_cols[i - 4]
        with col:
            st.markdown(
                f"<div style='font-size:0.82rem;color:#5b5b85;margin-bottom:0.1rem;'>"
                f"{CATEGORY_HINTS[cat]}</div>",
                unsafe_allow_html=True,
            )
            spend_values[cat] = st.number_input(
                CATEGORY_LABELS[cat],
                min_value=0.0, max_value=50_000.0,
                value=0.0, step=10.0, format="%.0f",
                key=f"spend_{cat}",
            )

    # Section 3: Coping behaviours
    st.markdown('<div class="form-section-title">Coping Strategies</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#4e4e72;font-size:0.87rem;margin:-0.3rem 0 1rem;'>"
        "Select any strategies you have adopted in the past 6 months to manage rising prices.</p>",
        unsafe_allow_html=True,
    )
    bc1, bc2 = st.columns(2)
    with bc1:
        b_cheaper = st.checkbox("Switched to cheaper / own-label products", key="b_cheaper")
        b_cut     = st.checkbox("Cut back on non-essential spending",        key="b_cut")
    with bc2:
        b_trips   = st.checkbox("Reduced or planned shopping trips more carefully", key="b_trips")
        b_delay   = st.checkbox("Delayed big purchases (car, appliances, holidays)", key="b_delay")

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
    submitted = st.form_submit_button("Calculate my inflation impact",
                                      use_container_width=True)

# ── Validation & processing ───────────────────────────────────────────────────
if submitted:
    errors = []
    total_spend = sum(spend_values.values())

    if total_spend <= 0:
        errors.append("Please enter at least one spending category amount greater than zero.")

    if errors:
        for e in errors:
            st.error(e)
    else:
        behaviours = []
        if b_cheaper: behaviours.append("cheaper_brands")
        if b_cut:     behaviours.append("cut_non_essentials")
        if b_trips:   behaviours.append("fewer_shopping_trips")
        if b_delay:   behaviours.append("delayed_big_purchases")

        cpi_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                "data", "cpi.csv")
        cpi   = load_cpi(cpi_path)
        score = full_score(spend_values, cpi, behaviours)

        resp_id = insert_response(
            age_band=age_band,
            income_range=income_range,
            family_size=int(family_size),
            spend=spend_values,
            behaviours=behaviours,
            score=score,
        )

        st.session_state.update(
            response_id=resp_id,
            spend=spend_values,
            behaviours=behaviours,
            score=score,
            age_band=age_band,
            income_range=income_range,
            family_size=int(family_size),
        )

        label       = score["label"]
        badge_class = {"High": "badge-high", "Moderate": "badge-moderate",
                       "Low": "badge-low"}[label]

        # Result summary card
        behaviour_pills = "".join(
            f'<span class="behaviour-pill">{b.replace("_"," ").title()}</span>'
            for b in behaviours
        ) or '<span style="color:#4e4e72;font-size:0.85rem;">None selected</span>'

        st.markdown(
            f"""
            <div class="card" style="margin-top:1.2rem; border-color:#2e2e52;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.8rem;">
                    <div>
                        <div class="card-title">Response recorded</div>
                        <div style="font-size:1.6rem; font-weight:800; color:#e2e2ef; letter-spacing:-0.02em;">
                            {score['adjusted_rate']:.2f}%
                        </div>
                        <div style="color:#4e4e72; font-size:0.85rem; margin-top:0.25rem;">
                            Personal inflation rate &nbsp;·&nbsp; Headline: {score['headline_rate']:.1f}%
                        </div>
                    </div>
                    <span class="impact-badge {badge_class}">{label} Impact</span>
                </div>
                <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid #1e1e35;">
                    <div style="font-size:0.75rem; color:#5b5b85; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:0.5rem; font-weight:600;">
                        Coping strategies
                    </div>
                    {behaviour_pills}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.success("Saved. Navigate to **My Impact** in the sidebar to see your full results.")
