-- Denial Reasons: What are the most common reasons loans are denied?
-- Business Question: Distribution of denial reasons across all denied applications

SELECT
    denial_reason_1 AS denial_reason_code,
    CASE denial_reason_1
        WHEN 1 THEN 'Debt-to-Income Ratio'
        WHEN 2 THEN 'Employment History'
        WHEN 3 THEN 'Credit History'
        WHEN 4 THEN 'Collateral'
        WHEN 5 THEN 'Insufficient Cash'
        WHEN 6 THEN 'Unverifiable Information'
        WHEN 7 THEN 'Credit App Incomplete'
        WHEN 8 THEN 'Mortgage Insurance Denied'
        WHEN 9 THEN 'Other'
        ELSE 'Not Specified'
    END AS denial_reason,
    COUNT(*) AS num_denials,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_all_denials,
    derived_race AS applicant_race
FROM hmda_2024
WHERE action_taken IN (3, 4, 5)
  AND denial_reason_1 IS NOT NULL
GROUP BY denial_reason_1, derived_race
ORDER BY num_denials DESC
LIMIT 100
