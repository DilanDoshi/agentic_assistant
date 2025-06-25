#!/usr/bin/env python3
"""
Simple test script for Gmail client authentication
delete after use
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.google.gmail_client import GmailClient

def test_gmail_authentication():
    """Test Gmail authentication and basic functionality"""
    print("Testing Gmail client authentication...")
    
    # Check if credentials file exists
    if not os.path.exists("credentials.json"):
        print("❌ Error: credentials.json not found!")
        print("Please download your OAuth 2.0 credentials from Google Cloud Console")
        print("and save them as 'credentials.json' in the project root directory.")
        return False
    
    try:
        # Create and authenticate client
        client = GmailClient()
        
        print("🔐 Attempting to authenticate with Gmail...")
        if client.authenticate():
            print("✅ Gmail authentication successful!")
            
            # Test getting labels
            print("📋 Testing label retrieval...")
            labels = client.get_labels()
            print(f"✅ Found {len(labels)} labels")
            
            # Test getting messages
            print("📧 Testing message retrieval...")
            messages = client.get_messages(max_results=3)
            print(f"✅ Found {len(messages)} recent messages")

            # Test getting unread emails
            print("📧 Testing unread email retrieval...")
            unread_emails = client.get_unread_emails(count=3)
            for email in unread_emails:
                print(email)
            print(f"✅ Found {len(unread_emails)} unread emails")
            
            return True
        else:
            print("❌ Gmail authentication failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_gmail_authentication()
    if success:
        print("\n🎉 Gmail client is working correctly!")
    else:
        print("\n💥 Gmail client test failed!")
        sys.exit(1) 