# 🌈 Mood Tracker

A simple, minimalistic web application to track your daily mood with analytics and insights.

## ✨ Features

### Core Functionality
- **5 Mood Levels**: Super Sad, Sad, Neutral, Good, Super Good
- **Daily Logging**: One mood entry per day with optional notes
- **SQLite Database**: Lightweight, local data storage
- **PDF Export**: Download your mood history as a PDF report

### Analytics Dashboard
- **Current Streak**: Track consecutive good days (mood 4-5)
- **Best Streak**: Your longest streak of good days ever
- **Total Days**: Count of all tracked days
- **Monthly Trends**: Line chart showing average mood per month
- **Weekly Patterns**: See which days of the week you feel best/worst

### Enhanced Tracking
- **Notes Field**: Add context about your day (optional)
- **Visual Interface**: Color-coded mood buttons with emojis
- **Mood History**: Complete log of all entries with dates and notes

## 🚀 Quick Start

### Local Development
```bash
# Clone the repository
git clone https://github.com/alsophocus/mood-tracker.git
cd mood-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Visit `http://localhost:5000` in your browser.

### Using the App

1. **Log Your Mood**: Click one of the 5 mood buttons
2. **Add Notes** (Optional): Describe what influenced your mood
3. **View Analytics**: See your streaks and patterns in the dashboard
4. **Export Data**: Click "Export PDF" to download your mood history
5. **Track Trends**: Monitor your monthly mood trends in the chart

## 📊 Understanding Your Data

### Mood Scale
- **Super Sad** (1): 😢 Very low mood
- **Sad** (2): 😞 Below average mood  
- **Neutral** (3): 😐 Average/okay mood
- **Good** (4): 😊 Above average mood
- **Super Good** (5): 😄 Excellent mood

### Streaks
- **Current Streak**: Consecutive days with "Good" or "Super Good" mood
- **Best Streak**: Your longest streak of good days
- Streaks reset when you log "Neutral", "Sad", or "Super Sad"

### Weekly Patterns
- Shows average mood for each day of the week
- Helps identify patterns (e.g., "Mondays are tough", "Weekends are better")
- Scale: 1.0 (Super Sad) to 5.0 (Super Good)

## 🛠 Technical Details

### Built With
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **PDF Generation**: ReportLab

### File Structure
```
mood-tracker/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── render.yaml        # Render deployment config
├── templates/
│   └── index.html     # Main web interface
└── mood.db           # SQLite database (created automatically)
```

### Database Schema
```sql
CREATE TABLE moods (
    id INTEGER PRIMARY KEY,
    date TEXT,           -- YYYY-MM-DD format
    mood TEXT,           -- Mood level name
    notes TEXT           -- Optional user notes
);
```

## 🌐 Deployment

### Deploy to Render
1. Fork this repository
2. Go to [Render](https://render.com) and sign up/login
3. **Create PostgreSQL Database:**
   - Click "New" → "PostgreSQL"
   - Name: `mood-tracker-db`
   - Leave other settings as default
   - Click "Create Database"
   - Copy the "External Database URL"

4. **Create Web Service:**
   - Click "New" → "Web Service"
   - Connect your GitHub repository
   - Name: `mood-tracker`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   
5. **Add Environment Variable:**
   - In your web service settings
   - Add environment variable: `DATABASE_URL` = [paste your database URL]
   - Deploy!

### Local Development with PostgreSQL
```bash
# Set environment variable for local PostgreSQL (optional)
export DATABASE_URL="postgresql://username:password@localhost/mood_tracker"

# Or use SQLite (default for local development)
python app.py  # Will automatically use SQLite if no DATABASE_URL
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string (required for production)
- `PORT`: Automatically set by Render (default: 5000)

## 📈 Privacy & Data

- **Local Storage**: All data stored in local SQLite database
- **No External APIs**: No data sent to third parties
- **Export Control**: You own your data - export anytime as PDF
- **Simple Backup**: Copy `mood.db` file to backup your data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎯 Future Enhancements

- Mobile app version
- Data import/export (CSV)
- Mood triggers and tags
- Reminder notifications
- Advanced analytics and predictions
- Multi-user support

---

**Start tracking your mood today and discover patterns in your emotional well-being!** 🌟
