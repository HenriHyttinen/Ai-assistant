from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from typing import List
import os
from dotenv import load_dotenv
from pathlib import Path
import jinja2
import aiofiles

load_dotenv()

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER", "smtp.gmail.com"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'email_templates'
)

# Initialize Jinja2 template environment
template_loader = jinja2.FileSystemLoader(searchpath=str(conf.TEMPLATE_FOLDER))
template_env = jinja2.Environment(loader=template_loader)

async def send_verification_email(email: str, token: str) -> None:
    """Send email verification link."""
    template = template_env.get_template('verification.html')
    verification_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
    
    html_content = template.render(
        verification_url=verification_url,
        app_name="Numbers Don't Lie"
    )
    
    message = MessageSchema(
        subject="Verify your email address",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset link."""
    template = template_env.get_template('password_reset.html')
    reset_url = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
    
    html_content = template.render(
        reset_url=reset_url,
        app_name="Numbers Don't Lie"
    )
    
    message = MessageSchema(
        subject="Reset your password",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_weekly_summary_email(email: str, summary_data: dict) -> None:
    """Send weekly health summary email."""
    template = template_env.get_template('weekly_summary.html')
    
    html_content = template.render(
        summary=summary_data,
        app_name="Numbers Don't Lie"
    )
    
    message = MessageSchema(
        subject="Your Weekly Health Summary",
        recipients=[email],
        body=html_content,
        subtype="html"
    )
    
    fm = FastMail(conf)
    await fm.send_message(message) 