# Inflation Impact Analyzer

A multi-page **Streamlit** application that computes each household's **personal inflation rate** from their spending patterns and compares it to the published headline CPI.

---

## Features

| Page | Description |
|---|---|
| 📝 Survey | Collect age band, income, family size, per-category monthly spend, and coping behaviours |
| 🎯 My Impact | Gauge chart, Low/Moderate/High badge, waterfall chart, per-category table |
| 📊 Category Analysis | Grouped bar, horizontal contribution bar, donut, radar chart |
| 🌐 Dashboard | Aggregate stats, income/age heatmap, coping adoption, family-size trend |
| 📥 Export | One-click CSV and PDF download of the personal report |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Seed the database (40 demo responses)

```bash
python seed_data.py
```

### 3. Run the app

```bash
streamlit run app.py
```

The app will open at **http://localhost:8501**.

---

## Running Tests

```bash
python test_scoring.py
# or, with pytest:
python -m pytest test_scoring.py -v
```

All 20+ unit tests should pass.

---

## Project Structure

```
inflation-impact-analyzer/
├── app.py                   # Landing page + global CSS
├── app_styles.py            # Shared CSS injection helper
├── scoring.py               # Pure scoring logic (unit-tested)
├── database.py              # SQLite helpers
├── seed_data.py             # 40 fake responses seeder
├── test_scoring.py          # Unit tests for scoring.py
├── requirements.txt
├── README.md
├── data/
│   └── cpi.csv              # Category inflation rates (placeholder)
└── pages/
    ├── 1_Survey.py
    ├── 2_My_Impact.py
    ├── 3_Category_Analysis.py
    ├── 4_Dashboard.py
    └── 5_Export.py
```

---

## Replacing Placeholder CPI Data

Open `data/cpi.csv` and replace the `annual_rate` values with official ONS (UK) or BLS (US) figures:

```csv
category,annual_rate
food,8.5
transport,6.2
housing,5.8
education,7.1
healthcare,9.4
entertainment,3.2
other,5.0
headline,6.4
```

The `headline` row is used as the benchmark CPI for comparison.

---

## Scoring Logic

1. **Personal rate** = Σ (monthly_spend_i / total_spend × cpi_rate_i) for each category  
2. **Coping penalty** = sum of behaviour-specific penalties (0.10 – 0.25 pp each)  
3. **Adjusted rate** = personal_rate + coping_penalty  
4. **Classification**:
   - **Low** → adjusted_rate < headline − 1.0 pp  
   - **Moderate** → headline − 1.0 ≤ adjusted_rate < headline + 2.0 pp  
   - **High** → adjusted_rate ≥ headline + 2.0 pp  

---

## Tech Stack

- **Python 3.9+**
- **Streamlit** – multi-page UI
- **Pandas** – data wrangling
- **Plotly** – interactive charts (gauge, waterfall, bar, radar, heatmap)
- **SQLite** (stdlib) – local persistence
- **ReportLab** – PDF generation
- **Faker** – realistic seed data

---

## License

MIT
