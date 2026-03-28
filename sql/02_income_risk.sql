-- Income Risk Analysis: Income patterns and loan approval by income bracket
-- Business Question: How does applicant income relate to approval outcomes?

SELECT
    CASE
        WHEN income < 50 THEN 'Under $50K'
        WHEN income < 100 THEN '$50K-$100K'
        WHEN income < 150 THEN '$100K-$150K'
        WHEN income < 200 THEN '$150K-$200K'
        ELSE 'Over $200K'
    END AS income_bracket,
    COUNT(*) AS num_applications,
    SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) AS num_approved,
    SUM(CASE WHEN action_taken IN (3, 4, 5) THEN 1 ELSE 0 END) AS num_denied,
    ROUND(100.0 * SUM(CASE WHEN action_taken = 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_approved,
    ROUND(AVG(loan_amount), 0) AS avg_loan_amount,
    ROUND(AVG(income), 0) AS avg_income
FROM hmda_2024
WHERE income IS NOT NULL AND income > 0 AND income < 9999
GROUP BY income_bracket
ORDER BY avg_income ASC
