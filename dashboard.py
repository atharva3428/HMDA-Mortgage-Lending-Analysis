"""
HMDA Lending Analysis Dashboard
================================
Production-ready Streamlit dashboard for exploring mortgage lending data.
Auto-discovers and visualizes SQL analyses with comprehensive metrics,
interactive filters, and professional layout.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import duckdb
import urllib.request
from pathlib import Path
from datetime import datetime

# ============================================================================
# S3 Configuration
# ============================================================================
S3_DB_URL = "https://hmda-mortgage-analysis.s3.us-east-2.amazonaws.com/hmda.duckdb"
DB_CACHE_PATH = Path(__file__).resolve().parent / "hmda.duckdb"


def ensure_database():
    """Download database from S3 if not cached locally."""
    if DB_CACHE_PATH.exists():
        return True, None

    try:
        progress = st.empty()
        progress.info("Downloading database from S3 (847 MB, one-time only)...")

        def reporthook(count, block_size, total_size):
            if total_size > 0:
                pct = min(int(count * block_size * 100 / total_size), 100)
                progress.info(f"Downloading database from S3... {pct}%")

        urllib.request.urlretrieve(S3_DB_URL, DB_CACHE_PATH, reporthook)
        progress.success("Database downloaded and cached.")
        return True, None
    except Exception as e:
        return False, f"Failed to download database: {str(e)[:200]}"

# ============================================================================
# Configuration & Styling
# ============================================================================
st.set_page_config(
    page_title="HMDA Lending Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better spacing
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .section-header {
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 10px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Database & File Discovery
# ============================================================================
@st.cache_resource
def get_db_connection():
    """Establish DuckDB connection, downloading from S3 if needed."""
    try:
        # Try local skills path first (development), then cached path (production)
        local_path = Path(__file__).resolve().parent.parent / "hmda-data-setup" / "data" / "hmda.duckdb"
        if local_path.exists():
            db_path = local_path
        else:
            ok, err = ensure_database()
            if not ok:
                return None, err
            db_path = DB_CACHE_PATH

        conn = duckdb.connect(str(db_path), read_only=True)
        conn.execute("SELECT 1").fetchone()
        return conn, None
    except Exception as e:
        return None, f"Connection failed: {str(e)[:150]}"

@st.cache_data
def discover_sql_files():
    """Auto-discover and validate SQL files"""
    # Local dev path
    sql_dir = Path(__file__).resolve().parent.parent / "hmda-data-setup" / "sql"
    # Streamlit Cloud path (sql/ folder alongside dashboard.py)
    if not sql_dir.exists():
        sql_dir = Path(__file__).resolve().parent / "sql"
    if not sql_dir.exists():
        return [], "SQL directory not found"

    sql_files = sorted(sql_dir.glob("*.sql"))
    if not sql_files:
        return [], "No SQL files discovered"

    return sql_files, None

def load_sql_file(filename):
    """Load SQL file with validation"""
    try:
        sql_dir = Path(__file__).resolve().parent.parent / "hmda-data-setup" / "sql"
        with open(sql_dir / filename, 'r') as f:
            content = f.read()
        if not content.strip():
            return None, "File is empty"
        return content, None
    except Exception as e:
        return None, str(e)

# ============================================================================
# Query Execution
# ============================================================================
@st.cache_data
def execute_analysis(filename):
    """Execute SQL analysis with comprehensive error handling"""
    try:
        conn, error = get_db_connection()
        if error:
            return None, error

        sql_dir = Path(__file__).resolve().parent.parent / "hmda-data-setup" / "sql"
        sql_path = sql_dir / filename
        if not sql_path.exists():
            return None, f"File not found: {filename}"

        query, error = load_sql_file(filename)
        if error:
            return None, error

        df = conn.execute(query).fetchdf()
        return df, None

    except duckdb.Error as e:
        return None, f"SQL Error: {str(e)[:100]}"
    except Exception as e:
        return None, f"Error: {str(e)[:100]}"

# ============================================================================
# Analysis Metadata
# ============================================================================
ANALYSIS_METADATA = {
    "01_lender_analysis.sql": {
        "title": "Lender Performance Analysis",
        "description": "Approval vs. denial rates by lender, market share, trends",
        "icon": "🏦",
        "chart_type": "lender_bar",
        "key_metrics": ["approval_rate", "pct_originated", "num_applications"]
    },
    "02_income_risk.sql": {
        "title": "Income Risk Analysis",
        "description": "Approval patterns across income levels, risk assessment",
        "icon": "💰",
        "chart_type": "income_line",
        "key_metrics": ["pct_originated", "pct_approved", "pct_denied"]
    },
    "03_geographic_gaps.sql": {
        "title": "Geographic Disparity Analysis",
        "description": "Lending gaps by state and race, equity insights",
        "icon": "🗺️",
        "chart_type": "gap_scatter",
        "key_metrics": ["approval_rate_gap_pp", "pct_approved"]
    },
    "04_denial_reasons.sql": {
        "title": "Denial Reason Analysis",
        "description": "Top denial reasons by lender, pattern identification",
        "icon": "❌",
        "chart_type": "denial_barh",
        "key_metrics": ["num_denials", "pct_of_lender_denials"]
    },
    "05_yoy_trends.sql": {
        "title": "Year-over-Year Trends",
        "description": "2023 vs 2024 comparisons, growth and change metrics",
        "icon": "📈",
        "chart_type": "trend_comparison",
        "key_metrics": ["apps_2024", "approval_rate_2024"]
    }
}

# ============================================================================
# Visualization Engine
# ============================================================================
def create_chart(df, analysis_type):
    """Create specialized visualization based on analysis type"""
    if df is None or len(df) == 0:
        return None

    try:
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        string_cols = df.select_dtypes(include=['object']).columns.tolist()

        if analysis_type == "lender_bar" and string_cols and numeric_cols:
            fig = px.bar(df.head(15), x=string_cols[0], y=numeric_cols[0],
                        color=numeric_cols[0], color_continuous_scale='Viridis',
                        title=f"Top Lenders by {numeric_cols[0]}")
            fig.update_layout(height=500, xaxis_tickangle=-45)
            return fig

        elif analysis_type == "income_line" and string_cols and numeric_cols:
            fig = px.line(df, x=string_cols[0], y=numeric_cols[0],
                         markers=True, title="Income Analysis Trends")
            fig.update_layout(height=500, hovermode='x unified')
            return fig

        elif analysis_type == "gap_scatter" and len(numeric_cols) >= 2:
            fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                           color=string_cols[0] if string_cols else None,
                           title="Geographic Lending Analysis",
                           trendline="ols")
            fig.update_layout(height=500)
            return fig

        elif analysis_type == "denial_barh" and string_cols and numeric_cols:
            df_top = df.head(10)
            fig = px.bar(df_top, x=numeric_cols[0], y=string_cols[0],
                        orientation='h', color=numeric_cols[0],
                        color_continuous_scale='Reds',
                        title="Top Denial Reasons")
            return fig

        elif analysis_type == "trend_comparison" and len(numeric_cols) >= 2:
            fig = go.Figure()
            for col in numeric_cols[:3]:
                fig.add_trace(go.Scatter(y=df[col], mode='lines+markers',
                                        name=col.replace('_', ' ')))
            fig.update_layout(title="Trends Comparison", height=500)
            return fig

        return None
    except Exception as e:
        return None

# ============================================================================
# Summary Metrics Generator
# ============================================================================
def calculate_summary_metrics(df, key_metric_names):
    """Extract and format summary metrics"""
    metrics = {}

    for metric in key_metric_names:
        metric_lower = metric.lower()
        # Find matching column (case-insensitive)
        matching_col = next((col for col in df.columns
                           if col.lower() == metric_lower), None)

        if matching_col:
            col_data = df[matching_col]
            if col_data.dtype in ['int64', 'float64']:
                if 'pct' in metric_lower or 'rate' in metric_lower:
                    metrics[metric] = f"{col_data.mean():.1f}%"
                elif 'num' in metric_lower or 'count' in metric_lower or 'applications' in metric_lower:
                    metrics[metric] = f"{int(col_data.sum()):,}"
                else:
                    metrics[metric] = f"{col_data.mean():.2f}"

    return metrics

# ============================================================================
# Sidebar
# ============================================================================
with st.sidebar:
    st.markdown("## 🎛️ Dashboard Controls")

    display_mode = st.radio(
        "Display Mode:",
        ["Dashboard Overview", "Detailed Analysis", "Comparison View"]
    )

    st.divider()

    show_sql = st.checkbox("📝 Show SQL Queries", value=False)
    show_metrics = st.checkbox("📊 Show Summary Metrics", value=True)
    show_table = st.checkbox("📋 Show Data Tables", value=True)

    st.divider()

    export_type = st.selectbox(
        "📥 Export Format:",
        ["CSV", "JSON", "Excel (coming soon)"]
    )

    st.divider()

    st.markdown("""
    ### ℹ️ About
    **HMDA Dashboard v1.0**

    Interactive visualization of mortgage lending data with auto-discovery
    of SQL analyses and professional charting.

    **Last Updated:** 2024-Q1
    """)

# ============================================================================
# Main Dashboard
# ============================================================================
st.title("📊 HMDA Lending Analysis Dashboard")
st.markdown("*Comprehensive exploration of U.S. mortgage lending patterns*")

# Discover analyses
sql_files, discovery_error = discover_sql_files()

if discovery_error or not sql_files:
    st.error(f"❌ {discovery_error}")
    st.stop()

# ============================================================================
# Dashboard Overview
# ============================================================================
if display_mode == "Dashboard Overview":
    st.markdown("### 📈 Executive Summary")

    # Top metrics grid
    metric_cols = st.columns(len(sql_files))
    analysis_data = {}

    for col, sql_file in zip(metric_cols, sql_files):
        filename = sql_file.name
        df, error = execute_analysis(filename)
        analysis_data[filename] = (df, error)

        with col:
            if error:
                st.metric(filename.replace('.sql', ''), "N/A", "❌")
            else:
                st.metric(
                    ANALYSIS_METADATA[filename]["icon"] + " " +
                    ANALYSIS_METADATA[filename]["title"],
                    f"{len(df):,} rows"
                )

    st.divider()

    # Grid of visualizations
    st.markdown("### 📊 Analysis Preview")

    for idx, sql_file in enumerate(sql_files):
        filename = sql_file.name
        df, error = analysis_data[filename]

        if idx % 2 == 0:
            col1, col2 = st.columns(2)
        col = col1 if idx % 2 == 0 else col2

        with col:
            metadata = ANALYSIS_METADATA[filename]

            with st.container():
                st.subheader(f"{metadata['icon']} {metadata['title']}")
                st.caption(metadata['description'])

                if error:
                    st.error(f"⚠️ {error}")
                else:
                    # Chart
                    fig = create_chart(df, metadata['chart_type'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

                    # Metrics
                    if show_metrics:
                        metrics = calculate_summary_metrics(df, metadata['key_metrics'])
                        if metrics:
                            st.markdown("**Key Metrics:**")
                            for metric, value in list(metrics.items())[:3]:
                                st.caption(f"• {metric}: **{value}**")

# ============================================================================
# Detailed Analysis
# ============================================================================
elif display_mode == "Detailed Analysis":
    st.markdown("### 🔍 Detailed Analysis View")

    selected_analysis = st.selectbox(
        "Select Analysis:",
        sql_files,
        format_func=lambda x: ANALYSIS_METADATA[x.name]["title"]
    )

    if selected_analysis:
        filename = selected_analysis.name
        metadata = ANALYSIS_METADATA[filename]
        df, error = execute_analysis(filename)

        st.subheader(f"{metadata['icon']} {metadata['title']}")
        st.write(metadata['description'])

        if error:
            st.error(f"❌ {error}")
        else:
            # Metrics row
            if show_metrics:
                st.markdown("#### Summary Statistics")
                metrics = calculate_summary_metrics(df, metadata['key_metrics'])
                if metrics:
                    metric_cols = st.columns(min(3, len(metrics)))
                    for col, (metric, value) in zip(metric_cols, metrics.items()):
                        with col:
                            st.metric(metric.replace('_', ' '), value)
                else:
                    st.info("No summary metrics available for this analysis.")

            st.divider()

            # Visualization
            st.markdown("#### Visualization")
            fig = create_chart(df, metadata['chart_type'])
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # SQL Query
            if show_sql:
                st.markdown("#### SQL Query")
                query, _ = load_sql_file(filename)
                st.code(query, language="sql")

            # Data Table
            if show_table:
                st.markdown("#### Data Table")
                st.dataframe(df, use_container_width=True, height=400)

                # Export
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📥 Download as CSV"):
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="CSV",
                            data=csv,
                            file_name=f"{filename.replace('.sql', '')}.csv",
                            mime="text/csv"
                        )
                with col2:
                    if st.button("📥 Download as JSON"):
                        json = df.to_json(orient="records", indent=2)
                        st.download_button(
                            label="JSON",
                            data=json,
                            file_name=f"{filename.replace('.sql', '')}.json",
                            mime="application/json"
                        )

# ============================================================================
# Comparison View
# ============================================================================
else:  # Comparison View
    st.markdown("### 🔄 Cross-Analysis Comparison")

    # Load all analyses
    all_data = {}
    for sql_file in sql_files:
        df, error = execute_analysis(sql_file.name)
        all_data[sql_file.name] = (df, error)

    # Show all in tabs
    tabs = st.tabs([ANALYSIS_METADATA[f.name]["icon"] + " " +
                   ANALYSIS_METADATA[f.name]["title"] for f in sql_files])

    for tab, sql_file in zip(tabs, sql_files):
        with tab:
            df, error = all_data[sql_file.name]
            metadata = ANALYSIS_METADATA[sql_file.name]

            if error:
                st.error(f"❌ {error}")
            else:
                # Compact view
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown("**Info**")
                    st.caption(metadata['description'])
                    st.metric("Records", len(df))
                    st.metric("Columns", len(df.columns))

                with col2:
                    fig = create_chart(df, metadata['chart_type'])
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# Footer & Documentation
# ============================================================================
st.divider()

with st.expander("ℹ️ Dashboard Help & Documentation"):
    st.markdown("""
    ### How to Use This Dashboard

    **Display Modes:**
    - **Dashboard Overview**: Quick metrics and preview charts for all analyses
    - **Detailed Analysis**: Deep dive into a single analysis with full data
    - **Comparison View**: Side-by-side comparison of all analyses

    **Controls:**
    - Toggle SQL queries, metrics, and data tables in the sidebar
    - Select export format (CSV/JSON) for downloaded data
    - Use interactive Plotly charts (zoom, pan, hover for details)

    ### Analyses Included

    1. **Lender Performance** — Top lenders by approval rate, market share
    2. **Income Risk** — How applicant income affects approval probability
    3. **Geographic Gaps** — State-level lending disparities by race
    4. **Denial Reasons** — Most common reasons for loan denials
    5. **Year-over-Year** — Trends from 2023 to 2024

    ### Data Source
    - **Data**: HMDA (Home Mortgage Disclosure Act) mortgage lending data
    - **Coverage**: U.S. national mortgage lending (2023-2024)
    - **Database**: DuckDB (data/hmda.duckdb)

    ### Disclaimer
    Analysis of lending patterns by race or other characteristics
    reflect correlation, not causation. Disparities may reflect legitimate
    credit/financial differences.
    """)

st.markdown(f"*Dashboard v1.0 • Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
