from typing import List, Dict
from datetime import datetime

class Email:
    def __init__(self):
        # Basic identifiers
        self.id: str = ""                    # Gmail message ID
        self.thread_id: str = ""             # Gmail thread ID
        self.message_id: str = ""            # RFC 2822 Message-ID header
        
        # Header information
        self.subject: str = ""
        self.from_email: str = ""            # Full "Name <email@domain.com>" format
        self.from_name: str = ""             # Just the name part
        self.from_address: str = ""          # Just the email part
        self.to: List[str] = []              # List of recipients
        self.cc: List[str] = []              # CC recipients
        self.bcc: List[str] = []             # BCC recipients (rarely available)
        self.reply_to: str = ""              # Reply-To header
        
        # Dates and timing
        self.date: str = ""                  # Original Date header
        self.received_date: datetime = None   # When Gmail received it
        self.sent_date: datetime = None      # Parsed from Date header
        
        # Content
        self.body_text: str = ""             # Plain text body
        self.body_html: str = ""             # HTML body
        self.snippet: str = ""               # Gmail's snippet (preview)
        

        # Size and technical details
        self.size_estimate: int = 0          # Size in bytes
        self.internal_date: str = ""         # Gmail's internal timestamp
        
        # Additional headers (store as dict for flexibility)
        self.headers: Dict[str, str] = {}    # All other headers
        
        # Processing metadata
        self.raw_message: Dict = {}          # Store original API response if needed