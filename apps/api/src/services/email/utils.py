from pydantic import EmailStr
from config.config import get_learnhouse_config
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

# Optional import for Resend - only needed if using Resend provider
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend module not available. SMTP will be used as default.")


def send_email_smtp(to: EmailStr, subject: str, body: str, config) -> bool:
    """
    Send an email using SMTP.
    Returns True if sent successfully, False otherwise.
    """
    try:
        if not config.smtp_host or not config.system_email_address:
            logger.warning("SMTP configuration is missing. Cannot send email.")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"LearnHouse <{config.system_email_address}>"
        msg['To'] = to
        
        # Add HTML body
        html_part = MIMEText(body, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server
        if config.smtp_use_tls:
            server = smtplib.SMTP(config.smtp_host, config.smtp_port or 587)
            server.starttls()
        else:
            server = smtplib.SMTP(config.smtp_host, config.smtp_port or 25)
        
        # Authenticate if credentials are provided
        if config.smtp_username and config.smtp_password:
            server.login(config.smtp_username, config.smtp_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent successfully to {to} via SMTP")
        return True
    except Exception as e:
        logger.warning(f"Failed to send email to {to} via SMTP: {str(e)}")
        return False


def send_email_resend(to: EmailStr, subject: str, body: str, config) -> bool:
    """
    Send an email using Resend API.
    Returns True if sent successfully, False otherwise.
    """
    if not RESEND_AVAILABLE:
        logger.error("Resend module is not installed. Cannot send email via Resend.")
        return False
    
    try:
        if not config.resend_api_key or not config.system_email_address:
            logger.warning("Resend API key or system email address is missing.")
            return False
        
        params = {
            "from": f"LearnHouse <{config.system_email_address}>",
            "to": [to],
            "subject": subject,
            "html": body,
        }

        resend.api_key = config.resend_api_key
        email = resend.Emails.send(params)
        logger.info(f"Email sent successfully to {to} via Resend")
        return True
    except Exception as e:
        logger.warning(f"Failed to send email to {to} via Resend: {str(e)}")
        return False


def send_email(to: EmailStr, subject: str, body: str):
    """
    Send an email using the configured email provider (SMTP or Resend).
    Returns a truthy value if sent successfully, None otherwise.
    This allows the application to continue functioning even if email is not configured.
    """
    try:
        lh_config = get_learnhouse_config()
        mailing_config = lh_config.mailing_config
        
        # Check if email is configured at all
        if not mailing_config.system_email_address:
            logger.warning("System email address is not configured. Skipping email send.")
            return None
        
        # Route to appropriate email provider
        if mailing_config.email_provider == "smtp":
            result = send_email_smtp(to, subject, body, mailing_config)
            return result if result else None
        elif mailing_config.email_provider == "resend":
            result = send_email_resend(to, subject, body, mailing_config)
            return result if result else None
        else:
            logger.warning(f"Unknown email provider: {mailing_config.email_provider}. Skipping email send.")
            return None
    except Exception as e:
        # Log the error but don't raise it - allow the application to continue
        logger.warning(f"Failed to send email to {to}: {str(e)}")
        return None
        
