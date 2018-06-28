from PriceTrail.settings import BASE_DIR

from django.core.mail import send_mail
from django.template import Context, Template

import socket
import smtplib
import os

class EmailFormatter:
    @staticmethod
    def create_html_notification(products, username):
        data = {}
        data['status'] = 'success'

        email_data = {"products": products, 'username': username}
        fileaddr = 'templates/emails/newsletter-mailchimp.html'
        html_message = EmailFormatter._create_generic_html_message(email_data, fileaddr)
        return html_message

    @staticmethod
    def _create_generic_html_message(data, fileaddr):
        template_dir = os.path.join(BASE_DIR, fileaddr)

        email_template = open(template_dir, 'r')
        template = Template(email_template.read())

        context = Context(data)

        return template.render(context)

class EmailClient:
    @staticmethod
    def send_best_price_notification(to_emails, products, username):
        data = {}
        data['error'] = 'None'

        emaildata = {"products": products, 'username': username}
        fileaddr = 'templates/emails/newsletter.html'
        html_message = EmailClient._create_generic_html_message(emaildata, fileaddr)

        try:
            send_mail(
                subject='Price drop in shopping-list.ro',
                message='Hi',
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
    def say_hi(to_email, username):
        data = {}
        data['error'] = 'None'

        emaildata = {'username': username}
        fileaddr = 'templates/emails/newsletter-hi.html'
        html_message = EmailClient._create_generic_html_message(emaildata, fileaddr)

        try:
            send_mail(
                subject='Price drop in shopping-list.ro',
                message='Hi',
                from_email='admin@shopping-list.ro',
                recipient_list=[to_email],
                fail_silently=False,
                html_message=html_message,
            )
        except smtplib.SMTPException as ex:
            data['error'] = ex.strerror
        except socket.error as ex:
            data['error'] = ex.strerror
        return data

    @staticmethod
    def _create_generic_html_message(data, fileaddr):
        template_dir = os.path.join(BASE_DIR, fileaddr)

        email_template = open(template_dir, 'r')
        template = Template(email_template.read())

        context = Context(data)

        return template.render(context)