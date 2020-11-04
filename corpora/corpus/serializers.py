from corpus.models import (
    RecordingQualityControl, Sentence, Recording, Source, Text,
    SentenceQualityControl, RecordingMetadata
)
from rest_framework import serializers
from people.helpers import get_person
from rest_framework.response import Response
from django.utils.timezone import localtime

from django.core.files.base import ContentFile
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.conf import settings
from boto.s3.connection import S3Connection

from corpus.aggregate import build_qualitycontrol_stat_dict

from six import text_type
import base64
import uuid
import logging

logger = logging.getLogger('corpora')


class SetPersonFromTokenWhenSelf(object):
    def run_validation(self, data):
        d2 = None
        if 'person' in data.keys():
            if data['person'] == 'self':
                d2 = data.copy()
                person = get_person(self.context['request'])
                if person is not None:
                    d2['person'] = person.id
                else:
                    d2['person'] = None
        if d2 is None:
            d2 = data
        return super(SetPersonFromTokenWhenSelf, self).run_validation(d2)


class RecordingQualityControlHyperLinkedRelatedField(
        serializers.HyperlinkedRelatedField):

    def to_representation(self, value):
        self.view_name = 'api:{0}-detail'.format(
            value.__class__.__name__.lower()
        )
        return super(
            RecordingQualityControlHyperLinkedRelatedField,
            self
        ).to_representation(value)


class SentenceQualityControlHyperLinkedRelatedField(
        serializers.HyperlinkedRelatedField):

    def to_representation(self, value):
        self.view_name = 'api:{0}-detail'.format(
            value.__class__.__name__.lower()
        )
        return super(
            SentenceQualityControlHyperLinkedRelatedField,
            self
        ).to_representation(value)


class RecordingQualityControlSerializer(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):
    # recording = RecordingQualityControlHyperLinkedRelatedField(
    #     read_only=True,
    #     view_name='api:recording-detail'
    #     )

    class Meta:
        model = RecordingQualityControl
        fields = ('id', 'good', 'bad', 'approved', 'approved_by', 'updated',
                  'person', 'recording', 'content_type', 'object_id',
                  'trash', 'follow_up', 'noise', 'star',
                  'machine', 'source', 'notes', 'pronunciation')

    def validate(self, data):
        if 'content_type' in data and 'object_id' in data:
            if data['content_type'] and data['object_id']:
                if 'recording' in data['content_type'].name.lower():
                    try:
                        data['recording'] = Recording.objects.get(
                            pk=data['object_id'])
                    except ObjectDoesNotExist:
                        pass
        return super().validate(data)


class SentenceQualityControlSerializer(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):
    # sentence = SentenceQualityControlHyperLinkedRelatedField(
    #     read_only=True,
    #     view_name='api:sentence-detail'
    #     )

    class Meta:
        model = SentenceQualityControl
        fields = ('id', 'good', 'bad', 'approved', 'approved_by', 'updated',
                  'person', 'sentence', 'trash',
                  'machine', 'source', 'notes')


class RecordingQualityControRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = RecordingQualityControlSerializer(
            value, context=self.parent.context)
        return serializer.data


class SentenceQualityControRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = SentenceQualityControlSerializer(
            value, context=self.parent.context)
        return serializer.data


class ListenQualityControRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = RecordingQualityControlSerializer(
            value, context=self.parent.context)
        person = get_person(self.parent.context['request'])
        data = serializer.data
        return data
        if person is data['person']:
            return serializer.data
        else:
            return None


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ('author',
                  'id',
                  'description',
                  'source_name',
                  'source_type',
                  'url',
                  'source_url',
                  'added_by',)
        read_only_fields = ('added_by',)
        extra_kwargs = {
            'url': {'view_name': 'api:source-detail'}
        }
        validators = []

    def create(self, validated_data):
        try:
            source_obj, created = Source.objects.get_or_create(
                **validated_data)
        except Exception as e:
            raise Exception(e)
        return source_obj


class SentenceSerializer(serializers.HyperlinkedModelSerializer):
    quality_control = SentenceQualityControRelatedField(
        many=True,
        read_only=True,
    )
    text = serializers.CharField(max_length=1024, validators=[])
    # We set the validators to [] as this allows us to get the model
    # when one with text already exists

    def create(self, validated_data):
        try:
            sentence_obj, created = Sentence.objects.get_or_create(
                **validated_data)
        except Exception as e:
            raise Exception(e)
        return sentence_obj

    class Meta:
        model = Sentence
        fields = ('id', 'text', 'language',
                  'quality_control', 'updated', 'source')
        extra_kwargs = {
            'source': {'view_name': 'api:source-detail'}
        }


