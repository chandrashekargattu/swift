from typing import Optional, Dict, Any
import logging
from app.models.booking import BookingModel
from app.models.user import UserModel
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling various types of notifications"""
    
    async def send_email(self, to_email: str, subject: str, body: str):
        """Send email notification"""
        await send_email(to_email, subject, body)
    
    async def send_sms(self, to_phone: str, message: str):
        """Send SMS notification"""
        await send_sms(to_phone, message)
    
    async def send_push_notification(self, user_id: str, title: str, body: str, data: Optional[Dict[str, Any]] = None):
        """Send push notification"""
        await send_push_notification(user_id, title, body, data)
    
    async def broadcast_to_medical_team(self, data: Dict[str, Any]):
        """Broadcast to medical response team dashboard"""
        # In production, this would use WebSocket or real-time messaging
        logger.info(f"Broadcasting to medical team: {data}")
        # Example: await websocket_manager.broadcast_to_group("medical_team", data)


async def send_booking_confirmation(booking: BookingModel):
    """Send booking confirmation to user via email and SMS."""
    try:
        # Send email
        await send_email(
            to_email=booking.user_email,
            subject=f"Booking Confirmed - {booking.booking_id}",
            body=f"""
            Dear {booking.user_name},
            
            Your booking has been confirmed!
            
            Booking Details:
            - Booking ID: {booking.booking_id}
            - From: {booking.pickup_location.name}, {booking.pickup_location.city}
            - To: {booking.drop_location.name}, {booking.drop_location.city}
            - Date: {booking.pickup_datetime.strftime('%d %b %Y')}
            - Time: {booking.pickup_datetime.strftime('%I:%M %p')}
            - Cab Type: {booking.cab_type.title()}
            - Total Fare: ₹{booking.final_fare}
            
            We will assign a driver shortly and notify you.
            
            Thank you for choosing RideSwift!
            """
        )
        
        # Send SMS
        await send_sms(
            to_phone=booking.user_phone,
            message=f"Booking {booking.booking_id} confirmed! "
                   f"Pickup: {booking.pickup_datetime.strftime('%d %b, %I:%M %p')}. "
                   f"Fare: ₹{booking.final_fare}"
        )
        
    except Exception as e:
        logger.error(f"Failed to send booking confirmation: {e}")


async def send_driver_assigned_notification(booking: BookingModel):
    """Notify user when driver is assigned."""
    try:
        message = f"""
        Driver assigned for booking {booking.booking_id}!
        Driver: {booking.driver_name}
        Contact: {booking.driver_phone}
        OTP for ride start: {booking.otp}
        """
        
        await send_sms(to_phone=booking.user_phone, message=message)
        
    except Exception as e:
        logger.error(f"Failed to send driver assignment notification: {e}")


async def send_ride_started_notification(booking: BookingModel):
    """Notify user when ride starts."""
    try:
        message = f"Your ride has started! Booking ID: {booking.booking_id}. Have a safe journey!"
        await send_sms(to_phone=booking.user_phone, message=message)
        
    except Exception as e:
        logger.error(f"Failed to send ride started notification: {e}")


async def send_ride_completed_notification(booking: BookingModel):
    """Notify user when ride is completed."""
    try:
        message = f"""
        Ride completed! 
        Booking ID: {booking.booking_id}
        Total Fare: ₹{booking.final_fare}
        Please rate your experience.
        """
        await send_sms(to_phone=booking.user_phone, message=message)
        
    except Exception as e:
        logger.error(f"Failed to send ride completed notification: {e}")


async def send_email(to_email: str, subject: str, body: str):
    """Send email using SendGrid."""
    # In production, implement actual SendGrid integration
    logger.info(f"Email to {to_email}: {subject}")
    logger.info(f"Body: {body}")
    
    # Example SendGrid implementation:
    # from sendgrid import SendGridAPIClient
    # from sendgrid.helpers.mail import Mail
    # 
    # message = Mail(
    #     from_email=settings.FROM_EMAIL,
    #     to_emails=to_email,
    #     subject=subject,
    #     plain_text_content=body
    # )
    # 
    # try:
    #     sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
    #     response = sg.send(message)
    # except Exception as e:
    #     logger.error(f"SendGrid error: {e}")


async def send_sms(to_phone: str, message: str):
    """Send SMS using Twilio."""
    # In production, implement actual Twilio integration
    logger.info(f"SMS to {to_phone}: {message}")
    
    # Example Twilio implementation:
    # from twilio.rest import Client
    # 
    # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # 
    # try:
    #     message = client.messages.create(
    #         body=message,
    #         from_=settings.TWILIO_PHONE_NUMBER,
    #         to=to_phone
    #     )
    # except Exception as e:
    #     logger.error(f"Twilio error: {e}")


async def send_push_notification(user_id: str, title: str, body: str, data: Optional[dict] = None):
    """Send push notification to mobile app."""
    # In production, implement actual push notification service
    logger.info(f"Push notification to user {user_id}: {title} - {body}")
