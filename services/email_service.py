import logging
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _get_base_url(request=None) -> str:
    if request is not None:
        return request.build_absolute_uri("/").rstrip("/")
    return getattr(settings, "BACKEND_BASE_URL", "http://localhost:8000")


def send_verification_email(user, token: str, request=None) -> bool:
    """
    Sends 24-hour cryptographic email verification link.
    Never blocks or raises an exception.
    """
    try:
        base_url = _get_base_url(request)
        verification_url = f"{base_url}/accounts/verify-email/{token}/"
        student_name = user.get_full_name() or user.username

        context = {
            "student_name": student_name,
            "verification_url": verification_url,
            "base_url": base_url,
        }
        html_content = render_to_string("emails/verify_email.html", context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject="Confirm your Riverside Academy email address",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
        logger.info(f"Verification email dispatched to {user.email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send verification email to {user.email}: {exc}")
        return False


def send_login_notification(user, request=None) -> bool:
    """
    Sends non-blocking login notification security email.
    """
    try:
        ip_address = "Unknown"
        device = "Unknown browser/device"
        if request is not None:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            ip_address = (
                forwarded.split(",")[0].strip()
                if forwarded
                else request.META.get("REMOTE_ADDR", "Unknown")
            )
            device = request.META.get("HTTP_USER_AGENT", "Unknown browser/device")

        login_time = datetime.now().strftime("%d %B %Y, %I:%M %p")
        user_name = user.get_full_name() or user.username

        context = {
            "user_name": user_name,
            "login_time": login_time,
            "ip_address": ip_address,
            "device": device,
        }
        html_content = render_to_string("emails/login_notification.html", context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject="New login to your Riverside Academy account",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
        logger.info(f"Login notification dispatched to {user.email}")
        return True
    except Exception as exc:
        logger.error(f"Failed to send login notification to {user.email}: {exc}")
        return False


def send_payment_notification(application, amount, due_date=None, request=None) -> bool:
    """
    Dispatches payment request notification for approved applicant.
    """
    try:
        base_url = _get_base_url(request)
        payment_url = f"{base_url}/admissions/apply"
        portal_url = f"{base_url}/portal"
        student_name = (
            f"{application.student_first_name} {application.student_last_name}"
        )

        context = {
            "student_name": student_name,
            "guardian_name": application.guardian_full_name,
            "reference": application.reference,
            "class_applying_for": application.class_applying_for,
            "academic_session": application.academic_session,
            "amount": amount,
            "due_date": due_date,
            "payment_url": payment_url,
            "portal_url": portal_url,
        }
        html_content = render_to_string("emails/payment_notification.html", context)
        text_content = strip_tags(html_content)

        to_emails = [application.guardian_email]
        if (
            application.student_email
            and application.student_email != application.guardian_email
        ):
            to_emails.append(application.student_email)

        msg = EmailMultiAlternatives(
            subject="Your Riverside Academy admission – payment required",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
        logger.info(
            f"Payment notification dispatched for application {application.reference}"
        )
        return True
    except Exception as exc:
        logger.error(
            f"Failed to send payment notification for {application.reference}: {exc}"
        )
        return False


def send_admission_approved_notification(application, request=None) -> bool:
    """
    Dispatches admission approval notice.
    """
    try:
        base_url = _get_base_url(request)
        portal_url = f"{base_url}/admissions/status"
        student_name = (
            f"{application.student_first_name} {application.student_last_name}"
        )

        context = {
            "student_name": student_name,
            "reference": application.reference,
            "portal_url": portal_url,
        }
        html_content = render_to_string("emails/admission_approved.html", context)
        text_content = strip_tags(html_content)

        to_emails = [application.guardian_email]
        if application.student_email:
            to_emails.append(application.student_email)

        msg = EmailMultiAlternatives(
            subject="Your Riverside Academy admission application has been approved",
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=to_emails,
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
        return True
    except Exception as exc:
        logger.error(
            f"Failed to send approval email for {application.reference}: {exc}"
        )
        return False
