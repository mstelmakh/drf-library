from celery import shared_task
from library.services import notify_book_instance_subscribers


@shared_task
def send_notification_email_task(book_instance_id):
    notify_book_instance_subscribers(book_instance_id)
