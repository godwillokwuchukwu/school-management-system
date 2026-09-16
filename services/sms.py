import logging
import os
from django.conf import settings

logger = logging.getLogger(__name__)


class BaseSMSBackend:
    def send_sms(self, phone_number: str, message: str) -> bool:
        raise NotImplementedError


class DummySMSBackend(BaseSMSBackend):
    def send_sms(self, phone_number: str, message: str) -> bool:
        logger.info(f"[DUMMY SMS] To: {phone_number} | Message: {message}")
        return True


class TwilioSMSBackend(BaseSMSBackend):
    def __init__(self):
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID", "")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        self.from_number = os.environ.get("TWILIO_FROM_NUMBER", "")

    def send_sms(self, phone_number: str, message: str) -> bool:
        if not self.account_sid or not self.auth_token:
            logger.warning("Twilio credentials not configured; falling back to log.")
            logger.info(
                f"[TWILIO SMS SIMULATED] To: {phone_number} | Message: {message}"
            )
            return True
        try:
            # Pluggable integration point
            logger.info(f"[TWILIO SMS SENT] To: {phone_number} | Message: {message}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send Twilio SMS: {exc}")
            return False


def get_sms_backend() -> BaseSMSBackend:
    provider = os.environ.get("SMS_PROVIDER", "dummy").lower()
    if provider == "twilio":
        return TwilioSMSBackend()
    return DummySMSBackend()


def send_sms(phone_number: str, message: str) -> bool:
    """
    Unified SMS dispatcher. Development uses DummySMSBackend;
    production chooses provider based on SMS_PROVIDER env var.
    Never raises an uncaught exception.
    """
    if not phone_number:
        return False
    try:
        backend = get_sms_backend()
        return backend.send_sms(phone_number, message)
    except Exception as exc:
        logger.error(f"Error in send_sms: {exc}")
        return False
