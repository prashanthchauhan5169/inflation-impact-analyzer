"""
pages/5_Export.py – Export personal result as CSV or PDF.
"""

import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime

from database import init_db, get_response
from scoring import full_score, load_cpi
from app_styles import inject_styles

st.set_page_config(page_title="Export – Inflation Impact Analyzer",
                   page_icon=None, layout="wide")
inject_styles()
init_db()

st.markdown(
    """
    <div class="page-header">
        <div class="section-label">Export</div>
        <h1>Download Your Report</h1>
        <p>Export your personalised inflation impact analysis as a structured CSV 
           or a formatted PDF report.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Session check ─────────────────────────────────────────────────────────────
if "score" not in st.session_state:
    if "response_id" in st.session_state:
        row = get_response(st.session_state["response_id"])
        if row:
            cpi_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                    "data", "cpi.csv")
            cpi = load_cpi(cpi_path)
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

score        = st.session_state["score"]
spend        = st.session_state["spend"]
behaviours   = st.session_state.get("behaviours", [])
age_band     = st.session_state.get("age_band", "—")
income_range = st.session_state.get("income_range", "—")
family_size  = st.session_state.get("family_size", "—")
breakdown    = score["breakdown"]
generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
label        = score["label"]
badge_class  = {"High": "badge-high", "Moderate": "badge-moderate",
                "Low": "badge-low"}[label]

# ── Report preview ────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Preview</div>', unsafe_allow_html=True)
st.markdown("### Report summary")

behaviour_display = (
    " · ".join(b.replace("_", " ").title() for b in behaviours)
    if behaviours else "None"
)

delta = round(score["adjusted_rate"] - score["headline_rate"], 2)
delta_sign = "+" if delta >= 0 else ""

st.markdown(
    f"""
    <div class="card" style="border-color:#2e2e52;">
        <div style="display:flex; justify-content:space-between; align-items:center;
                    flex-wrap:wrap; gap:1rem; margin-bottom:1.4rem;">
            <div>
                <div style="font-size:0.72rem; font-weight:700; letter-spacing:0.08em;
                            text-transform:uppercase; color:#5b5b85; margin-bottom:0.4rem;">
                    Inflation Impact Report
                </div>
                <div style="font-size:0.84rem; color:#4e4e72;">Generated {generated_at}</div>
            </div>
            <span class="impact-badge {badge_class}">{label} Impact</span>
        </div>

        <div class="summary-grid" style="margin-bottom:1.4rem;">
            <div class="sg-cell">
                <div class="sg-label">Age band</div>
                <div class="sg-val">{age_band}</div>
            </div>
            <div class="sg-cell">
                <div class="sg-label">Household income</div>
                <div class="sg-val">{income_range}</div>
            </div>
            <div class="sg-cell">
                <div class="sg-label">Household size</div>
                <div class="sg-val">{family_size} person(s)</div>
            </div>
            <div class="sg-cell">
                <div class="sg-label">Personal rate</div>
                <div class="sg-val" style="font-family:'JetBrains Mono',monospace;">
                    {score['personal_rate']:.2f}%
                </div>
            </div>
            <div class="sg-cell">
                <div class="sg-label">Adjusted rate</div>
                <div class="sg-val" style="font-family:'JetBrains Mono',monospace;">
                    {score['adjusted_rate']:.2f}%
                    <span style="font-size:0.78rem; color:#5b5b85; font-family:Inter;">
                        ({delta_sign}{delta:.2f} pp vs CPI)
                    </span>
                </div>
            </div>
            <div class="sg-cell">
                <div class="sg-label">Headline CPI</div>
                <div class="sg-val" style="font-family:'JetBrains Mono',monospace;">
                    {score['headline_rate']:.1f}%
                </div>
            </div>
        </div>

        <div style="border-top:1px solid #1e1e35; padding-top:1.1rem; margin-bottom:1rem;">
            <div class="sg-label" style="margin-bottom:0.5rem;">Coping strategies</div>
            <div style="color:#a0a0c0; font-size:0.9rem;">{behaviour_display}</div>
        </div>

        <div style="border-top:1px solid #1e1e35; padding-top:1.1rem;">
            <div class="sg-label" style="margin-bottom:0.5rem;">Analysis</div>
            <p style="color:#a0a0c0; font-size:0.92rem; line-height:1.7; margin:0;">
                {score['explanation']}
            </p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Export helpers ────────────────────────────────────────────────────────────
def build_summary_df() -> pd.DataFrame:
    return pd.DataFrame([
        {"Field": "Generated at",       "Value": generated_at},
        {"Field": "Age band",            "Value": age_band},
        {"Field": "Income range",        "Value": income_range},
        {"Field": "Household size",      "Value": str(family_size)},
        {"Field": "Coping behaviours",   "Value": behaviour_display},
        {"Field": "Personal rate (%)",   "Value": f"{score['personal_rate']:.4f}"},
        {"Field": "Coping penalty (pp)", "Value": f"{score['penalty']:.4f}"},
        {"Field": "Adjusted rate (%)",   "Value": f"{score['adjusted_rate']:.4f}"},
        {"Field": "Headline CPI (%)",    "Value": f"{score['headline_rate']:.1f}"},
        {"Field": "Impact label",        "Value": label},
    ])


def build_breakdown_df() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "Category":          cat.capitalize(),
            "Monthly Spend (₹)": spend.get(cat, 0),
            "Spend Share (%)":   info["share"],
            "CPI Rate (%)":      info["cpi_rate"],
            "Contribution (pp)": info["contribution"],
        }
        for cat, info in breakdown.items()
    ])


