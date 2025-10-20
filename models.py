"""
Domain models following SOLID principles
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from enum import Enum

class MoodType(Enum):
    """Mood types enum - Open/Closed Principle for easy extension"""
    VERY_BAD = "very bad"
    BAD = "bad"
    SLIGHTLY_BAD = "slightly bad"
    NEUTRAL = "neutral"
    SLIGHTLY_WELL = "slightly well"
    WELL = "well"
    VERY_WELL = "very well"
    
    @classmethod
    def get_value(cls, mood_str: str) -> int:
        """Get numeric value for mood - Single Responsibility"""
        mood_values = {
            cls.VERY_BAD.value: 1,
            cls.BAD.value: 2,
            cls.SLIGHTLY_BAD.value: 3,
            cls.NEUTRAL.value: 4,
            cls.SLIGHTLY_WELL.value: 5,
            cls.WELL.value: 6,
            cls.VERY_WELL.value: 7
        }
        return mood_values.get(mood_str, 4)

@dataclass
class MoodEntry:
    """Mood entry domain model - Single Responsibility Principle"""
    id: Optional[int]
    user_id: int
    date: date
    mood: MoodType
    notes: str
    timestamp: datetime
    
    @property
    def mood_value(self) -> int:
        """Get numeric mood value"""
        return MoodType.get_value(self.mood.value)
    
    @property
    def hour(self) -> int:
        """Get hour from timestamp"""
        return self.timestamp.hour
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'mood': self.mood.value,
            'mood_value': self.mood_value,
            'notes': self.notes,
            'timestamp': self.timestamp.isoformat(),
            'hour': self.hour
        }

@dataclass
class User:
    """User domain model - Single Responsibility Principle"""
    id: Optional[int]
    email: str
    name: str
    provider: str
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'provider': self.provider,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
