# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-27 07:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0050_auto_20181204_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='demographic',
            name='tribe',
            field=models.ManyToManyField(blank=True, help_text='Which tribe(s) do you identify with?', to='people.Tribe', verbose_name='tribe'),
        ),
    ]