class SentenceSerializerNotNested(serializers.HyperlinkedModelSerializer):
    # quality_control = serializers.PrimaryKeyRelatedField(
    #     many=True,
    #     read_only=True
    # )

    class Meta:
        model = Sentence
        fields = ('id', 'text', 'language', 'source')
        extra_kwargs = {
            'source': {'view_name': 'api:source-detail'}
        }


class ReadSentenceSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Sentence
        fields = ('id', 'text', 'language',)


class RecordingSerializerPost(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):

    '''
    Okay, so we need to validate properly. We need to ensure a recording has a
    language associated with it unless we figure it out ourselves.
    right now we can post without a setnecne object and if the recording doesnt
    have a language we don't know the language.
    '''

    sentence = SentenceSerializerNotNested(
        many=False,
        read_only=True,
        required=False
    )

    class Meta:
        model = Recording
        fields = (
            'sentence_text', 'user_agent', 'audio_file',
            'person', 'id', 'sentence', 'private', 'language')

    def create(self, validated_data):
        # This sets a person even when you don't say person=self
        try:
            person = validated_data['person']
            if person is None:
                raise KeyError
        except KeyError:
            person = get_person(self.context['request'])
            if person is not None:
                validated_data['person'] = person

        recording = \
            super(RecordingSerializerPost, self).create(validated_data)

        # result = transcribe_audio(recording, validated_data['audio_file'])

        return recording
        # serializer = self.get_serializer(recording)
        # data = serializer.data
        # return Response(data)


class Base64FieldMixin(object):

    def _decode(self, data):
        if isinstance(data, text_type) and data.startswith('data:'):
            # base64 encoded file - decode
            # format ~= data:image/X,
            format, datastr = data.split(';base64,')
            ext = format.split('/')[-1]    # guess file extension
            if ext[:3] == 'svg':
                ext = 'svg'
            data = ContentFile(
                base64.b64decode(datastr),
                name='{}.{}'.format(uuid.uuid4(), ext)
            )

            logger.debug("Data as string?")
            logger.debug(data[0:10])

        elif isinstance(data, text_type) and data.startswith('http'):
            logger.debug("FAIL")
            raise SkipField()

        elif isinstance(data, text_type):
            logger.debug('WTF - last resort')
            data = ContentFile(
                base64.b64decode(data),
                name='{}.{}'.format(uuid.uuid4(), 'm4a')
            )

        return data

    def to_internal_value(self, data):
        try:
            logger.debug("Data as send to to_internal_value")
            logger.debug(data[0:10])
        except:
            pass

        data = self._decode(data)

        try:
            logger.debug("Data as decoded")
            logger.debug(data[0:10])
        except:
            pass

        return super(Base64FieldMixin, self).to_internal_value(data)


class Base64FileField(Base64FieldMixin, serializers.FileField):
    pass


class RecordingSerializerPostBase64(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):
    audio_file = Base64FileField()

    class Meta:
        model = Recording
        fields = (
            'sentence_text', 'user_agent', 'audio_file',
            'person', 'id', 'sentence')


class RecordingFetchSerializer(serializers.ModelSerializer):
    audio_file_url = serializers.SerializerMethodField()
    transcription = serializers.SerializerMethodField()
    person = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )
    sentence = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )
    quality_control_aggregate = serializers.SerializerMethodField()

    class Meta:
        model = Recording
        fields = ('person', 'sentence', 'audio_file_url',
                  'id', 'sentence_text', 'updated',
                  'audio_file_md5', 'audio_file_wav_md5',
                  'private', 'transcription', 'quality_control_aggregate',)
        depth = 1

    def get_audio_file_url(self, obj):
        return obj.get_recording_file_url(self.context['request'])

    def get_transcription(self, obj):
        t = obj.transcription_set.first()
        if t:
            return {'text': t.text, 'wer': t.word_error_rate}
        return None

    def get_quality_control_aggregate(self, obj):
        if hasattr(obj, 'metadata'):
            if 'quality_control_aggregate' in obj.metadata.metadata:
                return obj.metadata.metadata['quality_control_aggregate']
        return None


