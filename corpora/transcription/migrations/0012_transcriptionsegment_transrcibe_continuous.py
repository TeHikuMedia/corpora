# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-06-23 01:44
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transcription', '0011_transcriptionsegment_transcriber_error'),
    ]

    operations = [
        migrations.AddField(
            model_name='transcriptionsegment',
            name='transrcibe_continuous',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
    ]
