-- Database reset script
-- Clear all mood data and reset sequences

-- Delete all mood entries
DELETE FROM moods;

-- Reset the auto-increment sequence
ALTER SEQUENCE moods_id_seq RESTART WITH 1;

-- Show remaining data
SELECT 'Moods count:' as info, COUNT(*) as count FROM moods
UNION ALL
SELECT 'Users count:' as info, COUNT(*) as count FROM users;
