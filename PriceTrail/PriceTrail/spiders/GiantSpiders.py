from lxml import html
from requests.exceptions import ConnectionError

import time
import httplib
import requests
import ssl
import locale
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
        self.title_parent_div = None
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

    def filter_price(self, price):
        return price

    def filter_title(self, title, tree):
        return title

    def config_spider(self, price_parent_div, price_div, title_div, unavailable_div = None):
        self.price_parent_div = price_parent_div
        self.price_div = price_div
        self.title_div = title_div
        self.unavailable_div = unavailable_div

    def _get_price(self, content_tree):
        price_parent_node = content_tree.xpath(self.price_parent_div)

        if not price_parent_node:
            return None

        for element in price_parent_node[0].iter():
            new_price_node = element.find(self.price_div)

            if new_price_node is not None:
                if new_price_node.text:
                    return new_price_node.text.replace('.', '').strip()
        return None

    def _get_title(self, content_tree):
        title_parent_node = content_tree.xpath(self.title_parent_div)

        if not title_parent_node:
            return None

        for element in title_parent_node[0].iter():
            title_node = element.find(self.title_div)

            if title_node is not None:
                if title_node.text:
                    return title_node.text.strip()
        return None

    def parse_data(self, url):
        status = self._request_url(url)
        if httplib.OK != status:
            return status

        tree = html.fromstring(self.result.content)

        # get price
        price = self._get_price(tree)
        if not price:
            return data.PRODUCT_UNAVAILABLE
        self.product.price = self.filter_price(price)

        # get title
        title = self._get_title(tree)
        if not title:
            return data.PRODUCT_UNAVAILABLE
        self.product.name = self.filter_title(title, tree)

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

        self.title_parent_div = '//div[@id="detalii"]'
        self.title_div = 'h1[@class="product-title"]'
        # self.title_div = '//h1[@class="product-title"]/text()'


class EVOMagSpider(Spider):
    def __init__(self):
        super(EVOMagSpider, self).__init__('evomag')
        self.price_parent_div = '//div[@class="price_ajax"]'
        self.price_div = 'div[@class="pret_rons"]'

        self.title_parent_div = '//div[@class="product_right_inside slim"]'
        # self.title_div = '//h1[@class="product_name"]/text()'
        self.title_div = 'h1[@class="product_name"]'


class CelSpider(Spider):
    def __init__(self):
        super(CelSpider, self).__init__('cel')
        self.price_parent_div = '//div[@class="pret_tabela"]'
        self.price_div = 'span[@class="productPrice"]'

        #self.title_div = '//h2[@class="productName"]/text()'
        self.title_parent_div = '//div[@class="productWrapper"]'
        self.title_div = 'h2[@class="productName"]'


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

        # self.title_div = '//h1[@itemprop="name"]/text()'
        self.title_parent_div = '//form[@id="productForm"]'
        self.title_div = 'h1[@itemprop="name"]'

    def parse_data(self, url):
        status = self._request_url(url)
        if httplib.OK != status:
            return status

        tree = html.fromstring(self.result.content)

        product_node_tree = tree.xpath(self.price_parent_div)

        prod_price = 0
        price_data = []

        if not product_node_tree:
           return data.PRODUCT_UNAVAILABLE

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
        self.product.price = prod_price

        # get title
        title = self._get_title(tree)
        if not title:
            return data.PRODUCT_UNAVAILABLE
        self.product.name = title

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

        # self.title_div = '//div[@class="product-page-title page-product-title-wth"]/text()'
        self.title_parent_div = '//div[@class="product-details-padding visible-xs visible-sm"]'
        self.title_div = 'div[@class="product-page-title"]'

        self.brand_div = '//div[@class="product-page-brand"]'
        self.brand_name = './/a[@href]'

    def filter_title(self, title, tree):
        # detect and append brand name in product name
        brand_div = tree.xpath(self.brand_div)
        if brand_div:
            for element in brand_div[0].iter():
                brand_name = element.find(self.brand_name)
                if brand_name is not None:
                    title = brand_name.text.strip() + ' ' + title.strip()
                    break
        return title


class OtterSpider(Spider):
    def __init__(self):
        super(OtterSpider, self).__init__('otter')
        self.price_parent_div = '//div[@class="product-details-container"]'
        self.price_div = 'span[@class="price"]'

        # absolute path to title's parent div
        self.title_parent_div = '//div[@id="nume_produs"]'
        # relative path to title's parent div
        self.title_div = 'span[@class="h1"]'

    # price looks like: u'799,99 RON'
    def filter_price(self, price):
        price_tokens = price.split('RON')
        price = price_tokens[0]
        trimmedPrice = price.replace(',', '.')
        price = locale.atof(trimmedPrice)
        return price


class SpiderGenerator():

    def __init__(self):
        self.emag = EmagSpider()
        self.avstore = AVStoreSpider()
        self.evomag = EVOMagSpider()
        self.cel = CelSpider()
        self.germanos = GermanosSpider()
        self.quickmobile = QuickMobileSpider()
        self.otter = OtterSpider()

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
        elif name == 'otter':
            return self.otter