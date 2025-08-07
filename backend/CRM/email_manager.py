import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

# Email configuration
RESEND_API_KEY = os.getenv("RESEND_API_KEY") or "re_1234567890abcdef"  # Replace with your real API key for testing
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "onboarding@resend.dev")  # Use Resend's sandbox domain

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_verification_email(recipient_email: str, verification_link: str) -> bool:
    """
    Sends an email using Resend with the verification link.
    """
    if not RESEND_API_KEY or RESEND_API_KEY == "re_1234567890abcdef":
        logger.warning("Using test API key - emails will not be sent")
        logger.info(f"Verification link for {recipient_email}: {verification_link}")
        return False  # Return False to indicate email was not sent

    message_data = {
        "from": f"Account Verification <{SENDER_EMAIL}>",
        "to": [recipient_email],
        "subject": "Verify Your Account",
        "html": f"""
        <html>
        <body>
            <h1>Verify Your Account</h1>
            <p>Thank you for registering!</p>
            <p>Click <a href="{verification_link}">here</a> to verify your account.</p>
            <p>If you did not register, please ignore this email.</p>
        </body>
        </html>
        """
    }

    logger.info("Sending verification email to %s", recipient_email)
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=message_data
    )
    logger.info("Resend returned status %s: %s", response.status_code, response.text)

    if response.status_code != 200:
        logger.error("Failed to send verification email: %s", response.text)
        raise Exception(f"Failed to send email: {response.text}")

    return True

def send_password_reset_email(recipient_email: str, reset_token: str) -> bool:
    """
    Sends an email with password reset instructions using Resend.
    """
    if not RESEND_API_KEY or RESEND_API_KEY == "re_1234567890abcdef":
        logger.warning("Using test API key - emails will not be sent")
        logger.info(f"Password reset token for {recipient_email}: {reset_token}")
        return False  # Return False to indicate email was not sent

    # Create a reset link that includes the token
    reset_link = f"http://localhost:5173/reset-password?token={reset_token}"

    message_data = {
        "from": f"Password Reset <{SENDER_EMAIL}>",
        "to": [recipient_email],
        "subject": "Reset Your Password",
        "html": f"""
        <html>
        <body>
            <h1>Reset Your Password</h1>
            <p>You requested a password reset.</p>
            <p>Your password reset token is: <strong>{reset_token}</strong></p>
            <p>Click <a href="{reset_link}">here</a> to reset your password.</p>
            <p>If you did not request this reset, please ignore this email.</p>
        </body>
        </html>
        """
    }

    logger.info("Sending password reset email to %s", recipient_email)
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=message_data
    )
    logger.info("Resend returned status %s: %s", response.status_code, response.text)

    if response.status_code != 200:
        logger.error("Failed to send password reset email: %s", response.text)
        raise Exception(f"Failed to send email: {response.text}")

    return True

def send_welcome_email(recipient_email: str, username: str) -> bool:
    """
    Sends a welcome email using Resend.
    """
    if not RESEND_API_KEY or RESEND_API_KEY == "re_1234567890abcdef":
        logger.warning("Using test API key - emails will not be sent")
        logger.info(f"Welcome email for {recipient_email} (username: {username})")
        return False  # Return False to indicate email was not sent

    message_data = {
        "from": f"Welcome <{SENDER_EMAIL}>",
        "to": [recipient_email],
        "subject": "Welcome to Your Application",
        "html": f"""
        <html>
        <body>
            <h1>Welcome to Your Application!</h1>
            <p>Hello {username},</p>
            <p>Thank you for creating an account with us.</p>
            <p>You can now log in and start using our services.</p>
            <p>Best regards,<br>Your Application Team</p>
        </body>
        </html>
        """
    }

    logger.info("Sending welcome email to %s", recipient_email)
    response = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        },
        json=message_data
    )
    logger.info("Resend returned status %s: %s", response.status_code, response.text)

    if response.status_code != 200:
        logger.error("Failed to send welcome email: %s", response.text)
        raise Exception(f"Failed to send email: {response.text}")

    return True 