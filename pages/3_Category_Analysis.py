"""
pages/3_Category_Analysis.py – Category spend vs inflation analysis.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from database import init_db
from scoring import load_cpi, category_impact_breakdown
from app_styles import inject_styles

st.set_page_config(page_title="Category Analysis – Inflation Impact Analyzer",
                   page_icon=None, layout="wide")
inject_styles()
init_db()

st.markdown(
    """
    <div class="page-header">
        <div class="section-label">Analysis</div>
        <h1>Category Analysis</h1>
        <p>Explore how your spending mix interacts with category inflation rates 
           and which categories are contributing most to your personal rate.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────────
if "spend" not in st.session_state:
    st.warning("No survey data found. Complete the **Survey** first.")
    st.stop()

spend     = st.session_state["spend"]
cpi_path  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cpi.csv")
cpi       = load_cpi(cpi_path)
headline  = cpi.get("headline", 6.4)
breakdown = category_impact_breakdown(spend, cpi)

rows = []
for cat, info in breakdown.items():
    rows.append({
        "Category":        cat.capitalize(),
        "Spend Share (%)": info["share"],
        "CPI Rate (%)":    info["cpi_rate"],
        "Contribution":    info["contribution"],
        "Monthly Spend":   spend.get(cat, 0),
    })
df = pd.DataFrame(rows).sort_values("Contribution", ascending=False)

# Palette — indigo family with semantic overrides
PALETTE = ["#5b4dff","#7c6dff","#9e90ff","#b8b0ff","#10b981","#d97706","#e05252"]
CAT_COLORS = {
    "Food":          "#5b4dff",
    "Transport":     "#4f86c6",
    "Housing":       "#0ea5c9",
    "Education":     "#10b981",
    "Healthcare":    "#e05252",
    "Entertainment": "#d97706",
    "Other":         "#8b7aff",
}
df["Color"] = df["Category"].map(CAT_COLORS).fillna("#5b4dff")

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#334155", "family": "Inter"},
    margin=dict(t=20, b=10, l=10, r=10),
)
GRID_COLOR = "rgba(226,232,240,1)"
TICK_COLOR = "#64748b"

# ── Chart 1: Grouped bar ──────────────────────────────────────────────────────
st.markdown('<div class="section-label">Spend share vs inflation</div>',
            unsafe_allow_html=True)
st.markdown("### Your spending weight vs category CPI rate")

fig1 = go.Figure()
fig1.add_trace(go.Bar(
    name="Spend Share (%)",
    x=df["Category"],
    y=df["Spend Share (%)"],
    marker=dict(color="#5b4dff",
                line=dict(width=0)),
    text=df["Spend Share (%)"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    textfont=dict(size=11, color="#a0a0c0"),
))
fig1.add_trace(go.Bar(
    name="CPI Rate (%)",
    x=df["Category"],
    y=df["CPI Rate (%)"],
    marker=dict(color="#10b981",
                line=dict(width=0)),
    text=df["CPI Rate (%)"].apply(lambda x: f"{x:.1f}%"),
    textposition="outside",
    textfont=dict(size=11, color="#a0a0c0"),
))
fig1.add_hline(y=headline, line_dash="dash", line_color="#d97706", line_width=1.5,
               annotation_text=f"  Headline {headline:.1f}%",
               annotation_font_color="#d97706", annotation_font_size=11)
fig1.update_layout(
    **CHART_BASE,
    barmode="group",
    height=400,
    bargap=0.25,
    bargroupgap=0.08,
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#9090b8",
                orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(color=TICK_COLOR, size=11),
               title="Percentage (%)", title_font=dict(color=TICK_COLOR, size=11),
               zeroline=False),
    xaxis=dict(gridcolor="rgba(0,0,0,0)",
               tickfont=dict(color="#a0a0c0", size=11)),
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Charts 2 + 3: Contribution bar | Donut ────────────────────────────────────
left_col, right_col = st.columns(2, gap="large")

with left_col:
    st.markdown('<div class="section-label">Biggest drivers</div>', unsafe_allow_html=True)
    st.markdown("### Contribution to your personal rate")

    df_sorted = df.sort_values("Contribution")
    fig2 = go.Figure(go.Bar(
        x=df_sorted["Contribution"],
        y=df_sorted["Category"],
        orientation="h",
        marker=dict(
            color=df_sorted["Contribution"],
            colorscale=[[0, "#10b981"], [0.4, "#d97706"], [1, "#e05252"]],
            showscale=True,
            colorbar=dict(
                title="pp",
                tickfont=dict(color=TICK_COLOR, size=10),
                titlefont=dict(color=TICK_COLOR, size=10),
                thickness=10,
                len=0.7,
            ),
            line=dict(width=0),
        ),
        text=df_sorted["Contribution"].apply(lambda x: f"{x:.3f} pp"),
        textposition="outside",
        textfont=dict(size=11, color="#a0a0c0"),
    ))
    fig2.update_layout(
        **CHART_BASE,
        height=360,
        xaxis=dict(title="Contribution (pp)",
                   gridcolor=GRID_COLOR,
                   tickfont=dict(color=TICK_COLOR, size=11),
                   title_font=dict(color=TICK_COLOR, size=11),
                   zeroline=True, zerolinecolor="#cbd5e1"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)",
                   tickfont=dict(color="#a0a0c0", size=11)),
        margin=dict(t=10, b=10, l=10, r=80),
    )
    st.plotly_chart(fig2, use_container_width=True)

