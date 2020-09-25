# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 02:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('people', '0019_auto_20171120_0210'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='sites',
        ),
        migrations.AddField(
            model_name='license',
            name='sites',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='license', to='sites.Site'),
        ),
    ]
