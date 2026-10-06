"""
pages/4_Dashboard.py – Aggregate dashboard across all survey responses.
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from database import init_db, get_all_responses, response_count
from scoring import load_cpi
from app_styles import inject_styles

st.set_page_config(page_title="Dashboard – Inflation Impact Analyzer",
                   page_icon=None, layout="wide")
inject_styles()
init_db()

st.markdown(
    """
    <div class="page-header">
        <div class="section-label">Aggregate view</div>
        <h1>Dashboard</h1>
        <p>Trends and patterns across all survey responses — 
           impact by income band, age, family size, and coping behaviour adoption.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

cpi_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "cpi.csv")
cpi      = load_cpi(cpi_path)
headline = cpi.get("headline", 6.4)

# ── Load data ─────────────────────────────────────────────────────────────────
total = response_count()

if total == 0:
    st.info(
        "**No responses recorded yet.**  \n"
        "Run `python seed_data.py` to load 40 demo responses, "
        "or submit the Survey form first.",
    )
    st.stop()

if total < 5:
    st.warning(
        f"Only **{total}** response(s) so far. Some charts need more data to be meaningful.  \n"
        "Run `python seed_data.py` to add 40 sample entries.",
    )

all_rows = get_all_responses()
df = pd.DataFrame(all_rows)

# ── Derived columns ───────────────────────────────────────────────────────────
df["total_spend"] = (
    df["spend_food"] + df["spend_transport"] + df["spend_housing"] +
    df["spend_education"] + df["spend_healthcare"] +
    df["spend_entertainment"] + df["spend_other"]
)
df["n_coping"] = (
    df["coping_cheaper_brands"] + df["coping_cut_non_essentials"] +
    df["coping_fewer_shopping_trips"] + df["coping_delayed_big_purchases"]
)

INCOME_ORDER = ["Under ₹20k", "₹20k-₹35k", "₹35k-₹50k", "₹50k-₹75k", "Over ₹75k"]
AGE_ORDER    = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
df["income_range"] = pd.Categorical(df["income_range"],
                                    categories=INCOME_ORDER, ordered=True)
df.sort_values("income_range", inplace=True)

CHART_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font={"color": "#334155", "family": "Inter"},
)
GRID  = "rgba(226,232,240,1)"
TICK  = "#64748b"
LABEL = "#64748b"

# ── KPI metrics ───────────────────────────────────────────────────────────────
avg_adj  = df["adjusted_rate"].mean()
pct_high = (df["impact_label"] == "High").mean() * 100
pct_mod  = (df["impact_label"] == "Moderate").mean() * 100
pct_low  = (df["impact_label"] == "Low").mean() * 100
avg_cope = df["n_coping"].mean()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Responses",      f"{total:,}")
c2.metric("Avg Adjusted Rate",    f"{avg_adj:.2f}%",
          delta=f"{avg_adj - headline:+.2f} pp vs headline",
          delta_color="inverse")
c3.metric("High Impact",          f"{pct_high:.0f}%")
c4.metric("Moderate Impact",      f"{pct_mod:.0f}%")
c5.metric("Low Impact",           f"{pct_low:.0f}%")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 1: Distribution + Coping ──────────────────────────────────────────────
row1_l, row1_r = st.columns(2, gap="large")

with row1_l:
    st.markdown('<div class="section-label">Score distribution</div>',
                unsafe_allow_html=True)
    st.markdown("### Impact classification breakdown")
    label_counts = (
        df["impact_label"]
        .value_counts()
        .reindex(["High", "Moderate", "Low"], fill_value=0)
        .reset_index()
    )
    label_counts.columns = ["Label", "Count"]
    label_counts["Pct"] = label_counts["Count"] / total * 100
    color_map = {"High": "#e05252", "Moderate": "#d97706", "Low": "#10b981"}

    fig_dist = go.Figure(go.Bar(
        x=label_counts["Label"],
        y=label_counts["Count"],
        marker=dict(
            color=[color_map[l] for l in label_counts["Label"]],
            line=dict(width=0),
            opacity=0.85,
        ),
        text=label_counts.apply(lambda r: f"{r['Count']} ({r['Pct']:.0f}%)", axis=1),
        textposition="outside",
        textfont=dict(size=11, color=LABEL),
    ))
    fig_dist.update_layout(
        **CHART_BASE,
        height=320,
        bargap=0.35,
        yaxis=dict(gridcolor=GRID, tickfont=dict(color=TICK, size=11),
                   title="Responses", title_font=dict(color=TICK, size=11),
                   zeroline=False),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=LABEL, size=12)),
        margin=dict(t=20, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_dist, use_container_width=True)

