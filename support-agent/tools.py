import logging
from livekit.agents import function_tool, RunContext, get_job_context, ToolError
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText
from typing import Optional
from pathlib import Path
import asyncio

@function_tool()
async def unblock_user(context: RunContext, username: str) -> str:
    """
    Unblock users so they can log in again.
    """
    try:
        # Get path to blockusers.txt
        THIS_DIR = Path(__file__).parent
        block_file = THIS_DIR / "generic_corporate_app" / "public" / "blockusers.txt"
        
        if not block_file.exists():
            logging.error(f"Block file not found at {block_file}")
            return "Unblock failed: blockusers.txt file not found"
            
        # Clear the file contents
        block_file.write_text("")
        
        logging.info("Successfully cleared blockusers.txt")
        
        room = get_job_context().room
        participant_identity = next(iter(room.remote_participants))
        
        try:
            # Add 3 second delay
            await asyncio.sleep(3)
            response = await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method="client.showNotification",
                payload=json.dumps({
                    "type": "unblock_user",
                    "username": username
                }),
                response_timeout=30.0  # Increased timeout to 30 seconds
            )
            logging.info(f"unblock_user response: {response}")
            return f"User {username} has been unblocked successfully and the response is: {response}"
        except Exception as rpc_error:
            logging.error(f"RPC error: {rpc_error}")
            # Still return success if file was cleared but RPC failed
            return f"User {username} has been unblocked, but notification failed: {str(rpc_error)}"
 
    except Exception as e:
        logging.error(f"Error clearing block file: {e}")
        raise ToolError("Unable to use tool unblock_user at this time.")

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

        room = get_job_context().room
        participant_identity = next(iter(room.remote_participants))

        try:
            # Add 3 second delay
            await asyncio.sleep(3)
            response = await room.local_participant.perform_rpc(
                destination_identity=participant_identity,
                method="client.showNotification",
                payload=json.dumps({
                    "type": "send_email",
                    "email_address": to_email
                }),
                response_timeout=30.0  # Increased timeout to 30 seconds
            )
            logging.info(f"unblock_user response: {response}")
            return f"The email sent and the notification has been shown as well with response: {response}"
        except Exception as rpc_error:
            logging.error(f"RPC error: {rpc_error}")
            # Still return success if file was cleared but RPC failed
            return f"The notification to client was unsuccessful: {str(rpc_error)}"
        
    except smtplib.SMTPAuthenticationError:
        logging.error("Gmail authentication failed")
        return "Email sending failed: Authentication error. Please check your Gmail credentials."
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return f"Email sending failed: SMTP error - {str(e)}"
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        return f"An error occurred while sending email: {str(e)}"
