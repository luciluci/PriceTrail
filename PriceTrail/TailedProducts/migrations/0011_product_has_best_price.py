# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-03-30 08:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('TailedProducts', '0010_auto_20180329_0810'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='has_best_price',
            field=models.BooleanField(default=False),
        ),
    ]
