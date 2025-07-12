"""
Base Google API client for the Agentic Assistant.

This module provides a base class for Google API clients, handling
common authentication and shared functionality.
"""

import os.path
import json
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Unified scopes for all Google services used in the application
UNIFIED_SCOPES = [
    # Gmail scopes
    "https://www.googleapis.com/auth/gmail.readonly",    # Read emails and metadata
    "https://www.googleapis.com/auth/gmail.send",        # Send emails
    "https://www.googleapis.com/auth/gmail.compose",     # Create and modify drafts
    "https://www.googleapis.com/auth/gmail.modify",      # Modify emails (labels, etc.)
    # Calendar scopes
    "https://www.googleapis.com/auth/calendar"           # Full calendar access
]

class BaseGoogleClient:
    """
    Base class for Google API clients.
    
    This class provides common authentication and shared functionality
    for all Google API clients in the application.
    """
    
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json", scopes: list = None):
        """
        Initialize the base Google client with authentication.
        
        Args:
            credentials_path (str): Path to the Google Cloud credentials file
            token_path (str): Path to store/load the OAuth token
            scopes (list): List of Google API scopes required for this client
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes or []
        self.service = None  # API service instance
        
    def authenticate(self) -> bool:
        """
        Authenticate the user to Google APIs and return True if successful.
        
        This method handles the OAuth2 flow for Google API access. It first tries
        to load existing credentials from the token file, and if that fails or
        the token is expired, it initiates a new authentication flow.
        
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        creds = None
        
        # Check if token file exists and load credentials
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)
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
                        self.credentials_path, self.scopes
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
            # Store credentials for subclasses to use
            self.credentials = creds
            return True
            
        except HttpError as error:
            print(f"Google API error: {error}")
            return False
        except Exception as error:
            print(f"Unexpected error: {error}")
            return False
    
    def build_service(self, service_name: str, version: str = "v1"):
        """
        Build a Google API service.
        
        Args:
            service_name (str): Name of the Google API service (e.g., 'gmail', 'calendar')
            version (str): API version to use
            
        Returns:
            The built service object
        """
        if not self.credentials:
            raise RuntimeError("Not authenticated. Call authenticate() first.")
        
        return build(service_name, version, credentials=self.credentials) 