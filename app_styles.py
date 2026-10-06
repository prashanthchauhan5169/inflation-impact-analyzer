"""
app_styles.py – Shared CSS injection for all pages.
Import and call inject_styles() at the top of every page.
Responsive for desktop/laptop and mobile/Android devices.
"""

import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        /* ── Typography ───────────────────────────────── */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap');

        html, body, [class*="css"], .stMarkdown, p, span, div, label {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            color: #1e293b;
            -webkit-tap-highlight-color: transparent;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        }

        /* ── App Background ───────────────────────────── */
        .stApp {
            background: #f4f6f8; /* Soft pale grey/cream background */
        }

        /* Responsive Main Container */
        .main .block-container {
            padding-top: 1.8rem;
            padding-bottom: 3.5rem;
            max-width: 1240px;
            margin: 0 auto;
        }

        /* ── Sidebar ──────────────────────────────────── */
        section[data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid #e2e8f0 !important;
            box-shadow: 4px 0 24px rgba(0,0,0,0.03);
        }
        section[data-testid="stSidebar"] * {
            color: #475569 !important;
        }
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"] {
            border-radius: 12px;
            padding: 0.65rem 1rem;
            transition: all 0.2s ease;
            font-weight: 500;
        }
        section[data-testid="stSidebar"] a[data-testid="stSidebarNavLink"]:hover {
            background: #f1f5f9;
            color: #0f172a !important;
        }
        section[data-testid="stSidebar"] a[aria-selected="true"] {
            background: #111827 !important;
            color: #ffffff !important;
        }

        /* ── Headings ─────────────────────────────────── */
        h1, h2, h3, h4 { color: #0f172a !important; letter-spacing: -0.02em; }
        h1 { font-size: clamp(1.8rem, 4vw, 2.5rem) !important; font-weight: 800 !important; }
        h2 { font-size: clamp(1.3rem, 3vw, 1.6rem) !important; font-weight: 700 !important; }
        h3 { font-size: clamp(1.05rem, 2.5vw, 1.25rem) !important; font-weight: 600 !important; }

        /* ── Streamlit metric ─────────────────────────── */
        div[data-testid="stMetricValue"] {
            font-size: clamp(1.6rem, 3.5vw, 2.2rem) !important;
            font-weight: 800 !important;
            color: #0f172a !important;
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.03em;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
            color: #64748b !important;
            letter-spacing: 0.02em;
        }
        div[data-testid="stMetricDelta"] svg { display: none; }
        div[data-testid="stMetricDelta"] > div {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }
        div[data-testid="metric-container"] {
            background: #ffffff;
            border-radius: 20px;
            padding: 1.25rem 1.4rem !important;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid rgba(226, 232, 240, 0.6);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div[data-testid="metric-container"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        }

        /* ── Primary button ───────────────────────────── */
        .stButton > button {
            background: #111827;
            color: #ffffff;
            border: none;
            border-radius: 999px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 0.95rem;
            font-family: 'Plus Jakarta Sans', sans-serif;
            letter-spacing: 0.01em;
            transition: all 0.2s ease;
            box-shadow: 0 6px 16px rgba(17, 24, 39, 0.15);
            min-height: 48px; /* Touch-friendly Android button target */
        }
        .stButton > button:hover {
            background: #1e293b;
            transform: translateY(-2px);
            box-shadow: 0 10px 22px rgba(17, 24, 39, 0.2);
            color: white !important;
        }
        .stButton > button:active { transform: translateY(0); }

        /* ── Download button ──────────────────────────── */
        .stDownloadButton > button {
            background: #ffffff;
            color: #111827;
            border: 1.5px solid #cbd5e1;
            border-radius: 999px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            min-height: 48px;
        }
        .stDownloadButton > button:hover {
            background: #f8fafc;
            border-color: #0f172a;
            color: #0f172a !important;
        }

        /* ── Inputs ───────────────────────────────────── */
        .stNumberInput input,
        .stTextInput input {
            background: #ffffff !important;
            border: 1.5px solid #e2e8f0 !important;
            color: #0f172a !important;
            border-radius: 14px !important;
            font-size: 1rem !important;
            padding: 0.75rem 1rem !important;
            transition: all 0.2s ease;
            min-height: 44px;
        }
        .stNumberInput input:focus,
        .stTextInput input:focus {
            background: #ffffff !important;
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
        }
        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border: 1.5px solid #e2e8f0 !important;
            border-radius: 14px !important;
            color: #0f172a !important;
            min-height: 44px;
        }
        div[data-baseweb="select"] > div:focus-within {
            border-color: #3b82f6 !important;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.12) !important;
        }
        div[data-baseweb="popover"] { 
            background: #ffffff !important; 
            border: none !important; 
            border-radius: 16px !important;
            box-shadow: 0 10px 28px rgba(0, 0, 0, 0.12) !important; 
        }
        li[role="option"] { color: #475569 !important; font-weight: 500; padding: 0.6rem 1rem !important; }
        li[role="option"]:hover { background: #f1f5f9 !important; }
        li[aria-selected="true"] { background: #111827 !important; color: #ffffff !important; border-radius: 8px; }

        /* checkbox */
        input[type="checkbox"] + label,
        .stCheckbox label { 
            color: #334155 !important; 
            font-size: 0.95rem !important; 
            font-weight: 500;
            cursor: pointer;
        }

        /* ── Dataframe ────────────────────────────────── */
        .dataframe-container { 
            border-radius: 16px; 
            overflow-x: auto; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.03); 
        }
        [data-testid="stDataFrame"] {
            overflow-x: auto;
        }
        [data-testid="stDataFrame"] iframe { 
            border-radius: 16px !important; 
            border: none !important; 
        }

        /* ── Divider ──────────────────────────────────── */
        hr {
            border: none;
            border-top: 1px solid #e2e8f0;
            margin: 1.5rem 0;
        }

        /* ── Expander ─────────────────────────────────── */
        details {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 16px !important;
            box-shadow: 0 2px 12px rgba(0,0,0,0.02);
            margin-bottom: 1rem;
        }
        details summary {
            color: #0f172a !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            padding: 0.9rem 1.2rem !important;
            cursor: pointer;
        }

        /* ─────────────────────────────────────────────── */
        /* CUSTOM COMPONENTS                               */
        /* ─────────────────────────────────────────────── */

        /* Page header */
        .page-header {
            padding: 0.5rem 0 1.5rem 0;
            margin-bottom: 1rem;
        }
        .page-header h1 {
            margin: 0 0 0.5rem 0 !important;
            color: #0f172a !important;
        }
        .page-header p {
            margin: 0;
            color: #64748b;
            font-size: 1rem;
            line-height: 1.6;
            max-width: 680px;
        }

        /* Section label */
        .section-label {
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            color: #6366f1;
            margin-bottom: 0.4rem;
            font-family: 'Outfit', sans-serif;
        }

        /* Card */
        .card {
            background: #ffffff;
            border-radius: 20px;
            padding: 1.5rem;
            margin: 0.6rem 0;
            transition: all 0.3s ease;
            box-shadow: 0 4px 20px rgba(0,0,0,0.03);
            border: 1px solid rgba(226, 232, 240, 0.7);
        }
        .card:hover { transform: translateY(-2px); box-shadow: 0 10px 28px rgba(0,0,0,0.06); }
        .card-title {
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            color: #64748b;
            margin-bottom: 0.6rem;
        }
        .card-value {
            font-size: clamp(1.8rem, 3.5vw, 2.3rem);
            font-weight: 800;
            color: #0f172a;
            letter-spacing: -0.03em;
            line-height: 1.1;
            font-family: 'Outfit', sans-serif;
        }
        .card-sub {
            font-size: 0.85rem;
            color: #64748b;
            margin-top: 0.4rem;
            font-weight: 500;
        }

        /* Insight card – Fintech style (pastel backgrounds) */
        .insight-card {
            border-radius: 18px;
            padding: 1.25rem 1.4rem;
            margin: 0.6rem 0;
            border: none;
            transition: transform 0.2s ease;
        }
        .insight-card:hover { transform: translateY(-2px); }
        
        .insight-card.red   { background: #fef2f2; color: #991b1b; border: 1px solid #fee2e2; }
        .insight-card.amber { background: #fefce8; color: #854d0e; border: 1px solid #fef9c3; }
        .insight-card.green { background: #ecfdf5; color: #065f46; border: 1px solid #d1fae5; }
        
        .insight-card .ic-label {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.85;
            margin-bottom: 0.4rem;
        }
        .insight-card .ic-value {
            font-size: clamp(1.1rem, 2.5vw, 1.35rem);
            font-weight: 800;
            font-family: 'Outfit', sans-serif;
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
        }
        .insight-card .ic-sub {
            font-size: 0.85rem;
            opacity: 0.8;
            font-weight: 500;
            line-height: 1.45;
        }

        /* Impact badge */
        .impact-badge {
            display: inline-flex;
            align-items: center;
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .badge-high     { background: #dc2626; color: #ffffff; }
        .badge-moderate { background: #f59e0b; color: #ffffff; }
        .badge-low      { background: #10b981; color: #ffffff; }

        /* Nav card (home page) */
        .nav-card {
            background: #ffffff;
            border-radius: 18px;
            padding: 1.5rem 1.1rem;
            text-align: center;
            cursor: default;
            transition: all 0.3s ease;
            box-shadow: 0 4px 18px rgba(0,0,0,0.03);
            border: 1px solid rgba(226, 232, 240, 0.7);
            height: 100%;
        }
        .nav-card:hover { 
            transform: translateY(-3px); 
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.06); 
            border-color: #cbd5e1;
        }
        .nav-card .nc-icon {
            width: 44px; height: 44px;
            background: #f8fafc;
            border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 1rem;
            font-size: 1rem;
            color: #4f46e5;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid #e2e8f0;
        }
        .nav-card .nc-title {
            font-weight: 700;
            font-size: 1rem;
            color: #0f172a;
            margin-bottom: 0.35rem;
            font-family: 'Outfit', sans-serif;
        }
        .nav-card .nc-desc {
            font-size: 0.82rem;
            color: #64748b;
            line-height: 1.45;
        }

        /* Summary grid */
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
        }
        .sg-cell .sg-label {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #94a3b8;
            margin-bottom: 0.3rem;
        }
        .sg-cell .sg-val {
            font-size: 1.05rem;
            font-weight: 700;
            color: #0f172a;
        }

        /* Behaviour pill */
        .behaviour-pill {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            background: #f1f5f9;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 600;
            color: #334155;
            margin: 0.25rem 0.25rem 0.25rem 0;
            border: 1px solid #cbd5e1;
        }

        /* Plotly transparent bg & responsive styling */
        .js-plotly-plot .plotly,
        .js-plotly-plot .plotly .plot-container {
            background: transparent !important;
        }

        /* ── Mobile & Android Responsive Optimizations ────────────────── */
        @media (max-width: 768px) {
            .main .block-container {
                padding-top: 1rem !important;
                padding-bottom: 2rem !important;
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
            }
            .page-header {
                padding-bottom: 1rem !important;
            }
            .page-header h1 {
                font-size: 1.75rem !important;
            }
            .card {
                padding: 1.2rem !important;
                border-radius: 16px !important;
            }
            div[data-testid="metric-container"] {
                padding: 1rem !important;
                border-radius: 16px !important;
            }
            .nav-card {
                padding: 1.1rem 0.85rem !important;
                margin-bottom: 0.5rem;
            }
            .summary-grid {
                grid-template-columns: 1fr 1fr;
                gap: 0.8rem;
            }
            /* Full touch targets for mobile */
            .stButton > button, .stDownloadButton > button {
                width: 100% !important;
                font-size: 0.95rem !important;
                margin-bottom: 0.5rem;
            }
            /* Scrollable tables on mobile */
            [data-testid="stTable"], [data-testid="stDataFrame"] {
                width: 100% !important;
                overflow-x: auto !important;
                -webkit-overflow-scrolling: touch;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
