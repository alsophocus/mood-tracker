-- Fake data for October 2025 - PostgreSQL compatible
-- Insert test user if not exists
INSERT INTO users (id, email, name, provider) 
VALUES (1, 'test@example.com', 'Test User', 'local') 
ON CONFLICT (email) DO NOTHING;

-- Insert fake mood data for October 2025
INSERT INTO moods (user_id, date, mood, notes, timestamp) VALUES
(1, '2025-10-01', 'neutral', 'Feeling grateful', '2025-10-01 09:15:00'),
(1, '2025-10-01', 'slightly well', 'Had a productive morning', '2025-10-01 14:30:00'),
(1, '2025-10-01', 'well', 'Good day overall', '2025-10-01 19:45:00'),

(1, '2025-10-02', 'slightly bad', 'Feeling a bit tired', '2025-10-02 08:20:00'),
(1, '2025-10-02', 'neutral', 'Relaxing weekend', '2025-10-02 16:10:00'),

(1, '2025-10-03', 'well', 'Excited about new project', '2025-10-03 10:30:00'),
(1, '2025-10-03', 'very well', 'Feeling great today!', '2025-10-03 15:45:00'),
(1, '2025-10-03', 'well', 'Beautiful weather today', '2025-10-03 20:15:00'),

(1, '2025-10-04', 'neutral', 'Need more sleep', '2025-10-04 07:45:00'),
(1, '2025-10-04', 'slightly well', 'Good day overall', '2025-10-04 12:30:00'),

(1, '2025-10-05', 'bad', 'Stressed about work', '2025-10-05 09:00:00'),
(1, '2025-10-05', 'slightly bad', 'Feeling a bit tired', '2025-10-05 17:20:00'),
(1, '2025-10-05', 'neutral', '', '2025-10-05 21:10:00'),

(1, '2025-10-06', 'slightly well', 'Had a productive morning', '2025-10-06 08:15:00'),
(1, '2025-10-06', 'well', 'Feeling grateful', '2025-10-06 13:45:00'),

(1, '2025-10-07', 'very well', 'Feeling great today!', '2025-10-07 11:20:00'),
(1, '2025-10-07', 'well', 'Excited about new project', '2025-10-07 16:30:00'),
(1, '2025-10-07', 'slightly well', 'Relaxing weekend', '2025-10-07 19:50:00'),

(1, '2025-10-08', 'neutral', 'Good day overall', '2025-10-08 09:40:00'),
(1, '2025-10-08', 'slightly well', 'Beautiful weather today', '2025-10-08 14:15:00'),

(1, '2025-10-09', 'well', 'Had a productive morning', '2025-10-09 10:10:00'),
(1, '2025-10-09', 'very well', 'Feeling grateful', '2025-10-09 18:25:00'),

(1, '2025-10-10', 'slightly bad', 'Need more sleep', '2025-10-10 07:30:00'),
(1, '2025-10-10', 'neutral', 'Stressed about work', '2025-10-10 15:40:00'),
(1, '2025-10-10', 'slightly well', '', '2025-10-10 20:55:00'),

-- Week 2
(1, '2025-10-11', 'well', 'Feeling great today!', '2025-10-11 08:45:00'),
(1, '2025-10-11', 'very well', 'Excited about new project', '2025-10-11 12:20:00'),

(1, '2025-10-12', 'neutral', 'Relaxing weekend', '2025-10-12 09:30:00'),
(1, '2025-10-12', 'slightly well', 'Good day overall', '2025-10-12 17:15:00'),

(1, '2025-10-13', 'bad', 'Feeling a bit tired', '2025-10-13 08:00:00'),
(1, '2025-10-13', 'slightly bad', 'Need more sleep', '2025-10-13 19:30:00'),

(1, '2025-10-14', 'neutral', 'Had a productive morning', '2025-10-14 10:45:00'),
(1, '2025-10-14', 'well', 'Beautiful weather today', '2025-10-14 16:20:00'),
(1, '2025-10-14', 'slightly well', 'Feeling grateful', '2025-10-14 21:00:00'),

