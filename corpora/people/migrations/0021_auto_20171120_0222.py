# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 02:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('people', '0020_auto_20171120_0216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='sites',
        ),
        migrations.AddField(
            model_name='license',
            name='sites',
            field=models.ManyToManyField(blank=True, null=True, related_name='license', to='sites.Site'),
        ),
    ]
