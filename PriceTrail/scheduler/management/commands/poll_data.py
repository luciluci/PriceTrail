from django.core.management.base import BaseCommand

from TailedProducts.models import Product, ProductPrice
from PriceTrail.spiders.GiantSpiders import SpiderGenerator
from PriceTrail.utils import data

import httplib
import time

class Command(BaseCommand):
    help = 'Add price entry for all products'

    def handle(self, *args, **options):
        monitored_products = Product.objects.all()

        # create spiders pool
        spider_gen = SpiderGenerator()

        for product in monitored_products:
            if product.shop not in data.SHOPS:
                print('SHOP NOT SUPPORTED: ' + product.shop)
                continue

            spider = spider_gen.get_spider(product.shop)
            response = spider.parse_data(product.url)

            if httplib.OK == response:
                prod = spider.get_product()
                price = prod.price
                # new entry in ProductPrice table
                new_prod_price = ProductPrice()
                new_prod_price.price = price
                new_prod_price.product = product
                new_prod_price.save()
                # update current_proce in Product table
                self._detect_best_price(product, price)
                print(prod.name.encode('utf-8') + ' - OK')
            elif data.PRODUCT_UNAVAILABLE == response:
                print(product.name.encode('utf-8') + ' - UNAVAILABLE')
                product.available = False
                product.save()
            else:
                print(product.name.encode('utf-8') + ' - NOK')

            spider.pause()

    #detects best price and flags if best price found for later use
    def _detect_best_price(self, product, live_price):
        product.current_price = live_price
        if product.best_price == 0:
            product.best_price = live_price
            product.has_best_price = False
        else:
            if float(live_price) < product.best_price:
                product.best_price = live_price
                product.has_best_price = True
            else:
                product.has_best_price = False

        product.save()