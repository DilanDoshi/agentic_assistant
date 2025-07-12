"""
Event data model for the Agentic Assistant.

This module defines the Event class that represents Google Calendar events
with all their metadata, content, and processing information.
"""

from typing import List, Dict, Optional
from datetime import datetime

class Event:
    """
    Event model to represent Google Calendar events.
    
    This class encapsulates all the data associated with a Google Calendar event,
    including metadata, attendees, timing, and processing information.
    It provides a structured way to work with calendar event data throughout
    the application.
    """
    
    def __init__(self):
        """
        Initialize a new Event instance with default values.
        
        All fields are initialized with appropriate default values
        to ensure the object is always in a valid state.
        """
        # Basic identifiers for Google Calendar API
        self.id: str = ""                    # Google Calendar event ID (unique identifier)
        self.calendar_id: str = ""           # Calendar ID where the event belongs
        self.html_link: str = ""             # Web link to view the event
        
        # Event basic information
        self.summary: str = ""               # Event title/summary
        self.description: str = ""           # Event description
        self.location: str = ""              # Event location
        
        # Timing information
        self.start_time: datetime = None     # Event start time
        self.end_time: datetime = None       # Event end time
        self.start_date: str = ""            # Start date (for all-day events)
        self.end_date: str = ""              # End date (for all-day events)
        self.is_all_day: bool = False        # Whether this is an all-day event
        self.timezone: str = ""              # Event timezone
        
        # Attendee information
        self.attendees: List[Dict] = []      # List of attendee objects with email, name, response status
        self.organizer: Dict = {}            # Organizer information (email, name, self)
        
        # Event status and visibility
        self.status: str = ""                # Event status (confirmed, tentative, cancelled)
        self.visibility: str = ""            # Event visibility (default, public, private, confidential)
        self.transparency: str = ""          # Event transparency (opaque, transparent)
        
        # Recurrence information
        self.recurrence: List[str] = []      # Recurrence rules (RRULE, EXDATE, etc.)
        self.recurring_event_id: str = ""    # ID of the recurring event series
        
        # Reminders and notifications
        self.reminders: Dict = {}            # Reminder settings (useDefault, overrides)
        self.notifications: List[Dict] = []  # Notification settings
        
        # Additional metadata
        self.created: datetime = None        # When the event was created
        self.updated: datetime = None        # When the event was last updated
        self.creator: Dict = {}              # Creator information
        self.original_start_time: datetime = None  # Original start time for recurring events
        
        # Processing metadata
        self.raw_event: Dict = {}            # Store original Google Calendar API response if needed
        
        # AI processing fields
        self.ai_summary: str = ""            # AI-generated summary of the event
        self.ai_analysis: str = ""           # AI analysis of the event content
        self.status: str = ""                # Processing status (pending, processed, error) 