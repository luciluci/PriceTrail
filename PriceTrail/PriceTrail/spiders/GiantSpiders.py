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
         self.shop = ''

class Spider(object):
    MAX_RETRIES = 3
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'From': 'lucian_apetre@yahoo.com'
    }

    def __init__(self, shop):
        self.product = Product()
        self.product.shop = shop
        self.result = None

    def get_product(self):
        return self.product

    def _request_url(self, url, retries=0):
        try:
            result = requests.get(url, timeout=10, headers=self.headers)
        except ssl.SSLError:
            if retries == self.MAX_RETRIES:
                return httplib.INTERNAL_SERVER_ERROR
            time.sleep(1)
            return self._request_url(url, retries + 1)

        except ConnectionError as e:
            if retries == self.MAX_RETRIES:
                return httplib.INTERNAL_SERVER_ERROR
            time.sleep(1)
            return self._request_url(url, retries + 1)

        self.result = result
        return result.status_code

    def parse_data(self, url):
        return httplib.NOT_IMPLEMENTED

    @staticmethod
    def get_shop_from_url(url):
        shop_name = url.split(".", 2)
        if len(shop_name) < 3:
            return ''
        return shop_name[1]

    def pause(self):
        time.sleep(2)


class EmagSpider(Spider):

    def __init__(self):
        super(EmagSpider, self).__init__('emag')

    def parse_data(self, url):
        if httplib.OK != self._request_url(url):
            return self.result.status_code

        tree = html.fromstring(self.result.content)

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
        self.product.name = page_title[0].strip()

        return httplib.OK

    def pause(self):
        time.sleep(3)

class AVStoreSpider(Spider):

    def __init__(self):
        super(AVStoreSpider, self).__init__('avstore')

    def parse_data(self, url):
        if httplib.OK != self._request_url(url):
            return self.result.status_code

        tree = html.fromstring(self.result.content)

        product_node_tree = tree.xpath('//div[@class="st mainproductprice"]')

        prod_price_str = ''
        for element in product_node_tree[0].iter():
            new_price_node = element.find('span[@class="pret-nou number"]')
            if new_price_node is not None:
                prod_price_str = new_price_node.text.replace('.', '').strip()
                break

        page_title = tree.xpath('//h1[@class="product-title"]/text()')

        if not prod_price_str or not page_title:
            return httplib.NO_CONTENT

        self.product.price = prod_price_str.replace('.', '').strip()
        # assume it's the first element in the array
        self.product.name = page_title[0].strip()

        return httplib.OK


class SpiderGenerator():

    def __init__(self):
        self.emag = EmagSpider()
        self.avstore = AVStoreSpider()

    def get_spider(self, name):
        if name == "emag":
            return self.emag
        elif name == "avstore":
            return self.avstore