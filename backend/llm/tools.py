from backend.google.gmail_client import GmailClient
from backend.google.emails import Email
from backend.pipelines.chat import chat_with_agent, create_chat_id
from backend.llm import init_llm
from backend.llm import prompts
from backend.google.gmail_client import GmailClient

import ast


GMAIL_CLIENT = GmailClient()

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
    if GMAIL_CLIENT.authenticate() is False:
        return "Failed to authenticate with Gmail"
    
    emails = GMAIL_CLIENT.get_unread_emails(count)
    
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

def create_drafts_for_unread_emails(email_ids: list[str]) -> dict:
    """ 
    This tool will create drafts to respond to the unread emails. Use this tool when you need to create drafts to the user's unread emails.
    This tool will also decide which emails require a response and which emails do not.
    Only use this tool if the user has unread emails.

    Args:
        email_ids(list(str)): A list of google message email ids. Use the get_unread_emails tool to get the google message email ids.
    Returns:
        A dictionary of email ids and their drafts.
    """
    emails_dict = {}
    drafts = []
    email_objs = {}


    g_client = GmailClient()
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
            'draft': ''
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

def edit_existing_draft() -> dict:
    pass

def get_calendar_events() -> dict:
    pass

def set_meeting() -> dict:
    pass



def get_user_profile() -> dict:
    """ Use this tool to get the user's profile from their gmail.
    """
TOOLS = [get_unread_emails, create_drafts_for_unread_emails, send_drafts]