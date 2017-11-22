# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 02:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('people', '0018_auto_20171115_0256'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='sites',
            field=models.ManyToManyField(blank=True, null=True, related_name='license', to='sites.Site'),
        ),
        migrations.AlterField(
            model_name='demographic',
            name='sex',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('TF', 'Transexual (Male to Female)'), ('TM', 'Transexual (Female to Male)')], help_text='Gender', max_length=2, null=True),
        ),
    ]