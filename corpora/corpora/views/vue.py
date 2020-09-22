from django.views.generic import TemplateView

class VueFrontend(TemplateView):
    template_name = "universal/vue_frontend.html"
