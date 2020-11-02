from django.contrib import admin

from .models import \
    Person, Demographic, KnownLanguage,\
    Tribe, Group

from django.db.models import Count

from people.forms import DemographicFormAdmin
from corpus.models import Recording


class PersonRecordingsInline(admin.StackedInline):
    model = Recording
    extra = 0
    can_delete = True
    fields = ['sentence', 'sentence_text', 'user_agent', 'audio_file_admin']
    readonly_fields = ['user_agent', 'audio_file_admin']
    raw_id_fields = ('sentence', )
    # def myaudio_file_admin(self, obj):
    #     return obj.audio_file_admin()


class PersonGroupInline(admin.TabularInline):
    model = Person.groups.through
    extra = 0
    raw_id_fields = ('group', )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'username',
        'email',
        'user',
        'uuid',
        'score',
        'get_groups'
    )
    raw_id_fields = ('user', )
    readonly_fields = (
        'profile_email', 'score_comp', 'num_recordings', 'num_reviews',
        'num_reviews_comp', 'num_recordings_comp')
    inlines = [PersonRecordingsInline, PersonGroupInline]
    exclude = ('groups', )  # see PersonGroupInline
    search_fields = [
        'username', 'profile_email', 'user__username', 'user__email',
        'full_name', 'user__emailaddress__email']

    def get_groups(self, obj):
        return ', '.join([g.name for g in obj.groups.all()])
    get_groups.short_description = 'groups'


@admin.register(Demographic)
class DemographicAdmin(admin.ModelAdmin):
    form = DemographicFormAdmin
    list_display = (
        'person',
        'gender',
        'age',
        'tribe_names')


@admin.register(KnownLanguage)
class KnownLanguageAdmin(admin.ModelAdmin):
    list_display = (
        'person',
        'language',
        'level_of_proficiency',
        'dialect',
        'accent',
        'active',
    )


class MembershipInline(admin.TabularInline):
    extra = 0
    model = Person.groups.through
    raw_id_fields = ('person', )


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'created_by', 'score')
    readonly_fields = \
        ('score', 'num_recordings', 'created', 'created_by', 'duration')
    inlines = [MembershipInline]


@admin.register(Tribe)
class TribeAdmin(admin.ModelAdmin):
    list_display = ('name', 'number_members')

    def get_queryset(self, request):
        qs = super(TribeAdmin, self).get_queryset(request)
        return qs.annotate(num_members=Count('demographic'))

    def number_members(self, obj):
        return obj.num_members
    number_members.short_description = 'Number of Members'
    number_members.admin_order_field = 'num_members'
