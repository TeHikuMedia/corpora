# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-17 09:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0045_auto_20180917_2146'),
    ]

    operations = [
        migrations.RenameField(
            model_name='Text',
            old_name='uploaded_file',
            new_name='original_file',
        ),
        migrations.RenameField(
            model_name='Text',
            old_name='language',
            new_name='primary_language',
        ),
    ]
