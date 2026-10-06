"""
app.py – Main entry point for the Inflation Impact Analyzer.

Run with:
    streamlit run app.py
"""

import streamlit as st
from database import init_db

st.set_page_config(
    page_title="Inflation Impact Analyzer",
    page_icon="data/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

from app_styles import inject_styles
inject_styles()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header" style="border-bottom:none; padding-bottom:0;">
        <div class="section-label">Personal Finance Tool</div>
        <h1>Inflation Impact Analyzer</h1>
        <p style="max-width:580px;">
            Go beyond the headline CPI figure. Enter your household's spending
            and discover your <strong style="color:#c4b5fd;">personal inflation rate</strong>
            — and what you can do about it.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

# ── How it works strip ────────────────────────────────────────────────────────
cols = st.columns(5)
nav_items = [
    ("01", "Survey",            "Enter your monthly spending across 7 categories"),
    ("02", "My Impact",         "See your personal rate vs the headline CPI"),
    ("03", "Category Analysis", "Drill into which categories drive your exposure"),
    ("04", "Dashboard",         "Explore aggregate trends across all respondents"),
    ("05", "Export",            "Download your results as CSV or PDF"),
]

for col, (num, title, desc) in zip(cols, nav_items):
    with col:
        st.markdown(
            f"""
            <div class="nav-card">
                <div class="nc-icon"
                     style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;
                            font-weight:700;color:#5b4dff;">
                    {num}
                </div>
                <div class="nc-title">{title}</div>
                <div class="nc-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<hr>", unsafe_allow_html=True)

# ── About section ─────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    st.markdown("### How the score is calculated")
    st.markdown(
        """
        The standard CPI measures price changes using a national average spending basket.
        But your basket is different — you might spend more on healthcare than transport,
        or more on food than education.

        This tool computes your **personal inflation rate** by weighting each category's
        inflation by *your* share of spend, then applies a small adjustment for any
        financial coping behaviours you've adopted (switching brands, cutting discretionary
        spend, etc.), which signal additional strain beyond the raw rate.

        The result is classified as **Low**, **Moderate**, or **High** relative to the
        published headline CPI.
        """,
        unsafe_allow_html=False,
    )

with right:
    st.markdown("### Quick start")
    st.markdown(
        """
        1. Open **Survey** in the sidebar  
        2. Enter your monthly spend per category  
        3. Tick any coping behaviours that apply  
        4. Submit — then navigate to **My Impact**
        """,
    )
    st.info(
        "The dashboard is pre-loaded with 40 realistic sample responses "
        "so you can explore aggregate trends straight away.",
        icon=None,
    )

st.markdown(
    "<p style='color:#2e2e52;font-size:0.75rem;margin-top:2rem;'>CPI data is placeholder. "
    "Replace data/cpi.csv with official ONS / BLS figures.</p>",
    unsafe_allow_html=True,
)
