# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HMDA Mortgage Lending Analysis** is a Python data analysis project that ingests US mortgage lending data from the FFIEC HMDA Platform, analyzes it using DuckDB SQL, and surfaces insights through an interactive Streamlit dashboard.

The project has four core components:
1. **Data Ingestion/ETL** — Download HMDA national snapshot CSVs (2023, 2024) and load into DuckDB
2. **SQL Analysis Engine** — All business logic lives in `.sql` files organized by theme
3. **Python Orchestration** — Scripts that execute SQL queries and return Pandas dataframes
4. **Streamlit Dashboard** — Interactive 5-page dashboard with Plotly visualizations and sidebar filters

## Tech Stack

- **Python 3.x** — Core language for ingestion, orchestration, and dashboard
- **DuckDB** — SQL analysis layer (file-based, no server needed)
- **Pandas** — Result handling and transformation
- **Streamlit** — Interactive dashboard framework
- **Plotly** — Chart visualization
- **Requirements** — All pinned in `requirements.txt`

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Download HMDA CSVs and ingest into DuckDB
python scripts/ingest.py

# Run data quality checks and profiling
python scripts/profile.py

# Launch the dashboard (opens at http://localhost:8501)
streamlit run dashboard.py
```

## Common Development Commands

### Data Ingestion
```bash
# Download 2023 and 2024 HMDA datasets and load into DuckDB
python scripts/ingest.py
# Creates/updates: data/hmda.duckdb
```

### Run Analysis Queries
```bash
# Execute a specific SQL analysis and print results
python scripts/analysis.py --query lender_analysis
python scripts/analysis.py --query income_risk
python scripts/analysis.py --query geographic_gaps
python scripts/analysis.py --query denial_reasons
python scripts/analysis.py --query yoy_trends
```

### Data Profiling
```bash
# Run data quality checks and summary statistics
python scripts/profile.py
```

### Dashboard Development
```bash
# Launch Streamlit dashboard locally
streamlit run dashboard.py

