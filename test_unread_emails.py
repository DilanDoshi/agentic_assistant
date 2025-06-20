#!/usr/bin/env python3
"""
Test script to extract information from unread emails
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.google.gmail_client import GmailClient

def format_date(timestamp_ms):
    """Convert Gmail timestamp to readable date"""
    if timestamp_ms:
        return datetime.fromtimestamp(int(timestamp_ms) / 1000).strftime('%Y-%m-%d %H:%M:%S')
    return "Unknown"

def test_unread_emails():
    """Test extracting information from unread emails"""
    print("📧 Testing unread email extraction...")
    
    # Check if credentials file exists
    if not os.path.exists("credentials.json"):
        print("❌ Error: credentials.json not found!")
        print("Please download your OAuth 2.0 credentials from Google Cloud Console")
        print("and save them as 'credentials.json' in the project root directory.")
        return False
    
    try:
        # Create and authenticate client
        client = GmailClient()
        
        print("🔐 Authenticating with Gmail...")
        if not client.authenticate():
            print("❌ Gmail authentication failed!")
            return False
        
        print("✅ Gmail authentication successful!")
        
        # Get unread emails info
        print("\n📬 Fetching unread emails...")
        unread_emails = client.get_unread_emails_info(max_results=5)
        
        if not unread_emails:
            print("📭 No unread emails found!")
            return True
        
        print(f"📨 Found {len(unread_emails)} unread emails:")
        print("=" * 80)
        
        for i, email in enumerate(unread_emails, 1):
            print(f"\n📧 Email {i}:")
            print(f"   Subject: {email.get('subject', 'No subject')}")
            print(f"   From: {email.get('from', 'Unknown')}")
            print(f"   Date: {format_date(email.get('internal_date'))}")
            print(f"   Snippet: {email.get('snippet', 'No snippet')[:100]}...")
            
            # Show first 200 characters of body
            body = email.get('body', '')
            if body:
                print(f"   Body preview: {body[:200]}...")
            else:
                print("   Body: No body content")
            
            print("-" * 40)
        
        # Example: Mark first email as read
        if unread_emails:
            first_email_id = unread_emails[0].get('id')
            if first_email_id:
                print(f"\n🔖 Marking first email as read...")
                if client.mark_as_read(first_email_id):
                    print("✅ Email marked as read!")
                else:
                    print("❌ Failed to mark email as read")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_unread_emails()
    if success:
        print("\n🎉 Unread email extraction test completed!")
    else:
        print("\n💥 Unread email extraction test failed!")
        sys.exit(1) 