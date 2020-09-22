from django.utils.translation import ugettext_lazy as _
from transcription.models import \
    Transcription, TranscriptionSegment, AudioFileTranscription
from transcription.serializers import \
    TranscriptionSerializer,\
    TranscriptionSegmentSerializer,\
    AudioFileTranscriptionSerializer

from reo_api.models import UserAPI
from rest_framework import viewsets, permissions, pagination
from rest_framework.response import Response

from people.helpers import get_person
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from corpus.views.api import TenResultPagination, OneHundredResultPagination

from transcription.utils import build_vtt, compile_aft
from transcription.transcribe import transcribe_segment

from transcription.tasks import transcribe_recording

import logging
logger = logging.getLogger('corpora')


class UserAPIPermissions(permissions.BasePermission):
    '''
    We're not using a new model for access to this API. This is a 
    temporary implementation to now close the API until we move
    things to somethign better.
    '''
    message = "Public beta testing is now closed. Please contact koreromaori@tehiku.nz for developer access."

    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        u, created = UserAPI.objects.get_or_create(user=request.user)
        return u.enabled


class TranscriptionPermissions(permissions.BasePermission):
    """
    Model permission to only allow staff the ability to
    get transcriptions and everyone the ability to post
    audio for transcriptions and only a person can access
    their own transcriptions..
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # TODO: Allow people to get a list of THEIR transcriptions.
            self.message = _("Only staff can read transcription lists.")
            return request.user.is_staff
        else:
            # Anyone can post a transcription
            if request.method in ['POST', 'PUT']:
                return True
        self.message = _("Reading transcription lists not allowed.")
        return False

    def has_object_permission(self, request, view, obj):
        person = get_person(request)

        if request.method in permissions.SAFE_METHODS:
            self.message = _("Only staff can read transcriptions.")
            if request.user.is_staff:
                person = get_person(request)
                cache.set(
                    '{0}:{0}:listen'.format(person.uuid, obj.recording.id), True, 15)
                return True
            elif person is not None:
                # Allow people to get their own transcriptions.
                return person == obj.recording.person
        else:
            if request.method in ['PUT']:
                if request.user.is_staff:
                    return True
                if person is not None:
                    self.message = _(
                        "You're not allowed to edit this transcription.")
                    return person == obj.recording.person
        self.message = _("Reading transcriptions is not allowed.")
        return False


class TranscriptionViewSet(viewsets.ModelViewSet):
    """
    This API Endpoint is for the automatic transcriptions of recordings
    that the backend does. This helps us more efficiently review
    recordings based on their word error rate calculated from the
    transcription.

    ### Query Parameters
    - `filter`: Filter results by the following,
       - `recording:ID`: Filter result by recording id.
    """

    # TODO: Allow someone to get a list of ALL of their transcriptions.

    queryset = Transcription.objects.all()
    serializer_class = TranscriptionSerializer
    permission_classes = (UserAPIPermissions, TranscriptionPermissions)
    pagination_class = OneHundredResultPagination

    def get_queryset(self):
        person = get_person(self.request)
        queryset = Transcription.objects\
            .all()\
            .order_by('-updated')

        filter_by = self.request.query_params.get('filter')
        filt = None
        value = None
        if filter_by:
            parts = filter_by.split(':')
            if len(parts)==2:
                filt = parts[0].lower()
                value = parts[1]
                if filt == 'recording':
                    queryset = queryset.filter(recording__pk=value)

        logger.debug(queryset)
        if self.request.user.is_superuser and len(queryset)<2:
            if len(queryset) == 0:
                if filt=='recording':
                    transcribe_recording(value)
            elif queryset[0].metadata is None:
                # Let's transcribe this recording again
                # under this very certain circumstance
                # which is Pronunciation analysis
                transcribe_recording(queryset[0].pk)
        transcribe_recording(value)
        return queryset


class TranscriptionSegmentPermissions(permissions.BasePermission):
    """
    API permissions for Transcription Segments model.
    Only staff get get entire lists from TS.
    Anyone can PUT a TS object - but only if they OWN the object?
    """

    def has_permission(self, request, view):
        person = get_person(request)
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_staff:
                return True
            elif person is not None:
                return request.user.is_authenticated
            return False
        else:
            if request.method in ['PUT']:
                return request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        person = get_person(request)
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_staff:
                return True
            elif person is not None:
                return person == obj.parent.uploaded_by
        else:
            if request.method in ['PUT']:
                if request.user.is_staff:
                    return True
                if person is not None:
                    return person == obj.parent.uploaded_by
        return False


class TranscriptionSegmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Transcription Segments to be viewed or edited.
    """

    queryset = TranscriptionSegment.objects.all()
    serializer_class = TranscriptionSegmentSerializer
    permission_classes = (UserAPIPermissions, TranscriptionSegmentPermissions)
    pagination_class = TenResultPagination

    def get_queryset(self):
        person = get_person(self.request)
        queryset = TranscriptionSegment.objects\
            .filter(parent__uploaded_by=person)\
            .order_by('start')\
            .order_by('-parent__created')

        return queryset

    def retrieve(self, request, pk=None):
        ts = get_object_or_404(self.get_queryset(), pk=pk)

        if (ts.text is None and
                ts.edited_by is None and
                not ts.parent.ignore and not ts.no_speech_detected):
            transcribe_segment(ts)

        serializer = self.serializer_class(ts)

        response = Response(serializer.data)

        return response


