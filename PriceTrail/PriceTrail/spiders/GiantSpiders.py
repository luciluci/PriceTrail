from lxml import html
from requests.exceptions import ConnectionError

import time
import httplib
import requests
import ssl
import locale

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
        # locale - determines how float numbers are expressed
        # FR locale interprets comma as decimals
        # locale.setlocale(locale.LC_ALL, 'fr_FR')
        self.price_parent_div = None
        self.price_div = None
        self.title_div = None
        self.unavailable_div = None

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

    @staticmethod
    def get_shop_from_url(url):
        shop_name = url.split(".", 2)
        if len(shop_name) < 3:
            return ''
        return shop_name[1]

    def pause(self):
        time.sleep(2)

    def config_spider(self, price_parent_div, price_div, title_div, unavailable_div = None):
        self.price_parent_div = price_parent_div
        self.price_div = price_div
        self.title_div = title_div
        self.unavailable_div = unavailable_div

    def parse_data(self, url):
        if httplib.OK != self._request_url(url):
            return self.result.status_code

        tree = html.fromstring(self.result.content)

        product_node_tree = tree.xpath(self.price_parent_div)

        prod_price_str = ''
        for element in product_node_tree[0].iter():
            if self.unavailable_div:
                unavailable_node = element.find(self.unavailable_div)
                if unavailable_node != None:
                    return data.PRODUCT_UNAVAILABLE
            new_price_node = element.find(self.price_div)
            if new_price_node is not None:
                prod_price_str = new_price_node.text.replace('.', '').strip()
                break

        page_title = tree.xpath(self.title_div)

        if not prod_price_str or not page_title:
            return httplib.NO_CONTENT

        self.product.price = prod_price_str.replace('.', '').strip()
        # assume it's the first element in the array
        self.product.name = page_title[0].strip()

        return httplib.OK


class EmagSpider(Spider):

    def __init__(self):
        super(EmagSpider, self).__init__('emag')
        self.price_parent_div = '//div[@class="product-highlight product-page-pricing"]'
        self.price_div = 'p[@class="product-new-price"]'
        self.title_div = '//h1[@class="page-title"]/text()'
        self.unavailable_div = 'span[@class="label label-unavailable"]'

    def pause(self):
        time.sleep(3)

class AVStoreSpider(Spider):

    def __init__(self):
        super(AVStoreSpider, self).__init__('avstore')
        self.price_parent_div = '//div[@class="st mainproductprice"]'
        self.price_div = 'span[@class="pret-nou number"]'
        self.title_div = '//h1[@class="product-title"]/text()'


class EVOMagSpider(Spider):
    def __init__(self):
        super(EVOMagSpider, self).__init__('evomag')
        self.price_parent_div = '//div[@class="price_ajax"]'
        self.price_div = 'div[@class="pret_rons"]'
        self.title_div = '//h1[@class="product_name"]/text()'


class CelSpider(Spider):
    def __init__(self):
        super(CelSpider, self).__init__('cel')
        self.price_parent_div = '//div[@class="pret_tabela"]'
        self.price_div = 'span[@class="productPrice"]'
        self.title_div = '//h2[@class="productName"]/text()'


class SpiderGenerator():

    def __init__(self):
        self.emag = EmagSpider()
        self.avstore = AVStoreSpider()
        self.evomag = EVOMagSpider()
        self.cel = CelSpider()

    def get_spider(self, name):
        if name == "emag":
            return self.emag
        elif name == "avstore":
            return self.avstore
        elif name == "evomag":
            return self.evomag
        elif name == "cel":
            return self.cel