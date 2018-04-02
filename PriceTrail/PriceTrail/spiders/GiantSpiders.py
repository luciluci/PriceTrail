from lxml import html
from requests.exceptions import ConnectionError

import time
import httplib
import requests
import ssl

import logging

from PriceTrail.utils import data

class Product():

     def __init__(self):
         self.name = ''
         self.price = ''

class EmagSpider():
    MAX_RETRIES = 3
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'From': 'lucian_apetre@yahoo.com.com'
    }

    def __init__(self):
        self.logger = logging.getLogger('SpiderLog')
        self.product = Product()

    def req_product(self, url, retries=0):

        if not url.startswith('https://www.emag.ro'):
            return httplib.NOT_IMPLEMENTED
        try:
            self.logger.info("requesting to URL:" + url)
            result = requests.get(url, timeout=10, headers=self.headers)
        except ssl.SSLError:
            time.sleep(1)
            self.logger.error("SSL error")
            if retries == self.MAX_RETRIES:
                return httplib.INTERNAL_SERVER_ERROR
            return self.req_product(url, retries + 1)

        except ConnectionError as e:
            time.sleep(1)
            self.logger.error("Connection error")
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
                self.logger.error("Product unavailable")
                return data.PRODUCT_UNAVAILABLE
            new_price_node = element.find('p[@class="product-new-price"]')
            if new_price_node:
                prod_price_str = new_price_node.text.replace('.', '').strip()
                break

        page_title = tree.xpath('//h1[@class="page-title"]/text()')

        if not prod_price_str or not page_title:
            self.logger.error("No content")
            return httplib.NO_CONTENT

        self.product.price = prod_price_str.replace('.', '').strip()
        # assume it's the first element in the array
        self.product.name  = page_title[0].strip()

        return httplib.OK

    def get_product(self):
        return self.product