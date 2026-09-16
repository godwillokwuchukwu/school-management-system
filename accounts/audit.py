from .models import AuditLog


def record(
    *,
    actor,
    action,
    instance,
    old_value=None,
    new_value=None,
    request=None,
    description="",
    user_agent="",
):
    """
    Write one AuditLog row. Call this from serializer.update()/create()
    or view methods for any sensitive mutation (grades, attendance,
    message deletion, etc).
    """
    ip_address = None
    if request is not None:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.META.get("REMOTE_ADDR")
        )
        if not user_agent:
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:255]

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        model_name=instance.__class__.__name__ if instance else "System",
        object_id=str(instance.pk) if instance else "0",
        description=description,
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
        user_agent=user_agent,
    )
