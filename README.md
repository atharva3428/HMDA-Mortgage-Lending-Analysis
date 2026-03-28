# HMDA Mortgage Lending Analysis

Analyzes US mortgage lending data from the FFIEC HMDA Platform using DuckDB SQL, surfacing insights through an interactive Streamlit dashboard.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the dashboard
python -m streamlit run .claude/skills/hmda-dashboard/dashboard.py
```

Dashboard opens at **http://localhost:8501**

## Project Structure

```
Finance_Project/
├── README.md
├── requirements.txt
└── .claude/
    └── skills/
        ├── hmda-data-setup/        # Data layer
        │   ├── data/
        │   │   ├── hmda.duckdb     # DuckDB database (~800 MB, gitignored)
        │   │   └── 2024_public_lar.csv  # Raw HMDA data (~4.6 GB, gitignored)
        │   └── sql/                # Analysis queries (run these against the DB)
        │       ├── 01_lender_analysis.sql
        │       ├── 02_income_risk.sql
        │       ├── 03_geographic_gaps.sql
        │       └── 04_denial_reasons.sql
        ├── hmda-analysis/          # SQL generation skill (Claude)
        │   └── SKILL.md
        └── hmda-dashboard/         # Dashboard skill (Claude)
            ├── SKILL.md
            └── dashboard.py        # Streamlit app
```

## Dashboard Pages

| Page | Analysis |
|------|----------|
| Lender Analysis | Approval/denial rates and market share by lender |
| Income Risk | Loan approval patterns across income brackets |
| Geographic Gaps | State-level lending disparities |
| Denial Reasons | Common denial reasons by applicant demographics |

## Data

- **Source:** [FFIEC HMDA Platform](https://ffiec.cfpb.gov/) — 2024 national snapshot
- **Size:** ~12–13M loan records, 100+ fields
- **Database:** DuckDB (file-based, no server required)

Data is gitignored. To re-ingest, download the 2024 HMDA snapshot CSV from ffiec.cfpb.gov and load it into DuckDB as `hmda_2024`.

## Tech Stack

- **DuckDB** — SQL analytics engine
- **Streamlit** — Interactive dashboard
- **Plotly** — Charts and visualizations
- **Pandas** — Data handling

## Fair Lending Note

Approval rate disparities may reflect legitimate factors (credit scores, debt-to-income, loan characteristics). Do not draw causal conclusions from aggregate patterns alone.
