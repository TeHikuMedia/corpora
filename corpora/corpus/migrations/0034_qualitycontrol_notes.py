# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-07-27 03:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0033_recording_audio_file_md5'),
    ]

    operations = [
        migrations.AddField(
            model_name='qualitycontrol',
            name='notes',
            field=models.TextField(blank=True, help_text='Field for providing extra information about a review.', null=True),
        ),
    ]
