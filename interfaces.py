"""
Data access interfaces following SOLID principles
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import date

class MoodReader(ABC):
    """Interface for reading mood data - Interface Segregation Principle"""
    
    @abstractmethod
    def get_user_moods(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get user moods with optional limit"""
        pass
    
    @abstractmethod
    def get_moods_by_date(self, user_id: int, target_date: date) -> List[Dict[str, Any]]:
        """Get moods for specific date"""
        pass

class MoodWriter(ABC):
    """Interface for writing mood data - Interface Segregation Principle"""
    
    @abstractmethod
    def save_mood(self, user_id: int, mood_date: date, mood: str, notes: str = '') -> Dict[str, Any]:
        """Save a new mood entry"""
        pass

class UserReader(ABC):
    """Interface for reading user data - Single Responsibility Principle"""
    
    @abstractmethod
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        pass

class UserWriter(ABC):
    """Interface for writing user data - Single Responsibility Principle"""
    
    @abstractmethod
    def create_or_update_user(self, email: str, name: str, provider: str) -> Dict[str, Any]:
        """Create or update user"""
        pass

class DatabaseConnection(ABC):
    """Interface for database connection management - Single Responsibility Principle"""
    
    @abstractmethod
    def get_connection(self):
        """Get database connection context manager"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize database schema"""
        pass
