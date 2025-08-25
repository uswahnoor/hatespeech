#!/usr/bin/env python
"""
Email configuration test script for Django
"""

import os
import sys
import django
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hate_speech_api.settings')

# Setup Django
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.test import TestCase
from decouple import config

def test_email_settings():
    """Test email configuration settings"""
    print("=== EMAIL CONFIGURATION TEST ===")
    
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print()

def test_smtp_connection():
    """Test direct SMTP connection"""
    print("=== SMTP CONNECTION TEST ===")
    
    try:
        # Test SMTP connection
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.set_debuglevel(1)  # Enable debug output
        
        if settings.EMAIL_USE_TLS:
            print("Starting TLS...")
            server.starttls()
        
        print("Logging in...")
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        
        print("✓ SMTP connection successful!")
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"✗ SMTP Authentication failed: {e}")
        print("Check if you're using an App Password for Gmail (not your regular password)")
        return False
    except smtplib.SMTPException as e:
        print(f"✗ SMTP error: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

def test_django_email():
    """Test Django's send_mail function"""
    print("=== DJANGO EMAIL TEST ===")
    
    test_email = input("Enter test email address (or press Enter to use configured email): ").strip()
    if not test_email:
        test_email = settings.EMAIL_HOST_USER
    
    try:
        result = send_mail(
            subject='Test Email from Django',
            message='This is a test email sent from your Django application to verify email functionality.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[test_email],
            fail_silently=False,
        )
        
        if result:
            print(f"✓ Email sent successfully to {test_email}")
            print("Check your inbox (including spam folder)")
            return True
        else:
            print("✗ Email sending failed (no exception but result was 0)")
            return False
            
    except Exception as e:
        print(f"✗ Django email error: {e}")
        return False

def test_gmail_app_password():
    """Check if using Gmail app password"""
    print("=== GMAIL APP PASSWORD CHECK ===")
    
    if 'gmail.com' in settings.EMAIL_HOST:
        print("You're using Gmail SMTP.")
        print("Make sure you're using an App Password, not your regular Gmail password:")
        print("1. Go to Google Account settings")
        print("2. Security → 2-Step Verification → App passwords")
        print("3. Generate an app password for 'Mail'")
        print("4. Use that 16-character password in your .env file")
        print()
        
        # Check password format
        if len(settings.EMAIL_HOST_PASSWORD) == 16 and settings.EMAIL_HOST_PASSWORD.isalnum():
            print("✓ Password format looks like a Gmail App Password")
        else:
            print("✗ Password doesn't look like a Gmail App Password (should be 16 alphanumeric characters)")

def diagnose_email_issues():
    """Run comprehensive email diagnostics"""
    print("Django Email Diagnostics")
    print("=" * 50)
    
    # Test settings
    test_email_settings()
    
    # Gmail-specific checks
    test_gmail_app_password()
    
    # Test SMTP connection
    smtp_ok = test_smtp_connection()
    
    if smtp_ok:
        # Test Django email
        test_django_email()
    else:
        print("Skipping Django email test due to SMTP connection failure")
    
    print("\n=== RECOMMENDATIONS ===")
    if not smtp_ok:
        print("1. Check your Gmail App Password")
        print("2. Ensure 2-Step Verification is enabled on your Google account")
        print("3. Verify EMAIL_HOST_PASSWORD in .env file")
    else:
        print("SMTP connection is working. If emails aren't received:")
        print("1. Check spam/junk folder")
        print("2. Verify recipient email address")
        print("3. Check Gmail's 'Sent' folder")

if __name__ == '__main__':
    diagnose_email_issues()