class AudioFileTranscriptionPermissions(permissions.BasePermission):
    """
    API permissions for Audio File Transcriptions model.
    """

    def has_permission(self, request, view):
        person = get_person(request)
        if request.method in permissions.SAFE_METHODS:

            if request.user.is_staff:
                return True
            elif person is not None:
                return request.user.is_authenticated
            return False
            # return request.user.is_staff
        else:
            # Anyone can post a transcription
            if request.method in ['POST', 'PUT', 'DELETE']:
                return request.user.is_authenticated

        return False

    def has_object_permission(self, request, view, obj):
        person = get_person(request)

        if request.method in permissions.SAFE_METHODS:
            if request.user.is_staff:
                return True
            elif person is not None:
                # Allow people to get their own TS objects.
                return person == obj.uploaded_by
        else:
            if request.method in ['PUT', 'DELETE']:
                if request.user.is_staff:
                    return True
                if person is not None:
                    return person == obj.uploaded_by
        return False


class AudioFileTranscriptionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Audio File Transcriptions (AFT) to be viewed or
    edited.

    retrieve:
    Return an AFT object.

    list:
    Return a list of all AFT objects.

    create:
    Create an AFT.

    # Downloading Transcriptions #
    You can download the full transcription by appending `.format` to
    the API endpoint. For example, to download a plain text file of a
    transcription call `/api/transcription/123.txt`.

    Supported formats are,

    -  `txt`: A plain text file with all transcription segments joined by a
    space
    - `vtt`: A webvtt formatted file which includes timestamps. This file
      can be used as captions.

    """

    queryset = AudioFileTranscription.objects.all()
    serializer_class = AudioFileTranscriptionSerializer
    permission_classes = (UserAPIPermissions, AudioFileTranscriptionPermissions)
    pagination_class = TenResultPagination

    def get_queryset(self):
        person = get_person(self.request)
        queryset = AudioFileTranscription.objects\
            .filter(uploaded_by=person)

        return queryset

    def retrieve(self, request, pk, format=None):
        # return format
        if format:
            if format in 'txt':
                aft = self.get_object()
                compile_aft(aft.pk)
                return Response(aft.transcription)
            if format in 'vtt':
                aft = self.get_object()
                return Response(build_vtt(aft))
        #     return 'False'
        return super(AudioFileTranscriptionViewSet, self).retrieve(request, pk)
