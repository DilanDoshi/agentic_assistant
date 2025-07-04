"""
Gmail API client for the Agentic Assistant.

This module provides a comprehensive interface to the Gmail API, handling
authentication, email retrieval, parsing, and draft creation. It encapsulates
all Gmail-related operations needed by the AI assistant.
"""

import os.path
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import base64
from email.mime.text import MIMEText
import re

from backend.google.emails import Email
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes required for the application
# If modifying these scopes, delete the file token.json to force re-authentication
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",    # Read emails and metadata
    "https://www.googleapis.com/auth/gmail.send",        # Send emails
    "https://www.googleapis.com/auth/gmail.compose",     # Create and modify drafts
    "https://www.googleapis.com/auth/gmail.modify"       # Modify emails (labels, etc.)
]

class GmailClient:
    """
    Gmail API client for handling email operations.
    
    This class provides methods for authenticating with Gmail, retrieving emails,
    parsing email content, and creating drafts. It handles all the complexity
    of working with the Gmail API and provides a clean interface for the rest
    of the application.
    """
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        """
        Initialize the Gmail client with authentication.
        
        Args:
            credentials_path (str): Path to the Google Cloud credentials file
            token_path (str): Path to store/load the OAuth token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None  # Gmail API service instance
        self.authenticate()  # Automatically authenticate on initialization
        
    def authenticate(self) -> bool:
        """
        Authenticate the user to the Gmail API and return True if successful.
        
        This method handles the OAuth2 flow for Gmail API access. It first tries
        to load existing credentials from the token file, and if that fails or
        the token is expired, it initiates a new authentication flow.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        creds = None
        
        # Check if token file exists and load credentials
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
            except Exception as e:
                print(f"Error loading existing token: {e}")
                # Remove invalid token file
                os.remove(self.token_path)
                creds = None
        
        # If no valid credentials available, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_path}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False
                
                # Save the credentials for the next run
                try:
                    with open(self.token_path, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"Error saving token: {e}")
        
        try:
            # Build the Gmail service
            self.service = build("gmail", "v1", credentials=creds)
            
            return True
            
        except HttpError as error:
            print(f"Gmail API error: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error: {error}")
            return False
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """Get all Gmail labels"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            results = self.service.users().labels().list(userId="me").execute()
            return results.get("labels", [])
        except HttpError as error:
            print(f"Error getting labels: {error}")
            return []
    
    def get_messages(self, query: str = "", max_results: int = 10) -> List[Dict[str, Any]]:
        """Get messages based on query"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            results = self.service.users().messages().list(
                userId="me", 
                q=query, 
                maxResults=max_results
            ).execute()
            
            messages = results.get("messages", [])
            return messages
        except HttpError as error:
            print(f"Error getting messages: {error}")
            return []
    
    def get_unread_emails(self, count: int) -> List[Email]:
        """Get unread emails"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            results = self.service.users().messages().list(
                userId="me",
                q="is:unread",
                maxResults=count
            ).execute()
            msgs = results.get("messages", [])
            emails = []
            for msg in msgs:
                # Get full message details using the message ID
                full_msg = self.service.users().messages().get(
                    userId="me",
                    id=msg["id"],
                    format="full"  # Gets complete message with headers and body
                ).execute()
                #extract info from full_msg
                email = self.create_email_from_message(full_msg)
                emails.append(email)
            return emails
        except HttpError as error:
            print(f"Error getting unread emails: {error}")
            return []
    
    def fetch_email_by_msg_id(self, msg_id: str) -> List[Email]:
        """Fetch a specific email by its message ID"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            # Get full message details using the message ID
            full_msg = self.service.users().messages().get(
                userId="me",
                id=msg_id,
                format="full"  # Gets complete message with headers and body
            ).execute()
            
            # Create Email object from the message
            email = self.create_email_from_message(full_msg)
            return [email]
            
        except HttpError as error:
            print(f"Error fetching email with ID {msg_id}: {error}")
            return []
        except Exception as error:
            print(f"Unexpected error fetching email with ID {msg_id}: {error}")
            return []
        
    def create_email_from_message(self, full_msg: Dict) -> Email:
        """Create an Email object from Gmail API message response"""
        email = Email()
        
        # Basic identifiers
        email.id = full_msg.get("id", "")
        email.thread_id = full_msg.get("threadId", "")
        email.snippet = full_msg.get("snippet", "")
        email.size_estimate = full_msg.get("sizeEstimate", 0)
        email.internal_date = full_msg.get("internalDate", "")
        email.raw_message = full_msg  # Store original response
        
        # Extract payload and headers
        payload = full_msg.get("payload", {})
        headers = payload.get("headers", [])
        
        # Convert headers to dictionary for easy access
        header_dict = {header["name"]: header["value"] for header in headers}
        email.headers = header_dict
        
        # Extract header information
        email.subject = header_dict.get("Subject", "")
        email.from_email = header_dict.get("From", "")
        email.reply_to = header_dict.get("Reply-To", "")
        email.date = header_dict.get("Date", "")
        email.message_id = header_dict.get("Message-ID", "")
        
        # Parse from_email to extract name and address
        email.from_name, email.from_address = self.parse_email_address(email.from_email)
        
        # Parse recipient lists
        email.to = self.parse_email_list(header_dict.get("To", ""))
        email.cc = self.parse_email_list(header_dict.get("Cc", ""))
        email.bcc = self.parse_email_list(header_dict.get("Bcc", ""))
        
        # Parse dates
        email.sent_date = self.parse_date(email.date)
        email.received_date = self.parse_internal_date(email.internal_date)
        
        # Extract body content
        email.body_text, email.body_html = self.extract_body_content(payload)
        
        return email
    
    def create_draft_from_email(self, email: Email) -> str:
        """Create a draft from an Email object
        Args:
            email(Email): An Email object that contains the draft to be created
        Returns:
            str: The message id of the created draft (draft_id)
        """
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            # 1. Build the MIME message
            message = MIMEText(email.draft, "plain")

            # Get all relevant people the email needs to be sent to (reply all)
            profile = self.service.users().getProfile(userId="me").execute()   
            user_email = profile['emailAddress']
            

            # Build recipient lists for reply-all
            orig_to = email.to or []
            orig_cc = email.cc or []
            orig_bcc = email.bcc or []
            
            # Clean up email lists to only contain plain email addresses
            orig_to = [self.extract_email_only(x) for x in orig_to]
            orig_cc = [self.extract_email_only(x) for x in orig_cc]
            orig_bcc = [self.extract_email_only(x) for x in orig_bcc]

            orig_to.append(email.from_address)
            
            
            orig_to = [x for x in orig_to if x != user_email]
            cc_send = [x for x in orig_cc if x != user_email]
            bcc_send = [x for x in orig_bcc if x != user_email]

            # Set recipients
            if orig_to:
                message["To"] = ', '.join(orig_to)
            else:
                return "ERROR CREATING DRAFT: No recipients found"
            if cc_send:
                message["Cc"] = ", ".join(cc_send)
            if bcc_send:
                message["Bcc"] = ", ".join(bcc_send)
        
            # Format subject for reply (add "Re:" if not already present)
            subject = email.subject
            if not subject.lower().startswith("re:"):
                subject = f"Re: {subject}"
            message["Subject"] = subject

            # Set reply headers for proper threading
            if email.message_id:
                message["In-Reply-To"] = email.message_id
                message["References"] = email.message_id

            # 2. Base64-encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # 3. Wrap it in the request body with thread ID for conversation threading
            create_body = {
                "message": {
                    "raw": raw_message,
                    "threadId": email.thread_id
                }
            }

            draft = (
                self.service.users()
                    .drafts()
                    .create(userId='me', body=create_body)
                    .execute()
            )

            return draft['id']
        except HttpError as error:
            print(f"Error creating draft: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error creating draft: {error}")
            return False

    def edit_existing_draft(self, draft_id: str, new_body: str, new_subject: str, new_to: list[str], new_cc: list[str], new_bcc: list[str]) -> str:
        """Edit an existing draft by its draft ID"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")

        try:
            # Get the draft information from draft id from API
            try:
                draft = self.service.users().drafts().get(userId='me', id=draft_id, format='full').execute()
            except HttpError as e:
                return "Error editing draft: Draft not found or access denied"
            except Exception as e:
                return "Error editing draft: Network or API error"
            
            draft_obj = self.create_email_from_message(draft['message'])

            draft_message = ""
            
            if new_body:
                draft_message = MIMEText(new_body, "plain")
            else:
                draft_message = MIMEText(draft_obj.body_text, "plain")

            if new_subject:
                draft_message["Subject"] = new_subject
            else:
                draft_message["Subject"] = draft_obj.subject

            if new_to:
                draft_message["To"] = ", ".join(new_to)
            else:
                draft_message["To"] = ", ".join(draft_obj.to)

            if new_cc:
                draft_message["Cc"] = ", ".join(new_cc)
            else:
                draft_message["Cc"] = ", ".join(draft_obj.cc)

            if new_bcc:
                draft_message["Bcc"] = ", ".join(new_bcc)
            else:
                draft_message["Bcc"] = ", ".join(draft_obj.bcc)

            # Set reply headers for proper threading
            if draft_obj.message_id:
                draft_message["In-Reply-To"] = draft_obj.message_id
                draft_message["References"] = draft_obj.message_id

            # 2. Base64-encode the message
            raw_message = base64.urlsafe_b64encode(draft_message.as_bytes()).decode()

            # 3. Wrap it in the request body with thread ID for conversation threading
            create_body = {
                'id': draft_id,
                "message": {
                    "raw": raw_message,
                    "threadId": draft_obj.thread_id
                }
            }

            # 4. Call the API
            try:
                new_draft = self.service.users().drafts().update(userId="me", id=draft_id, body=create_body).execute()
            except HttpError as e:
                return "Error editing draft: Update failed"
            except Exception as e:
                return "Error editing draft: Network or API error during update"

            return new_draft['id']
        except HttpError as error:
            print(f"Error editing draft: {error}")
            return "Error editing draft"
        except Exception as error:
            print(f"Unexpected error editing draft: {error}")
            return "Unexpected error editing draft"

    def send_draft(self, draft_id: str) -> bool:
        """Send a draft by its message ID"""
        if not self.service:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        try:
            body = {'id': draft_id}
            sent_message = (
                self.service.users()
                    .drafts()
                    .send(userId='me', body=body)
                    .execute()
            )
            return True
        except HttpError as e:
            print(f"Error sending draft: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error sending draft: {e}")
            return False

    def extract_email_only(self, email_str):
        """Extract just the email address from formatted strings like 'Name <email@domain.com>'"""

        # Pattern to match email in angle brackets
        match = re.search(r'<(.+@.+)>', email_str)
        if match:
            return match.group(1)
        # If no angle brackets, return as is
        return email_str

    def parse_email_address(self, email_string: str) -> tuple[str, str]:
        """Parse 'Name <email@domain.com>' format into name and address"""
        import re
        
        if not email_string:
            return "", ""
        
        # Pattern to match "Name <email@domain.com>" or just "email@domain.com"
        match = re.match(r'^(.*?)\s*<(.+@.+)>$', email_string.strip())
        if match:
            name = match.group(1).strip(' "')
            address = match.group(2).strip()
            return name, address
        else:
            # Just an email address without name
            return "", email_string.strip()

    def parse_email_list(self, email_string: str) -> List[str]:
        """Parse comma-separated email list"""
        if not email_string:
            return []
        
        # Split by comma and clean up each email
        emails = [email.strip() for email in email_string.split(',')]
        return [email for email in emails if email]  # Remove empty strings

    def parse_date(self, date_string: str) -> datetime:
        """Parse RFC 2822 date string to datetime object"""
        from email.utils import parsedate_to_datetime
        
        if not date_string:
            return None
        
        try:
            return parsedate_to_datetime(date_string)
        except (ValueError, TypeError):
            return None

    def parse_internal_date(self, internal_date: str) -> datetime:
        """Parse Gmail internal date (milliseconds since epoch) to datetime"""
        if not internal_date:
            return None
        
        try:
            # Convert milliseconds to seconds
            timestamp = int(internal_date) / 1000
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            return None

    def extract_body_content(self, payload: Dict) -> tuple[str, str]:
        """Extract both text and HTML body content"""
        text_body = ""
        html_body = ""
        
        def process_part(part):
            nonlocal text_body, html_body
            mime_type = part.get("mimeType", "")
            
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    text_body += self.decode_base64(data)
                    
            elif mime_type == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    html_body += self.decode_base64(data)
                    
            elif mime_type.startswith("multipart/"):
                # Process nested parts
                for sub_part in part.get("parts", []):
                    process_part(sub_part)
        
        # Handle multipart vs single part messages
        if "parts" in payload:
            for part in payload["parts"]:
                process_part(part)
        else:
            process_part(payload)
        
        return text_body.strip(), html_body.strip()

    def decode_base64(self, data: str) -> str:
        """Decode base64url encoded data"""
        import base64
        
        try:
            # Add padding if needed
            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            
            # Replace URL-safe characters and decode
            data = data.replace('-', '+').replace('_', '/')
            return base64.b64decode(data).decode('utf-8', errors='ignore')
        except Exception:
            return ""

def authenticate_gmail() -> Optional[GmailClient]:
    
    """Legacy function for backward compatibility"""
    client = GmailClient()
    if client.authenticate():
        return client
    return None



