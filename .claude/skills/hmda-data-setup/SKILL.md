---
name: hmda-data-setup
description: "Download 2023 and 2024 HMDA mortgage lending datasets from ffiec.cfpb.gov and load them into DuckDB. Creates /data folder, saves CSVs (hmda_2023.csv and hmda_2024.csv), and creates hmda.duckdb for querying. Use this skill to set up the data layer as a one-time initialization."
---

## Overview

This skill downloads HMDA (Home Mortgage Disclosure Act) mortgage lending data and loads it into DuckDB for querying. It:

1. Creates `/data` folder
2. Downloads 2023 and 2024 HMDA national snapshots (~2-3 GB each)
3. Saves as separate CSVs: `hmda_2023.csv` and `hmda_2024.csv`
4. Loads both into `/data/hmda.duckdb`
5. Updates `.gitignore` to exclude large files

## Prerequisites

- Python 3.x
- Virtual environment at `C:\ClaudeCode.venv`
- ~6-8 GB free disk space

## How to Run

### 1. Activate Virtual Environment

```bash
C:\ClaudeCode.venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt should contain:**
```
requests>=2.31.0
pandas>=2.0.0
duckdb>=0.9.0
```

### 3. Execute the Script

```bash
python scripts/ingest.py
```

This will download and load the data (~20-45 minutes depending on connection speed).

## After Completion

You should see:
- `/data/hmda_2023.csv` (~2-3 GB)
- `/data/hmda_2024.csv` (~2-3 GB)
- `/data/hmda.duckdb` (~3-4 GB)
- Console output with row counts for each year

Both years are loaded in separate tables (`hmda_2023` and `hmda_2024`) and unified in a `hmda_combined` view in DuckDB.

## Troubleshooting

**Connection timeout:** Check internet connection. Script has 3 retry attempts built in.

**Disk space error:** Free up space and re-run. Script will skip already-downloaded CSVs.

**DuckDB corruption:** Delete `/data/hmda.duckdb` and re-run `ingest.py` to recreate (CSVs will be reused).
