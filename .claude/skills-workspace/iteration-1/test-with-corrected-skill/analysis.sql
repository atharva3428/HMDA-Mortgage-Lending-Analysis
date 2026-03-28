-- Query: Approval Rates by Lender (LEI) - Top 10 by Application Volume
-- Purpose: Compare lending approval patterns across major lenders in 2024
-- Metric: Approval rates for originated loans (action_taken = 1), sorted by application volume

WITH lender_outcomes AS (
  -- Count applications by lender and outcome
  SELECT
    lei,
    action_taken,
    COUNT(*) as num_applications
  FROM hmda_2024
  WHERE activity_year = 2024
    AND lei IS NOT NULL
  GROUP BY lei, action_taken
),

lender_summary AS (
  -- Calculate approval metrics for each lender
  SELECT
    lei,
    SUM(CASE WHEN action_taken = 1 THEN num_applications ELSE 0 END) as num_originated,
    SUM(CASE WHEN action_taken = 3 THEN num_applications ELSE 0 END) as num_denied,
    SUM(num_applications) as total_applications,
    ROUND(100.0 * SUM(CASE WHEN action_taken = 1 THEN num_applications ELSE 0 END) / SUM(num_applications), 2) as pct_approval_rate
  FROM lender_outcomes
  GROUP BY lei
)

SELECT
  lei,
  total_applications,
  num_originated,
  num_denied,
  pct_approval_rate
FROM lender_summary
WHERE total_applications > 0
ORDER BY total_applications DESC
LIMIT 10;
