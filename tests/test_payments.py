import pytest
from payments.services import (
    BasePaymentGateway,
    DummyPaymentGateway,
    FlutterwavePaymentGateway,
    PaystackPaymentGateway,
    get_payment_gateway,
)


def test_base_payment_gateway_not_implemented():
    gateway = BasePaymentGateway()
    with pytest.raises(NotImplementedError):
        gateway.initialize_payment(
            "test@example.com", 100.0, "REF123", "http://callback"
        )
    with pytest.raises(NotImplementedError):
        gateway.verify_payment("REF123")


def test_dummy_payment_gateway():
    gateway = DummyPaymentGateway()
    res = gateway.initialize_payment(
        "test@example.com", 50000.0, "REF-TEST-001", "https://example.com/callback"
    )
    assert res["status"] is True
    assert res["data"]["reference"] == "REF-TEST-001"
    assert "https://example.com/callback" in res["data"]["authorization_url"]

    # Test auto-generated reference when empty
    res_auto = gateway.initialize_payment(
        "test@example.com", 50000.0, "", "https://example.com/callback"
    )
    assert res_auto["status"] is True
    assert res_auto["data"]["reference"].startswith("PAY-")

    verify_res = gateway.verify_payment("REF-TEST-001")
    assert verify_res["status"] is True
    assert verify_res["data"]["status"] == "success"
    assert verify_res["data"]["reference"] == "REF-TEST-001"


def test_paystack_payment_gateway(monkeypatch):
    monkeypatch.delenv("PAYSTACK_SECRET_KEY", raising=False)
    gateway = PaystackPaymentGateway()
    res = gateway.initialize_payment(
        "test@example.com", 1000.0, "PSTK-01", "http://callback"
    )
    assert res["status"] is True
    v_res = gateway.verify_payment("PSTK-01")
    assert v_res["status"] is True

    # With key set
    monkeypatch.setenv("PAYSTACK_SECRET_KEY", "sk_test_123456789")
    gateway_with_key = PaystackPaymentGateway()
    res2 = gateway_with_key.initialize_payment(
        "test@example.com", 1000.0, "PSTK-02", "http://callback"
    )
    assert res2["status"] is True
    v_res2 = gateway_with_key.verify_payment("PSTK-02")
    assert v_res2["status"] is True


def test_flutterwave_payment_gateway(monkeypatch):
    gateway = FlutterwavePaymentGateway()
    res = gateway.initialize_payment(
        "test@example.com", 2000.0, "FLW-01", "http://callback"
    )
    assert res["status"] is True
    v_res = gateway.verify_payment("FLW-01")
    assert v_res["status"] is True


def test_get_payment_gateway(monkeypatch):
    monkeypatch.setenv("PAYMENT_PROVIDER", "dummy")
    assert isinstance(get_payment_gateway(), DummyPaymentGateway)

    monkeypatch.setenv("PAYMENT_PROVIDER", "paystack")
    assert isinstance(get_payment_gateway(), PaystackPaymentGateway)

    monkeypatch.setenv("PAYMENT_PROVIDER", "flutterwave")
    assert isinstance(get_payment_gateway(), FlutterwavePaymentGateway)

    monkeypatch.setenv("PAYMENT_PROVIDER", "unknown")
    assert isinstance(get_payment_gateway(), DummyPaymentGateway)
