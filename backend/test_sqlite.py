#!/usr/bin/env python
"""
Simple test script to verify SQLite database is working
"""

import os
import sys
import django

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hate_speech_api.settings')

# Setup Django
django.setup()

from django.db import connection
from django.contrib.auth.models import User
from users.models import User as CustomUser
from detection.models import DetectionResult

def test_database():
    """Test database connectivity and basic operations"""
    print("Testing SQLite database connection...")
    
    # Test database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()
            print(f"✓ SQLite version: {version[0]}")
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
    
    # Test tables exist
    try:
        tables = connection.introspection.table_names()
        print(f"✓ Found {len(tables)} tables in database")
        
        # Check for key tables
        expected_tables = ['users_user', 'detection_detectionresult']
        missing_tables = []
        for table in expected_tables:
            if table not in tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"✗ Missing tables: {missing_tables}")
        else:
            print("✓ All expected tables found")
            
    except Exception as e:
        print(f"✗ Could not list tables: {e}")
        return False
    
    # Test model queries
    try:
        user_count = CustomUser.objects.count()
        detection_count = DetectionResult.objects.count()
        print(f"✓ Database queries working - Users: {user_count}, Detections: {detection_count}")
    except Exception as e:
        print(f"✗ Model queries failed: {e}")
        return False
    
    print("✓ SQLite database is working correctly!")
    return True

if __name__ == '__main__':
    test_database()
