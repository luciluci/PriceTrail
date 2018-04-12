from PriceTrail.settings import BASE_DIR
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template import Context, Template

import json
import socket
import smtplib
import os

class EmailClient:
    @staticmethod
    def send_best_price_notification(to_emails, products, username):
        data = {}
        data['error'] = 'None'

        message = EmailClient._create_email_message(products)

        try:
            send_mail(
                'Price drop in shopping-list.ro',
                message,
                'admin@shopping-list.ro',
                to_emails,
                fail_silently=False,
            )
        except smtplib.SMTPException as ex:
            data['error'] = ex.strerror
        except socket.error as ex:
            data['error'] = ex.strerror
        return data

    @staticmethod
    def _create_email_message(products):
        template_dir = os.path.join(BASE_DIR, 'templates/emails/newsletter.html')
        email_template = open(template_dir, 'r')
        template = Template(email_template.read())

        context = Context({"products": products})
        return template.render(context)