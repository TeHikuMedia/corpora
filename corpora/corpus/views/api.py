from django.utils.dateparse import parse_datetime
from django.utils.translation import ugettext_lazy as _
from corpus.models import (
    RecordingQualityControl, Sentence, Recording, Source, Text,
    SentenceQualityControl, RecordingMetadata
)
from django.db.models import \
    Count, Q, Sum, Case, When, Value, IntegerField, Max,\
    Prefetch
from django.db.models.functions import Length

from django.contrib.contenttypes.models import ContentType

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie

from people.helpers import get_person, get_current_language

from people.competition import \
    filter_qs_for_competition, \
    filter_recordings_to_top_ten, \
    filter_recordings_distribute_reviews
from corpus.helpers import get_next_sentence
from rest_framework import viewsets, permissions, pagination

from corpus.serializers import (
    RecordingQualityControlSerializer,
    SentenceQualityControlSerializer,
    SentenceSerializer,
    RecordingSerializer,
    RecordingFetchSerializer,
    RecordingSerializerPost,
    RecordingSerializerPostBase64,
    ListenSerializer,
    SourceSerializer,
    TextSerializer,
    RecordingMetadataSerializer
)

from rest_framework import generics, serializers
from rest_framework.parsers import JSONParser, FormParser, MultiPartParser
from django.core.cache import cache
import random
import logging

from django.conf import settings
LANGUAGES = settings.LANGUAGES


logger = logging.getLogger('corpora')


class ViewSetCacheMixin(object):
    cache_length = 60

    def list(self, request, *args, **kwargs):
        sort_by = self.request.query_params.get('sort_by', None)
        if sort_by is None:
            return self.cached_list(request, *args, **kwargs)
        else:
            return super(ViewSetCacheMixin, self)\
                .list(request, *args, **kwargs)

    @method_decorator(cache_page(cache_length))
    @method_decorator(vary_on_headers('Authorization', 'Cookie'))
    def cached_list(self, request, *args, **kwargs):
        return super(ViewSetCacheMixin, self)\
            .list(request, *args, **kwargs)

    @method_decorator(cache_page(cache_length))
    @method_decorator(vary_on_headers('Authorization', 'Cookie'))
    def retrieve(self, request, *args, **kwargs):
        return super(ViewSetCacheMixin, self)\
            .retrieve(request, *args, **kwargs)


class OneHundredResultPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'


