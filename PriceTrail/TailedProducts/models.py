from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField(max_length=150)
    url = models.TextField()
    shop = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class ProductPrice(models.Model):
    product = models.ForeignKey(Product, default=1)
    date = models.DateField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

class UserToProduct(models.Model):
    product = models.ForeignKey(Product, default=1)
    user = models.ForeignKey(User, default=1)