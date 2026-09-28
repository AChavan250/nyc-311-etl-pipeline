-- =========================================================
-- NYC 311 ANALYTICS QUERIES
-- =========================================================


-- 1. TOTAL RECORDS
SELECT
    COUNT(*) AS total_requests
FROM nyc_311_requests;


-- 2. REQUESTS BY BOROUGH
SELECT
    borough,
    COUNT(*) AS total_requests
FROM nyc_311_requests
GROUP BY borough
ORDER BY total_requests DESC;


-- 3. MOST COMMON COMPLAINT TYPES
SELECT
    complaint_type,
    COUNT(*) AS total_requests
FROM nyc_311_requests
GROUP BY complaint_type
ORDER BY total_requests DESC
LIMIT 10;


-- 4. REQUESTS BY AGENCY
SELECT
    agency,
    COUNT(*) AS total_requests
FROM nyc_311_requests
GROUP BY agency
ORDER BY total_requests DESC;


-- 5. OPEN VS CLOSED REQUESTS
SELECT
    is_closed,
    COUNT(*) AS total_requests
FROM nyc_311_requests
GROUP BY is_closed
ORDER BY is_closed;


-- 6. AVERAGE RESOLUTION TIME BY AGENCY
SELECT
    agency,
    ROUND(
        AVG(resolution_hours)::numeric,
        2
    ) AS avg_resolution_hours,
    COUNT(*) AS resolved_requests
FROM nyc_311_requests
WHERE resolution_hours IS NOT NULL
GROUP BY agency
HAVING COUNT(*) >= 10
ORDER BY avg_resolution_hours DESC;


-- 7. DAILY REQUEST VOLUME
SELECT
    DATE(created_at) AS request_date,
    COUNT(*) AS total_requests
FROM nyc_311_requests
GROUP BY DATE(created_at)
ORDER BY request_date;


-- 8. DATA QUALITY CHECK
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT request_id) AS unique_request_ids,
    COUNT(*) FILTER (
        WHERE latitude IS NULL
           OR longitude IS NULL
    ) AS missing_coordinates
FROM nyc_311_requests;