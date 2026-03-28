-- Lender Analysis: Approval vs. denial rates, market share
-- Business Question: Which lenders have the best/worst approval rates?

SELECT
    lei AS lender_id,
    COUNT(*) AS num_applications,
    SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) AS num_approved,
    SUM(CASE WHEN action_taken IN (3, 4, 5) THEN 1 ELSE 0 END) AS num_denied,
    ROUND(100.0 * SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_approved,
    ROUND(100.0 * SUM(CASE WHEN action_taken IN (3, 4, 5) THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_denied,
    ROUND(AVG(loan_amount), 0) AS avg_loan_amount
FROM hmda_2024
WHERE lei IS NOT NULL
GROUP BY lei
HAVING COUNT(*) >= 100
ORDER BY num_applications DESC
LIMIT 50
