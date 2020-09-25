from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings

class UserCheckView(UserPassesTestMixin, TemplateView):
    template_name = "universal/management.html"

    def test_func(self):
    	return (
    		self.request.user.is_authenticated and
    		self.request.user.is_superuser
    	)
    