class RecordingSerializer(serializers.ModelSerializer):
    sentence = SentenceSerializerNotNested(
        many=False,
        read_only=True,
        required=False
    )
    person = serializers.PrimaryKeyRelatedField(
        many=False,
        read_only=True
    )
    # quality_control = RecordingQualityControRelatedField(
    #     many=True,
    #     read_only=True,
    # )
    audio_file_url = serializers.SerializerMethodField()
    quality_control_aggregate = serializers.SerializerMethodField()
    transcription = serializers.SerializerMethodField()
    word_error_rate = serializers.SerializerMethodField()
    # metadata = serializers.SerializerMethodField()

    class Meta:
        model = Recording
        fields = ('person', 'sentence', 'audio_file_url',  # 'quality_control',
                  'id', 'sentence_text', 'user_agent', 'updated',
                  'audio_file_md5', 'audio_file_wav_md5',
                  'quality_control_aggregate', 'transcription',
                  'word_error_rate', 'private', )  # 'metadata'

    def get_audio_file_url(self, obj):
        return obj.get_recording_file_url(self.context['request'])

    def get_quality_control_aggregate(self, obj):
        if hasattr(obj, 'metadata'):
            if 'quality_control_aggregate' in obj.metadata.metadata:
                return obj.metadata.metadata['quality_control_aggregate']

        return build_qualitycontrol_stat_dict(obj.quality_control.all())

    def get_transcription(self, obj):
        t = obj.transcription_set.first()
        if t:
            return t.text
        return None

    def get_word_error_rate(self, obj):
        t = obj.transcription_set.first()
        if t:
            return t.word_error_rate
        return None


class ListenSerializer(serializers.ModelSerializer):
    sentence = ReadSentenceSerializer(
        many=False,
        read_only=True
    )
    # quality_control = QualityControRelatedField(
    #     many=True,
    #     read_only=True,
    # )
    audio_file_url = serializers.SerializerMethodField()
    #CharField(source='get_recording_file_url', read_only=True)
    # quality_control_aggregate = serializers.SerializerMethodField()

    class Meta:
        model = Recording
        fields = (
            'sentence', 'audio_file_url', 'id', 'sentence_text',
        )

    def get_audio_file_url(self, obj):
        return obj.get_recording_file_url(self.context['request'])

    # def get_quality_control_aggregate(self, obj):
    #     return build_qualitycontrol_stat_dict(obj.quality_control.all())


class S3FileField(serializers.FileField):
    def get_redirect_url(self, **kwargs):
        if settings.ENVIRONMENT_TYPE == 'local':
            return kwargs['filepath']
        s3 = S3Connection(settings.AWS_ACCESS_KEY_ID_S3,
                          settings.AWS_SECRET_ACCESS_KEY_S3,
                          is_secure=True)
        # Create a URL valid for 60 seconds.
        return s3.generate_url(60, 'GET',
                               bucket=settings.AWS_STORAGE_BUCKET_NAME,
                               key=kwargs['filepath'])

    def to_representation(self, value):
        if value.name is '':
            return None
        user = self.context['request'].user
        if user.is_staff:
            return self.get_redirect_url(filepath=value.name)
        else:
            return value.name


class TextSerializer(serializers.ModelSerializer):
    source = SourceSerializer(required=False)
    original_file = S3FileField(required=False)
    cleaned_file = S3FileField(required=False)

    class Meta:
        model = Text
        fields = (
            'id',
            'primary_language', 'secondary_language', 'dialect',
            'copyright', 'description', 'notes',
            'config',
            'original_file', 'original_file_md5',
            'cleaned_file', 'cleaned_file_md5',
            'source', 'updated',
        )

    def create(self, validated_data):

        try:
            source = validated_data.pop('source')

            try:
                source_obj, created = Source.objects.get_or_create(**source)
            except Exception as e:
                raise Exception(e)

        except KeyError:
            source_obj = None
            pass

        if source_obj:
            text = Text.objects.create(source=source_obj, **validated_data)
        else:
            text = Text.objects.create(**validated_data)

        return text


class RecordingMetadataSerializer(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):

    class Meta:
        model = RecordingMetadata
        fields = ('recording', 'metadata', 'id')
