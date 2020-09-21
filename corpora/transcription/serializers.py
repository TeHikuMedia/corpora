from django.core.exceptions import ValidationError

from transcription.models import \
    Transcription, TranscriptionSegment, AudioFileTranscription, \
    TranscriptionQualityControl

from people.helpers import get_person

from rest_framework import serializers
# from people.helpers import get_person
# from transcription.transcribe import transcribe_audio
from rest_framework.response import Response

from corpus.serializers import RecordingSerializer, SetPersonFromTokenWhenSelf

from transcription.transcribe import transcribe_audio_quick, calculate_word_probabilities

import logging
logger = logging.getLogger('corpora')


class TranscriptionSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = ('transcription', 'text', 'corrected_text', 'updated',
                  'source', )


class TranscriptionQualityControlHyperLinkedRelatedField(
        serializers.HyperlinkedRelatedField):

    def to_representation(self, value):
        self.view_name = 'api:{0}-detail'.format(
            value.__class__.__name__.lower()
            )
        return super(
            TranscriptionQualityControlHyperLinkedRelatedField,
            self
            ).to_representation(value)


class TranscriptionQualityControlSerializer(
        SetPersonFromTokenWhenSelf, serializers.ModelSerializer):
    content_object = TranscriptionQualityControlHyperLinkedRelatedField(
        read_only=True,
        view_name='api:sentence-detail'
        )

    class Meta:
        model = TranscriptionQualityControl
        fields = ('id', 'good', 'bad', 'approved', 'approved_by', 'updated',
                  'person', 'transcription',
                  'trash', 'follow_up', 'noise', 'star',
                  'machine', 'source', 'notes')


class TranscriptionQualityControRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        serializer = TranscriptionQualityControlSerializer(value, context=self.parent.context)
        return serializer.data


class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = (
            'recording', 'text', 'corrected_text',
            'id', 'source', 'updated',
            'transcriber_log', 'word_error_rate',
            'words', 'metadata')



class TranscriptionSegmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TranscriptionSegment
        fields = ('corrected_text', 'start', 'end', 'parent', 'edited_by',
                  'pk', 'no_speech_detected', 'transcriber_log')


class AudioFileTranscriptionSerializer(serializers.ModelSerializer):
    segments = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    metadata = serializers.SerializerMethodField(read_only=True)
    words = serializers.SerializerMethodField(read_only=True)
    model_version = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = AudioFileTranscription
        fields = (
            'uploaded_by', 'audio_file', 'pk', 'name',
            'transcription', 'segments', 'status', 'metadata', 'words',
            'model_version')
        read_only_fields = ('uploaded_by',)

    def get_segments(self, obj):
        return TranscriptionSegment.objects\
            .filter(parent=obj)\
            .values_list('pk', flat=True).order_by('pk')

    def get_status(self, obj):
        query = TranscriptionSegment.objects.filter(parent=obj)
        total = float(query.count())
        completed = float(query.filter(text__isnull=False).count())

        if total == 0:
            return {'status': 'waiting to transcribe', 'percent': 0}
        elif total == completed:
            return {'status': 'complete', 'percent': 100}
        else:
            return {
                'status': 'transcribing',
                'percent': int(round(completed/total*100))}

    def get_words(self, obj):
        try:
            return calculate_word_probabilities(obj.metadata)
        except Exception as e:
            logger.error(e)
            return None

    def get_metadata(self, obj):
        try:
            return obj.metadata
        except AttributeError:
            return None

    def get_model_version(self, obj):
        try:
            return obj.model_version
        except AttributeError:
            return None

    def validate_uploaded_by(self, validated_data):
        # if validated_data is None:
        return get_person(self.context['request'])
        # return validated_data

    def create(self, validated_data):
        request = self.context['request']
        validated_data['uploaded_by'] = get_person(request)

        method = request.GET.get('method', '')
        if 'stream' in method:
            logger.debug(type(validated_data['audio_file']))
            result = transcribe_audio_quick(validated_data['audio_file'])
            text = result['transcription'].strip()
            validated_data['transcription'] = text

            # For streaming, let's not create an AFT
            # Instead we should just have a log of a transcription
            # I meand we could keep the audio as well...
            aft = AudioFileTranscription()
            for key in validated_data.keys():
                setattr(aft, key, validated_data[key])

            try:
                aft.metadata = result['metadata']
            except KeyError:
                pass

            try:
                aft.model_version = result['model_version']
            except KeyError:
                pass

            # try:
            #     aft.save()
            # except:
            #     pass

            return aft

        if 'name' not in validated_data.keys():
            fname = validated_data['audio_file'].name
            validated_data['name'] = ''.join(fname.split('.')[:-1])

        return super(AudioFileTranscriptionSerializer, self).create(validated_data)

    # def validate_audio_file(self, validated_data):
    #     if validated_data is None:
    #         raise ValidationError('A file is required')
    #     return validated_data
