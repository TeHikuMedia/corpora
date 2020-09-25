# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import UserAPI, ApplicationAPI
# Register your models here.


@admin.register(UserAPI)
class UserAPIAdmi(admin.ModelAdmin):
    readonly_fields =('user','person', 'token',)
    list_display = ('user', 'token', 'enabled')
    list_editable = ('enabled',)

@admin.register(ApplicationAPI)
class UserAPIAdmi(admin.ModelAdmin):
    readonly_fields =('key',)
    list_display = ('user', 'key', 'enabled')

    