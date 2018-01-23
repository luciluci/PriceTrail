from lxml import html

import httplib
import requests
import ssl

class Product():

     def __init__(self):
         self.name = ''
         self.price = ''

class EmagSpider():

    def __init__(self):
        self.product = Product()

    def req_product(self, url):
        if not url.startswith('https://www.emag.ro'):
            return httplib.NOT_IMPLEMENTED
        try:
            result = requests.get(url)
        except ssl.SSLError:
            return httplib.INTERNAL_SERVER_ERROR

        if result.status_code != 200:
            return result.status_code

        tree = html.fromstring(result.content)
        product_new_price = tree.xpath('//p[@class="product-new-price"]/text()')
        page_title = tree.xpath('//h1[@class="page-title"]/text()')

        if not product_new_price or not page_title:
            return httplib.NO_CONTENT

        #assume it's the first element in the array
        prod_price_str = product_new_price[0]
        self.product.price = prod_price_str.replace('.', '').strip()
        self.product.name  = page_title[0].strip()

        return httplib.OK

    def get_product(self):
        return self.product