from django.core.mail import send_mail

from Chat_API import settings
from Chat_API.celery import app


@app.task
def add_numbers(a, b):
    c = 1 / 8457867
    return a + b * c * 29839859856987