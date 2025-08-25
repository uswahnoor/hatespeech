#!/usr/bin/env python
"""
Test the actual user registration email flow
"""

import os
import sys
import django
import requests
import json

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hate_speech_api.settings')

# Setup Django
django.setup()

from django.conf import settings
from users.models import User
from django.core.signing import Signer

def test_registration_email_flow():
    """Test the complete registration and email verification flow"""
    
    print("Testing User Registration Email Flow")
    print("=" * 50)
    
    # Test email address
    test_email = input("Enter test email address for registration: ").strip()
    if not test_email:
        print("No email provided, exiting...")
        return
    
    # Check if user already exists
    existing_user = User.objects.filter(email=test_email).first()
    if existing_user:
        print(f"User with email {test_email} already exists.")
        delete_user = input("Delete existing user and continue? (y/n): ").strip().lower()
        if delete_user == 'y':
            existing_user.delete()
            print("Existing user deleted.")
        else:
            print("Exiting...")
            return
    
    # Test data
    registration_data = {
        "username": f"testuser_{test_email.split('@')[0]}",
        "email": test_email,
        "password": "TestPassword123!",
        "password2": "TestPassword123!"
    }
    
    print(f"Attempting to register user: {registration_data['username']}")
    print(f"Email: {registration_data['email']}")
    
    # Start Django development server programmatically would be complex,
    # so let's test the email sending part directly
    from users.views import signup
    from rest_framework.test import APIRequestFactory
    from rest_framework.request import Request
    
    factory = APIRequestFactory()
    request = factory.post('/api/users/signup/', registration_data, format='json')
    
    try:
        response = signup(request)
        print(f"Registration response status: {response.status_code}")
        print(f"Registration response data: {response.data}")
        
        if response.status_code == 201:
            print("✓ User registration successful!")
            print("✓ Email should have been sent!")
            
            # Get the created user
            user = User.objects.get(email=test_email)
            print(f"User created: {user.username} ({user.email})")
            print(f"Email verified: {user.email_verified}")
            
            # Generate verification token manually to show the link
            signer = Signer()
            token = signer.sign(user.email)
            verify_link = f"{settings.FRONTEND_URL.rstrip('/')}/auth/verify-email/{token}"
            print(f"Verification link: {verify_link}")
            
        else:
            print("✗ User registration failed!")
            
    except Exception as e:
        print(f"✗ Error during registration: {e}")

def test_email_verification():
    """Test email verification with a token"""
    
    print("\nTesting Email Verification")
    print("=" * 30)
    
    test_email = input("Enter email to verify: ").strip()
    if not test_email:
        print("No email provided, exiting...")
        return
    
    try:
        user = User.objects.get(email=test_email)
        
        if user.email_verified:
            print(f"✓ User {test_email} is already verified!")
        else:
            # Verify the user
            user.email_verified = True
            user.save()
            print(f"✓ User {test_email} has been manually verified!")
            
    except User.DoesNotExist:
        print(f"✗ User with email {test_email} not found!")

if __name__ == '__main__':
    try:
        test_registration_email_flow()
        test_email_verification()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
