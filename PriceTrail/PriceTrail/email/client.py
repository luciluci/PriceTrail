from PriceTrail.settings import BASE_DIR

from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template import Context, Template

import socket
import smtplib
import os

class EmailClient:
    @staticmethod
    def send_best_price_notification(to_emails, products, username):
        data = {}
        data['error'] = 'None'

        html_message = EmailClient._create_html_message(products)

        #mail = EmailMultiAlternatives('', 'This is message', 'from_email', to_emails)
        #mail.attach_alternative(message, "text/html")

        try:
            #mail.send()
            send_mail(
                subject='Price drop in shopping-list.ro',
                message=None,
                from_email='admin@shopping-list.ro',
                recipient_list=to_emails,
                fail_silently=False,
                html_message=html_message,
            )
        except smtplib.SMTPException as ex:
            data['error'] = ex.strerror
        except socket.error as ex:
            data['error'] = ex.strerror
        return data

    @staticmethod
    def _create_html_message(products):
        #template_dir = os.path.join(BASE_DIR, 'templates/emails/newsletter.html')
        template_dir = os.path.join(BASE_DIR, 'templates/emails/newsletter-test.html')
        email_template = open(template_dir, 'r')
        template = Template(email_template.read())

        #context = Context({"products": products})
        context = Context({"product": products[0]})
        return template.render(context)