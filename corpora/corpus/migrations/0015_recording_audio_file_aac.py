# -*- coding: utf-8 -*-
# Generated by Django 1.10.8 on 2017-10-04 01:18
from __future__ import unicode_literals

import corpus.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0014_auto_20171003_0102'),
    ]

    operations = [
        migrations.AddField(
            model_name='recording',
            name='audio_file_aac',
            field=models.FileField(null=True, upload_to=corpus.models.upload_directory),
        ),
    ]
