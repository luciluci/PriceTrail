from lxml import html
from requests.exceptions import ConnectionError

import time
import httplib
import requests
import ssl

from PriceTrail.utils import data

class Product():

     def __init__(self):
         self.name = ''
         self.price = ''

class EmagSpider():
    MAX_RETRIES = 3

    def __init__(self):
        self.product = Product()

    def req_product(self, url, retries=0):

        if not url.startswith('https://www.emag.ro'):
            return httplib.NOT_IMPLEMENTED
        try:
            result = requests.get(url, timeout=10)
        except ssl.SSLError:
            time.sleep(1)
            if retries == self.MAX_RETRIES:
                return httplib.INTERNAL_SERVER_ERROR
            return self.req_product(url, retries + 1)

        except ConnectionError as e:
            time.sleep(1)
            if retries == self.MAX_RETRIES:
                return httplib.INTERNAL_SERVER_ERROR
            return self.req_product(url, retries + 1)

        if result.status_code != 200:
            return result.status_code

        tree = html.fromstring(result.content)

        product_node_tree = tree.xpath('//div[@class="product-highlight product-page-pricing"]')

        prod_price_str = ''
        for element in product_node_tree[0].iter():
            unavailable_node = element.find('span[@class="label label-unavailable"]')
            if unavailable_node != None:
                return data.PRODUCT_UNAVAILABLE
            new_price_node = element.find('p[@class="product-new-price"]')
            if new_price_node:
                prod_price_str = new_price_node.text.replace('.', '').strip()
                break

        page_title = tree.xpath('//h1[@class="page-title"]/text()')

        if not prod_price_str or not page_title:
            return httplib.NO_CONTENT

        self.product.price = prod_price_str.replace('.', '').strip()
        # assume it's the first element in the array
        self.product.name  = page_title[0].strip()

        return httplib.OK

    def get_product(self):
        return self.product