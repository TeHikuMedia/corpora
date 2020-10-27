from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic.detail import DetailView
from message.models import Message
from people.models import Person
from django.conf import settings
import jwt


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


class MessageView(UserPassesTestMixin, DetailView):
    model = Message
    template_name = "message/email/email_message.html"

    def test_func(self, **kwargs):
        '''
        Method to verify that someone can view this message
        '''

        if self.request.user.is_authenticated:
            if self.request.user.is_staff or self.request.user.is_superuser:
                return True

        token = self.request.GET.get('tokena', None)
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            except:
                return False
            email = payload['email']
            message = self.get_object()
            if message.pk != payload['message']:
                return False
            if Person.objects.filter(profile_email=email).exists():
                return True
            elif User.objects.filter(email=email).exists():
                return True
            else:
                return False

        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        message = self.get_object()
        context['content'] = message.content
        email = self.request.GET.get('email', None)
        if email:
            context['email'] = email
        return context
