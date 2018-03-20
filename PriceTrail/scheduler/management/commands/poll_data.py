from django.core.management.base import BaseCommand

from TailedProducts.models import Product, ProductPrice
from PriceTrail.spiders import GiantSpiders
from PriceTrail.utils import data

import httplib

class Command(BaseCommand):
    help = 'Add price entry for all products'

    def handle(self, *args, **options):
        help = "Append price each day for each product"

        monitored_products = Product.objects.all()
        for product in monitored_products:
            shop = product.shop

            if shop == 'emag':
                spider = GiantSpiders.EmagSpider()
                response = spider.req_product(product.url)
                if httplib.OK == response:
                    prod = spider.get_product()
                    price = prod.price

                    new_prod_price = ProductPrice()
                    new_prod_price.price = price
                    new_prod_price.product = product
                    new_prod_price.save()
                    self.stdout.write(self.style.SUCCESS(prod.name + ' - OK'))
                elif data.PRODUCT_UNAVAILABLE == response:
                    self.stdout.write(self.style.ERROR(product.name + ' - UNAVAILABLE'))
                    product.available = False
                    product.save()
                else:
                    self.stdout.write(self.style.ERROR(product.name + ' - NOK'))
            else:
                self.stdout.write(self.style.ERROR('SHOP NOT SUPPORTED: ' + shop))