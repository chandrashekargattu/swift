"""Email tasks for Celery."""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from celery import Task
from app.core.celery_app import celery_app
from app.services.notification import NotificationService
from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailTask(Task):
    """Base email task with retry logic."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True


@celery_app.task(base=EmailTask, name="send_email")
def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Send email asynchronously.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content
        plain_content: Plain text content (optional)
        attachments: List of attachments
        
    Returns:
        Dict with status and message
    """
    try:
        logger.info(f"Sending email to {to_email} with subject: {subject}")
        
        # Get notification service
        notification_service = NotificationService()
        
        # Prepare email data
        email_data = {
            "to": to_email,
            "subject": subject,
            "html_content": html_content,
            "plain_content": plain_content or html_content,
            "from_email": settings.SENDGRID_FROM_EMAIL,
            "from_name": settings.PROJECT_NAME,
        }
        
        # Add attachments if provided
        if attachments:
            email_data["attachments"] = attachments
        
        # Send email
        result = notification_service.send_email(**email_data)
        
        if result:
            logger.info(f"Email sent successfully to {to_email}")
            return {
                "status": "success",
                "message": "Email sent successfully",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Failed to send email to {to_email}")
            return {
                "status": "failed",
                "message": "Failed to send email",
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error sending email to {to_email}: {e}")
        raise


@celery_app.task(base=EmailTask, name="send_welcome_email")
def send_welcome_email(user_id: str, user_email: str, user_name: str) -> Dict[str, Any]:
    """
    Send welcome email to new user.
    
    Args:
        user_id: User ID
        user_email: User email
        user_name: User name
        
    Returns:
        Dict with status and message
    """
    subject = f"Welcome to {settings.PROJECT_NAME}!"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb;">Welcome to {settings.PROJECT_NAME}, {user_name}!</h1>
                
                <p>Thank you for joining our premium interstate cab booking service.</p>
                
                <h2 style="color: #1e40af;">Get Started</h2>
                <ul>
                    <li>Book your first ride and get 10% off</li>
                    <li>Explore our fleet of comfortable vehicles</li>
                    <li>Enjoy 24/7 customer support</li>
                </ul>
                
                <div style="margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/bookings" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Book Your First Ride
                    </a>
                </div>
                
                <p>If you have any questions, feel free to contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    This email was sent to {user_email}. If you didn't sign up for {settings.PROJECT_NAME}, 
                    please ignore this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    plain_content = f"""
    Welcome to {settings.PROJECT_NAME}, {user_name}!
    
    Thank you for joining our premium interstate cab booking service.
    
    Get Started:
    - Book your first ride and get 10% off
    - Explore our fleet of comfortable vehicles
    - Enjoy 24/7 customer support
    
    Book your first ride at: {settings.FRONTEND_URL}/bookings
    
    If you have any questions, feel free to contact our support team.
    
    This email was sent to {user_email}. If you didn't sign up for {settings.PROJECT_NAME}, 
    please ignore this email.
    """
    
    return send_email.delay(
        to_email=user_email,
        subject=subject,
        html_content=html_content,
        plain_content=plain_content
    ).get()


@celery_app.task(base=EmailTask, name="send_booking_confirmation")
def send_booking_confirmation(
    booking_id: str,
    user_email: str,
    user_name: str,
    booking_details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Send booking confirmation email.
    
    Args:
        booking_id: Booking ID
        user_email: User email
        user_name: User name
        booking_details: Booking details
        
    Returns:
        Dict with status and message
    """
    subject = f"Booking Confirmed - {booking_id}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb;">Booking Confirmed!</h1>
                
                <p>Dear {user_name},</p>
                
                <p>Your booking has been confirmed. Here are the details:</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Booking Details</h3>
                    <table style="width: 100%;">
                        <tr>
                            <td><strong>Booking ID:</strong></td>
                            <td>{booking_id}</td>
                        </tr>
                        <tr>
                            <td><strong>Pickup:</strong></td>
                            <td>{booking_details.get('pickup_location', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Drop-off:</strong></td>
                            <td>{booking_details.get('dropoff_location', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Date & Time:</strong></td>
                            <td>{booking_details.get('pickup_datetime', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Vehicle Type:</strong></td>
                            <td>{booking_details.get('cab_type', 'N/A')}</td>
                        </tr>
                        <tr>
                            <td><strong>Total Fare:</strong></td>
                            <td>₹{booking_details.get('estimated_fare', 0):,.2f}</td>
                        </tr>
                    </table>
                </div>
                
                <p><strong>Important:</strong> Your driver will contact you 30 minutes before pickup.</p>
                
                <div style="margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/bookings/{booking_id}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Booking Details
                    </a>
                </div>
                
                <p>For any changes or cancellations, please visit your bookings page or contact support.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    This is an automated email. Please do not reply to this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email.delay(
        to_email=user_email,
        subject=subject,
        html_content=html_content
    ).get()


@celery_app.task(base=EmailTask, name="send_password_reset")
def send_password_reset(
    user_email: str,
    user_name: str,
    reset_token: str
) -> Dict[str, Any]:
    """
    Send password reset email.
    
    Args:
        user_email: User email
        user_name: User name
        reset_token: Password reset token
        
    Returns:
        Dict with status and message
    """
    subject = "Password Reset Request"
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2563eb;">Password Reset Request</h1>
                
                <p>Hi {user_name},</p>
                
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <div style="margin: 30px 0;">
                    <a href="{reset_link}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 6px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #2563eb;">{reset_link}</p>
                
                <p><strong>This link will expire in 1 hour.</strong></p>
                
                <p>If you didn't request a password reset, please ignore this email. 
                   Your password won't be changed.</p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #6b7280;">
                    This is an automated email. Please do not reply to this email.
                </p>
            </div>
        </body>
    </html>
    """
    
    return send_email.delay(
        to_email=user_email,
        subject=subject,
        html_content=html_content
    ).get()


@celery_app.task(name="send_bulk_emails")
def send_bulk_emails(
    email_list: List[Dict[str, str]],
    subject: str,
    template: str,
    batch_size: int = 100
) -> Dict[str, Any]:
    """
    Send bulk emails in batches.
    
    Args:
        email_list: List of dicts with 'email' and 'name' keys
        subject: Email subject
        template: Email template with placeholders
        batch_size: Number of emails per batch
        
    Returns:
        Dict with status and statistics
    """
    total = len(email_list)
    sent = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = email_list[i:i + batch_size]
        
        for recipient in batch:
            try:
                # Replace placeholders in template
                html_content = template.replace("{name}", recipient.get("name", "User"))
                html_content = html_content.replace("{email}", recipient["email"])
                
                send_email.delay(
                    to_email=recipient["email"],
                    subject=subject,
                    html_content=html_content
                )
                sent += 1
                
            except Exception as e:
                logger.error(f"Failed to send email to {recipient['email']}: {e}")
                failed += 1
    
    return {
        "status": "completed",
        "total": total,
        "sent": sent,
        "failed": failed,
        "timestamp": datetime.utcnow().isoformat()
    }
