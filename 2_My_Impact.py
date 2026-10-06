"""
pages/2_My_Impact.py – Personal inflation impact results.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from database import init_db, get_response
from scoring import full_score, load_cpi, category_impact_breakdown
from app_styles import inject_styles

st.set_page_config(page_title="My Impact – Inflation Impact Analyzer",
                   page_icon=None, layout="wide")
inject_styles()
init_db()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="page-header">
        <div class="section-label">Results</div>
        <h1>My Inflation Impact</h1>
        <p>Your personalised rate compared to the headline CPI, with a full 
           breakdown of which categories are driving the difference.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Session retrieval ─────────────────────────────────────────────────────────
if "score" not in st.session_state or "spend" not in st.session_state:
    if "response_id" in st.session_state:
        row = get_response(st.session_state["response_id"])
        if row:
            cpi_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    "data", "cpi.csv")
            cpi   = load_cpi(cpi_path)
            spend = {
                "food": row["spend_food"], "transport": row["spend_transport"],
                "housing": row["spend_housing"], "education": row["spend_education"],
                "healthcare": row["spend_healthcare"],
                "entertainment": row["spend_entertainment"],
                "other": row["spend_other"],
            }
            bmap = {
                "cheaper_brands":        row["coping_cheaper_brands"],
                "cut_non_essentials":    row["coping_cut_non_essentials"],
                "fewer_shopping_trips":  row["coping_fewer_shopping_trips"],
                "delayed_big_purchases": row["coping_delayed_big_purchases"],
            }
            behaviours = [k for k, v in bmap.items() if v]
            score = full_score(spend, cpi, behaviours)
            st.session_state.update(
                spend=spend, behaviours=behaviours, score=score,
                age_band=row["age_band"], income_range=row["income_range"],
                family_size=row["family_size"],
            )
    else:
        st.warning("No survey response found. Complete the **Survey** first.")
        st.stop()

score      = st.session_state["score"]
spend      = st.session_state["spend"]
behaviours = st.session_state.get("behaviours", [])
personal   = score["personal_rate"]
adjusted   = score["adjusted_rate"]
headline   = score["headline_rate"]
penalty    = score["penalty"]
label      = score["label"]
explanation= score["explanation"]
breakdown  = score["breakdown"]

badge_class = {"High": "badge-high", "Moderate": "badge-moderate",
               "Low": "badge-low"}[label]
delta       = round(adjusted - headline, 2)
delta_sign  = "+" if delta >= 0 else ""
delta_color = "#f87171" if delta > 0 else "#34d399" if delta < 0 else "#a0a0c0"

# ── KPI metrics ───────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Personal Rate", f"{personal:.2f}%",
              help="Weighted by your category spend shares")
with m2:
    st.metric("Adjusted Rate", f"{adjusted:.2f}%",
              delta=f"{delta_sign}{delta:.2f} pp vs headline",
              delta_color="inverse")
with m3:
    st.metric("Headline CPI", f"{headline:.1f}%",
              help="Published national CPI benchmark")
with m4:
    st.metric("Coping Penalty", f"+{penalty:.2f} pp",
              help="Added impact from financial stress indicators")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Gauge + classification ─────────────────────────────────────────────────────
gauge_col, info_col = st.columns([1, 1.6], gap="large")

with gauge_col:
    gauge_color = {"High": "#e05252", "Moderate": "#d97706", "Low": "#10b981"}[label]

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=adjusted,
        delta={
            "reference":   headline,
            "valueformat": ".2f",
            "suffix":      " pp",
            "increasing":  {"color": "#f87171"},
            "decreasing":  {"color": "#34d399"},
        },
        number={"suffix": "%", "font": {"size": 44, "color": "#1e293b",
                                         "family": "Inter"}},
        gauge={
            "axis": {
                "range":     [0, 15],
                "tickwidth": 1,
                "tickcolor": "#cbd5e1",
                "tickfont":  {"color": "#64748b", "size": 10},
                "nticks":    6,
            },
            "bar":   {"color": gauge_color, "thickness": 0.22},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, headline - 1],         "color": "rgba(16,185,129,0.1)"},
                {"range": [headline - 1, headline + 2], "color": "rgba(217,119,6,0.1)"},
                {"range": [headline + 2, 15],        "color": "rgba(224,82,82,0.1)"},
            ],
            "threshold": {
                "line":      {"color": "#6b6b9e", "width": 2},
                "thickness": 0.72,
                "value":     headline,
            },
        },
        title={
            "text": "Rate vs Headline CPI",
            "font": {"color": "#64748b", "size": 12, "family": "Inter"},
        },
    ))
    fig_gauge.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#e2e2ef",
        height=300,
        margin=dict(t=50, b=20, l=20, r=20),
    )
    st.plotly_chart(fig_gauge, use_container_width=True)

with info_col:
    behaviour_labels = {
        "cheaper_brands":        "Switched to cheaper brands",
        "cut_non_essentials":    "Cut non-essential spending",
        "fewer_shopping_trips":  "Reduced shopping trips",
        "delayed_big_purchases": "Delayed major purchases",
    }
    pills = "".join(
        f'<span class="behaviour-pill">{behaviour_labels[b]}</span>'
        for b in behaviours if b in behaviour_labels
    ) if behaviours else '<span style="color:#4e4e72;font-size:0.84rem;">None selected</span>'

    st.markdown(
        f"""
        <div class="card" style="height:100%;box-sizing:border-box;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
                <div class="card-title" style="margin:0;">Impact Classification</div>
                <span class="impact-badge {badge_class}">{label} Impact</span>
            </div>
            <p style="color:#a0a0c0;line-height:1.75;font-size:0.92rem;margin:0 0 1.2rem;">
                {explanation}
            </p>
            <div style="border-top:1px solid #1e1e35;padding-top:1rem;">
                <div style="font-size:0.72rem;font-weight:700;letter-spacing:0.08em;
                            text-transform:uppercase;color:#5b5b85;margin-bottom:0.5rem;">
                    Coping strategies applied
                    {f'<span style="color:#4e4e72;font-weight:400;"> · +{penalty:.2f} pp penalty</span>' if penalty else ''}
                </div>
                {pills}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ── Waterfall ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Rate composition</div>', unsafe_allow_html=True)
