from backend.google.gmail_client import GmailClient
from backend.google.emails import Email
from backend.google.gcal_client import GoogleCalendarClient
from backend.google.events import Event
from backend.pipelines.chat import chat_with_agent, create_chat_id
from backend.llm import init_llm
from backend.llm import prompts
from backend.google.gmail_client import GmailClient

import ast


def get_unread_emails(count: int) -> dict:
    """Gets unread emails from the user's Gmail inbox.
    
    Args:
        count (int): Number of unread emails to retrieve. If unspecified, default to 10.
        
    Returns:
        dict: Dictionary containing:
            success (bool): Whether the operation succeeded
            data (dict): Email data keyed by ID if successful
            error (str): Error message if unsuccessful
    """
    g_client = GmailClient()
    
    emails = g_client.get_unread_emails(count)
    
    # Convert emails list to dictionary keyed by email ID
    email_dict = {}
    for email in emails:
        email_dict[email.id] = {
            # Gmail message ID
            #'thread_id': email.thread_id,        # Gmail thread ID 
            #'message_id': email.message_id,      # RFC 2822 Message-ID header
            'subject': email.subject,
            'from_email': email.from_email,      # Full "Name <email@domain.com>" format
            'from_name': email.from_name,        # Just the name part
            'from_address': email.from_address,  # Just the email part
            'to': email.to,                      # List of recipients
            'cc': email.cc,                      # CC recipients
            'bcc': email.bcc,                    # BCC recipients (rarely available)
            'reply_to': email.reply_to,          # Reply-To header
            'date': email.date,                  # Original Date header
            'received_date': email.received_date, # When Gmail received it
            'body_text': email.body_text,        # Plain text body
            'headers': email.headers,            # All other headers

        }

    # Figure out to get email attachments to be fed as context
    
    # TODO: Figure out how to send the full emails to front end to display
    
    return email_dict

def create_drafts_for_unread_emails(email_info_dict: dict[str, str]) -> dict:
    """ 
    This tool will create drafts to respond to the unread emails. Use this tool when you need to create drafts to the user's unread emails.
    This tool will also decide which emails require a response and which emails do not.
    Only use this tool if the user has unread emails.

    Use the value in the parameter email_info_dict to include information about the draft that needs to be created for the respective email_id. Use this value to indicate that a meeting is being created, to pass important user information, etc.

    Args:
        email_info_dict(dict[str, str]): A dictionary where keys are google message email ids and values are strings containing important information that is required for the drat creating agent. Use the get_unread_emails tool to get the google message email ids.
    Returns:
        A dictionary of email ids and their drafts.
    """
    g_client = GmailClient()
    emails_dict = {}
    drafts = []
    email_objs = {}

    # Extract email IDs from the dictionary keys
    email_ids = list(email_info_dict.keys())

    for email_id in email_ids:
        email_obj = g_client.fetch_email_by_msg_id(email_id)[0]
        email_objs[email_id] = email_obj
        emails_dict[email_id] = {
            'subject': email_obj.subject,
            'from_email': email_obj.from_email,
            'from_name': email_obj.from_name,
            'from_address': email_obj.from_address,
            'to': email_obj.to,
            'cc': email_obj.cc,
            'bcc': email_obj.bcc,
            'reply_to': email_obj.reply_to,
            'date': email_obj.date,
            'received_date': email_obj.received_date,
            'body_text': email_obj.body_text,
            'draft': '',
            'draft_specications': email_info_dict[email_id]
        }
    
    emails_for_llm = str(emails_dict)

    # Ask LLM to get the msgs_ids that are needed to be replied to 
    prompt_content = prompts.get_msg_ids_prompt(emails_for_llm)
    messages = [
        {"role": "system", "content": prompt_content},
        {"role": "user", "content": "follow the prompt exactly"}
    ]
    response = init_llm.claude.invoke(messages)

    # The response is an AIMessage object, not a dictionary
    msg_id_from_llm = response.content

    # Convert response to python list 
    email_ids_from_llm = ast.literal_eval(msg_id_from_llm)

    # Create drafts
    draft_messages = [
            {"role": "user", "content": "follow the prompts exactly. I will give them to you in the next message."}
        ]
    
    # TODO: add a function that gets the user profile from user gmail such as name, title, signature etc. 

    for email_id in email_ids_from_llm:
        # Ask LLM to create a draft for the email
        email_info = str(emails_dict[email_id])

        draft_prompt_content = prompts.get_drating_agent_prompt(email_info)
        draft_messages.append({"role": "user", "content": draft_prompt_content})

        draft_response = init_llm.claude.invoke(draft_messages)
        # The draft_response is also an AIMessage object
        emails_dict[email_id]['draft'] = draft_response.content
        
        # Update the email object with the draft
        email_objs[email_id].draft = draft_response.content

        # Send to drafts via API
        draft_id = g_client.create_draft_from_email(email_objs[email_id])
        email_objs[email_id].draft_id = draft_id
        emails_dict[email_id]['draft_id'] = draft_id

        draft_messages.append({"role": "assistant", "content": draft_response.content})
        
        # Give AI ready_to_send field (False by default)
        emails_dict[email_id]['ready_to_send'] = email_objs[email_id].ready_to_send

        # Mark the email as read
        g_client.mark_as_read(email_id)

    # TODO: Figure out how to send the drafts to front end to display
    return emails_dict

