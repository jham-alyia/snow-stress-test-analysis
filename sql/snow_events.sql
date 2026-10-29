-- snow_events.sql
-- Does  snow days correspond to more traffic incidents in Calgary?

 -- ============================================================
-- Query 1: one row per day, with snow category and incident count
-- Use this to see the raw daily data, or export it for charts.
-- ============================================================

--Snow categories:
--   heavy_snow   : 5+ cm of new snow that day
--   light_snow   : more than 0 and under 5 cm of new snow
--   snow_on_ground: no new snow, but 1+ cm still on the ground
--   clear        : no new snow and no snow on the ground
 
WITH daily_incidents AS (
    SELECT date, COUNT(*) AS incidents
    FROM incidents
    GROUP BY date
),
date_range AS (
    -- only keep days the incident data actually covers
    SELECT MIN(date) AS first_day, MAX(date) AS last_day FROM incidents
)
SELECT
    w.date,
    w.total_snow,
    w.snow_on_ground,
    w.mean_temp,
    CASE
        WHEN COALESCE(w.total_snow, 0) >= 5 THEN 'heavy_snow'
        WHEN COALESCE(w.total_snow, 0) > 0 THEN 'light_snow'
        WHEN COALESCE(w.snow_on_ground, 0) >= 1 THEN 'snow_on_ground'
        ELSE 'clear'
    END AS snow_category,
    COALESCE(d.incidents, 0) AS incidents      -- LEFT JOIN keeps zero-incident days
FROM weather w
LEFT JOIN daily_incidents d ON d.date = w.date
CROSS JOIN date_range r
WHERE w.date BETWEEN r.first_day AND r.last_day
ORDER BY w.date;
 
 
-- ============================================================
-- Query 2: the headline result.
-- Average incidents per day for each snow category, and how
-- that compares with clear days (ratio_vs_clear = 1.5 means 50% more).
-- ============================================================
WITH daily_incidents AS (
    SELECT date, COUNT(*) AS incidents
    FROM incidents
    GROUP BY date
),
date_range AS (
    SELECT MIN(date) AS first_day, MAX(date) AS last_day FROM incidents
),
days AS (
    SELECT
        CASE
            WHEN COALESCE(w.total_snow, 0) >= 5 THEN 'heavy_snow'
            WHEN COALESCE(w.total_snow, 0) > 0 THEN 'light_snow'
            WHEN COALESCE(w.snow_on_ground, 0) >= 1 THEN 'snow_on_ground'
            ELSE 'clear'
        END AS snow_category,
        COALESCE(d.incidents, 0) AS incidents
    FROM weather w
    LEFT JOIN daily_incidents d ON d.date = w.date
    CROSS JOIN date_range r
    WHERE w.date BETWEEN r.first_day AND r.last_day
),
summary AS (
    SELECT
        snow_category,
        COUNT(*)                     AS num_days,
        SUM(incidents)               AS total_incidents,
        ROUND(AVG(incidents * 1.0), 2) AS avg_incidents_per_day
    FROM days
    GROUP BY snow_category
)
SELECT
    s.snow_category,
    s.num_days,
    s.total_incidents,
    s.avg_incidents_per_day,
    ROUND(s.avg_incidents_per_day / c.avg_incidents_per_day, 2) AS ratio_vs_clear
FROM summary s
CROSS JOIN (SELECT avg_incidents_per_day FROM summary WHERE snow_category = 'clear') c
ORDER BY s.avg_incidents_per_day DESC;
 
 
-- ============================================================
-- Query 3: average incidents per day by quadrant, snow vs no snow.
-- Shows whether some parts of the city are hit harder by snow.
-- ============================================================
WITH date_range AS (
    SELECT MIN(date) AS first_day, MAX(date) AS last_day FROM incidents
),
day_type AS (
    SELECT
        w.date,
        CASE WHEN COALESCE(w.total_snow, 0) > 0 THEN 'snow_day' ELSE 'no_snow' END AS day_type
    FROM weather w
    CROSS JOIN date_range r
    WHERE w.date BETWEEN r.first_day AND r.last_day
),
day_counts AS (
    SELECT day_type, COUNT(*) AS num_days FROM day_type GROUP BY day_type
)
SELECT
    i.quadrant,
    t.day_type,
    COUNT(*) AS total_incidents,
    ROUND(COUNT(*) * 1.0 / dc.num_days, 2) AS avg_incidents_per_day
FROM incidents i
JOIN day_type t  ON t.date = i.date
JOIN day_counts dc ON dc.day_type = t.day_type
WHERE i.quadrant IS NOT NULL
GROUP BY i.quadrant, t.day_type, dc.num_days
ORDER BY i.quadrant, t.day_type;
 
 
-- ============================================================
-- Query 4: average incidents by hour of day, snow vs no snow.
-- Shows whether snow makes rush hour worse.
-- ============================================================
WITH date_range AS (
    SELECT MIN(date) AS first_day, MAX(date) AS last_day FROM incidents
),
day_type AS (
    SELECT
        w.date,
        CASE WHEN COALESCE(w.total_snow, 0) > 0 THEN 'snow_day' ELSE 'no_snow' END AS day_type
    FROM weather w
    CROSS JOIN date_range r
    WHERE w.date BETWEEN r.first_day AND r.last_day
),
day_counts AS (
    SELECT day_type, COUNT(*) AS num_days FROM day_type GROUP BY day_type
)
SELECT
    i.hour,
    t.day_type,
    ROUND(COUNT(*) * 1.0 / dc.num_days, 2) AS avg_incidents_per_day
FROM incidents i
JOIN day_type t  ON t.date = i.date
JOIN day_counts dc ON dc.day_type = t.day_type
GROUP BY i.hour, t.day_type, dc.num_days
ORDER BY i.hour, t.day_type;
 

 --duckdb data/processed/calgary_snow.duckdb -c ".read sql/snow_events.sql"