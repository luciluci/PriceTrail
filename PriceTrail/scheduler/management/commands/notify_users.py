from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from TailedProducts.helpers import filters
from PriceTrail.email.client import EmailClient

class Command(BaseCommand):
    help = 'Add price entry for all products'

    def handle(self, *args, **options):
        data = {}
        users = User.objects.all()
        for user in users:
            product_list = filters.get_best_display_products_by_user(user.id)
            data[user.username] = str(len(product_list)) + ' products'
            if len(product_list) == 0:
                continue
            username = ''
            if user.first_name or user.last_name:
                username = user.first_name + ' ' + user.last_name
            else:
                username = user.username
            if user.email:
                email_data = EmailClient.send_best_price_notification([user.email], product_list, username)
                data.update(email_data)
            else:
                data['warn'] = 'user ' + user.username + ' does not have an email'

        print(data)