"""SMS tasks for Celery."""
import logging
from typing import Dict, List, Optional
from datetime import datetime

from celery import Task
from app.core.celery_app import celery_app
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)


class SMSTask(Task):
    """Base SMS task with retry logic."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 300  # 5 minutes
    retry_jitter = True


@celery_app.task(base=SMSTask, name="send_sms")
def send_sms(
    phone_number: str,
    message: str,
    sender_id: Optional[str] = None
) -> Dict[str, any]:
    """
    Send SMS asynchronously.
    
    Args:
        phone_number: Recipient phone number
        message: SMS message content
        sender_id: Optional sender ID
        
    Returns:
        Dict with status and message
    """
    try:
        logger.info(f"Sending SMS to {phone_number}")
        
        # Get notification service
        notification_service = NotificationService()
        
        # Send SMS
        result = notification_service.send_sms(
            phone_number=phone_number,
            message=message
        )
        
        if result:
            logger.info(f"SMS sent successfully to {phone_number}")
            return {
                "status": "success",
                "message": "SMS sent successfully",
                "phone_number": phone_number,
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Failed to send SMS to {phone_number}")
            return {
                "status": "failed",
                "message": "Failed to send SMS",
                "phone_number": phone_number,
                "timestamp": datetime.utcnow().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error sending SMS to {phone_number}: {e}")
        raise


@celery_app.task(base=SMSTask, name="send_otp_sms")
def send_otp_sms(phone_number: str, otp_code: str) -> Dict[str, any]:
    """
    Send OTP SMS.
    
    Args:
        phone_number: Recipient phone number
        otp_code: OTP code
        
    Returns:
        Dict with status and message
    """
    message = f"Your RideSwift verification code is: {otp_code}. Valid for 10 minutes."
    
    return send_sms.delay(
        phone_number=phone_number,
        message=message
    ).get()


@celery_app.task(base=SMSTask, name="send_booking_sms")
def send_booking_sms(
    phone_number: str,
    booking_id: str,
    pickup_time: str,
    driver_name: Optional[str] = None,
    driver_phone: Optional[str] = None
) -> Dict[str, any]:
    """
    Send booking confirmation SMS.
    
    Args:
        phone_number: Recipient phone number
        booking_id: Booking ID
        pickup_time: Pickup time
        driver_name: Driver name (optional)
        driver_phone: Driver phone (optional)
        
    Returns:
        Dict with status and message
    """
    if driver_name and driver_phone:
        message = (
            f"Booking {booking_id} confirmed! "
            f"Pickup: {pickup_time}. "
            f"Driver: {driver_name} ({driver_phone})"
        )
    else:
        message = (
            f"Booking {booking_id} confirmed! "
            f"Pickup: {pickup_time}. "
            f"Driver details will be shared soon."
        )
    
    return send_sms.delay(
        phone_number=phone_number,
        message=message
    ).get()


@celery_app.task(base=SMSTask, name="send_driver_arrival_sms")
def send_driver_arrival_sms(
    phone_number: str,
    driver_name: str,
    vehicle_number: str,
    otp_code: str
) -> Dict[str, any]:
    """
    Send driver arrival SMS.
    
    Args:
        phone_number: Recipient phone number
        driver_name: Driver name
        vehicle_number: Vehicle registration number
        otp_code: Trip OTP code
        
    Returns:
        Dict with status and message
    """
    message = (
        f"Your driver {driver_name} has arrived! "
        f"Vehicle: {vehicle_number}. "
        f"Share OTP {otp_code} to start trip."
    )
    
    return send_sms.delay(
        phone_number=phone_number,
        message=message
    ).get()


@celery_app.task(base=SMSTask, name="send_trip_completed_sms")
def send_trip_completed_sms(
    phone_number: str,
    booking_id: str,
    fare_amount: float,
    payment_method: str
) -> Dict[str, any]:
    """
    Send trip completion SMS.
    
    Args:
        phone_number: Recipient phone number
        booking_id: Booking ID
        fare_amount: Total fare amount
        payment_method: Payment method used
        
    Returns:
        Dict with status and message
    """
    message = (
        f"Trip completed! "
        f"Booking: {booking_id}. "
        f"Fare: ₹{fare_amount:,.2f} "
        f"({payment_method}). "
        f"Thank you for choosing RideSwift!"
    )
    
    return send_sms.delay(
        phone_number=phone_number,
        message=message
    ).get()


@celery_app.task(base=SMSTask, name="send_cancellation_sms")
def send_cancellation_sms(
    phone_number: str,
    booking_id: str,
    cancellation_charge: Optional[float] = None
) -> Dict[str, any]:
    """
    Send booking cancellation SMS.
    
    Args:
        phone_number: Recipient phone number
        booking_id: Booking ID
        cancellation_charge: Cancellation charge if applicable
        
    Returns:
        Dict with status and message
    """
    if cancellation_charge:
        message = (
            f"Booking {booking_id} cancelled. "
            f"Cancellation charge: ₹{cancellation_charge:,.2f} "
            f"will be deducted."
        )
    else:
        message = f"Booking {booking_id} cancelled successfully."
    
    return send_sms.delay(
        phone_number=phone_number,
        message=message
    ).get()


@celery_app.task(name="send_bulk_sms")
def send_bulk_sms(
    phone_numbers: List[str],
    message: str,
    batch_size: int = 100
) -> Dict[str, any]:
    """
    Send bulk SMS in batches.
    
    Args:
        phone_numbers: List of phone numbers
        message: SMS message
        batch_size: Number of SMS per batch
        
    Returns:
        Dict with status and statistics
    """
    total = len(phone_numbers)
    sent = 0
    failed = 0
    
    for i in range(0, total, batch_size):
        batch = phone_numbers[i:i + batch_size]
        
        for phone_number in batch:
            try:
                send_sms.delay(
                    phone_number=phone_number,
                    message=message
                )
                sent += 1
                
            except Exception as e:
                logger.error(f"Failed to send SMS to {phone_number}: {e}")
                failed += 1
    
    return {
        "status": "completed",
        "total": total,
        "sent": sent,
        "failed": failed,
        "timestamp": datetime.utcnow().isoformat()
    }
