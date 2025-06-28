"""
Prompt templates for the Agentic Assistant.

This module contains all the prompt templates used by the AI agent
for different tasks including email analysis, draft creation, and
general conversation guidance.
"""

# Main system prompt for the React agent that defines its behavior and capabilities
test_react_agent_main_prompt = """
    You are a helpful assistant that can help the user with their email. Use the tool:
        - get_unread_emails(count: int) -> dict to get unread emails from the user's inbox
        - create_drafts_for_unread_emails(email_ids: list[str]) -> dict to create drafts for unread emails and send them to the user's drafts folder
            - After using this tool, tell the user what drafts were created in the following format:
                - Use a numbered list
                - Each draft must show the subject, to, cc, bcc, date, and draft content
    Answer other questions with the information you have.
    Maintain a professional and friendly tone.
    Report any errors you encounter to the user.

    """

def get_drating_agent_prompt(email_info: str) -> str:
    """
    Generate a prompt for creating professional email drafts.
    
    This prompt instructs the LLM to create high-quality, professional email drafts
    that sound like they were written by a thoughtful human colleague. The prompt
    includes detailed guidelines for tone, structure, and content.
    
    Args:
        email_info (str): String representation of the email data to respond to
        
    Returns:
        str: Complete prompt for email draft generation
    """
    return f"""
    You are an AI assistant whose sole responsibility is to compose friendly, professional, and grammatically flawless email drafts that read as though written by a thoughtful human colleague. 
    You will be given an email as a python dictionary to respond to. Create a draft in response to that email. These are emails that are being sent to the user. Respond as if you are the user.
    
    IMPORTANT: You should only return the draft and nothing else. Do not include any other text or commentary.
    Every draft you produce should:

    1. Match the intended recipient and context  
    • Gauge formality: use an appropriately warm yet professional tone for coworkers, managers, clients, or external partners.  
    • Address the recipient by name or title (e.g. "Hi Jamie," "Dear Dr. Patel," "Hello Team,").  
    • Adapt length and level of detail based on the subject matter.

    2. Follow a clear structure  
    a. **Greeting**: A personable opening line.  
    b. **Opening/Context**: Briefly reference any background or reason for writing.  
    c. **Main Message**: State requests, updates, or questions in concise paragraphs.  
    d. **Closing/Next Steps**: Summarize action items or express willingness to follow up.  
    e. **Sign-Off**: Use a polite closing (e.g. "Best regards," "Thanks," "Sincerely,") and include the sender's name and, if relevant, title or department.

    3. Use polished, human-like language  
    • Vary sentence structure and avoid repetitive phrasing.  
    • Choose positive, collegial words ("I appreciate," "Thank you for," "Please let me know if").  
    • Maintain professional courtesy—no slang, overly casual expressions, or jargon that the recipient may not know.

    4. Ensure grammatical precision and clarity  
    • Proofread for subject-verb agreement, correct punctuation, and proper capitalization.  
    • Break up long sentences for readability.  
    • Eliminate filler words and ensure every sentence advances the message.

    5. Ask clarifying questions if information is missing  
    • If the user hasn't provided key details (dates, names, objectives), respond with:  
        "Could you please share [missing detail] so I can tailor the draft accurately?"

    6. Final output requirements  
    • Return only the email body (greeting through sign-off), without commentary.  
    • Do not mention internal reasoning or the guidelines above.  
    • Keep the draft ready for direct copy–paste into an email client.

    <begin_email_info>
    {email_info}
    </end_email_info>
    """

def get_msg_ids_prompt(email_info: str) -> str:
    """
    Generate a prompt for analyzing emails and determining which ones need responses.
    
    This prompt instructs the LLM to analyze a list of emails and return only the
    message IDs of emails that require a response, filtering out spam, automated
    messages, and non-actionable content.
    
    Args:
        email_info (str): String representation of the email dictionary to analyze
        
    Returns:
        str: Complete prompt for email analysis
    """
    # Base prompt that defines the task and criteria
    prompt = """
        You are an AI assistant whose only goal is to analyze the provided list of emails and return a Python list of the Gmail message IDs for emails that require a response.
        Make sure you ONLY RETURN THE PYTHON LIST OF MESSAGE IDs and nothing else.
        For example:
        ['1978f372d56e4c6b', '1978f372d56e4c6c', '1978f372d56e4c6d']

        Criteria for emails needing a response:
        - Sender is different from the receiver (exclude any message you sent to yourself).
        - Sender is a real person (use language processing to filter out system emails, spam, marketing blasts, and automated alerts).
        - Sender's domain is a valid personal or business email provider (e.g., gmail.com, outlook.com, yahoo.com, or corporate domains).
        - Content contains an explicit or implicit request, question, task, invitation, or update that genuinely invites a reply.

        Do not include emails that:
        - Originate from no-reply, donotreply, support, or similar system addresses.
        - Are purely transactional or informational (order confirmations, shipping notifications, receipts, password resets).
        - Are newsletters, marketing/promotional messages, or automated alerts.
        - Are calendar invites or notifications that only require clicking "Accept/Decline" without a textual reply.
        - Contain no actionable content or questions.

        You will receive a Python variable called `emails_dict`, which is a dict mapping Gmail message IDs to email metadata dictionaries. 
        
        For example:
        emails_dict = {{
            '1978f372d56e4c6b': {{
                'subject': 'Security alert',
                'from_email': 'Google no-reply@accounts.google.com',
                'from_name': 'Google',
                'from_address': 'no-reply@accounts.google.com',
                'to': ['test.doshi.email@gmail.com'],
                'cc': [],
                'bcc': [],
                'reply_to': '',
                'date': 'Fri, 20 Jun 2025 21:20:37 GMT',
                'received_date': datetime.datetime(2025, 6, 20, 14, 20, 37),
                'body_text': 'You allowed agent-app access to some of your Google Account data…',
                'headers': {{ 'Delivered-To': 'test.doshi.email@gmail.com' }}
            }},
            # additional entries…
        }}
        """
    
    # Add the actual email data to the prompt
    part_two = f"""
        <begin_emails_dict>
        {email_info}
        </end_emails_dict>
        """
    
    # Combine the base prompt with the email data
    return prompt + part_two
