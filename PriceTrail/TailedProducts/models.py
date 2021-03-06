from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import json

class Product(models.Model):
    name = models.CharField(max_length=150)
    url = models.TextField()
    shop = models.CharField(max_length=50)
    available = models.BooleanField(default=True)
    current_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    best_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    has_best_price = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, default=1)
    date = models.DateField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class UserToProduct(models.Model):
    product = models.ForeignKey(Product, default=1)
    user = models.ForeignKey(User, default=1)

#object to be displayed and cached
class DisplayProduct():
    def __init__(self):
        self.id = 0
        self.name = ""
        self.date_prices = []
        self.shop = ""
        self.url = ""
        self.price = 0
        self.trend = "EQ"
        self.percent = 0
        self.available = True
        self.aff_url = ""

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

class DisplayDatePriceProduct():

    def __init__(self, date, price):
        self.date = date.strftime('%d, %b %Y')
        self.price = price