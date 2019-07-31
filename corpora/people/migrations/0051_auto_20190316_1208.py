# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-03-15 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0050_auto_20181204_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='knownlanguage',
            name='language',
            field=models.CharField(choices=[(b'mi', 'Maori'), (b'haw', 'Hawaiian'), (b'smo', 'Samoan'), (b'rar', 'Cook Island Maori')], max_length=16, verbose_name='language'),
        ),
    ]