class OneResultPagination(pagination.PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page_size'


class TenResultPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class PutOnlyStaffReadPermission(permissions.BasePermission):
    """
    Model permission to only allow staff the ability to
    get and everyone the ability to post/put.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            self.message = _("Only staff can {0}.".format(
                permissions.SAFE_METHODS))
            return request.user.is_staff
        else:
            # Anyone can post
            if request.method in ['PUT', 'POST']:
                return True
            else:
                self.message = _("PONIES Method {0} not allowed.".format(
                    request.method))
                return request.user.is_staff


class RecordingQualityControlViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows qc to be viewed or edited.
    """
    queryset = RecordingQualityControl.objects.all()
    serializer_class = RecordingQualityControlSerializer
    permission_classes = (PutOnlyStaffReadPermission,)
    pagination_class = OneHundredResultPagination


class SentenceQualityControlViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows qc to be viewed or edited.
    """
    queryset = SentenceQualityControl.objects.all()
    serializer_class = SentenceQualityControlSerializer
    permission_classes = (PutOnlyStaffReadPermission,)
    pagination_class = OneHundredResultPagination


class SourceViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    list:
    Returns a list of all Sources.

    Supported query parameters: `author`

    - `author=name` returns a list of all sources which contain 'name'
      in their author field.

    create:

    - `source_type` is one of,
        ('W', 'Website'),
        ('A', 'Article'),
        ('B', 'Book'),
        ('I', 'Interview'),
        ('S', 'Self'),
        ('D', 'Document'),
        ('M', 'Machine'),

    When creating Sources for Machines, use the following convention.

    - `source_type: 'M'`
    - `author`: Use an API version string for the particular API that belongs
    to the machine. For example, 'nga-korero-hohonu.1.0.2018-06-13' is the API
    version string for a particular Machine Transcription model.
    - `source_name`: For machines that transcrinbe, use 'Transcription API.'
    For machines that review, use 'Review API', etc.

    Sources are unique by `source_type`, `author`, `source_url`, and `source_name. If you
    can't create a source because it already exists, use `list` to find the
    source id.
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = OneHundredResultPagination

    def get_queryset(self):
        queryset = Source.objects.all()
        filter_author = self.request.query_params.get('author', None)
        if filter_author:
            queryset = queryset.filter(author__icontains=filter_author)

        return queryset


class TextViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    list:
    Returns a list of all Texts.

    Supported query parameters: None yet...

    create:
    todo

    read:
    todo


    """
    queryset = Text.objects.all()
    serializer_class = TextSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = OneHundredResultPagination


# OBSOLETE???
class SentenceViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows sentences to be viewed or edited.
    """
    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = OneHundredResultPagination


class IsStaffOrReadOnly(permissions.BasePermission):
    """
    Model permission to only allow staff the ability to
    edit and post new sentences.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only admins can edit sentences
        else:
            self.message = _("Only staff can post/put sentences.")
            return request.user.is_staff


class SentencePermission(permissions.BasePermission):
    """
    Model permission to only allow staff the ability to
    edit and post new sentences.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            q = request.query_params.get('recording', 'False')
            if eval(q):
                return True
            self.message = _("Only staff can get sentence lists.")
            return request.user.is_staff
        else:
            # Anyone can post a recording
            if request.method in ['POST', 'PUT']:
                return True
        self.message = _("Reading recording lists not allowed.")
        return False

    def has_object_permission(self, request, view, obj):
        person = get_person(request)

        if request.method in permissions.SAFE_METHODS:
            self.message = _("Only staff can read recordings.")
            if request.user.is_staff:
                person = get_person(request)
                cache.set('{0}:{1}:listen'.format(
                    person.uuid, obj.id), True, 15)
                logger.debug(
                    'SET KEY '+'{0}:{1}:listen'.format(person.uuid, obj.id))
                return True
            elif person is not None:
                # Allow people to get their own recordings.
                return person == obj.person
        else:
            if request.method in ['PUT']:
                if request.user.is_staff:
                    return True
                if person is not None:
                    self.message = _(
                        "You're not allowed to edit this recording.")
                    return obj.person == person
        self.message = _("Reading recording is not allowed.")
        return False


class SentencesView(generics.ListCreateAPIView):
    """
    API endpoint that allows sentences to be viewed or edited.

    ### Supported Query Parameters
      - `recording=True`: This will return a random, approved sentence that a person hasn't read.
      - `recording_paginated=True`: This will return multiple sentences that a person hasn't read.
      - `quality_control__approved=True`: This returns all approved sentences.
      - `sort_by`: The following sorting options are implemented. Use `-` in front of the string to reverse.
        - `num_recordings`


    """

    queryset = Sentence.objects.all()
    serializer_class = SentenceSerializer
    pagination_class = OneHundredResultPagination
    permission_classes = (SentencePermission, IsStaffOrReadOnly)
    throttle_scope = 'sentence'

    def get_queryset(self):

        person = get_person(self.request)
        language = get_current_language(self.request)

        q = self.request.query_params.get('language', None)
        if q:
            for l in LANGUAGES:
                if q == l[0]:
                    language = q

        logger.debug(language)
        queryset = Sentence.objects.filter(language=language)\
            .order_by('quality_control__approved', 'quality_control__updated')

        q = self.request.query_params.get('recording', 'False')
        if 'True' in q:
            sentence = get_next_sentence(self.request)
            if sentence:
                queryset = [sentence]
            else:
                return []

        else:

            query = self.request.query_params.get(
                'quality_control__approved')
            if query:
                queryset = queryset.annotate(sum_approved=Sum(
                    Case(
                        When(
                            quality_control__approved=True,
                            then=Value(1)),
                        When(
                            quality_control__approved=False,
                            then=Value(0)),
                        When(
                            quality_control__isnull=True,
                            then=Value(0)),
                        default=Value(0),
                        output_field=IntegerField())
                ))
                try:
                    if eval(query) is True:
                        queryset = queryset\
                            .filter(sum_approved__gte=1)\
                            .order_by('-updated')
                    elif eval(query) is False:
                        queryset = queryset\
                            .filter(sum_approved__lte=0)\
                            .annotate(text_length=Length('text'))\
                            .filter(text_length__gte=12)\
                            .order_by('-updated')\
                            .order_by(Length('text').asc())
                    else:
                        raise ValueError(
                            "Specify either True or False for \
                            quality_control__approved=")
                except:
                    raise ValueError(
                        "Specify either True or False for \
                        quality_control__approved=")

            query = self.request.query_params.get(
                'recording_paginated', 'False')
            if eval(query):
                queryset = queryset.exclude(recording__person=person)

            query = self.request.query_params.get(
                'sort_by', '')

            if query in 'num_recordings -num_recordings':
                queryset = queryset.annotate(Count('recording'))
                if query == '-num_recordings':
                    queryset = queryset.order_by('-recording__count')
                else:
                    queryset = queryset.order_by('recording__count')

            if query in 'num_approved_recordings -num_approved_recordings':
                queryset = queryset\
                    .annotate(Count('recording'))\
                    .annotate(num_approved_recordings=Sum(
                        Case(
                            When(
                                recording__quality_control__approved=True,
                                then=Value(1)),
                            When(
                                recording__quality_control__approved=False,
                                then=Value(0)),
                            When(
                                recording__quality_control__isnull=True,
                                then=Value(0)),
                            default=Value(0),
                            output_field=IntegerField())
                    ))
                if query == '-num_approved_recordings':
                    queryset = queryset.order_by(
                        '-recording__count', '-num_approved_recordings')
                else:
                    queryset = queryset.order_by(
                        'recording__count', 'num_approved_recordings')

        return queryset


class RecordingPermissions(permissions.BasePermission):
    """
    Model permission to only allow staff the ability to
    get recordings and everyone the ability to post
    recordings and only a person can delete their
    own recording.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            self.message = _("Only staff can read recording lists.")
            return request.user.is_staff
        else:
            # Anyone can post a recording
            if request.method in ['POST', 'PUT']:
                return True
        self.message = _("Reading recording lists not allowed.")
        return False

    def has_object_permission(self, request, view, obj):
        person = get_person(request)
        if request.method in permissions.SAFE_METHODS:
            self.message = _("Only staff can read recordings.")
            if request.user.is_staff:
                person = get_person(request)
                cache.set('{0}:{1}:listen'.format(
                    person.uuid, obj.id), True, 15)
                logger.debug(
                    'SET KEY '+'{0}:{1}:listen'.format(person.uuid, obj.id))
                return True
            elif person is not None:
                # Allow people to get their own recordings.
                return person == obj.person
        else:
            if request.method in ['PUT']:
                if request.user.is_staff:
                    return True
                if person is not None:
                    self.message = _(
                        "You're not allowed to edit this recording.")
                    return obj.person == person
        self.message = _("Reading recording is not allowed.")
        return False


class RecordingFetchViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all().order_by('pk')
    serializer_class = RecordingFetchSerializer
    permission_classes = (RecordingPermissions,)
    pagination_class = OneHundredResultPagination


class RecordingViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    list:
    API endpoint that allows recordings to be viewed or edited. This is used by
    staff only for GET requests. This is used by anyone to POST recordings.

    If a `sort_by` query is provided, we exclude recordings that have have
    one or more reviews.

    read:
    This api provides acces to a `audio_file_url` field. This allows the
    retrival of an audio file in the m4a container with the aac audio codec.
    To retrieve an audio file in the wave format at 16kHz and 16bits, append
    the query `?format=wav` to the url given by the `audio_file_url` field.

    `audio_file_url` provides an a link to an s3 object that will expire after
    a certain duration.

    create:
    You can post audio this API endpoint. If you have a Token, you can set
    `person="self"` which will assign the person of the token to the posted
    recording.

    ### Query Parameters
    The following query parameters are implemented.

    - `sort_by`: A number of sorting options are provided.

        The following will exclude Recordings that have one or more reviews.

        - `listen`, `random`, `recent`, `wer`, `-wer

        These will not exclude results

        - `num_approved`, `-num_approved`

    - `updated_after`

        Get recording objects that were updated after the provided datetime.
        Format is `'%Y-%m-%dT%H:%M:%S%z'`. If time zone offset is omited, we
        assume local time for the machine (likely +1200).

            /api/recordings/?updated_after=2016-10-03T19:00:00%2B0200

    - `encoding`

        Set the encoding of the posted file. Currently we only support
        `?encoding=base64` which will allow you to base64 encode a file
        and post as a normal string field for example when doing a json
        type post.

    - `filter` You can pass the following filters
        - `sentence:ID` - this returns recordings from a particular sentence.

    ### Metadata
    The metadata from Recording Metadata model is provided for convienince. 
    To update the metadata for recordings, you have to PUT to the
    `/api/recordingmetadata/{recording.id}/` endpoint. If no metadata
    exists, you need to first create it using a POST request to 
    `/api/recordingmetadata/`.


    """

    queryset = Recording.objects.all().order_by('pk')
    serializer_class = RecordingSerializer
    permission_classes = (RecordingPermissions,)
    pagination_class = TenResultPagination

    # parser_classes = (MultiPartParser, JSONParser, FormParser, )

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        # This might stuff up our documentation as self.request is none
        # when building docs.
        if self.request:
            if self.request.method == 'POST':
                enc = self.request.query_params.get('encoding', '')
                if enc == 'base64':
                    return RecordingSerializerPostBase64
                return RecordingSerializerPost

        return serializer_class

    def get_queryset(self):
        language = get_current_language(self.request)

        q = self.request.query_params.get('language', None)
        if q:
            for l in LANGUAGES:
                if q == l[0]:
                    language = q

        queryset = Recording.objects.filter(language=language)\
            .prefetch_related(
                Prefetch(
                    'quality_control',
                    queryset=RecordingQualityControl.objects.all()
                )
        )\
            .select_related('person', 'sentence', 'source')

        sort_by = self.request.query_params.get('sort_by', '')
        sort_by = sort_by.lower()
        person = get_person(self.request)

        if sort_by in ['listen', 'random', 'recent', 'wer', '-wer']:

            # Disable this for now
            # if sort_by not in 'recent':
            #    queryset = filter_qs_for_competition(queryset)

            # Could this be faster?
            if 'wer' not in sort_by:
                queryset = queryset\
                    .annotate(
                        reviewed=Case(
                            When(quality_control__approved=True, then=Value(1)),
                            When(quality_control__trash=True, then=Value(1)),
                            When(quality_control__good__gte=1, then=Value(1)),
                            When(quality_control__bad__gte=1, then=Value(1)),
                            When(quality_control__isnull=True, then=Value(0)),
                            # When(quality_control__follow_up=True, then=Value(0)),  # potential to kee; showing up - need to remove follow up
                            default=Value(1),
                            output_field=IntegerField()))\
                    .filter(reviewed=0)\
                    # .distinct()

            # If we want to handle simultaneous but recent
            # we could serve 5 sets of the most recent recordings
            # We should make sure each set is the length of the
            # pagination so that on getting the next page the dataset
            # is reset based on the filters above. This allows
            # us to keep hitting next. However the will eventull
            # get the same sentences again and so will need to approve
            # them. Otherwise we need to store a skip or "pass" on the
            # QC object.
            # shift = cache.get('recent_recording_shift')
            # cache.set('recent_recording_shift')

            if 'recent' in sort_by:
                queryset = queryset.order_by('-pk')
                return queryset
            elif 'wer' in sort_by:

                queryset = queryset\
                    .annotate(
                        reviewed=Case(
                            When(quality_control__approved=True, then=Value(1)),
                            When(quality_control__trash=True, then=Value(1)),
                            When(quality_control__good__gte=5, then=Value(1)),
                            When(quality_control__bad__gte=5, then=Value(1)),
                            When(quality_control__isnull=True, then=Value(0)),
                            default=Value(1),
                            output_field=IntegerField()))\
                    .filter(reviewed=0)\
                    .filter(transcription__word_error_rate__gte=0.05)

                if '-wer' in sort_by:
                    queryset = queryset.order_by(
                        'transcription__word_error_rate')
                else:
                    queryset = queryset.order_by(
                        '-transcription__word_error_rate')

                return queryset

            # We use these for comps, disabling for now as they're VERY slow.
            # queryset = filter_recordings_to_top_ten(queryset)
            # queryset = filter_recordings_distribute_reviews(queryset)

            # Here we return a single object, so rather than making a whole
            # new DB query lets be clever an use a cache. We'll need to get
            # the most recent recording that was served however...
            query_cache_key = '{0}:{1}:recording-viewset'.format(
                person.uuid, language)
            try:
                pk = get_random_pk_from_queryset(queryset, query_cache_key)
            except IndexError:
                return []
            return [Recording.objects.get(pk=pk)]

        updated_after = self.request.query_params.get('updated_after', None)
        if updated_after:

            date = parse_datetime(updated_after)
            if date is None:
                raise serializers.ValidationError("Improper datetime fromat.")
            q1 = queryset\
                .filter(updated__gte=date)\
                .annotate(changed=Max('updated'))  # Added as dummy for join.
            q2 = queryset\
                .filter(updated__lt=date)\
                .annotate(changed=Max('quality_control__updated'))\
                .filter(changed__gte=date)
            queryset = q1.union(q2)

        filter_by = self.request.query_params.get('filter')
        if filter_by:
            parts = filter_by.split(':')
            if len(parts) == 2:
                filt = parts[0].lower()
                value = parts[1]
                if filt == 'sentence':
                    queryset = queryset.filter(sentence__pk=value)

        if sort_by in ['num_approved', '-num_approved']:
            queryset = queryset.annotate(num_approved=Sum(
                Case(
                    When(
                        quality_control__approved=True,
                        then=Value(1)),
                    When(
                        quality_control__approved=False,
                        then=Value(0)),
                    When(
                        quality_control__isnull=True,
                        then=Value(0)),
                    default=Value(0),
                    output_field=IntegerField())
            ))
            queryset = queryset.order_by(sort_by)

        return queryset


class ListenPermissions(permissions.BasePermission):
    """
    Model permission to only allow anyone to get a recording.
    """

    def has_permission(self, request, view):
        logger.debug("listen perm has perm")
        if request.method in permissions.SAFE_METHODS:
            # Unregisted people can only listen up to 100 recordings
            return True
            # Registered people can only listen up to 1000 recordings
            # return request.user.is_staff
        else:
            self.message = _("{0} not allowed with this API\
                             endpoint.".format(request.method))
            return False

    def has_object_permission(self, request, view, obj):
        logger.debug("listen perm has object perm")
        if request.method in permissions.SAFE_METHODS:
            # We can create a short lived token here to allow someone to access
            # the file URL. We will need to store in the cache framework.
            person = get_person(request)
            if person is not None:
                uuid = person.uuid
            else:
                uuid = 'None-Person-Object'

            key = '{0}:{1}:listen'.format(uuid, obj.id)
            cache.set(key, True, 15)
            logger.debug('   CAN VIEW: {0} {1}'.format(key, True))
            return True
        else:
            self.message = _("{0} not allowed with this API\
                             endpoint.".format(request.method))
            return False


class ListenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a single recording to be viewed.
    This api obfuscates extra recording information and only provides the
    recording file link and the id.

    By default we exclude approved recordings, and we exclude listening to
    ones own recordings
    """

    queryset = Recording.objects.exclude(private=True)
    pagination_class = TenResultPagination
    serializer_class = ListenSerializer
    permission_classes = (ListenPermissions,)
    throttle_scope = 'listen'

    def get_queryset(self):
        person = get_person(self.request)
        logger.debug(person)
        language = get_current_language(self.request)

        q = self.request.query_params.get('language', None)
        if q:
            for l in LANGUAGES:
                if q == l[0]:
                    language = q

        # we should treat all anonymous usesrs as the same so we dont' overload shit!
        awhi = self.request.query_params.get('awhi', False)
        if awhi:
            # Awhi takes a sentence id and returns an approved recording with that sentence.
            try:
                pk = int(awhi)
            except:
                raise ValueError('You must pass an integer to the awhi field')

            recordings = Recording.objects\
                .filter(language=language)\
                .filter(sentence__pk=int(awhi))\
                .filter(quality_control__approved=True)\
                .first()

            # if len(recordings) > 0:
            #     query_cache_key = '{0}:{1}:listen-awhi'.format(pk, language)
            #     cpk = get_random_pk_from_queryset(recordings, query_cache_key)
            #     return [Recording.objects.get(pk=cpk)]

            return recordings

        # ctm = ContentTypeManager()

        if person:
            queryset = Recording.objects\
                .exclude(person=person)\
                .exclude(quality_control__person=person)
        else:
            queryset = Recording.objects.all()

        queryset = Recording.objects\
            .filter(language=language)\
            .filter(private=False)\
            .prefetch_related(
                Prefetch(
                    'quality_control',
                    queryset=RecordingQualityControl.objects.all()
                )
            )\
            .select_related('sentence')

        if self.request.user.is_staff:
            person_id = self.request.query_params.get('person_id', '')
            try:
                filtered_queryset = queryset.filter(person__id=person_id)
                if filtered_queryset.count() > 0:
                    queryset = filtered_queryset
            except:
                pass

        test_query = self.request.query_params.get('test_query', '')

        if test_query == 'exclude':
            queryset = queryset\
                .exclude(quality_control__approved=True) \
                .exclude(quality_control__trash=True) \
                .exclude(quality_control__bad__gte=1)\
                .exclude(quality_control__good__gte=1)

        elif test_query == 'when':
            queryset = queryset.annotate(reviewed=Sum(
                Case(
                    When(
                        quality_control__isnull=True,
                        then=Value(0)),
                    When(
                        quality_control__approved=True,
                        then=Value(1)),
                    When(
                        quality_control__bad__gte=1,
                        then=Value(1)),
                    When(
                        quality_control__good__gte=1,
                        then=Value(1)),
                    When(
                        quality_control__trash=True,
                        then=Value(1)),
                    When(
                        quality_control__person=person,
                        then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField())))\
                .filter(reviewed=0)
        else:

            # This strategy is fast but it means we only get one review per
            # item. It works for now until we reviewed everything.
            q1 = queryset\
                .annotate(num_qc=Count('quality_control'))\
                .filter(num_qc__lte=0)

            if q1.count() > 0:
                queryset = q1
            else:
                queryset = queryset\
                    .annotate(num_qc=Count('quality_control'))\
                    .filter(num_qc__lte=4)

        sort_by = self.request.query_params.get('sort_by', '')

        # Let's just get a random recording.
        '''
        queryset = queryset\
            .annotate(num_qc=Count('quality_control'))\
            .order_by('num_qc')
        '''

        if queryset.count() == 0:
            return []

        # Check if this is a /listen/ID url
        # logger.debug(self.request.path)
        # logger.debug(self.lookup_url_kwarg)
        # logger.debug(self.lookup_field)
        # logger.debug(self.kwargs)
        if self.lookup_field in self.kwargs.keys():
            return queryset

        if 'random' in sort_by.lower() or not self.request.user.is_staff:
            queryset = queryset \
                .filter(quality_control__isnull=True)

            logger.debug('this many without review: ' + str(queryset.count()))

            if person is not None:
                uuid = person.uuid
            else:
                uuid = 'None-Person-Object'

            query_cache_key = '{0}:{1}:listen-viewset'.format(uuid, language)
            try:
                pk = get_random_pk_from_queryset(queryset, query_cache_key)
            except IndexError:
                return queryset

            # This meanms we don't ahve to do the extra call
            key = '{0}:{1}:listen'.format(uuid, pk)
            cache.set(key, True, 15)

            return [Recording.objects.get(pk=pk)]

        logger.debug(queryset.count())
        return queryset


def get_random_pk_from_queryset(queryset, cache_key):
    '''
    Returns a random object from a queryset in the form of a queryset e.g. [obj].

    This function caches the original queryset and picks a new random object from
    the first set while excluding objects that were already returned. It sets a max
    list size so as to not blow up the cache size. It also randobly picks a block
    from a queryset that exceeepts the max size so as to introduce more randomness
    from the
    '''

    MAX_LIST_SIZE = 100

    queryset_cache_key = "{0}:avai-pks".format(cache_key)
    queryset_cache = cache.get(queryset_cache_key)

    if queryset_cache is None or len(queryset_cache) == 0:
        pks = list(queryset.values_list('pk', flat=True))
        queryset_cache = []
        loop_count = 0
        while len(queryset_cache) <= MAX_LIST_SIZE and len(pks) > 0:
            i = random.randint(0, len(pks) - 1)
            queryset_cache.append(pks.pop(i))

    if len(queryset_cache) == 0:
        raise IndexError('No items in list cache')
    pk = queryset_cache.pop()
    cache.set(queryset_cache_key, queryset_cache, 60*5)

    return pk


class RecordingMetadataViewSet(ViewSetCacheMixin, viewsets.ModelViewSet):
    """
    ### Recording Metadata
    This API allows us to associate any sort of metadata with each recording.

    Lookups for this API use the recording ID.
    `/api/recordingmetadata/{recording.id}/`
    """
    queryset = RecordingMetadata.objects.all()
    serializer_class = RecordingMetadataSerializer
    permission_classes = (PutOnlyStaffReadPermission,)
    pagination_class = OneHundredResultPagination
    lookup_field = 'recording'

    # def get_queryset(self):
    #     q = super().get_queryset()
    #     recording = self.request.query_params.get('recording', None)
    #     if recording:
    #         return q.filter(recording__pk=recording)
