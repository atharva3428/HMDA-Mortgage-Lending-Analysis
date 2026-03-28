---
name: hmda-analysis
description: Generate SQL analysis queries for HMDA mortgage lending data. Use this whenever the user asks business questions about lending patterns, approval rates, denial reasons, income analysis, geographic gaps, lender performance, or any other HMDA data investigation. The skill takes a business question (e.g., "Which lenders have the highest denial rates?") and intelligently generates a SQL query, executes it against the DuckDB database, and returns a summary report with key findings. Perfect for exploratory data analysis and creating reusable analysis scripts.
compatibility: Requires Python 3.x, DuckDB, Pandas. Assumes HMDA data is pre-loaded in data/hmda.duckdb.
---

# HMDA Analysis Skill

## What This Skill Does

This skill converts **business questions about HMDA mortgage lending data** into executable SQL analysis queries. It:

1. **Understands the question** — parses what the user wants to know about lending patterns, applicants, lenders, or geographic trends
2. **Generates SQL intelligently** — creates a well-structured, optimized SQL query that answers the question using CTEs and clear aliases
3. **Executes against DuckDB** — runs the query against the already-loaded HMDA data in `data/hmda.duckdb`
4. **Produces a summary report** — shows key findings, insights, and saves the `.sql` file to `/sql` for future reference

## When to Use This Skill

Use this skill when the user asks **any question that requires analysis of HMDA data**, such as:
- "Which lenders have the highest denial rates?"
- "Show me approval rates by race and gender"
- "What are the most common reasons for loan denial?"
- "Which states have the biggest lending gaps?"
- "How did approval rates change year-over-year?"
- "Analyze the relationship between income and loan approval"

You should **always use this skill** when a user asks a data analysis question about HMDA lending patterns, even if they don't explicitly say "write a query" or "create an analysis". The user is asking for insight, and this skill is the right tool to deliver it.

## HMDA Data Schema

The HMDA data is stored in `hmda_2024` table in DuckDB. Key columns include:

**Applicant & Loan Info:**
- `income` — Applicant income (in dollars, as integer)
- `derived_ethnicity` — Ethnicity category (derived field)
- `derived_race` — Race category (derived field, recommended for analysis)
- `applicant_race_1`, `applicant_race_2`, etc. — Individual race fields
- `applicant_sex` — Gender of applicant (1=male, 2=female, 3=no co-applicant)
- `loan_amount` — Loan amount (in dollars, as integer)
- `derived_loan_product_type` — Type of loan (e.g., conventional, FHA)
- `derived_dwelling_category` — Type of property (e.g., single-family)
- `loan_purpose` — Purpose of loan (1=purchase, 2=home improvement, 3=refinance)

**Outcome & Reason:**
- `action_taken` — Application outcome
  - 1 = Loan originated
  - 2 = Application approved but not accepted
  - 3 = Application denied
  - 4 = Application withdrawn
  - 5 = File closed for incompleteness
  - 6 = Purchased by institution
- `denial_reason_1`, `denial_reason_2`, `denial_reason_3` — Codes for denial reasons

**Lender & Location:**
- `lei` — Legal Entity Identifier (unique lender ID)
- `state_code` — State code (e.g., 'CA', 'NY')
- `county_code` — County code
- `activity_year` — Year of application (2024, 2023, etc.)
- `derived_msa_md` — Metropolitan Statistical Area/Metropolitan Division code

## How to Generate SQL Queries

When generating a SQL query for an HMDA analysis question:

1. **Clarify what the user is really asking** — Identify the key metric (approval rate, count, average), the grouping dimension (by lender, by race, by state), and any filters (year, loan purpose, etc.)

2. **Follow SQL best practices** from the CLAUDE.md guidelines:
   - Use CTEs (Common Table Expressions) to break the query into logical steps
   - Use clear, descriptive column aliases (e.g., `num_loans_denied`, `pct_approved`, `yr_over_yr_change`)
   - Add comments for non-obvious logic
   - Use `num_*` for counts, `pct_*` for percentages, `yr_*` for year-over-year metrics

3. **Write for readability** — The SQL should be understandable by someone who opens the file later without reading any Python code

