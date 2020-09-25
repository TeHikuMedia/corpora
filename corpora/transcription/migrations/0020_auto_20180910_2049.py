# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-09-10 08:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0019_auto_20180803_1823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcriptionsegment',
            name='end',
            field=models.PositiveIntegerField(editable=False, help_text='End time in hundreths of a second for audio segment'),
        ),
        migrations.AlterField(
            model_name='transcriptionsegment',
            name='start',
            field=models.PositiveIntegerField(editable=False, help_text='Start time in hundreths of a second for audio segment'),
        ),
    ]
