from .models import AuditLog


def record(*, actor, action, instance, old_value=None, new_value=None, request=None):
    """
    Write one AuditLog row. Call this from serializer.update()/create()
    or view methods for any sensitive mutation (grades, attendance,
    message deletion, etc):

        audit.record(
            actor=request.user,
            action="grade.update",
            instance=grade,
            old_value={"score": old_score},
            new_value={"score": grade.score},
            request=request,
        )
    """
    ip_address = None
    if request is not None:
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = (
            forwarded_for.split(",")[0].strip()
            if forwarded_for
            else request.META.get("REMOTE_ADDR")
        )

    return AuditLog.objects.create(
        actor=actor,
        action=action,
        model_name=instance.__class__.__name__,
        object_id=str(instance.pk),
        old_value=old_value,
        new_value=new_value,
        ip_address=ip_address,
    )