(1, '2025-10-15', 'very well', 'Feeling great today!', '2025-10-15 09:15:00'),
(1, '2025-10-15', 'well', 'Excited about new project', '2025-10-15 14:40:00'),

(1, '2025-10-16', 'slightly well', 'Good day overall', '2025-10-16 11:30:00'),
(1, '2025-10-16', 'neutral', 'Relaxing weekend', '2025-10-16 18:45:00'),

(1, '2025-10-17', 'well', 'Had a productive morning', '2025-10-17 08:20:00'),
(1, '2025-10-17', 'very well', 'Beautiful weather today', '2025-10-17 13:10:00'),
(1, '2025-10-17', 'well', 'Feeling grateful', '2025-10-17 19:35:00'),

-- Week 3
(1, '2025-10-18', 'neutral', 'Need more sleep', '2025-10-18 07:50:00'),
(1, '2025-10-18', 'slightly well', 'Stressed about work', '2025-10-18 15:25:00'),

(1, '2025-10-19', 'well', 'Feeling great today!', '2025-10-19 09:40:00'),
(1, '2025-10-19', 'very well', 'Excited about new project', '2025-10-19 17:15:00'),

(1, '2025-10-20', 'slightly bad', 'Feeling a bit tired', '2025-10-20 08:30:00'),
(1, '2025-10-20', 'neutral', 'Good day overall', '2025-10-20 12:45:00'),
(1, '2025-10-20', 'slightly well', 'Relaxing weekend', '2025-10-20 20:20:00'),

(1, '2025-10-21', 'well', 'Had a productive morning', '2025-10-21 10:15:00'),
(1, '2025-10-21', 'very well', 'Beautiful weather today', '2025-10-21 16:50:00'),

(1, '2025-10-22', 'neutral', 'Feeling grateful', '2025-10-22 09:25:00'),
(1, '2025-10-22', 'slightly well', '', '2025-10-22 14:30:00'),

(1, '2025-10-23', 'bad', 'Need more sleep', '2025-10-23 07:40:00'),
(1, '2025-10-23', 'slightly bad', 'Stressed about work', '2025-10-23 18:55:00'),

(1, '2025-10-24', 'neutral', 'Feeling great today!', '2025-10-24 11:10:00'),
(1, '2025-10-24', 'well', 'Excited about new project', '2025-10-24 19:25:00'),

-- Week 4
(1, '2025-10-25', 'slightly well', 'Good day overall', '2025-10-25 08:35:00'),
(1, '2025-10-25', 'very well', 'Relaxing weekend', '2025-10-25 15:20:00'),

(1, '2025-10-26', 'well', 'Had a productive morning', '2025-10-26 09:50:00'),
(1, '2025-10-26', 'neutral', 'Beautiful weather today', '2025-10-26 17:40:00'),

(1, '2025-10-27', 'slightly well', 'Feeling grateful', '2025-10-27 10:25:00'),
(1, '2025-10-27', 'well', 'Feeling great today!', '2025-10-27 16:15:00'),
(1, '2025-10-27', 'very well', 'Excited about new project', '2025-10-27 21:30:00'),

(1, '2025-10-28', 'neutral', 'Need more sleep', '2025-10-28 08:10:00'),
(1, '2025-10-28', 'slightly well', 'Good day overall', '2025-10-28 13:45:00'),

(1, '2025-10-29', 'well', 'Relaxing weekend', '2025-10-29 11:55:00'),
(1, '2025-10-29', 'very well', 'Had a productive morning', '2025-10-29 18:20:00'),

(1, '2025-10-30', 'slightly bad', 'Feeling a bit tired', '2025-10-30 09:05:00'),
(1, '2025-10-30', 'neutral', 'Stressed about work', '2025-10-30 14:50:00'),

(1, '2025-10-31', 'well', 'Beautiful weather today', '2025-10-31 10:40:00'),
(1, '2025-10-31', 'very well', 'Feeling grateful', '2025-10-31 16:25:00'),
(1, '2025-10-31', 'well', 'Feeling great today!', '2025-10-31 20:15:00');
