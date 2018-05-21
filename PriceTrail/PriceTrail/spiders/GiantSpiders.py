from lxml import html
from requests.exceptions import ConnectionError

import time
import httplib
import requests
import ssl
from PriceTrail.settings import logger

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
        self.brand_div = None
        self.brand_name = None

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

        if not product_node_tree:
            return data.PRODUCT_UNAVAILABLE

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
        if not prod_price_str:
            logger.error("ERROR! product price not available")
        if not page_title:
            logger.error("ERROR! product title not available")

        if not prod_price_str or not page_title:
            return httplib.NO_CONTENT

        self.product.price = prod_price_str.replace('.', '').strip()

        # assume it's the first element in the array
        self.product.name = page_title[0].strip()

        #detect and append brand name in product name
        if self.brand_div and self.brand_name:
            brand_div = tree.xpath(self.brand_div)
            if brand_div:
                for element in brand_div[0].iter():
                    brand_name = element.find(self.brand_name)
                    if brand_name is not None:
                        self.product.name = brand_name.text + ' ' + self.product.name
                        break

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

class GermanosSpider(Spider):

    imgToNumber = {'/images/price/big/zero.gif':  0,
                   '/images/price/big/one.gif':   1,
                   '/images/price/big/two.gif':   2,
                   '/images/price/big/three.gif': 3,
                   '/images/price/big/four.gif':  4,
                   '/images/price/big/five.gif':  5,
                   '/images/price/big/six.gif':   6,
                   '/images/price/big/seven.gif': 7,
                   '/images/price/big/eight.gif': 8,
                   '/images/price/big/nine.gif':  9,
                   '/images/price/big/cent/zero.gif':  0,
                   '/images/price/big/cent/one.gif':   1,
                   '/images/price/big/cent/two.gif':   2,
                   '/images/price/big/cent/three.gif': 3,
                   '/images/price/big/cent/four.gif':  4,
                   '/images/price/big/cent/five.gif':  5,
                   '/images/price/big/cent/six.gif':   6,
                   '/images/price/big/cent/seven.gif': 7,
                   '/images/price/big/cent/eight.gif': 8,
                   '/images/price/big/cent/nine.gif':  9
                   }

    comma = '/images/price/big/comma.gif'
    comma_dash = '/images/price/big/comma-dash.gif'

    def __init__(self):
        super(GermanosSpider, self).__init__('germanos')
        self.price_parent_div = '//div[@class="bigprice"]'
        self.title_div = '//h1[@itemprop="name"]/text()'

    def parse_data(self, url):
        if httplib.OK != self._request_url(url):
            return self.result.status_code

        tree = html.fromstring(self.result.content)

        product_node_tree = tree.xpath(self.price_parent_div)

        prod_price = 0
        price_data = []

        element = product_node_tree[0]
        if self.unavailable_div:
            unavailable_node = element.find(self.unavailable_div)
            if unavailable_node != None:
                return data.PRODUCT_UNAVAILABLE
        elem_subitems = element.iter()
        for img_element in elem_subitems:
            if img_element is not None and hasattr(img_element, 'attrib'):
                if 'src' in img_element.attrib:
                    print (img_element.attrib)
                    price_data.append(img_element.attrib)

        prod_price = GermanosSpider._get_price_from_array(price_data)
        page_title = tree.xpath(self.title_div)

        if not prod_price or not page_title:
            return httplib.NO_CONTENT

        self.product.price = prod_price
        # assume it's the first element in the array
        self.product.name = page_title[0].strip()

        return httplib.OK

    @staticmethod
    def _get_price_from_array(price_data):
        fidx = 1
        didx = 1
        rev = price_data[::-1]

        float_nr = 0
        decimal_nr = 0.
        is_decimal = False
        for item in rev:
            if item['src'] in GermanosSpider.imgToNumber:
                nr = GermanosSpider.imgToNumber[item['src']]
            elif item['src'] == GermanosSpider.comma or item['src'] == GermanosSpider.comma_dash:
                is_decimal = True
                continue
            else:
                print ("Invalid number")
                continue

            if is_decimal:
                decimal_nr += didx * nr
                didx *= 10
            else:
                float_nr += fidx * nr
                fidx *= 10

        final_float = float(float_nr)/10**len(str(float_nr))
        final_nr = final_float + decimal_nr
        return final_nr

class QuickMobileSpider(Spider):

    def __init__(self):
        super(QuickMobileSpider, self).__init__('quickmobile')
        self.price_parent_div = '//div[@class="priceFormat total-price price-fav"]'
        self.price_div = 'div[@class="priceFormat total-price price-fav product-page-price"]'
        self.title_div = '//div[@class="product-page-title page-product-title-wth"]/text()'
        self.brand_div = '//div[@class="product-page-brand"]'
        self.brand_name = './/a[@href]'


class SpiderGenerator():

    def __init__(self):
        self.emag = EmagSpider()
        self.avstore = AVStoreSpider()
        self.evomag = EVOMagSpider()
        self.cel = CelSpider()
        self.germanos = GermanosSpider()
        self.quickmobile = QuickMobileSpider()

    def get_spider(self, name):
        if name == "emag":
            return self.emag
        elif name == "avstore":
            return self.avstore
        elif name == "evomag":
            return self.evomag
        elif name == "cel":
            return self.cel
        elif name == 'germanos':
            return self.germanos
        elif name == 'quickmobile':
            return self.quickmobile