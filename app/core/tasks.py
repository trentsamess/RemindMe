from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.mail import EmailMultiAlternatives

from app.core.models import User
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
    context.update({
        'button': True,
        'button_text': 'Verify Email',
        'button_link': link,
    })
    recipients = [user.email]
    subject = "Confirm your email"
    text_content = f"{context['text']} Link: {link}"
    msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_EMAIL, recipients)
    msg.send()
