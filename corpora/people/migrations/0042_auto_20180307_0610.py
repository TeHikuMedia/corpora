# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-03-07 06:10
from __future__ import unicode_literals

from django.db import migrations


def set_default_daily_subscription_to_false(apps, schema_editor):
    Person = apps.get_model('people', 'Person')
    for person in Person.objects.all():
        person.receive_daily_updates = False
        person.save()


def reverse_above(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0041_auto_20180306_2345'),
    ]

    operations = [
        migrations.RunPython(set_default_daily_subscription_to_false, reverse_code=reverse_above),
    ]
