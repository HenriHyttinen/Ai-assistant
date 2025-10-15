from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List, Optional
import os
from dotenv import load_dotenv
from pathlib import Path
import jinja2
import aiofiles
import json

load_dotenv()

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "your-email@example.com"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "your-password"),
    MAIL_FROM=os.getenv("MAIL_FROM", "your-email@example.com"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME", "Numbers Don't Lie"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / 'templates'
)

# Initialize FastMail
fastmail = FastMail(conf)

# Initialize Jinja2
template_loader = jinja2.FileSystemLoader(searchpath=str(conf.TEMPLATE_FOLDER))
template_env = jinja2.Environment(loader=template_loader)

async def send_email(
    email_to: str,
    subject: str,
    template_name: str,
    template_data: dict
) -> None:
    """Send an email using a template."""
    try:
        # Load and render template
        template = template_env.get_template(f"{template_name}.html")
        html_content = template.render(**template_data)
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=html_content,
            subtype="html"
        )
        
        # Send email
        await fastmail.send_message(message)
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

async def send_verification_email(email: str, token: str) -> None:
    """Send email verification link."""
    verification_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/verify-email?token={token}"
    
    # For development: always show the verification link
    print(f"\n{'='*60}")
    print(f"📧 EMAIL VERIFICATION REQUIRED")
    print(f"{'='*60}")
    print(f"To: {email}")
    print(f"Subject: Verify your email address")
    print(f"Verification URL: {verification_url}")
    print(f"{'='*60}")
    print(f"Click the link above to verify your email address.")
    print(f"{'='*60}\n")
    
    # Try to send real email, but don't fail if it doesn't work
    try:
        await send_email(
            email_to=email,
            subject="Verify your email address",
            template_name="verification_email",
            template_data={
                "verification_url": verification_url,
                "app_name": "Numbers Don't Lie"
            }
        )
        print(f"✅ Verification email sent to {email}")
    except Exception as e:
        print(f"⚠️  Could not send email to {email}: {str(e)}")
        print(f"📋 Use the verification URL above to complete registration")
        # Don't raise the exception - let the system continue

async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset link."""
    reset_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:5173')}/reset-password?token={token}"
    
    # For development: always show the reset link
    print(f"\n{'='*60}")
    print(f"🔗 PASSWORD RESET REQUIRED")
    print(f"{'='*60}")
    print(f"To: {email}")
    print(f"Subject: Reset your password")
    print(f"Reset URL: {reset_url}")
    print(f"{'='*60}")
    print(f"Click the link above to reset your password.")
    print(f"{'='*60}\n")
    
    # Try to send real email, but don't fail if it doesn't work
    try:
        await send_email(
            email_to=email,
            subject="Reset your password",
            template_name="password_reset_email",
            template_data={
                "reset_url": reset_url,
                "app_name": "Numbers Don't Lie"
            }
        )
        print(f"✅ Password reset email sent to {email}")
    except Exception as e:
        print(f"⚠️  Could not send email to {email}: {str(e)}")
        print(f"📋 Use the reset URL above to complete password reset")
        # Don't raise the exception - let the system continue

async def send_2fa_setup_email(email: str, qr_code: str) -> None:
    """Send 2FA setup instructions."""
    await send_email(
        email_to=email,
        subject="Set up two-factor authentication",
        template_name="2fa_setup_email",
        template_data={
            "qr_code": qr_code,
            "app_name": "Numbers Don't Lie"
        }
    )

async def send_health_report_email(email: str, report_data: dict) -> None:
    """Send health report email."""
    await send_email(
        email_to=email,
        subject="Your Health Report",
        template_name="health_report_email",
        template_data={
            "report": report_data,
            "app_name": "Numbers Don't Lie"
        }
    )

async def send_goal_achievement_email(email: str, goal_data: dict) -> None:
    """Send goal achievement notification."""
    await send_email(
        email_to=email,
        subject="Goal Achieved! 🎉",
        template_name="goal_achievement_email",
        template_data={
            "goal": goal_data,
            "app_name": "Numbers Don't Lie"
        }
    )

async def send_weekly_summary_email(email: str, summary_data: dict) -> None:
    """Send weekly activity summary."""
    await send_email(
        email_to=email,
        subject="Your Weekly Health Summary",
        template_name="weekly_summary_email",
        template_data={
            "summary": summary_data,
            "app_name": "Numbers Don't Lie"
        }
    ) 