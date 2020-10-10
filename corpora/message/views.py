from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import DetailView
from message.models import Message


class RenderEmailView(UserPassesTestMixin, TemplateView):
    template_name = "message/email/email_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = Message.objects.first()
        context['content'] = message.content
        context['messageID'] = message.pk
        email = self.request.GET.get('email', None)
        if email:
            context['email'] = email
        return context

    def test_func(self):
        return self.request.user.is_superuser


class MessageView(DetailView):
    model = Message
    template_name = "message/email/email_message.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        context['content'] = message.content
        email = self.request.GET.get('email', None)
        if email:
            context['email'] = email
        return context
