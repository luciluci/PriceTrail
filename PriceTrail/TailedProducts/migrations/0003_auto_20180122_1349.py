# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2018-01-22 13:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('TailedProducts', '0002_product_user_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='date',
        ),
        migrations.RemoveField(
            model_name='product',
            name='price',
        ),
        migrations.RemoveField(
            model_name='product',
            name='user_name',
        ),
    ]
