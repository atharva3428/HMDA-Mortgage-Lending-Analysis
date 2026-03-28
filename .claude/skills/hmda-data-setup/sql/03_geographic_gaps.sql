-- Geographic Gaps: State-level lending approval disparities
-- Business Question: Which states have the highest/lowest approval rates?

SELECT
    state_code AS state,
    COUNT(*) AS num_applications,
    SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) AS num_approved,
    SUM(CASE WHEN action_taken IN (3, 4, 5) THEN 1 ELSE 0 END) AS num_denied,
    ROUND(100.0 * SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate,
    ROUND(AVG(loan_amount), 0) AS avg_loan_amount,
    ROUND(AVG(income), 0) AS avg_income
FROM hmda_2024
WHERE state_code IS NOT NULL AND state_code != ''
GROUP BY state_code
HAVING COUNT(*) >= 100
ORDER BY approval_rate DESC
