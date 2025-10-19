-- Simple approach: Insert fake data using generate_series
-- This creates approximately 3,800 mood entries for 2024-2025

WITH 
user_info AS (
    SELECT id as user_id FROM users LIMIT 1
),
date_series AS (
    SELECT generate_series('2024-01-01'::date, '2025-12-31'::date, '1 day'::interval)::date as mood_date
),
fake_moods AS (
    SELECT 
        u.user_id,
        d.mood_date,
        (ARRAY['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well'])[floor(random() * 7 + 1)] as mood,
        (ARRAY['', '', '', 'Good day at work', 'Feeling stressed', 'Great workout today', 'Had coffee with friends', 'Busy day', 'Relaxing evening', 'Productive morning', 'Feeling grateful', 'Long day', 'Nice weather', 'Family time', 'Weekend vibes'])[floor(random() * 15 + 1)] as notes,
        d.mood_date + (interval '6 hours') + (random() * interval '17 hours') as timestamp,
        generate_series(1, floor(random() * 4 + 3)::int) as entry_num
    FROM user_info u
    CROSS JOIN date_series d
)
INSERT INTO moods (user_id, date, mood, notes, timestamp)
SELECT 
    user_id,
    mood_date,
    mood,
    notes,
    timestamp + (entry_num * interval '1 hour') + (random() * interval '30 minutes')
FROM fake_moods;

-- Show results
SELECT 
    COUNT(*) as total_entries,
    MIN(date) as earliest_date,
    MAX(date) as latest_date,
    COUNT(DISTINCT date) as days_with_data
FROM moods;
