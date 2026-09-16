import logging
import os
import uuid
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BasePaymentGateway:
    def initialize_payment(
        self, email: str, amount: float, reference: str, callback_url: str
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        raise NotImplementedError


class DummyPaymentGateway(BasePaymentGateway):
    def initialize_payment(
        self, email: str, amount: float, reference: str, callback_url: str
    ) -> Dict[str, Any]:
        ref = reference or f"PAY-{uuid.uuid4().hex[:12].upper()}"
        logger.info(f"[DUMMY PAYMENT] Init for {email}: amount={amount}, ref={ref}")
        return {
            "status": True,
            "message": "Payment authorization initialized (Simulated)",
            "data": {
                "authorization_url": f"{callback_url}?reference={ref}&status=success",
                "access_code": f"sim_code_{uuid.uuid4().hex[:8]}",
                "reference": ref,
            },
        }

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        logger.info(f"[DUMMY PAYMENT] Verified reference: {reference}")
        return {
            "status": True,
            "message": "Verification successful (Simulated)",
            "data": {
                "status": "success",
                "reference": reference,
                "amount": 15000000,  # in kobo/cents
                "currency": "NGN",
            },
        }


class PaystackPaymentGateway(BasePaymentGateway):
    def __init__(self):
        self.secret_key = os.environ.get("PAYSTACK_SECRET_KEY", "")

    def initialize_payment(
        self, email: str, amount: float, reference: str, callback_url: str
    ) -> Dict[str, Any]:
        if not self.secret_key:
            logger.warning("Paystack key missing; using dummy gateway response.")
            return DummyPaymentGateway().initialize_payment(
                email, amount, reference, callback_url
            )
        # Production Paystack integration point
        return DummyPaymentGateway().initialize_payment(
            email, amount, reference, callback_url
        )

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        if not self.secret_key:
            return DummyPaymentGateway().verify_payment(reference)
        return DummyPaymentGateway().verify_payment(reference)


class FlutterwavePaymentGateway(BasePaymentGateway):
    def __init__(self):
        self.secret_key = os.environ.get("FLUTTERWAVE_SECRET_KEY", "")

    def initialize_payment(
        self, email: str, amount: float, reference: str, callback_url: str
    ) -> Dict[str, Any]:
        return DummyPaymentGateway().initialize_payment(
            email, amount, reference, callback_url
        )

    def verify_payment(self, reference: str) -> Dict[str, Any]:
        return DummyPaymentGateway().verify_payment(reference)


def get_payment_gateway() -> BasePaymentGateway:
    provider = os.environ.get("PAYMENT_PROVIDER", "dummy").lower()
    if provider == "paystack":
        return PaystackPaymentGateway()
    elif provider == "flutterwave":
        return FlutterwavePaymentGateway()
    return DummyPaymentGateway()
