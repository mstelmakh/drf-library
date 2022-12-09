from django.db.models.signals import pre_save
from django.dispatch import receiver

from library.models import BookInstance
from library.tasks import send_notification_email_task


@receiver(pre_save, sender=BookInstance)
def save_profile(sender, instance: BookInstance, **kwargs):
    previous = BookInstance.objects.get(pk=instance.id)
    if (
        previous.status != instance.status
        and instance.status == BookInstance.LoanStatus.AVAILABLE
    ):
        send_notification_email_task.delay(instance.id)