4. **Example SQL structure:**
   ```sql
   -- Query: Approval Rates by Lender (LEI)
   -- Purpose: Compare lending approval patterns across major lenders

   WITH lender_outcomes AS (
     SELECT
       lei,
       action_taken,
       COUNT(*) as num_applications
     FROM hmda_2024
     WHERE activity_year = 2024
     GROUP BY lei, action_taken
   ),

   lender_summary AS (
     SELECT
       lei,
       SUM(CASE WHEN action_taken = 1 THEN num_applications ELSE 0 END) as num_originated,
       SUM(CASE WHEN action_taken IN (1, 2) THEN num_applications ELSE 0 END) as num_approved_total,
       SUM(num_applications) as total_applications,
       ROUND(100.0 * SUM(CASE WHEN action_taken = 1 THEN num_applications ELSE 0 END) / SUM(num_applications), 2) as pct_originated
     FROM lender_outcomes
     GROUP BY lei
   )

   SELECT
     lei,
     num_originated,
     num_approved_total,
     total_applications,
     pct_originated
   FROM lender_summary
   WHERE total_applications > 100  -- Filter for meaningful sample sizes
   ORDER BY total_applications DESC
   LIMIT 10;
   ```

## Execution & Output

### Running the Query

1. Save the generated SQL to `/sql` with a descriptive name (e.g., `06_lender_approval_rates.sql`)
2. Execute it using Python/DuckDB:
   ```python
   import duckdb
   import pandas as pd

   con = duckdb.connect('data/hmda.duckdb')
   result = con.execute(open('sql/06_lender_approval_rates.sql').read()).df()
   print(result)
   ```

### Summary Report Format

After executing the query, provide a summary report to the user with:
- **Business Question** — What was asked
- **Key Findings** — The top 3-5 insights from the data
- **Summary Table** — A preview of the results (top rows)
- **File Location** — Where the `.sql` file was saved
- **Recommendations** — Any next steps or follow-up questions

Example format:
```
## Analysis: Approval Rates by Lender

**Business Question:** Which lenders have the highest approval rates?

**Key Findings:**
- Lender X has the highest approval rate at 85% (12,450 approvals out of 14,647 applications)
- The median approval rate across major lenders is 72%
- Smaller regional banks have 10-15% higher approval rates than national banks

**Results Preview:**
| Lender Name | Approvals | Total Apps | Approval Rate |
|---|---|---|---|
| Lender A | 12,450 | 14,647 | 85.0% |
| Lender B | 9,832 | 13,421 | 73.3% |
...

**File Location:** `/sql/06_lender_approval_rates.sql`

**Next Steps:** Consider analyzing denial reasons or approval rates by demographics for deeper insights.
```

## Important Notes

- Always filter by year or time period when relevant — queries on the full dataset can be large
- Use `action_taken` value 1 for approved/originated, 2 for approved but not accepted, 3 for denied
- Denial reasons are in separate columns and should be handled with CASE statements or pivot logic
- Geographic analysis should account for missing county data
- Be thoughtful with demographic analysis — disparities may be explained by legitimate factors like credit scores or debt-to-income ratios; always provide context

## Examples

**Example 1: Income vs. Approval Rate**
> User asks: "Show me how approval rates differ by income level"
>
> Use CASE to bucket `income` column into ranges (e.g., <$50k, $50-100k, etc.)
> Filter WHERE `activity_year = 2024` and `income IS NOT NULL`
> Group by income bucket and calculate approval rates using `action_taken = 1` (originated)
> Result shows whether higher-income applicants have better approval rates

**Example 2: Geographic Lending Gaps**
> User asks: "Which states have the biggest approval disparities by race?"
>
> Use `state_code` for geography and `derived_race` for applicant race
> Filter WHERE `activity_year = 2024` and both fields are NOT NULL
> Calculate approval rates for each state-race combination
> Use self-join or window functions to find approval rate differences
> Result identifies states with largest racial disparities in lending

**Example 3: Year-over-Year Trends**
> User asks: "How did denial rates change from 2023 to 2024?"
>
> Create separate CTEs for 2024 and 2023 using `activity_year` filter
> Calculate key metrics (approval rate, avg loan amount, application count) for each year
> Use ROUND() and subtraction to calculate year-over-year percentage changes
> Result shows which metrics improved/worsened and by how much
