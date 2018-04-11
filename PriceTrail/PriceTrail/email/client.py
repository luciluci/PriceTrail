from django.core.mail import send_mail
from django.http import HttpResponse

import json
import socket
import smtplib

class EmailClient:
    @staticmethod
    def send_best_price_notification(to_emails, products):
        a_after = '</a>'
        new_line = '\n\r'
        data = {}
        data['error'] = 'None'

        if len(products) > 1:
            message = 'Price dropped for products:' + new_line
        else:
            message = 'Price dropped for product:' + new_line
        for product in products:
            a_before = '<a href=\"' + product.aff_url + '\" target=\"_blank\">'
            message += a_before + product.name + a_after + new_line
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
        return HttpResponse(json.dumps(data), content_type='application/json')