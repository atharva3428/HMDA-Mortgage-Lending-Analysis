"""
HMDA Data Ingestion Pipeline
Downloads 2024 HMDA national snapshot dataset from FFIEC and loads into DuckDB.

Usage:
    python .claude/skills/hmda-data-setup/scripts/ingest.py

This script:
1. Creates data directory in the skill folder
2. Downloads 2024 HMDA LAR CSV from ffiec.cfpb.gov
3. Saves it as 2024_public_lar.csv
4. Loads into DuckDB (hmda.duckdb)
5. Validates schema and prints summary statistics
"""

import sys
import csv
import zipfile
from pathlib import Path
from typing import Optional

try:
    import requests
    import pandas as pd
    import duckdb
except ImportError as e:
    print(f"Error: Required package not installed: {e}")
    print("Install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


# Configuration
# Use path relative to script location so it works from any directory
DATA_DIR = Path(__file__).parent.parent / "data"
DUCKDB_PATH = DATA_DIR / "hmda.duckdb"

# LAR (Loan/Application Records) download link from FFIEC
# Note: Downloaded as ZIP, will be extracted
LAR_DOWNLOAD = "https://files.ffiec.cfpb.gov/static-data/snapshot/2024/2024_public_lar_csv.zip"

# Expected column names from HMDA dataset (subset of key columns)
EXPECTED_COLUMNS = {
    "lei", "ffiec_rsa_id", "respondent_name", "agency_code", "app_year",
    "loan_amount_000s", "action_taken", "action_taken_name", "purchaser_type",
    "rate_spread", "hoepa_status", "lien_status", "co_applicant_sex", "applicant_ethnicity",
    "applicant_race_1", "applicant_sex", "applicant_age", "income_000s",
    "debt_to_income_ratio", "loan_purpose", "loan_product_type", "loan_term_months",
    "applicant_credit_score_type", "co_applicant_credit_score_type", "denial_reason_1"
}


def create_directories():
    """Create required project directories."""
    print("[*] Creating project directories...")
    DATA_DIR.mkdir(exist_ok=True)
    Path("scripts").mkdir(exist_ok=True)
    Path("sql").mkdir(exist_ok=True)
    print("[OK] Directory structure created")


def update_gitignore():
    """Update .gitignore to exclude large data files."""
    print("\n[*] Updating .gitignore...")
    gitignore_path = Path(".gitignore")

    entries_to_add = {
        "*.csv",
        "*.duckdb",
        ".python-version",
        ".claude/",
        "__pycache__/",
        "*.pyc",
        ".venv/",
        "venv/",
    }

    existing_entries = set()
    if gitignore_path.exists():
        with open(gitignore_path, "r") as f:
            existing_entries = set(line.strip() for line in f if line.strip() and not line.startswith("#"))

    new_entries = entries_to_add - existing_entries

    if new_entries:
        with open(gitignore_path, "a") as f:
            if existing_entries:  # Add newline if file has content
                f.write("\n")
            f.write("# Large data files (generated locally, not committed)\n")
            for entry in sorted(new_entries):
                f.write(f"{entry}\n")
        print(f"[OK] Added {len(new_entries)} entries to .gitignore")
    else:
        print("[OK] .gitignore already up to date")


def download_and_extract_lar(max_retries: int = 3) -> Optional[Path]:
    """
    Download HMDA LAR data ZIP from FFIEC and extract the CSV.

    Args:
        max_retries: Number of retry attempts if download fails

    Returns:
        Path to extracted CSV file, or None if download failed
    """
    csv_path = DATA_DIR / "2024_public_lar.csv"

    # Skip if already extracted
    if csv_path.exists():
        file_size_gb = csv_path.stat().st_size / (1024**3)
        print(f"[OK] 2024 LAR CSV already exists ({file_size_gb:.1f} GB)")
        return csv_path

    zip_path = DATA_DIR / "2024_public_lar_csv.zip"

    print(f"\n[*] Downloading 2024 HMDA LAR data from FFIEC...")
    print(f"    URL: {LAR_DOWNLOAD}")

    for attempt in range(max_retries):
        try:
            response = requests.get(LAR_DOWNLOAD, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            # Download ZIP file
            with open(zip_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            gb_downloaded = downloaded / (1024**3)
                            gb_total = total_size / (1024**3)
                            print(f"    Progress: {gb_downloaded:.1f} GB / {gb_total:.1f} GB ({percent:.0f}%)", end="\r")

            zip_size_gb = zip_path.stat().st_size / (1024**3)
            print(f"[OK] ZIP downloaded ({zip_size_gb:.1f} GB)              ")

            # Extract ZIP file
            print(f"\n[*] Extracting CSV from ZIP...")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                # Find the CSV file in the ZIP
                csv_files = [f for f in zip_ref.namelist() if f.endswith(".csv")]
                if not csv_files:
                    print(f"[ERR] No CSV file found in ZIP")
                    return None

                csv_file = csv_files[0]
                zip_ref.extract(csv_file, DATA_DIR)
                extracted_path = DATA_DIR / csv_file

                # Rename to standard name
                extracted_path.rename(csv_path)
                print(f"[OK] Extracted and saved to {csv_path.name}")

            # Clean up ZIP
            zip_path.unlink()
            return csv_path

        except (requests.RequestException, IOError, zipfile.BadZipFile) as e:
            print(f"[ERR] Download/extraction failed (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print(f"[ERR] Failed to download 2024 data after {max_retries} attempts")
                return None

    return None


def validate_csv_schema(csv_path: Path, year: int) -> bool:
    """Validate that CSV has expected HMDA columns."""
    print(f"\n[*] Validating {year} CSV schema...")

    try:
        # Read first row to check columns
        with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            first_row = next(reader, None)

            if not first_row:
                print(f"[ERR] CSV is empty")
                return False

            csv_columns = set(first_row.keys())

            # Check for key HMDA columns
            missing_columns = EXPECTED_COLUMNS - csv_columns

            if missing_columns:
                print(f"[WARN] Warning: Missing expected columns: {missing_columns}")
                # This is a warning, not a failure — schema may have changed

            print(f"[OK] {year} CSV has {len(csv_columns)} columns")
            return True

    except Exception as e:
        print(f"[ERR] Validation failed: {e}")
        return False


def load_csv_to_duckdb(csv_path: Path, year: int, conn: duckdb.DuckDBPyConnection) -> bool:
    """Load CSV into DuckDB."""
    print(f"\n[*] Loading {year} CSV into DuckDB...")

    try:
        table_name = f"hmda_{year}"

        # DuckDB can read CSVs directly
        # Escape the path to prevent SQL injection
        escaped_path = str(csv_path).replace("'", "''")
        query = f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{escaped_path}', sample_size=-1, nullstr='NA')
        """

        conn.execute(query)

        # Get row count
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"[OK] Loaded {row_count:,} rows from {year} data into table '{table_name}'")

        return True

    except Exception as e:
        print(f"[ERR] Failed to load {year} data: {e}")
        return False




def print_summary_statistics(conn: duckdb.DuckDBPyConnection):
    """Print summary statistics for loaded data."""
    print(f"\n[*] Summary Statistics")
    print("=" * 60)

    try:
        table_name = "hmda_2024"
        row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        col_count = len(conn.execute(f"DESCRIBE {table_name}").fetchall())
        print(f"2024: {row_count:>15,} rows  |  {col_count:>3} columns")

        print("=" * 60)
        print("\n[OK] Data successfully ingested!")

    except Exception as e:
        print(f"[WARN] Could not print statistics: {e}")


def main():
    """Main ingestion pipeline."""
    print("\n" + "="*60)
    print("HMDA Data Ingestion Pipeline")
    print("="*60)

    # Create directories
    create_directories()

    # Update gitignore
    update_gitignore()

    # Download and extract LAR CSV
    csv_path = download_and_extract_lar()

    if not csv_path:
        print("\n[ERR] No CSV file available. Cannot continue.")
        return False

    # Validate CSV
    if not validate_csv_schema(csv_path, 2024):
        print("\n[ERR] CSV validation failed. Cannot continue.")
        return False

    # Connect to DuckDB and load data
    print(f"\n[*] Connecting to DuckDB database...")
    try:
        conn = duckdb.connect(str(DUCKDB_PATH))
        print(f"[OK] Connected to {DUCKDB_PATH}")
    except Exception as e:
        print(f"[ERR] Failed to connect to DuckDB: {e}")
        return False

    # Load CSV
    if not load_csv_to_duckdb(csv_path, 2024, conn):
        print("\n[ERR] Data failed to load. Check errors above.")
        conn.close()
        return False

    # Print summary
    print_summary_statistics(conn)

    # Close connection
    conn.close()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
