from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, Role


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile_exists(sender, instance, created, **kwargs):
    """
    Safety net for users created outside RegisterSerializer (e.g. via
    `createsuperuser` or the Django admin) so `request.user.profile`
    never raises DoesNotExist in permission classes.
    """
    if not created:
        return

    default_role = Role.ADMIN if instance.is_superuser else Role.STUDENT
    Profile.objects.get_or_create(user=instance, defaults={"role": default_role})
