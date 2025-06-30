"""
Email data model for the Agentic Assistant.

This module defines the Email class that represents Gmail messages
with all their metadata, content, and processing information.
"""

from typing import List, Dict, Optional
from datetime import datetime

class Email:
    """
    Email model to represent Gmail messages.
    
    This class encapsulates all the data associated with a Gmail message,
    including headers, content, metadata, and processing information.
    It provides a structured way to work with email data throughout
    the application.
    """
    
    def __init__(self):
        """
        Initialize a new Email instance with default values.
        
        All fields are initialized with appropriate default values
        to ensure the object is always in a valid state.
        """
        # Basic identifiers for Gmail API and email standards
        self.id: str = ""                    # Gmail message ID (unique identifier)
        self.thread_id: str = ""             # Gmail thread ID (conversation grouping)
        self.message_id: str = ""            # RFC 2822 Message-ID header (email standard)
        
        # Header information extracted from email headers
        self.subject: str = ""               # Email subject line
        self.from_email: str = ""            # Full "Name <email@domain.com>" format
        self.from_name: str = ""             # Just the name part of sender
        self.from_address: str = ""          # Just the email address part of sender
        self.to: List[str] = []              # List of primary recipients
        self.cc: List[str] = []              # List of CC recipients
        self.bcc: List[str] = []             # List of BCC recipients (rarely available)
        self.reply_to: str = ""              # Reply-To header (where replies should go)
        
        # Dates and timing information
        self.date: str = ""                  # Original Date header from email
        self.received_date: datetime = None   # When Gmail received the email
        self.sent_date: datetime = None      # Parsed from Date header (when sender sent it)
        
        # Email content in different formats
        self.body_text: str = ""             # Plain text version of email body
        self.body_html: str = ""             # HTML version of email body
        self.snippet: str = ""               # Gmail's snippet (preview text)
        
        # Size and technical details
        self.size_estimate: int = 0          # Size in bytes (Gmail's estimate)
        self.internal_date: str = ""         # Gmail's internal timestamp
        
        # Additional headers (store as dict for flexibility)
        self.headers: Dict[str, str] = {}    # All other email headers as key-value pairs
        
        # Processing metadata
        self.raw_message: Dict = {}          # Store original Gmail API response if needed

        # Drafts
        self.draft: str = ""                 # AI-generated draft response to this email
        self.draft_id: str = ""              # Google message id for the draft
        self.ready_to_send: bool = False      # Whether the draft is ready to send, True if user has revied draft
        self.status: str = ""                 # Status of the draft, either '' or 'sent' if sent