def send_drafts(draft_ids: list[str], confirmation: bool) -> dict:
    """ 
    Use this tool only after you have called create_drafts_for_unread_emails tool.
    This tool will send the created drafts to the intended recipients.
    To use this tool, you need to ask confirm with user if they want to send the drafts as well as which drafts to send.
    Make sure to change the status of the draft under the field 'status' to 'sent' if the user confirmed to send the draft AFTER calling this tool and receive True.

    Args:
        draft_ids(list[str]): A list of google message email ids for the drafts that the user CONFIRMED to send. Use the draft_id field from the dict returned by the create_drafts_for_unread_emails tool.
        confirmation(bool): A boolean value that indicates if the user confirmed to send the drafts listed in the draft_ids parameter.
    
    Return:
        A dictionary of draft ids and their status. True if sent successfully, False if not. Report to the user which drafts were sent successfully and which were not.
    """

    g_client = GmailClient()
    status = {}
    for draft_id in draft_ids:
        status[draft_id] = g_client.send_draft(draft_id)

    return status

def edit_existing_draft(draft_ids: str, new_body: str, new_subject: str, new_to: list[str], new_cc: list[str], new_bcc: list[str], new_reply_to: str, thread_id: str) -> dict:
    """
    Use this tool to edit an existing draft. Use this tool only when the user requests to edit a particular draft. Must have used the create_drafts_for_unread_emails tool to prior to using this tool.
    Make sure to update the dict element of the draft_id (from the create_drafts_for_unread_emails tool) changed with the new values after receiving the output from this tool.
    Args are for the new values of the draft. If the user does not specify a new value, pass an empty string or list.

    Args:
        draft_ids(str): The draft id of the draft to edit.
        new_body(str): The new body of the draft.
        new_subject(str): The new subject of the draft.
        new_to(list[str]): The new to's of the draft.
        new_cc(list[str]): The new cc of the draft.
        new_bcc(list[str]): The new bcc of the draft.
        new_reply_to(str): The new reply to of the draft.
        thread_id(str): The thread id of the draft.

    Returns:
        A dict of the draft_id with its new updated values. Use this return value to update the email dict in chat history.

    """

    g_client = GmailClient()
    
    # Call the Gmail client method
    result = g_client.edit_existing_draft(draft_ids, new_body, new_subject, new_to, new_cc, new_bcc)
    
    # Check if the operation was successful
    if result.startswith("Error editing draft"):
        return {
            'error': result,
            'draft_id': draft_ids
        }
    
    updated_draft = f"Updated draft with body: {new_body}, subject: {new_subject}, to: {new_to}, cc: {new_cc}, bcc: {new_bcc}"

    return_dict = {
        'draft': updated_draft,
        'draft_id': result
    }

    return return_dict
    

def get_calendar_events(days: int = 7) -> dict:
    """
    Get upcoming calendar events for the user. Use this tool when the user requests to see their calendar events. or if a response requires a calendar event k number of days in the future. 
    This tool is meant to help you understand the user's calendar events and schedule a calendar event if needed.
    
    Args:
        days(int): Number of days to get events for. Default is 7 days. Adjust the parameter based on the user's requests or if an email response requires a calendar event n number of days in the future.
        
    Returns:
        dict: Dictionary containing:
            success (bool): Whether the operation succeeded
            events (list): List of upcoming calendar events
    """
    calendar_client = GoogleCalendarClient()
    
    # Get upcoming events as Event objects
    events = calendar_client.get_upcoming_events_as_objects(days=days, max_results=999)
    
    # Format events for easier consumption
    formatted_events = []
    for event in events:
        formatted_event = {
            'id': event.id,
            'summary': event.summary or 'No title',
            'description': event.description,
            'start_time': event.start_time.isoformat() if event.start_time else '',
            'end_time': event.end_time.isoformat() if event.end_time else '',
            'start_date': event.start_date,
            'end_date': event.end_date,
            'is_all_day': event.is_all_day,
            'location': event.location,
            'attendees': [attendee.get('email') for attendee in event.attendees],
            'organizer': event.organizer.get('email') if event.organizer else '',
            'status': event.status,
            'html_link': event.html_link
        }
        formatted_events.append(formatted_event)
    
    return {
        'success': True,
        'events': formatted_events
    }

def set_meeting(summary: str, description: str = None, start_time: str = None, end_time: str = None, attendees: list = None, location: str = None) -> dict:
    """
    Create a new calendar meeting/event.
    
    Args:
        summary (str): Meeting title/summary
        description (str): Meeting description
        start_time (str): Start time in ISO format (e.g., "2024-01-15T10:00:00")
        end_time (str): End time in ISO format (e.g., "2024-01-15T11:00:00")
        attendees (list): List of attendee email addresses
        location (str): Meeting location
        
    Returns:
        dict: Dictionary containing:
            success (bool): Whether the operation succeeded
            event_id (str): ID of the created event
            error (str): Error message if unsuccessful
    """
    calendar_client = GoogleCalendarClient()
    
    # Parse datetime strings
    from datetime import datetime
    start_dt = None
    end_dt = None
    
    if start_time:
        start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    
    if end_time:
        end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    
    # Create the event
    event = calendar_client.create_event(
        summary=summary,
        description=description,
        start_time=start_dt,
        end_time=end_dt,
        attendees=attendees,
        location=location
    )
    
    if event:
        return {
            'success': True,
            'event_id': event.get('id'),
            'event_link': event.get('htmlLink'),
            'message': f'Meeting "{summary}" created successfully'
        }
    else:
        return {
            'success': False,
            'error': 'Failed to create meeting'
        }

def get_user_profile() -> dict:
    """ Use this tool to get the user's profile from their gmail.
    """
TOOLS = [get_unread_emails, create_drafts_for_unread_emails, send_drafts, edit_existing_draft, get_calendar_events]