with row1_r:
    st.markdown('<div class="section-label">Coping strategies</div>',
                unsafe_allow_html=True)
    st.markdown("### Adoption rate across respondents")
    coping_map = {
        "coping_cheaper_brands":         "Cheaper brands",
        "coping_cut_non_essentials":     "Cut non-essentials",
        "coping_fewer_shopping_trips":   "Fewer shopping trips",
        "coping_delayed_big_purchases":  "Delayed big purchases",
    }
    coping_df = pd.DataFrame([
        {"Behaviour": lbl, "Respondents": int(df[col].sum()),
         "Pct": df[col].sum() / total * 100}
        for col, lbl in coping_map.items()
    ]).sort_values("Respondents", ascending=True)

    fig_cope = go.Figure(go.Bar(
        x=coping_df["Respondents"],
        y=coping_df["Behaviour"],
        orientation="h",
        marker=dict(color="#5b4dff", line=dict(width=0), opacity=0.85),
        text=coping_df["Pct"].apply(lambda x: f"{x:.0f}%"),
        textposition="outside",
        textfont=dict(size=11, color=LABEL),
    ))
    fig_cope.update_layout(
        **CHART_BASE,
        height=320,
        xaxis=dict(gridcolor=GRID, tickfont=dict(color=TICK, size=11),
                   title="Respondents", title_font=dict(color=TICK, size=11)),
        yaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(color=LABEL, size=11)),
        margin=dict(t=20, b=10, l=10, r=65),
    )
    st.plotly_chart(fig_cope, use_container_width=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 2: Income band ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Income analysis</div>', unsafe_allow_html=True)
st.markdown("### Average adjusted rate by income band")

if df["income_range"].nunique() >= 2:
    inc_grp = (
        df.groupby("income_range", observed=True)["adjusted_rate"]
        .agg(["mean", "min", "max", "count"])
        .reset_index()
    )
    fig_inc = go.Figure()
    fig_inc.add_trace(go.Bar(
        x=inc_grp["income_range"].astype(str),
        y=inc_grp["mean"],
        marker=dict(color="#5b4dff", line=dict(width=0), opacity=0.85),
        error_y=dict(
            type="data", symmetric=False,
            array=(inc_grp["max"] - inc_grp["mean"]).tolist(),
            arrayminus=(inc_grp["mean"] - inc_grp["min"]).tolist(),
            color="#7c6dff", thickness=1.5, width=6,
        ),
        text=inc_grp["mean"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(size=11, color=LABEL),
        name="Mean rate",
    ))
    fig_inc.add_hline(y=headline, line_dash="dash", line_color="#d97706",
                      line_width=1.5,
                      annotation_text=f"  Headline {headline:.1f}%",
                      annotation_font_color="#d97706", annotation_font_size=11)
    fig_inc.update_layout(
        **CHART_BASE,
        height=360,
        bargap=0.3,
        showlegend=False,
        yaxis=dict(gridcolor=GRID, tickfont=dict(color=TICK, size=11),
                   title="Avg adjusted rate (%)",
                   title_font=dict(color=TICK, size=11), zeroline=False),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", title="Income band",
                   tickfont=dict(color=LABEL, size=11),
                   title_font=dict(color=TICK, size=11)),
        margin=dict(t=20, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_inc, use_container_width=True)
else:
    st.info("Responses from at least 2 income bands are needed for this chart.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 3: Family size trend + Heatmap ────────────────────────────────────────
row3_l, row3_r = st.columns(2, gap="large")

with row3_l:
    st.markdown('<div class="section-label">Household composition</div>',
                unsafe_allow_html=True)
    st.markdown("### Rate by household size")

    if df["family_size"].nunique() >= 2:
        fs_grp = (
            df.groupby("family_size")["adjusted_rate"]
            .agg(["mean", "count"])
            .reset_index()
        )
        fig_fs = go.Figure()
        fig_fs.add_trace(go.Scatter(
            x=fs_grp["family_size"],
            y=fs_grp["mean"],
            mode="lines+markers",
            line=dict(color="#5b4dff", width=2.5),
            marker=dict(
                size=(fs_grp["count"] * 3.5).clip(upper=24),
                color="#7c6dff",
                line=dict(color="#ffffff", width=2),
            ),
            text=fs_grp["count"].apply(lambda n: f"n = {n}"),
            hovertemplate=(
                "Household size: %{x}<br>"
                "Avg rate: %{y:.2f}%<br>"
                "%{text}<extra></extra>"
            ),
        ))
        fig_fs.add_hline(y=headline, line_dash="dash", line_color="#d97706",
                         line_width=1.5,
                         annotation_text=f"  Headline {headline:.1f}%",
                         annotation_font_color="#d97706", annotation_font_size=11)
        fig_fs.update_layout(
            **CHART_BASE,
            height=340,
            xaxis=dict(gridcolor=GRID, dtick=1, title="Household size",
                       tickfont=dict(color=TICK, size=11),
                       title_font=dict(color=TICK, size=11)),
            yaxis=dict(gridcolor=GRID, title="Avg adjusted rate (%)",
                       tickfont=dict(color=TICK, size=11),
                       title_font=dict(color=TICK, size=11), zeroline=False),
            margin=dict(t=20, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_fs, use_container_width=True)
    else:
        st.info("Need more variation in household size for this chart.")

with row3_r:
    st.markdown('<div class="section-label">Demographic heatmap</div>',
                unsafe_allow_html=True)
    st.markdown("### Rate by income band and age group")

    pivot_data = (
        df.groupby(["income_range", "age_band"], observed=True)["adjusted_rate"]
        .mean()
        .reset_index()
    )
    if len(pivot_data) >= 4:
        pivot_table = pivot_data.pivot_table(
            index="income_range", columns="age_band",
            values="adjusted_rate", aggfunc="mean",
        )
        age_cols = [a for a in AGE_ORDER if a in pivot_table.columns]
        inc_rows = [i for i in INCOME_ORDER if i in pivot_table.index]
        pivot_table = pivot_table.reindex(index=inc_rows, columns=age_cols)

        fig_heat = px.imshow(
            pivot_table,
            color_continuous_scale=[[0, "#10b981"], [0.5, "#d97706"], [1, "#e05252"]],
            aspect="auto",
            text_auto=".1f",
            labels=dict(color="Rate (%)"),
        )
        fig_heat.update_traces(
            textfont=dict(size=11, color="#e2e2ef"),
        )
        fig_heat.update_layout(
            **CHART_BASE,
            height=340,
            xaxis=dict(title="Age band", tickfont=dict(color=LABEL, size=10),
                       title_font=dict(color=TICK, size=11)),
            yaxis=dict(title="Income range", tickfont=dict(color=LABEL, size=10),
                       title_font=dict(color=TICK, size=11)),
            coloraxis_colorbar=dict(
                thickness=10,
                tickfont=dict(color=TICK, size=10),
                titlefont=dict(color=TICK, size=10),
                len=0.85,
            ),
            margin=dict(t=20, b=10, l=10, r=10),
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("More data across income/age combinations is needed for the heatmap.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Row 4: Age band bar ───────────────────────────────────────────────────────
st.markdown('<div class="section-label">Age analysis</div>', unsafe_allow_html=True)
st.markdown("### Average rate by age band")

age_grp = (
    df.groupby("age_band")["adjusted_rate"]
    .agg(["mean", "count"])
    .reindex(AGE_ORDER)
    .dropna()
    .reset_index()
)
if len(age_grp) >= 2:
    fig_age = go.Figure(go.Bar(
        x=age_grp["age_band"],
        y=age_grp["mean"],
        marker=dict(color="#4f86c6", line=dict(width=0), opacity=0.85),
        text=age_grp["mean"].apply(lambda x: f"{x:.2f}%"),
        textposition="outside",
        textfont=dict(size=11, color=LABEL),
    ))
    fig_age.add_hline(y=headline, line_dash="dash", line_color="#d97706",
                      line_width=1.5,
                      annotation_text=f"  Headline {headline:.1f}%",
                      annotation_font_color="#d97706", annotation_font_size=11)
    fig_age.update_layout(
        **CHART_BASE,
        height=320,
        bargap=0.35,
        yaxis=dict(gridcolor=GRID, tickfont=dict(color=TICK, size=11),
                   title="Avg rate (%)", title_font=dict(color=TICK, size=11),
                   zeroline=False),
        xaxis=dict(gridcolor="rgba(0,0,0,0)", title="Age band",
                   tickfont=dict(color=LABEL, size=11),
                   title_font=dict(color=TICK, size=11)),
        margin=dict(t=20, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_age, use_container_width=True)
else:
    st.info("Need responses across at least 2 age bands for this chart.")

st.markdown("<hr>", unsafe_allow_html=True)

# ── Summary statistics ────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Statistics</div>', unsafe_allow_html=True)
st.markdown("### Summary by impact classification")

summary = (
    df.groupby("impact_label")["adjusted_rate"]
    .agg(Count="count", Mean="mean", Min="min", Max="max", Std="std")
    .reset_index()
    .rename(columns={"impact_label": "Impact"})
)
for col in ["Mean", "Min", "Max", "Std"]:
    summary[col] = summary[col].apply(lambda x: f"{x:.2f}%")

st.dataframe(summary, use_container_width=True, hide_index=True)
