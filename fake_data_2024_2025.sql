-- Generate fake mood data for 2024-2025
-- This script creates ~3,800 mood entries across 2 years

-- First, get the user ID (assuming first user)
DO $$
DECLARE
    target_user_id INTEGER;
    current_date DATE;
    end_date DATE;
    entries_per_day INTEGER;
    i INTEGER;
    random_hour INTEGER;
    random_minute INTEGER;
    random_second INTEGER;
    mood_timestamp TIMESTAMP;
    mood_options TEXT[] := ARRAY['very bad', 'bad', 'slightly bad', 'neutral', 'slightly well', 'well', 'very well'];
    note_options TEXT[] := ARRAY['', '', '', 'Good day at work', 'Feeling stressed', 'Great workout today', 'Had coffee with friends', 'Busy day', 'Relaxing evening', 'Productive morning', 'Feeling grateful', 'Long day', 'Nice weather', 'Family time', 'Weekend vibes', 'Early morning', 'Late night'];
    selected_mood TEXT;
    selected_note TEXT;
    total_entries INTEGER := 0;
BEGIN
    -- Get first user ID
    SELECT id INTO target_user_id FROM users LIMIT 1;
    
    IF target_user_id IS NULL THEN
        RAISE EXCEPTION 'No users found in database';
    END IF;
    
    RAISE NOTICE 'Using user ID: %', target_user_id;
    
    -- Set date range
    current_date := '2024-01-01'::DATE;
    end_date := '2025-12-31'::DATE;
    
    RAISE NOTICE 'Generating fake data from % to %', current_date, end_date;
    
    -- Loop through each day
    WHILE current_date <= end_date LOOP
        -- Random entries per day (3-6)
        entries_per_day := 3 + (random() * 4)::INTEGER;
        
        -- Generate entries for this day
        FOR i IN 1..entries_per_day LOOP
            -- Random time during active hours (6 AM to 11 PM)
            random_hour := 6 + (random() * 18)::INTEGER;
            random_minute := (random() * 60)::INTEGER;
            random_second := (random() * 60)::INTEGER;
            
            mood_timestamp := current_date + (random_hour || ' hours ' || random_minute || ' minutes ' || random_second || ' seconds')::INTERVAL;
            
            -- Random mood and note
            selected_mood := mood_options[1 + (random() * array_length(mood_options, 1))::INTEGER];
            selected_note := note_options[1 + (random() * array_length(note_options, 1))::INTEGER];
            
            -- Insert mood entry
            INSERT INTO moods (user_id, date, mood, notes, timestamp)
            VALUES (target_user_id, current_date, selected_mood, selected_note, mood_timestamp);
            
            total_entries := total_entries + 1;
        END LOOP;
        
        -- Progress indicator (first day of each month)
        IF EXTRACT(DAY FROM current_date) = 1 THEN
            RAISE NOTICE 'Processing %', TO_CHAR(current_date, 'Month YYYY');
        END IF;
        
        -- Next day
        current_date := current_date + INTERVAL '1 day';
    END LOOP;
    
    RAISE NOTICE 'Successfully inserted % mood entries', total_entries;
    
    -- Show statistics
    RAISE NOTICE 'Database statistics:';
    RAISE NOTICE 'Total entries for user %: %', target_user_id, (SELECT COUNT(*) FROM moods WHERE user_id = target_user_id);
    RAISE NOTICE 'Date range: % to %', (SELECT MIN(date) FROM moods WHERE user_id = target_user_id), (SELECT MAX(date) FROM moods WHERE user_id = target_user_id);
    
END $$;
