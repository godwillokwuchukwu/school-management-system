import logging
from django.db import transaction
from django.utils import timezone
from accounts import audit
from accounts.models import AdminNotificationType
from admissions.models import AdmissionApplication, ApplicationStatus
from services import email_service, notification_service, sms

logger = logging.getLogger(__name__)


def approve_application(
    application: AdmissionApplication, admin_user, notes: str = "", request=None
):
    """
    Approves an admission application, logs the audit, and notifies the applicant.
    """
    with transaction.atomic():
        old_status = application.status
        application.status = ApplicationStatus.APPROVED
        application.reviewed_by = admin_user
        if notes:
            application.decision_notes = notes
        application.save(
            update_fields=["status", "reviewed_by", "decision_notes", "updated_at"]
        )

        audit.record(
            actor=admin_user,
            action="admission.approve",
            instance=application,
            old_value={"status": old_status},
            new_value={"status": ApplicationStatus.APPROVED},
            description=f"Application {application.reference} approved by {admin_user.username}",
            request=request,
        )

        notification_service.notify_student(
            user=application.applicant,
            title="Application Approved",
            message=f"Congratulations! Your application {application.reference} has been approved.",
            notification_type="admission",
            link=f"/admissions/status",
        )

    email_service.send_admission_approved_notification(application, request=request)
    return application


def move_to_payment(
    application: AdmissionApplication,
    admin_user,
    amount: float = 150000.0,
    due_date=None,
    notes: str = "",
    request=None,
):
    """
    Moves an approved admission application to Payment Pending (Section 22).
    Dispatches payment email, optional SMS, creates internal notifications and audit trail.
    """
    with transaction.atomic():
        old_status = application.status
        application.status = ApplicationStatus.PAYMENT_PENDING
        application.reviewed_by = admin_user
        if notes:
            application.decision_notes = (
                f"{application.decision_notes}\n[Payment Requested] {notes}".strip()
            )
        application.save(
            update_fields=["status", "reviewed_by", "decision_notes", "updated_at"]
        )

        audit.record(
            actor=admin_user,
            action="admission.move_to_payment",
            instance=application,
            old_value={"status": old_status},
            new_value={"status": ApplicationStatus.PAYMENT_PENDING, "amount": amount},
            description=f"Moved {application.reference} to payment pending (Amount: {amount})",
            request=request,
        )

        notification_service.notify_student(
            user=application.applicant,
            title="Admission Fee Payment Required",
            message=f"Your admission application ({application.reference}) is approved! Please proceed with payment of ₦{amount:,.2f}.",
            notification_type="payment",
            link="/admissions/apply",
        )

        notification_service.notify_admin(
            title=f"Payment Requested for {application.reference}",
            message=f"Admin {admin_user.username} moved application {application.reference} to payment pending (₦{amount:,.2f}).",
            notification_type=AdminNotificationType.INFO,
            object_instance=application,
            user=admin_user,
        )

    # Dispatches outside transaction so network calls don't hold the DB transaction lock
    email_service.send_payment_notification(
        application, amount=amount, due_date=due_date, request=request
    )

    phone = application.guardian_phone or application.student_phone
    if phone:
        sms_msg = (
            f"Hello {application.student_first_name}, your Riverside Academy admission ({application.reference}) "
            f"has reached the payment stage. Please check your email or portal for instructions."
        )
        sms.send_sms(phone, sms_msg)

    return application


def reject_application(
    application: AdmissionApplication, admin_user, notes: str = "", request=None
):
    """
    Rejects an admission application with decision notes.
    """
    with transaction.atomic():
        old_status = application.status
        application.status = ApplicationStatus.REJECTED
        application.reviewed_by = admin_user
        if notes:
            application.decision_notes = notes
        application.save(
            update_fields=["status", "reviewed_by", "decision_notes", "updated_at"]
        )

        audit.record(
            actor=admin_user,
            action="admission.reject",
            instance=application,
            old_value={"status": old_status},
            new_value={"status": ApplicationStatus.REJECTED},
            description=f"Application {application.reference} rejected by {admin_user.username}",
            request=request,
        )

        notification_service.notify_student(
            user=application.applicant,
            title="Admission Decision",
            message=f"An update is available on your admission application {application.reference}.",
            notification_type="admission",
            link="/admissions/status",
        )

    return application
