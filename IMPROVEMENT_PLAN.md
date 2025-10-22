# Mood Tracker Improvement Plan
**Date**: October 22, 2025  
**Status**: In Progress

## Overview
Implementing Material Design 3 improvements to enhance user experience and data visualization.

---

## Phase 1: Weekly Patterns with Week Navigation ✅ COMPLETE
**Priority**: HIGH  
**Complexity**: MEDIUM  
**Risk**: MEDIUM  
**Status**: ✅ DEPLOYED AND TESTED

### Current State
- Year/Month/Week dropdowns (confusing)
- Week-of-month concept is unclear
- No easy way to navigate between weeks

### Target State
- Simple Previous/Next week buttons
- Date range display (e.g., "Oct 16 - Oct 22, 2025")
- Line graph showing daily averages (Mon-Sun)
- Colored dots based on mood values
- Variable dot sizes (more entries = bigger dots)
- Gaps in line where no data exists
- Enhanced tooltips with average, mood name, entry count

### Implementation Steps
1. ✅ Update backend route to accept `start_date` parameter
2. ✅ Modify `get_weekly_patterns_for_period()` to return null for no-data days
3. ✅ Add counts array for entry tracking
4. ⏳ Replace HTML dropdowns with navigation buttons
5. ⏳ Add JavaScript for week navigation
6. ⏳ Update chart rendering with colored dots
7. ⏳ Test thoroughly before moving to next phase

### Files to Modify
- `routes.py` - Add start_date support
- `analytics.py` - Update get_weekly_patterns_for_period
- `templates/index.html` - Replace controls, add JS functions

### Testing Checklist
- [x] Week navigation works (Previous/Next)
- [x] Date range displays correctly
- [x] Colored dots show proper mood colors
- [x] Dot sizes vary based on entry count
- [x] Line breaks where no data exists
- [x] Tooltips show all information
- [x] No JavaScript errors in console
- [ ] Works on mobile (not tested yet)

**Completion Date**: October 22, 2025  
**Issues Resolved**: Chart service vs direct chart access, retry logic for initialization

---

## Phase 2: Recent Moods Carousel
**Priority**: MEDIUM  
**Complexity**: HIGH  
**Risk**: HIGH

### Current State
- Static list of last 5 moods
- Takes vertical space
- Limited information display

### Target State
- Auto-scrolling horizontal carousel
- Shows last 15 mood entries as cards
- Material Design 3 elevated cards
- Pause/Play and manual navigation
- Colored cards matching mood
- Compact info: emoji, mood, date/time, truncated notes
- Smooth animations

### Implementation Steps
1. Create carousel HTML structure
2. Add Material Design 3 card styling
3. Implement auto-scroll JavaScript
4. Add pause/play functionality
5. Add manual navigation (arrows)
6. Implement hover-to-pause
7. Load data via AJAX
8. Add smooth transitions
9. Make responsive for mobile

### Files to Modify
- `templates/index.html` - Replace Recent Moods section
- Add CSS for carousel and cards
- Add JavaScript for carousel logic
- Possibly `routes.py` - Ensure /recent_moods returns 15 entries

### Material Design 3 Specifications
- Card elevation: Level 1
- Corner radius: 12px (medium)
- Padding: 16px
- Gap between cards: 16px
- Transition: 300ms emphasized easing
- Colors: Surface container with mood-based accent

### Testing Checklist
- [ ] Carousel auto-scrolls smoothly
- [ ] Pause/play button works
- [ ] Manual navigation works
- [ ] Hover pauses auto-scroll
- [ ] Cards display all information
- [ ] Colors match mood values
- [ ] Responsive on mobile
- [ ] No layout shifts
- [ ] Smooth animations

---

## Phase 3: Quick Stats Cards ✅ COMPLETE
**Priority**: LOW  
**Complexity**: LOW  
**Risk**: LOW  
**Status**: ✅ DEPLOYED AND TESTED

### Current State
- No quick overview of current state

### Target State
Three Material Design 3 cards showing:
1. **Today's Mood**
   - Large emoji
   - Mood name
   - Time of last entry
   
2. **This Week Average**
   - Average value
   - Mood name
   - Number of entries
   
3. **Trend Indicator**
   - Arrow (↗️ up, ↘️ down, → stable)
   - Change value (+0.8, -0.3, etc.)
   - Comparison period

### Implementation Steps
1. Add HTML for 3-card grid
2. Style with Material Design 3
3. Create backend endpoint for stats
4. Load data via AJAX
5. Update on mood submission

### Files to Modify
- `templates/index.html` - Add stats cards section
- `routes.py` - Add /api/quick-stats endpoint
- `analytics.py` - Add quick stats calculation methods

### Testing Checklist
- [x] Cards display correctly
- [x] Data is accurate
- [x] Updates after mood submission
- [x] Responsive layout
- [x] Material Design 3 styling
- [x] FontAwesome icons for Today and Trend
- [x] Correct timezone (Chile UTC-3)

**Completion Date**: October 22, 2025  
**Issues Resolved**: MOOD_VALUES import, timezone conversion, icon consistency

---

## Phase 4: Weekly Trends Improvement
**Priority**: LOW  
**Complexity**: MEDIUM  
**Risk**: LOW

### Current State
- Shows weekly trends for a month
- Confusing week-of-month concept

### Target State
- Rename to "4-Week Comparison"
- Show last 4 weeks as separate lines
- Each week labeled with date range
- Clear trend visualization

### Implementation Steps
1. Update backend to return last 4 weeks
2. Modify chart to show multiple lines
3. Update labels with date ranges
4. Add legend

### Files to Modify
- `analytics.py` - Modify weekly trends logic
- `templates/index.html` - Update chart configuration

---

## Phase 5: Monthly Trends Enhancement
**Priority**: LOW  
**Complexity**: LOW  
**Risk**: LOW

### Current State
- Shows monthly averages (good!)

### Target State
- Keep current functionality
- Add trend line overlay
- Show if improving/declining

### Implementation Steps
1. Calculate linear regression
2. Add trend line to chart
3. Add trend indicator

---

## Implementation Order
1. ✅ Weekly Patterns (CURRENT)
2. Recent Moods Carousel
3. Quick Stats Cards
4. Weekly Trends
5. Monthly Trends

## Rollback Plan
- Tag each working version: `v0.4.x-working`
- Test thoroughly before moving to next phase
- Keep git history clean
- Document any issues in this file

## Notes
- Always follow Material Design 3 specifications
- Test on both desktop and mobile
- Ensure accessibility (ARIA labels, keyboard navigation)
- Keep performance in mind (smooth animations)
- Maintain existing functionality during transitions
