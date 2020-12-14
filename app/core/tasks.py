from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives

from app.core.models import User, Reminder
from app.core.utils import TokenGenerator
from config import settings

logger = get_task_logger(__name__)


@shared_task()
def confirm_email(user_id: int):
    user = User.objects.get(id=user_id)
    token = TokenGenerator.create_email_activation_token(user)
    link = f"{settings.SITE_URL}/api/v1/verify-email?token={token}"
    context = {
        'text': "Account verification ",
        'title': 'Verify your email then be on the lookout.',
    }
    recipients = [user.email]
    subject = "Confirm your email"
    text_content = f"{context['text']} Link: {link}"
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_EMAIL, recipients)
    msg.send(fail_silently=True)


@shared_task()
def send_reminder_email(user_ids: list, remind_id: int):
    user_emails = User.objects.filter(id__in=user_ids).values_list('email', flat=True)
    remind = Reminder.objects.filter(id=remind_id).first()
    description = remind.description if remind.description else ''
    context = {
        'text': "Reminder",
        'title': "Look, you have a reminder for today",
    }
    recipients = list(user_emails)
    subject = "Reminder for today"
    text_content = f"{context['text']} Description: {description}"
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_EMAIL, recipients)
    msg.send(fail_silently=True)
