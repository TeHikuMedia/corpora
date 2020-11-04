from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.db import models

from django.contrib import messages

from corpus.models import (
    RecordingQualityControl, Sentence, Recording, Source, Text,
    SentenceQualityControl, RecordingMetadata
)
from corpus.tasks import transcode_audio
import time
from corpus.views.views import RecordingFileView
from .parser import save_sentences_from_text
from .helpers import approve_sentence


class RecordingQualityControlInline(admin.TabularInline):
    # max_num = 1
    extra = 0
    can_delete = False
    model = RecordingQualityControl
    raw_id_fields = ('person', 'approved_by', 'source', 'recording')


class SentenceQualityControlInline(admin.TabularInline):
    # max_num = 1
    extra = 0
    can_delete = False
    model = SentenceQualityControl
    raw_id_fields = ('person', 'approved_by', 'source', 'sentence')


class RecordingsInline(admin.TabularInline):
    extra = 0
    can_delete = False
    model = Recording
    raw_id_fields = ('person', 'source')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RecordingQualityControl)
class RecordingQualityControlAdmin(admin.ModelAdmin):
    list_display = ('recording', 'updated',
                    'good', 'bad', 'calculate_score',
                    'approved', 'trash', 'follow_up', 'noise', 'star')
    date_hierarchy = 'updated'
    raw_id_fields = ('person', 'approved_by', 'recording')
    list_filter = ('recording__language', 'updated')

@admin.register(SentenceQualityControl)
class SentenceQualityControlAdmin(admin.ModelAdmin):
    list_display = ('sentence', 'updated', 'good', 'bad',
                    'approved', 'approved_by', 'trash', )
    date_hierarchy = 'updated'
    raw_id_fields = ('person', 'approved_by', 'sentence')
    list_filter = ('sentence__language', 'updated', )

@admin.register(Sentence)
class SentenceAdmin(admin.ModelAdmin):
    list_display = ('text', 'source', 'updated', 'get_approved',
                    'get_approved_by', 'num_recordings')
    inlines = [SentenceQualityControlInline, RecordingsInline]
    search_fields = ['text']
    actions = ('approve_sentences',)
    list_filter = ('language', 'updated', )

    def get_queryset(self, request):
        qs = super(SentenceAdmin, self).get_queryset(request)
        qs = qs\
            .annotate(sum_approved=models.Sum(
                models.Case(
                    models.When(
                        quality_control__isnull=True,
                        then=models.Value(0)),
                    models.When(
                        quality_control__approved=True,
                        then=models.Value(1)),
                    models.When(
                        quality_control__approved=False,
                        then=models.Value(0)),
                    default=models.Value(0),
                    output_field=models.IntegerField())))
        return qs

    def get_approved(self, obj):
        return obj.sum_approved
    get_approved.short_description = 'Approvals'
    get_approved.admin_order_field = 'sum_approved'

    def get_approved_by(self, obj):
        qc = obj.quality_control
        results = qc.all()
        names = []
        if len(results) > 0:
            for r in results:
                if r.approved_by:
                    names.append(str(r.approved_by))
            return ', '.join(names)
        else:
            return _("None")
    get_approved_by.short_description = 'Approved By'
    get_approved_by.admin_order_field = 'quality_control__approved'

    def num_recordings(self, obj):
        return Recording.objects.filter(sentence=obj).count()
    num_recordings.short_description = '# Recordings'
    num_recordings.admin_order_field = 'recording__count'

    def approve_sentences(self, request, queryset):
        count = 0
        for sentence in queryset:
            count = count + 1 if approve_sentence(request, sentence) else count
        messages.add_message(
            request, messages.INFO,
            '{0} sentence(s) of {1} sentence(s) approved.'.format(
                count, queryset.count())
        )