with right_col:
    st.markdown('<div class="section-label">Budget split</div>', unsafe_allow_html=True)
    st.markdown("### Monthly spending distribution")

    df_pie = df[df["Monthly Spend"] > 0]
    fig3 = go.Figure(go.Pie(
        labels=df_pie["Category"],
        values=df_pie["Monthly Spend"],
        hole=0.52,
        marker=dict(
            colors=[CAT_COLORS.get(c, "#5b4dff") for c in df_pie["Category"]],
            line=dict(color="#ffffff", width=3),
        ),
        textinfo="label+percent",
        textfont=dict(color="#c0c0dc", size=11),
        insidetextorientation="radial",
        hovertemplate="<b>%{label}</b><br>₹%{value:,.0f} / month<br>%{percent}<extra></extra>",
    ))
    fig3.update_layout(
        **CHART_BASE,
        showlegend=False,
        height=360,
        annotations=[dict(
            text="Budget<br>Split",
            x=0.5, y=0.5,
            font=dict(size=13, color="#64748b", family="Inter"),
            showarrow=False,
        )],
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Radar ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Coverage view</div>', unsafe_allow_html=True)
st.markdown("### Radar — spend share vs CPI exposure")

categories_r = df["Category"].tolist()
spend_r      = df["Spend Share (%)"].tolist()
cpi_r        = df["CPI Rate (%)"].tolist()
max_cpi      = max(cpi_r) if cpi_r else 1
cpi_norm     = [v / max_cpi * 100 for v in cpi_r]

fig_radar = go.Figure()
fig_radar.add_trace(go.Scatterpolar(
    r=spend_r + [spend_r[0]],
    theta=categories_r + [categories_r[0]],
    fill="toself",
    name="Spend Share (%)",
    line=dict(color="#5b4dff", width=2),
    fillcolor="rgba(91,77,255,0.18)",
))
fig_radar.add_trace(go.Scatterpolar(
    r=cpi_norm + [cpi_norm[0]],
    theta=categories_r + [categories_r[0]],
    fill="toself",
    name="CPI Rate (normalised to 100)",
    line=dict(color="#10b981", width=2),
    fillcolor="rgba(16,185,129,0.12)",
))
fig_radar.update_layout(
    **CHART_BASE,
    polar=dict(
        bgcolor="rgba(248,250,252,0.5)",
        radialaxis=dict(
            visible=True,
            color="#cbd5e1",
            gridcolor="rgba(226,232,240,0.8)",
            tickfont=dict(color=TICK_COLOR, size=9),
        ),
        angularaxis=dict(
            color="#64748b",
            gridcolor="rgba(226,232,240,0.8)",
            tickfont=dict(color="#9090b8", size=11),
        ),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#9090b8",
                orientation="h", yanchor="bottom", y=1.02, x=0.5, xanchor="center"),
    height=420,
    margin=dict(t=50, b=20),
)
st.plotly_chart(fig_radar, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Insight cards ─────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Key findings</div>', unsafe_allow_html=True)
st.markdown("### Key insights")

top_hurt  = df.iloc[0]
big_spend = df.sort_values("Monthly Spend", ascending=False).iloc[0]
above_cpi = df[df["CPI Rate (%)"] > headline]
cats_above = ", ".join(above_cpi["Category"].tolist()) if len(above_cpi) else "None"

col_a, col_b, col_c = st.columns(3, gap="medium")
with col_a:
    st.markdown(
        f"""
        <div class="insight-card red">
            <div class="ic-label">Biggest rate contributor</div>
            <div class="ic-value">{top_hurt["Category"]}</div>
            <div class="ic-sub">{top_hurt["Contribution"]:.4f} pp contribution to your rate</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_b:
    st.markdown(
        f"""
        <div class="insight-card">
            <div class="ic-label">Largest budget item</div>
            <div class="ic-value">{big_spend["Category"]}</div>
            <div class="ic-sub">
                ₹{big_spend["Monthly Spend"]:,.0f} / month
                &nbsp;·&nbsp; {big_spend["Spend Share (%)"]:.1f}% of budget
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col_c:
    st.markdown(
        f"""
        <div class="insight-card amber">
            <div class="ic-label">Categories above headline CPI ({headline:.1f}%)</div>
            <div class="ic-value" style="font-size:1rem; line-height:1.5;">{cats_above}</div>
            <div class="ic-sub">These carry above-average inflation risk</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
