from backend.google.gmail_client import GmailClient

TOOLS = []
GMAIL_CLIENT = GmailClient()

def get_unread_emails(count: int = k):
    """ This tool will get the unread emails from the user's inbox. 
        Args:
            count: The number of emails to get. The user must specify this parameter. If the user does not, ask the user to specify before using this tool.
        Returns:
            A list of emails.
    """
    if GMAIL_CLIENT.authenticate() is False:
        return "Failed to authenticate with Gmail"
    
    


def create_drafts_for_unread_emails(emails: list[str], body: str):
    """ This tool will create drafts to respond to the unread emails.
        Args:
            subject: The subject of the email.
            body: The body of the email.
        Returns:
            A list of emails.
    """
    pass