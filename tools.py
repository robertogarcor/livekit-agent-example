import os
import smtplib
import logging
import requests
from livekit.agents import function_tool, RunContext
from langchain_community.tools import DuckDuckGoSearchRun
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
from datetime import datetime

from skills import get_skill_content, list_available_skills

@function_tool()
async def get_time(
    context: RunContext,  # type: ignore
    ) -> str:
    """Get current time."""
    try:
        now = datetime.now()
        return f"Hora actual: {now.strftime('%H:%M:%S')}\nFecha: {now.strftime('%Y-%m-%d')}"
    except Exception as e:
        logging.error(f"Error retrieving time: {e}")
        return f"An error occurred while retrieving time."


@function_tool()
async def get_weather(
    context: RunContext,  # type: ignore
    city: str) -> str:
    """
    Get the current weather for a given city.
    """
    try:
        response = requests.get(
            f"https://wttr.in/{city}?format=3")
        if response.status_code == 200:
            logging.info(f"Weather for {city}: {response.text.strip()}")
            return response.text.strip()   
        else:
            logging.error(f"Failed to get weather for {city}: {response.status_code}")
            return f"Could not retrieve weather for {city}."
    except Exception as e:
        logging.error(f"Error retrieving weather for {city}: {e}")
        return f"An error occurred while retrieving weather for {city}." 

@function_tool()
async def search_web(
    context: RunContext,  # type: ignore
    query: str) -> str:
    """
    Search the web using DuckDuckGo.
    """
    try:
        results = DuckDuckGoSearchRun().run(tool_input=query)
        logging.info(f"Search results for '{query}': {results}")
        return results
    except Exception as e:
        logging.error(f"Error searching the web for '{query}': {e}")
        return f"An error occurred while searching the web for '{query}'."    

@function_tool()    
async def send_email(
    context: RunContext,  # type: ignore
    to_email: str,
    subject: str,
    message: str,
    cc_email: Optional[str] = None
) -> str:
    """
    Send an email through Gmail.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        message: Email body content
        cc_email: Optional CC email address
    """
    try:
        # Gmail SMTP configuration
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        
        # Get credentials from environment variables
        gmail_user = os.getenv("GMAIL_USER")
        gmail_password = os.getenv("GMAIL_APP_PASSWORD")  # Use App Password, not regular password
        
        if not gmail_user or not gmail_password:
            logging.error("Gmail credentials not found in environment variables")
            return "Email sending failed: Gmail credentials not configured."
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add CC if provided
        recipients = [to_email]
        if cc_email:
            msg['Cc'] = cc_email
            recipients.append(cc_email)
        
        # Attach message body
        msg.attach(MIMEText(message, 'plain'))
        
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(gmail_user, gmail_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(gmail_user, recipients, text)
        server.quit()
        
        logging.info(f"Email sent successfully to {to_email}")
        return f"Email sent successfully to {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"


@function_tool()
async def list_skills(
    context: RunContext,  # type: ignore
) -> str:
    """
    List the names of all local skills available to load.

    Use this only if you are unsure of the exact skill name. Normally
    the available skills are already listed in your system prompt and
    you can call get_skill(name) directly.
    """
    names = list_available_skills()
    if not names:
        return "No hay skills locales disponibles."
    return "Skills disponibles: " + ", ".join(names)


@function_tool()
async def get_skill(
    context: RunContext,  # type: ignore
    skill_name: str,
) -> str:
    """
    Load the full content of a local skill by name.

    Use this when the user's question matches one of the skills listed
    in your system prompt (for example 'app-estadas'). The function
    returns the SKILL.md text so you can answer based on it.

    Args:
        skill_name: The exact name of the skill to load.
    """
    content = get_skill_content(skill_name)
    if content is None:
        return f"Skill '{skill_name}' no encontrada."
    return content