@admin.register(Recording)
class RecordingAdmin(admin.ModelAdmin):
    list_display = (
        'sentence_text',
        'person',
        'get_approved',
        # 'get_approved_by',
        'calculate_score',
        'created',
        'private',
    )
    list_editable = (
        'private',
    )

    inlines = [RecordingQualityControlInline]

    readonly_fields = (
        'duration',
        'audio_file',
        'audio_file_aac',
        'audio_file_wav',
        'audio_file_admin',
        'updated',
        'created',
    )

    list_filter = ('language', 'created', 'quality_control__approved', 'quality_control__trash',)


    raw_id_fields = ('person', 'sentence')

    search_fields = [
        'person__user__email',
        'person__full_name',
        'person__user__username']

    actions = ('encode_audio',)

    def audio_file_aac(self, obj):
        return 'test'

    def get_queryset(self, request):
        qs = super(RecordingAdmin, self).get_queryset(request)
        qs = qs\
            .annotate(sum_approved=models.Sum(
                models.Case(
                    models.When(
                        quality_control__isnull=True,
                        then=models.Value(0)),
                    models.When(
                        quality_control__approved=True,
                        then=models.Value(1)),
                    models.When(
                        quality_control__approved=False,
                        then=models.Value(0)),
                    default=models.Value(0),
                    output_field=models.IntegerField())))
        return qs

    def get_approved(self, obj):
        return obj.sum_approved
    get_approved.short_description = 'Approvals'
    # This could be cuasing the long response for admin as it would need to
    # run this on ALL rows for sort!
    # get_approved.admin_order_field = 'sum_approved'

    def get_approved_by(self, obj):
        qc = obj.quality_control
        results = qc.all()
        names = []
        if len(results) > 0:
            for r in results:
                if r.approved_by:
                    names.append(str(r.approved_by))
            return ', '.join(names)
        else:
            return _("None")
    get_approved_by.short_description = 'Approved By'
    get_approved_by.admin_order_field = 'quality_control__approved'

    def encode_audio(self, request, queryset):
        for obj in queryset:
            transcode_audio.apply_async(
                    args=[obj.pk, ],
                    task_id='transcode_audio-{0}-{1}'.format(
                        obj.pk,
                        time.strftime('%d%m%y%H%M%S'))
                    )
            messages.add_message(
                request, messages.INFO,
                'Sent encode task for {0}.'.format(obj))
    encode_audio.short_description = "Encode audio"



@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    actions = ('delete_unapproved',)

    def delete_unapproved(self, request, queryset):
        for obj in queryset:
            sentences = Sentence.objects\
                .filter(source=obj)\
                .annotate(sum_approved=models.Sum(
                    models.Case(
                        models.When(
                            quality_control__isnull=True,
                            then=models.Value(0)),
                        models.When(
                            quality_control__approved=True,
                            then=models.Value(1)),
                        models.When(
                            quality_control__approved=False,
                            then=models.Value(0)),
                        default=models.Value(0),
                        output_field=models.IntegerField())))\
                .filter(sum_approved=0)
            num_to_delete = sentences.count()
            sentences.delete()
            messages.add_message(
                request, messages.INFO,
                'Deleted {0} sentences from source {1}.'.format(
                    num_to_delete, obj))
    delete_unapproved.short_description = "Delete all upapproved sentences."


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = (
        'source', 'original_file', 'cleaned_file',
        'description', 'notes',
        'primary_language', 'secondary_language', 'dialect',
        'copyright', 'config', 'updated', )
    readonly_fields = ('updated', 'original_file_md5', 'cleaned_file_md5',)
    raw_id_fields = ('source', )
    actions = ('save_sentences', )
    list_filter = ('primary_language',)

    def save_sentences(self, request, queryset):
        for obj in queryset:
            info = save_sentences_from_text(obj)
            messages.add_message(
                request, messages.INFO,
                '%s sentences created from %s (%s errors)' % (
                    info['saved'], obj, info['errors']))


@admin.register(RecordingMetadata)
class RecordingMetadataAdmin(admin.ModelAdmin):
    list_display = ('recording', 'updated', 'created')
    raw_id_fields = ('recording',)