def build_csv() -> bytes:
    buf = io.StringIO()
    buf.write("# INFLATION IMPACT ANALYZER - PERSONAL REPORT\n\n")
    buf.write("## Summary\n")
    build_summary_df().to_csv(buf, index=False)
    buf.write("\n## Category Breakdown\n")
    build_breakdown_df().to_csv(buf, index=False)
    return buf.getvalue().encode("utf-8")


def build_pdf() -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle, HRFlowable)
    from reportlab.lib.enums import TA_LEFT, TA_CENTER

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
    )

    styles  = getSampleStyleSheet()
    C_BRAND = colors.HexColor("#5b4dff")
    C_DARK  = colors.HexColor("#1a1a2e")
    C_TEXT  = colors.HexColor("#2d2d3a")
    C_MUTED = colors.HexColor("#6b6b8a")
    C_LABEL_COLORS = {
        "High":     colors.HexColor("#e05252"),
        "Moderate": colors.HexColor("#d97706"),
        "Low":      colors.HexColor("#10b981"),
    }

    title_s = ParagraphStyle(
        "T1", parent=styles["Normal"],
        textColor=C_DARK, fontSize=22, fontName="Helvetica-Bold",
        spaceAfter=3, leading=26,
    )
    sub_s = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        textColor=C_MUTED, fontSize=10, leading=14, spaceAfter=2,
    )
    h2_s = ParagraphStyle(
        "H2", parent=styles["Normal"],
        textColor=C_BRAND, fontSize=11, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=4,
    )
    body_s = ParagraphStyle(
        "Body", parent=styles["Normal"],
        textColor=C_TEXT, fontSize=9.5, leading=14,
    )
    badge_s = ParagraphStyle(
        "Badge", parent=styles["Normal"],
        textColor=C_LABEL_COLORS[label], fontSize=14,
        fontName="Helvetica-Bold", alignment=TA_CENTER,
        spaceBefore=4, spaceAfter=4,
    )
    caption_s = ParagraphStyle(
        "Cap", parent=styles["Normal"],
        textColor=C_MUTED, fontSize=7, leading=10,
    )

    story = []
    story.append(Paragraph("Inflation Impact Analyzer", title_s))
    story.append(Paragraph(f"Personal Report  ·  {generated_at}", sub_s))
    story.append(HRFlowable(width="100%", thickness=1.5, color=C_BRAND,
                             spaceAfter=8))
    story.append(Paragraph(f"{label.upper()} IMPACT", badge_s))
    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#e0e0ef"), spaceAfter=6))
    story.append(Spacer(1, 0.2*cm))

    # Summary table
    story.append(Paragraph("Summary", h2_s))
    sd = build_summary_df()
    t_data = [["Field", "Value"]] + sd.values.tolist()
    t = Table(t_data, colWidths=[7*cm, 10*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), C_BRAND),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f4f3ff"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#ddddf0")),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 7),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4*cm))

    story.append(Paragraph("Analysis", h2_s))
    story.append(Paragraph(score["explanation"], body_s))
    story.append(Spacer(1, 0.4*cm))

    # Breakdown table
    story.append(Paragraph("Category Breakdown", h2_s))
    bd = build_breakdown_df()
    bd_data = [bd.columns.tolist()] + bd.values.tolist()
    for i in range(1, len(bd_data)):
        r = bd_data[i]
        bd_data[i] = [
            r[0],
            f"₹{r[1]:,.0f}",
            f"{r[2]:.1f}%",
            f"{r[3]:.1f}%",
            f"{r[4]:.4f} pp",
        ]
    t2 = Table(bd_data, colWidths=[3.5*cm, 3.3*cm, 3*cm, 3*cm, 3.7*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), colors.HexColor("#4f46e5")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), colors.white),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f4f3ff"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#ddddf0")),
        ("ALIGN",         (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t2)
    story.append(Spacer(1, 0.5*cm))

    story.append(HRFlowable(width="100%", thickness=0.5,
                             color=colors.HexColor("#ddddf0")))
    story.append(Paragraph(
        "CPI data is placeholder. Replace data/cpi.csv with official ONS / BLS figures.",
        caption_s,
    ))

    doc.build(story)
    return buf.getvalue()


# ── Download buttons ──────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown('<div class="section-label">Download</div>', unsafe_allow_html=True)
st.markdown("### Choose a format")

dl1, dl2, spacer = st.columns([1, 1, 2])

with dl1:
    csv_bytes = build_csv()
    fname_csv = f"inflation_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    st.download_button(
        label="Download as CSV",
        data=csv_bytes,
        file_name=fname_csv,
        mime="text/csv",
        use_container_width=True,
    )
    st.caption("Summary and category breakdown in CSV format.")

with dl2:
    try:
        pdf_bytes = build_pdf()
        fname_pdf = f"inflation_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        st.download_button(
            label="Download as PDF",
            data=pdf_bytes,
            file_name=fname_pdf,
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption("Formatted PDF report with tables and classification summary.")
    except ImportError:
        st.info("PDF export requires `reportlab`: `pip install reportlab`")
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# ── Raw data expander ─────────────────────────────────────────────────────────
st.markdown("<hr>", unsafe_allow_html=True)
with st.expander("View raw export data"):
    st.markdown("**Summary**")
    st.dataframe(build_summary_df(), use_container_width=True, hide_index=True)
    st.markdown("**Category Breakdown**")
    st.dataframe(build_breakdown_df(), use_container_width=True, hide_index=True)
