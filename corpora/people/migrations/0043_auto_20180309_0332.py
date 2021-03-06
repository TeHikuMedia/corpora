# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-09 03:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0042_auto_20180307_0610'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='Choose a group, or enter a group name to create a new one.', to='people.Group'),
        ),
    ]
