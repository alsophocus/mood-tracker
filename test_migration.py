#!/usr/bin/env python3
"""
Simple migration test script for Railway deployment
Tests basic migration operation and reports results
"""

import sys
import os
sys.path.append('.')

from admin_services import AdminService
from app import create_app

def test_basic_migration():
    """Test the basic migration operation"""
    try:
        app = create_app()
        with app.app_context():
            admin_service = AdminService()
            result = admin_service.run_basic_migration()
            
            print("=" * 50)
            print("MIGRATION TEST RESULT")
            print("=" * 50)
            print(f"Result: {result}")
            
            if result.get('success'):
                print("✅ MIGRATION SUCCESSFUL")
                return True
            else:
                print("❌ MIGRATION FAILED")
                print(f"Error: {result.get('error', 'Unknown error')}")
                return False
                
    except Exception as e:
        print("=" * 50)
        print("MIGRATION TEST EXCEPTION")
        print("=" * 50)
        print(f"Exception: {str(e)}")
        print(f"Type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_basic_migration()
    sys.exit(0 if success else 1)
