#!/usr/bin/env python
"""
Simple email test using Django's email functionality
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

from django.core.mail import EmailMessage
from django.conf import settings

def send_test_email():
    """Send a test email using Django EmailMessage"""
    
    test_email = input("Enter test email address: ").strip()
    if not test_email:
        test_email = settings.EMAIL_HOST_USER
    
    try:
        # Use EmailMessage instead of send_mail for better control
        email = EmailMessage(
            subject='Test Email from Django Application',
            body='This is a test email to verify email functionality is working correctly.\n\nIf you receive this, your email configuration is working!',
            from_email=settings.EMAIL_HOST_USER,
            to=[test_email],
        )
        
        result = email.send(fail_silently=False)
        
        if result:
            print(f"✓ Email sent successfully to {test_email}")
            print("Please check your inbox (including spam folder)")
        else:
            print("✗ Email sending failed")
            
    except Exception as e:
        print(f"✗ Error sending email: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == '__main__':
    print("Django Email Test")
    print("=" * 30)
    send_test_email()