# Run with debug/verbose output
streamlit run dashboard.py --logger.level=debug
```
## Project Structure
- Organize code into logical modules and packages.
- Use descriptive folder and file names.
- Separate notebooks, scripts, and utility files.
- Keep documentation and media assets in dedicated folders.
## Documentation
- Maintain clear and concise README files.
- Use Markdown for all documentation.
- Document setup, usage, and contribution guidelines.
  
## Architecture & File Organization

### `/sql` — Analysis Layer (Primary)
All business logic is SQL-first. Each `.sql` file contains a complete, standalone query that answers a specific business question:

- `01_lender_analysis.sql` — Approval vs. denial rates by lender, market share, approval rate trends
- `02_income_risk.sql` — Income-to-loan ratios, risk patterns by applicant demographics
- `03_geographic_gaps.sql` — Geographic lending disparity detection, regional approval/denial gaps
- `04_denial_reasons.sql` — Denial reason distribution by lender, demographics, geography
- `05_yoy_trends.sql` — 2023 vs. 2024 year-over-year comparisons across all metrics

**SQL Philosophy:** SQL files should be **readable and self-documenting**. Someone reviewing the repo should understand the business question by opening the `.sql` file alone — without reading any Python code. Use clear column aliases, CTEs with descriptive names, and comments where logic is not obvious.

### `/scripts` — Python Orchestration
- `ingest.py` — Downloads HMDA CSVs from ffiec.cfpb.gov, validates schema, loads into DuckDB
- `profile.py` — Data quality checks, row counts, NULL distributions, summary statistics
- `analysis.py` — Executes `.sql` files, returns results as Pandas dataframes for inspection/testing
- `dashboard.py` — Main Streamlit entry point (5 pages, sidebar filters, Plotly charts)

### `/data` — Data Directory (Gitignored)
- Raw HMDA CSV files (2023, 2024) — downloaded by `ingest.py`
- `hmda.duckdb` — DuckDB database file (binary, gitignored)
- Store only the ingestion script; raw files and `.duckdb` are regenerated locally

### `/` — Root
- `requirements.txt` — Pinned Python dependencies
- `README.md` — User-facing project documentation
- `CLAUDE.md` — This file

## Key Conventions

### SQL Files
1. **Organize by business question**, not by table. Each `.sql` file should answer one specific question (e.g., "approval rates by lender", not "SELECT * FROM applications").
2. **Use CTEs liberally** for readability. Break complex queries into named, logical steps.
3. **Alias columns clearly**. No generic `COUNT(*) as count` — use `COUNT(*) as num_loans_denied`.
4. **Comment non-obvious logic**. The SQL should be understandable without consulting Python.
5. **Use consistent naming**:
   - `num_*` for counts (e.g., `num_denied`, `num_applicants`)
   - `pct_*` for percentages (e.g., `pct_denied`)
   - `yr_*` for year-over-year calculations (e.g., `yr_over_yr_change`)

### Python Scripts
1. **Minimal inline SQL**. All substantial queries belong in `.sql` files. Python imports and executes them.
2. **Use `analysis.py` as the bridge**. Query execution, result fetching, and Pandas transformation all go through a consistent interface.
3. **No hardcoded paths**. Use `os.path.join()` or `pathlib.Path` for cross-platform compatibility.
4. **Log ingestion steps**. `ingest.py` should be transparent about what it downloads, validates, and loads.

### Dashboard (Streamlit)
1. **Organize by page**, with clear navigation in the sidebar.
2. **Filters first**. Sidebar should contain year, lender, geography, and demographic filters before any charts.
3. **Use Plotly** for all charts (consistent interactivity across pages).
4. **Cache expensive queries** with `@st.cache_data` to avoid re-executing SQL on every page refresh.
5. **Error handling** — if a query returns no results or fails, display a clear message to the user.

## Development Workflow

### Adding a New Analysis
1. Write the SQL query in `/sql/NN_theme.sql` (follow the numbering convention).
2. Test the query locally in DuckDB:
   ```bash
   duckdb data/hmda.duckdb < sql/NN_theme.sql
   ```
3. Add a function in `analysis.py` to execute the query and return a dataframe:
   ```python
   def get_theme_analysis():
       return execute_sql('NN_theme.sql')
   ```
4. Add a new page in `dashboard.py` that calls the function and displays results with filters.
5. Test end-to-end:
   ```bash
   streamlit run dashboard.py
   ```

### Testing Queries
- Use `python scripts/analysis.py --query theme_name` to run a query and inspect the dataframe.
- Use `scripts/profile.py` to validate data quality before adding new analyses.
- DuckDB CLI can be used directly: `duckdb data/hmda.duckdb` opens an interactive shell.

### Data Updates
- Re-run `python scripts/ingest.py` to download the latest HMDA CSVs and refresh DuckDB.
- Run `python scripts/profile.py` after ingestion to verify data integrity.

## Important Notes

### Data Size & Performance
- Each HMDA snapshot is ~10M rows. Queries should use appropriate filters (year, state, lender) to keep results manageable.
- DuckDB handles these sizes efficiently; consider indexing on frequently-filtered columns (e.g., `lender_id`, `year`, `state`).

### Fair Lending Sensitivity
- This project analyzes lending patterns across demographics. Be careful with presentation of results — disparities can be due to legitimate factors (e.g., credit scores, debt-to-income).
- Always include context (e.g., "approval rate by race, controlling for loan amount and applicant income").
- Avoid drawing causal conclusions from correlations.

### CSV Downloads
- HMDA CSVs are large (~2-3 GB each) and are gitignored. Document the download URLs in `ingest.py` comments.
- Store only scripts and the DuckDB schema in version control.

## References

- FFIEC HMDA Platform: https://ffiec.cfpb.gov/
- DuckDB Documentation: https://duckdb.org/docs/
- Streamlit Documentation: https://docs.streamlit.io/
- Plotly Python: https://plotly.com/python/
