# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.db import models

from django.contrib import messages
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Message, MessageAction


class MessageActionInline(admin.TabularInline):
    extra = 0
    model = MessageAction


@admin.register(MessageAction)
class MessageActionAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    inlines = [MessageActionInline]
    list_display = ('subject', 'id')
