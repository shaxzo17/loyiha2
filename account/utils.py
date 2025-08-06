import random
import string
from django.core.mail import send_mail
from django.conf import settings

def generate_code():
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for _ in range(6))

def send_to_mail(email, code):
    subject = 'Tasdiqlash kodi'
    message = f'Sizning tasdiqlash kodingiz: {code}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)