st.markdown("### How your rate is built up")

cats      = list(breakdown.keys())
contribs  = [breakdown[c]["contribution"] for c in cats]
labels_wf = [c.capitalize() for c in cats] + ["Coping Penalty", "Adjusted Total"]
measures  = ["relative"] * len(cats) + ["relative", "total"]
values_wf = contribs + [penalty, adjusted]

CHART_COLORS = {
    "paper_bg":  "rgba(0,0,0,0)",
    "plot_bg":   "rgba(255,255,255,0.0)",
    "grid":      "rgba(226,232,240,1)",
    "font":      "#334155",
    "axis_tick": "#64748b",
}

fig_wf = go.Figure(go.Waterfall(
    orientation="v",
    measure=measures,
    x=labels_wf,
    y=values_wf,
    connector={"line": {"color": "rgba(46,46,82,0.8)", "width": 1, "dash": "dot"}},
    increasing={"marker": {"color": "#5b4dff", "line": {"width": 0}}},
    decreasing={"marker": {"color": "#10b981", "line": {"width": 0}}},
    totals={"marker": {"color": "#7c6dff", "line": {"width": 0}}},
    text=[f"{v:.3f}" for v in values_wf],
    textfont={"color": "#1e293b", "size": 11},
    textposition="outside",
))
fig_wf.add_hline(
    y=headline,
    line_dash="dash",
    line_color="#d97706",
    line_width=1.5,
    annotation_text=f"  Headline {headline:.1f}%",
    annotation_font_color="#d97706",
    annotation_font_size=11,
)
fig_wf.update_layout(
    paper_bgcolor=CHART_COLORS["paper_bg"],
    plot_bgcolor=CHART_COLORS["plot_bg"],
    font={"color": CHART_COLORS["font"], "family": "Inter"},
    height=400,
    yaxis=dict(
        title="Contribution (pp)",
        gridcolor=CHART_COLORS["grid"],
        tickfont={"color": CHART_COLORS["axis_tick"], "size": 11},
        title_font={"color": CHART_COLORS["axis_tick"], "size": 11},
        zeroline=True, zerolinecolor="#cbd5e1", zerolinewidth=1,
    ),
    xaxis=dict(
        gridcolor="rgba(0,0,0,0)",
        tickfont={"color": "#a0a0c0", "size": 11},
    ),
    margin=dict(t=20, b=10, l=10, r=10),
    showlegend=False,
)
st.plotly_chart(fig_wf, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Breakdown table ───────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Detailed breakdown</div>', unsafe_allow_html=True)
st.markdown("### Category breakdown table")

df = pd.DataFrame([
    {
        "Category":           cat.capitalize(),
        "Monthly Spend (₹)":  f"₹{spend.get(cat, 0):,.0f}",
        "Spend Share":        f"{breakdown[cat]['share']:.1f}%",
        "CPI Rate":           f"{breakdown[cat]['cpi_rate']:.1f}%",
        "Contribution (pp)":  f"{breakdown[cat]['contribution']:.4f}",
    }
    for cat in cats
])
st.dataframe(df, use_container_width=True, hide_index=True)
