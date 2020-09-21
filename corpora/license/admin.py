from django.contrib import admin

from .models import \
    License, AcceptLicense, SiteLicense


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
	list_display = (
		'license_name', 'language'
		)


@admin.register(AcceptLicense)
class AcceptLicenseAdmin(admin.ModelAdmin):
    list_display = (
        'person',
        'license_names'
        )


@admin.register(SiteLicense)
class SiteLicenseAdmin(admin.ModelAdmin):
    list_display = (
        'site',
        'license'
    )
