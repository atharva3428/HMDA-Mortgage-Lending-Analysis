---
name: hmda-dashboard
description: Generate interactive Streamlit dashboards from HMDA SQL analysis files. Use this whenever the user wants to visualize HMDA data, create interactive dashboards, build data visualizations, or explore lending analysis results. The skill auto-discovers SQL files in the /sql/ folder, executes them against DuckDB, and creates separate pages with effective visualizations (bar charts, line charts, tables, etc.). Perfect for turning analysis queries into shareable, interactive dashboards that stakeholders can explore.
compatibility: Requires Python 3.x, Streamlit, Plotly, Pandas, DuckDB
---

# HMDA Dashboard Visualization Skill

## What This Skill Does

This skill transforms **HMDA SQL analysis files into interactive Streamlit dashboards**. It:

1. **Auto-discovers SQL files** in your `/sql/` folder
2. **Executes queries** against your DuckDB database
3. **Creates a multi-page dashboard** (one page per SQL file)
4. **Visualizes results effectively** using Plotly charts and tables
5. **Adds interactive filters** for exploring data by year, lender, state, income level, etc.

## When to Use This Skill

Use this skill when you want to:
- **Turn SQL analysis into dashboards** for exploration and sharing
- **Create interactive visualizations** from HMDA lending data
- **Build dashboards quickly** without writing Streamlit code
- **Generate reports** that stakeholders can filter and explore
- **Share findings** with non-technical users via an interactive interface

You should **always use this skill** when a user mentions dashboards, visualizations, interactive reports, or wanting to explore analysis results visually — even if they don't explicitly say "dashboard." The skill handles all the boilerplate.

## How It Works

### Step 1: Auto-Discovery
The skill scans your `/sql/` folder and finds all `.sql` files:
```
sql/
├── 01_lender_analysis.sql
├── 02_income_risk.sql
├── 03_geographic_gaps.sql
├── 04_denial_reasons.sql
└── 05_yoy_trends.sql
```

### Step 2: Page Creation
For each SQL file, the skill creates a **separate dashboard page**:
- **Page 1:** Lender Analysis → Bar chart of top lenders by approval rate
- **Page 2:** Income Risk → Line chart showing approval rates by income level
- **Page 3:** Geographic Gaps → Heatmap or scatter showing state disparities
- **Page 4:** Denial Reasons → Bar chart of most common denial reasons
- **Page 5:** YoY Trends → Comparison chart of 2023 vs 2024 metrics

### Step 3: Visualization Selection
The skill automatically chooses the best chart type based on the data:
- **Lender metrics** → Bar charts (comparison across lenders)
- **Income buckets** → Line or bar charts (trend across income levels)
- **Geographic data** → Maps or scatter plots (state-level analysis)
- **Denial reasons** → Horizontal bar charts (category comparison)
- **Time comparisons** → Line charts (2023 vs 2024 trends)

### Step 4: Interactivity
Each page includes:
- **Filters** in the sidebar (year, lender, state, income level, etc.)
- **Interactive charts** from Plotly (hover tooltips, zoom, pan)
- **Data tables** showing raw results
- **Summary metrics** highlighting key insights

## Dashboard Structure

```
dashboard.py
├── Page 1: Lender Analysis
│   ├── Visualization: Bar chart (top 10 lenders by approval rate)
│   ├── Metrics: Total applications, approval/denial counts
│   └── Interactions: Filter by lender type, show raw data
│
├── Page 2: Income Risk Analysis
│   ├── Visualization: Line chart (approval rate by income bucket)
│   ├── Metrics: Total by income level, approval trends
│   └── Interactions: Compare income levels, view statistics
│
├── Page 3: Geographic Gaps
│   ├── Visualization: Scatter/heatmap (approval rate gap by state)
│   ├── Metrics: Largest disparities, state-by-state comparison
│   └── Interactions: Filter by gap size, sort by disparity
│
├── Page 4: Denial Reasons
│   ├── Visualization: Bar chart (top denial reasons by lender)
│   ├── Metrics: Most common reasons, frequency distribution
│   └── Interactions: Filter by lender, drill into specific reasons
│
└── Page 5: YoY Trends
    ├── Visualization: Comparison chart (2023 vs 2024 metrics)
    ├── Metrics: Year-over-year changes, percentage deltas
    └── Interactions: View absolute or percentage changes
```

## Generated Files

When you run this skill, it creates:
```
dashboard.py              ← Main Streamlit app (auto-generated)
run_dashboard.sh         ← Script to launch the dashboard
```

## How to Run

### Option 1: Run the Generated Script
```bash
bash run_dashboard.sh
# Opens http://localhost:8501
```

### Option 2: Run Directly with Streamlit
```bash
streamlit run dashboard.py
```

### Option 3: Run with Custom Port
```bash
streamlit run dashboard.py --server.port 8502
```

## Visualization Types by Analysis

| SQL File | Data Type | Chart Type | Key Metric |
|---|---|---|---|
| `01_lender_analysis.sql` | Categorical (lenders) | Bar chart | Approval rate by lender |
| `02_income_risk.sql` | Ordinal (income buckets) | Line chart | Approval rate trend |
| `03_geographic_gaps.sql` | Geographic (states) | Scatter/heatmap | Approval rate disparity |
| `04_denial_reasons.sql` | Categorical (reasons) | Horizontal bar chart | Denial reason frequency |
| `05_yoy_trends.sql` | Time series (2023 vs 2024) | Grouped bar/line | YoY change |

## Customization

The generated dashboard can be customized:

### Add Filters
```python
selected_lender = st.sidebar.selectbox(
    "Filter by Lender",
    ["All"] + lenders_list
)
# Filter data based on selection
filtered_data = data[data['lei'] == selected_lender] if selected_lender != "All" else data
```

### Change Chart Types
```python
chart_type = st.sidebar.radio("Chart Type", ["Bar", "Line", "Area"])
if chart_type == "Bar":
    st.bar_chart(data)
elif chart_type == "Line":
    st.line_chart(data)
```

### Add Metrics
```python
col1, col2, col3 = st.columns(3)
col1.metric("Total Applications", f"{total:,}")
col2.metric("Approval Rate", f"{approval_pct:.2f}%")
col3.metric("Denial Count", f"{denials:,}")
```

## Key Features

✓ **Auto-discovers SQL files** — No configuration needed
✓ **Intelligent visualizations** — Chart type chosen automatically
✓ **Interactive filters** — Sidebar controls for exploring data
✓ **Multi-page layout** — One page per analysis
✓ **Summary metrics** — Key insights at a glance
✓ **Data tables** — View raw results alongside charts
✓ **Responsive design** — Works on desktop and tablet
✓ **Fast refresh** — Cached queries for performance

## Example Usage

**User asks:** "Create a dashboard for our HMDA analyses"

**Skill does:**
1. Finds all 5 SQL files in `/sql/`
2. Creates `dashboard.py` with 5 pages
3. Provides `run_dashboard.sh` script
4. Returns instructions for launching

**User runs:** `bash run_dashboard.sh`

**Result:** Interactive dashboard at `localhost:8501` with all analyses visualized

## Dependencies

The skill generates code using:
- **Streamlit** — Multi-page dashboard framework
- **Plotly** — Interactive visualizations
- **Pandas** — Data manipulation
- **DuckDB** — Query execution
- **Python 3.x** — Runtime

## Next Steps

After generating the dashboard:
1. Run `bash run_dashboard.sh`
2. Explore each page and verify visualizations
3. Use sidebar filters to drill into data
4. Share the dashboard link with stakeholders
5. Customize colors, filters, or chart types as needed
