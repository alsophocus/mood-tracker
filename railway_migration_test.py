#!/usr/bin/env python3
"""
Railway-specific migration test that handles environment properly
"""

import os
import sys
import traceback

def test_migration_on_railway():
    """Test migration with proper Railway environment handling"""
    try:
        # Ensure we're using Railway's environment
        if not os.getenv('RAILWAY_ENVIRONMENT'):
            print("❌ Not running in Railway environment")
            return False
            
        # Import after environment check
        sys.path.append('.')
        from admin_services import AdminService
        from app import create_app
        
        print("🚀 Testing migration on Railway...")
        print(f"Environment: {os.getenv('RAILWAY_ENVIRONMENT')}")
        print(f"Service: {os.getenv('RAILWAY_SERVICE_NAME')}")
        
        app = create_app()
        with app.app_context():
            admin_service = AdminService()
            result = admin_service.run_basic_migration()
            
            print("=" * 60)
            print("RAILWAY MIGRATION TEST RESULT")
            print("=" * 60)
            
            if result.get('success'):
                print("✅ MIGRATION SUCCESSFUL ON RAILWAY")
                print(f"Details: {result}")
                return True
            else:
                print("❌ MIGRATION FAILED ON RAILWAY")
                print(f"Error: {result.get('error', 'Unknown error')}")
                print(f"Full result: {result}")
                return False
                
    except Exception as e:
        print("=" * 60)
        print("RAILWAY MIGRATION TEST EXCEPTION")
        print("=" * 60)
        print(f"Exception: {str(e)}")
        print(f"Type: {type(e).__name__}")
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_migration_on_railway()
    print(f"\n🎯 Final result: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
