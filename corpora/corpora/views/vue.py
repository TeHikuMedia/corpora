from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

class VueFrontend(
		LoginRequiredMixin,
		TemplateView):
    login_url = '/login/'
    template_name = "universal/vue_frontend.html"
