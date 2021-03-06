# Generated by Django 2.2.5 on 2019-09-24 05:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reo_api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationAPI',
            fields=[
                ('name', models.CharField(max_length=256)),
                ('key', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='App Token')),
                ('enabled', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'key')},
            },
        ),
    ]
