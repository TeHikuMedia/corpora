from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.contrib.auth.models import User
from people.models import Person, KnownLanguage
from django.db.models import F
from corpus.models import Recording, RecordingQualityControl

class UserCheckView(UserPassesTestMixin, TemplateView):
    template_name = "universal/management.html"

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.is_superuser
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query = User.objects\
            .select_related('person')\
            .select_related('person__demographic')\
            .annotate(
                diff=(F('last_login')-F('date_joined')))\
            .order_by('diff')
        
        suspect = []
        for u in query:
            seconds = -1 if not u.diff else u.diff.total_seconds()

            if seconds < 200000:
                u.diff = seconds
                if u.person:
                    u.num_recordings = \
                        Recording.objects.filter(person=u.person).count()
                    u.num_reviewed = \
                        RecordingQualityControl.objects.filter(person=u.person).count()
                    u.known_language = \
                        KnownLanguage.objects.filter(person=u.person).first()
                suspect.append(u)

        context['suspect'] = suspect
        return context
