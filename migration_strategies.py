"""
SOLID-compliant migration strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from database import Database
import psycopg


class MigrationStrategyInterface(ABC):
    """Interface Segregation Principle - specific migration strategy interface"""
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the migration strategy"""
        pass


class AutocommitMigrationStrategy(MigrationStrategyInterface):
    """Single Responsibility - handles autocommit DDL operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def execute(self) -> Dict[str, Any]:
        try:
            conn = psycopg.connect(self.db.url, autocommit=True)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    category VARCHAR(30) NOT NULL,
                    color VARCHAR(7) DEFAULT '#6750A4'
                )
            """)
            
            cursor.execute("""
                INSERT INTO public.tags (name, category, color)
                VALUES ('work', 'work', '#FF6B6B')
                ON CONFLICT (name) DO NOTHING
            """)
            
            cursor.execute('SELECT COUNT(*) FROM public.tags')
            tag_count = cursor.fetchone()[0]
            conn.close()
            
            return {
                'success': True,
                'message': f'✅ Migration successful with autocommit! Created tags table with {tag_count} tags.',
                'tag_count': tag_count,
                'method': 'autocommit'
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'autocommit'}


class TransactionMigrationStrategy(MigrationStrategyInterface):
    """Single Responsibility - handles explicit transaction DDL operations"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def execute(self) -> Dict[str, Any]:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('BEGIN')
                
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = 'tags'
                    )
                """)
                table_exists = cursor.fetchone()[0]
                
                if not table_exists:
                    cursor.execute("""
                        CREATE TABLE public.tags (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(50) UNIQUE NOT NULL,
                            category VARCHAR(30) NOT NULL,
                            color VARCHAR(7) DEFAULT '#6750A4'
                        )
                    """)
                
                cursor.execute("""
                    INSERT INTO public.tags (name, category, color)
                    SELECT 'work', 'work', '#FF6B6B'
                    WHERE NOT EXISTS (SELECT 1 FROM public.tags WHERE name = 'work')
                """)
                
                cursor.execute('COMMIT')
                cursor.execute('SELECT COUNT(*) FROM public.tags')
                tag_count = cursor.fetchone()[0]
                
                return {
                    'success': True,
                    'message': f'✅ Migration successful with explicit transaction! Tags table has {tag_count} tags.',
                    'tag_count': tag_count,
                    'method': 'explicit_transaction',
                    'table_existed': table_exists
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'explicit_transaction'}


class ReadOnlyTestStrategy(MigrationStrategyInterface):
    """Single Responsibility - tests read-only operations when DDL fails"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def execute(self) -> Dict[str, Any]:
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM moods LIMIT 1')
                mood_count = cursor.fetchone()[0]
                
                return {
                    'success': False,
                    'error': 'DDL operations not supported, but DML works',
                    'message': f'❌ Cannot create tables, but can read data. Found {mood_count} moods.',
                    'mood_count': mood_count,
                    'method': 'read_only_test'
                }
        except Exception as e:
            return {'success': False, 'error': str(e), 'method': 'read_only_test'}


class MigrationExecutor:
    """Open/Closed Principle - can add new strategies without modification"""
    
    def __init__(self, strategies: list[MigrationStrategyInterface]):
        self.strategies = strategies
    
    def execute_with_fallback(self) -> Dict[str, Any]:
        """Dependency Inversion - depends on abstractions, not concretions"""
        errors = {}
        
        for strategy in self.strategies:
            result = strategy.execute()
            if result.get('success'):
                return result
            errors[result.get('method', 'unknown')] = result.get('error')
        
        return {
            'success': False,
            'error': 'All migration strategies failed',
            'message': '❌ Complete migration failure',
            'method': 'all_failed',
            'errors': errors
        }
