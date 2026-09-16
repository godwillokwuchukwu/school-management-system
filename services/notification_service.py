import logging
from django.contrib.contenttypes.models import ContentType
from accounts.models import AdminNotification, AdminNotificationType, PortalNotification

logger = logging.getLogger(__name__)


def notify_admin(
    title: str,
    message: str,
    notification_type=AdminNotificationType.INFO,
    object_instance=None,
    user=None,
):
    """
    Creates an AdminNotification visible in the Admin Dashboard notification bell.
    """
    try:
        content_type = None
        object_id = ""
        if object_instance is not None:
            content_type = ContentType.objects.get_for_model(object_instance)
            object_id = str(object_instance.pk)

        notification = AdminNotification.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            user=user,
            content_type=content_type,
            object_id=object_id,
        )
        logger.info(f"Admin notification created: {title}")
        return notification
    except Exception as exc:
        logger.error(f"Failed to create admin notification: {exc}")
        return None


def notify_student(
    user, title: str, message: str, notification_type: str = "general", link: str = ""
):
    """
    Creates an in-portal notification for a student or applicant user.
    """
    try:
        notification = PortalNotification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
        logger.info(f"Student notification created for {user.username}: {title}")
        return notification
    except Exception as exc:
        logger.error(
            f"Failed to create student notification for {user.username}: {exc}"
        )
        return None
