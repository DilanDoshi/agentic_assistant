"""
Google Calendar API client for the Agentic Assistant.

This module provides a comprehensive interface to the Google Calendar API,
handling calendar events, scheduling, and meeting management. It inherits
from BaseGoogleClient for authentication and shared functionality.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from googleapiclient.errors import HttpError

from backend.google.base_client import BaseGoogleClient
from backend.google.events import Event

# Import unified scopes from base client
from backend.google.base_client import UNIFIED_SCOPES

class GoogleCalendarClient(BaseGoogleClient):
    """
    Google Calendar API client for handling calendar operations.
    Inherits authentication logic from BaseGoogleClient.
    """
    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        super().__init__(credentials_path, token_path, UNIFIED_SCOPES)
        self.service = None
        self.authenticate()

    def authenticate(self) -> bool:
        """
        Authenticate and build the Calendar service.
        """
        if super().authenticate():
            self.service = self.build_service("calendar", "v3")
            return True
        return False

    def get_primary_calendar_id(self) -> str:
        """Return the user's primary calendar ID."""
        try:
            calendars = self.service.calendarList().list().execute().get('items', [])
            for cal in calendars:
                if cal.get('primary'):
                    return cal['id']
            return calendars[0]['id'] if calendars else 'primary'
        except HttpError as e:
            print(f"Error fetching primary calendar: {e}")
            return 'primary'

    def get_events(
        self,
        calendar_id: Optional[str] = None,
        max_results: int = 10,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Fetch events in a time window."""
        if not calendar_id:
            calendar_id = self.get_primary_calendar_id()
        if time_min is None:
            time_min = datetime.now(timezone.utc)
        if time_max is None:
            time_max = time_min + timedelta(days=7)

        try:
            return self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute().get('items', [])
        except HttpError as e:
            print(f"Error getting events: {e}")
            return []

    def get_events_as_objects(self, calendar_id: Optional[str] = None, max_results: int = 10, time_min: Optional[datetime] = None, time_max: Optional[datetime] = None) -> List[Event]:
        """Fetch events and return them as Event objects."""
        raw_events = self.get_events(calendar_id, max_results, time_min, time_max)
        return [self._raw_to_event(event) for event in raw_events]

    def get_upcoming_events(self, days: int = 7, max_results: int = 10, calendar_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get upcoming events for the specified number of days."""
        time_min = datetime.now(timezone.utc)
        time_max = time_min + timedelta(days=days)
        
        return self.get_events(
            calendar_id=calendar_id,
            max_results=max_results,
            time_min=time_min,
            time_max=time_max
        )

    def get_upcoming_events_as_objects(self, days: int = 7, max_results: int = 10, calendar_id: Optional[str] = None) -> List[Event]:
        """Get upcoming events as Event objects for the specified number of days."""
        time_min = datetime.now(timezone.utc)
        time_max = time_min + timedelta(days=days)
        
        return self.get_events_as_objects(
            calendar_id=calendar_id,
            max_results=max_results,
            time_min=time_min,
            time_max=time_max
        )

    def _raw_to_event(self, raw_event: Dict[str, Any]) -> Event:
        """Convert a raw Google Calendar API response to an Event object."""
        event = Event()
        
        # Basic identifiers
        event.id = raw_event.get('id', '')
        event.calendar_id = raw_event.get('calendarId', '')
        event.html_link = raw_event.get('htmlLink', '')
        
        # Event basic information
        event.summary = raw_event.get('summary', '')
        event.description = raw_event.get('description', '')
        event.location = raw_event.get('location', '')
        
        # Timing information
        start = raw_event.get('start', {})
        end = raw_event.get('end', {})
        
        if 'dateTime' in start:
            event.start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
            event.timezone = start.get('timeZone', '')
            event.is_all_day = False
        elif 'date' in start:
            event.start_date = start['date']
            event.is_all_day = True
            
        if 'dateTime' in end:
            event.end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
        elif 'date' in end:
            event.end_date = end['date']
        
        # Attendee information
        event.attendees = raw_event.get('attendees', [])
        event.organizer = raw_event.get('organizer', {})
        
        # Event status and visibility
        event.status = raw_event.get('status', '')
        event.visibility = raw_event.get('visibility', '')
        event.transparency = raw_event.get('transparency', '')
        
        # Recurrence information
        event.recurrence = raw_event.get('recurrence', [])
        event.recurring_event_id = raw_event.get('recurringEventId', '')
        
        # Reminders and notifications
        event.reminders = raw_event.get('reminders', {})
        
        # Additional metadata
        if 'created' in raw_event:
            event.created = datetime.fromisoformat(raw_event['created'].replace('Z', '+00:00'))
        if 'updated' in raw_event:
            event.updated = datetime.fromisoformat(raw_event['updated'].replace('Z', '+00:00'))
        
        event.creator = raw_event.get('creator', {})
        if 'originalStartTime' in raw_event:
            original_start = raw_event['originalStartTime']
            if 'dateTime' in original_start:
                event.original_start_time = datetime.fromisoformat(original_start['dateTime'].replace('Z', '+00:00'))
        
        # Store raw event for reference
        event.raw_event = raw_event
        
        return event

    def _event_to_raw(self, event: Event) -> Dict[str, Any]:
        """Convert an Event object to a raw Google Calendar API format."""
        raw_event = {
            'summary': event.summary,
            'description': event.description,
            'location': event.location,
        }
        
        # Timing information
        if event.is_all_day:
            raw_event['start'] = {'date': event.start_date}
            raw_event['end'] = {'date': event.end_date}
        else:
            raw_event['start'] = {
                'dateTime': event.start_time.isoformat(),
                'timeZone': event.timezone or 'UTC'
            }
            raw_event['end'] = {
                'dateTime': event.end_time.isoformat(),
                'timeZone': event.timezone or 'UTC'
            }
        
        # Attendees
        if event.attendees:
            raw_event['attendees'] = event.attendees
        
        # Event status and visibility
        if event.status:
            raw_event['status'] = event.status
        if event.visibility:
            raw_event['visibility'] = event.visibility
        if event.transparency:
            raw_event['transparency'] = event.transparency
        
        # Recurrence
        if event.recurrence:
            raw_event['recurrence'] = event.recurrence
        
        # Reminders
        if event.reminders:
            raw_event['reminders'] = event.reminders
        
        return raw_event

    def create_event(
        self,
        summary: str,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        attendees: Optional[List[str]] = None,
        location: Optional[str] = None,
        calendar_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new calendar event."""
        if not calendar_id:
            calendar_id = self.get_primary_calendar_id()
        if start_time is None:
            start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        if end_time is None:
            end_time = start_time + timedelta(hours=1)

        event: Dict[str, Any] = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC'
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC'
            },
        }
        if location:
            event['location'] = location
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            return self.service.events().insert(
                calendarId=calendar_id,
                body=event,
                sendUpdates='all'
            ).execute()
        except HttpError as e:
            print(f"Error creating event: {e}")
            return None

    def update_event(
        self,
        event_id: str,
        calendar_id: Optional[str] = None,
        **changes
    ) -> Optional[Dict[str, Any]]:
        """Update fields of an existing event."""
        if not calendar_id:
            calendar_id = self.get_primary_calendar_id()
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            for key, val in changes.items():
                if key in event:
                    event[key] = val
            return self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
        except HttpError as e:
            print(f"Error updating event {event_id}: {e}")
            return None

    def delete_event(
        self,
        event_id: str,
        calendar_id: Optional[str] = None
    ) -> bool:
        """Delete an event by ID."""
        if not calendar_id:
            calendar_id = self.get_primary_calendar_id()
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            return True
        except HttpError as e:
            print(f"Error deleting event {event_id}: {e}")
            return False

    def find_free_time(
        self,
        duration_minutes: int = 60,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        calendar_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return free time slots between start_date and end_date."""
        if start_date is None:
            start_date = datetime.now(timezone.utc)
        if end_date is None:
            end_date = start_date + timedelta(days=7)
        busy = self.service.freebusy().query(
            body={
                'timeMin': start_date.isoformat(),
                'timeMax': end_date.isoformat(),
                'items': [{'id': calendar_id or self.get_primary_calendar_id()}]
            }
        ).execute()['calendars']
        busy_slots = busy.get(calendar_id or self.get_primary_calendar_id(), {}).get('busy', [])

        free_slots: List[Dict[str, Any]] = []
        window_start = start_date
        for slot in busy_slots:
            start = datetime.fromisoformat(slot['start'])
            if window_start + timedelta(minutes=duration_minutes) <= start:
                free_slots.append({'start': window_start.isoformat(), 'end': (window_start + timedelta(minutes=duration_minutes)).isoformat()})
            window_start = max(window_start, datetime.fromisoformat(slot['end']))
        # Check after last busy
        if window_start + timedelta(minutes=duration_minutes) <= end_date:
            free_slots.append({'start': window_start.isoformat(), 'end': (window_start + timedelta(minutes=duration_minutes)).isoformat()})
        return free_slots


def authenticate_calendar() -> GoogleCalendarClient:
    """Legacy helper to get an authenticated client."""
    client = GoogleCalendarClient()
    return client if client.authenticate() else None
