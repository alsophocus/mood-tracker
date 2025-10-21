"""
Improved migration method to replace the failing migrate_basic
"""

def improved_migrate_basic(self) -> dict:
    """
    Improved basic migration that addresses the "0" error issue
    Uses multiple approaches to handle PostgreSQL DDL issues
    """
    try:
        # Approach 1: Try with autocommit mode
        try:
            import psycopg
            conn = psycopg.connect(self.db.url, autocommit=True)
            cursor = conn.cursor()
            
            # Create table with explicit schema and simpler syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.tags (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(50) UNIQUE NOT NULL,
                    category VARCHAR(30) NOT NULL,
                    color VARCHAR(7) DEFAULT '#6750A4'
                )
            """)
            
            # Insert test data
            cursor.execute("""
                INSERT INTO public.tags (name, category, color)
                VALUES ('work', 'work', '#FF6B6B')
                ON CONFLICT (name) DO NOTHING
            """)
            
            # Check results
            cursor.execute('SELECT COUNT(*) FROM public.tags')
            tag_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'success': True,
                'message': f'✅ Migration successful with autocommit! Created tags table with {tag_count} tags.',
                'tag_count': tag_count,
                'method': 'autocommit'
            }
            
        except Exception as autocommit_error:
            # Approach 2: Try with explicit transaction control
            try:
                with self.db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Start explicit transaction
                    cursor.execute('BEGIN')
                    
                    # Check if table exists first
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = 'tags'
                        )
                    """)
                    table_exists = cursor.fetchone()[0]
                    
                    if not table_exists:
                        # Create table with different syntax
                        cursor.execute("""
                            CREATE TABLE public.tags (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(50) UNIQUE NOT NULL,
                                category VARCHAR(30) NOT NULL,
                                color VARCHAR(7) DEFAULT '#6750A4'
                            )
                        """)
                    
                    # Insert test data
                    cursor.execute("""
                        INSERT INTO public.tags (name, category, color)
                        SELECT 'work', 'work', '#FF6B6B'
                        WHERE NOT EXISTS (SELECT 1 FROM public.tags WHERE name = 'work')
                    """)
                    
                    # Commit transaction
                    cursor.execute('COMMIT')
                    
                    # Check results
                    cursor.execute('SELECT COUNT(*) FROM public.tags')
                    tag_count = cursor.fetchone()[0]
                    
                    return {
                        'success': True,
                        'message': f'✅ Migration successful with explicit transaction! Tags table has {tag_count} tags.',
                        'tag_count': tag_count,
                        'method': 'explicit_transaction',
                        'table_existed': table_exists
                    }
                    
            except Exception as transaction_error:
                # Approach 3: Try minimal operation
                try:
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        
                        # Just try to select from existing tables to verify connection
                        cursor.execute('SELECT COUNT(*) FROM moods LIMIT 1')
                        mood_count = cursor.fetchone()[0]
                        
                        return {
                            'success': False,
                            'error': 'DDL operations not supported, but DML works',
                            'message': f'❌ Cannot create tables, but can read data. Found {mood_count} moods.',
                            'mood_count': mood_count,
                            'method': 'read_only_test',
                            'autocommit_error': str(autocommit_error),
                            'transaction_error': str(transaction_error)
                        }
                        
                except Exception as final_error:
                    return {
                        'success': False,
                        'error': f'All migration approaches failed: {str(final_error)}',
                        'message': '❌ Complete migration failure',
                        'method': 'all_failed',
                        'errors': {
                            'autocommit': str(autocommit_error),
                            'transaction': str(transaction_error),
                            'final': str(final_error)
                        }
                    }
                    
    except Exception as e:
        return {
            'success': False,
            'error': f'Migration initialization failed: {str(e)}',
            'message': f'❌ Migration setup error: {str(e)}'
        }
